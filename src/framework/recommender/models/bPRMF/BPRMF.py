'''
Created on Dec 18, 2018
Tensorflow Implementation of the Baseline Model, BPRMF, in:
Wang Xiang et al. KGAT: Knowledge Graph Attention Network for Recommendation. In KDD 2019.
@author: Xiang Wang (xiangwang@u.nus.edu)
@modifiedBy: Paulo do Carmo on Dec, 2025
@converted to PyTorch: Oct, 2026
'''
import torch
from torch import nn

from framework.recommender.utils.device import resolve_device
from framework.recommender.utils.initializers import variance_scaling


class BPRMF_model(nn.Module):
    def __init__(self, data_config, pretrain_data, args, device=None):
        super().__init__()
        self.device = resolve_device(device)

        self.model_type = 'mf'
        self.pretrain_data = pretrain_data

        self.n_users = data_config['n_users']
        self.n_items = data_config['n_items']

        self.lr = args.lr

        self.emb_dim = args.embed_size
        self.batch_size = args.batch_size

        self.regs = args.regs

        self.verbose = args.verbose

        # Variable definition.
        self.weights = self._init_weights()

        # Optimization process (replaces tf.compat.v1.train.AdamOptimizer).
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)

        self._statistics_params()

    def _init_weights(self):
        all_weights = nn.ParameterDict()

        if self.pretrain_data is None:
            user = nn.Parameter(variance_scaling((self.n_users, self.emb_dim), distribution="uniform", scale=1.0, device=self.device))
            item = nn.Parameter(variance_scaling((self.n_items, self.emb_dim), distribution="uniform", scale=1.0, device=self.device))
            print('using xavier initialization')
        else:
            user = nn.Parameter(torch.as_tensor(self.pretrain_data['user_embed'], dtype=torch.float32, device=self.device))
            item = nn.Parameter(torch.as_tensor(self.pretrain_data['item_embed'], dtype=torch.float32, device=self.device))
            print('using pretrained initialization')

        all_weights['user_embedding'] = user
        all_weights['item_embedding'] = item
        return all_weights

    def _create_bpr_loss(self, u_e, pos_i_e, neg_i_e):
        pos_scores = torch.sum(u_e * pos_i_e, dim=1)
        neg_scores = torch.sum(u_e * neg_i_e, dim=1)

        regularizer = (u_e ** 2).sum() + (pos_i_e ** 2).sum() + (neg_i_e ** 2).sum()

        maxi = torch.log(torch.sigmoid(pos_scores - neg_scores))
        mf_loss = -maxi.mean()
        reg_loss = self.regs[0] * regularizer

        return mf_loss, reg_loss

    def _forward_scores(self, batch):
        u_e = self.weights['user_embedding'][batch['users']]
        pos_i_e = self.weights['item_embedding'][batch['pos_items']]
        neg_i_e = self.weights['item_embedding'][batch['neg_items']]

        base_loss, reg_loss = self._create_bpr_loss(u_e, pos_i_e, neg_i_e)
        kge_loss = torch.zeros(1, dtype=torch.float32, device=self.device)
        loss = base_loss + kge_loss + reg_loss
        return loss, base_loss, kge_loss, reg_loss

    def predict(self, batch):
        u_e = self.weights['user_embedding'][batch['users']]
        i_e = self.weights['item_embedding'][batch['items']]
        return torch.mm(u_e, i_e.t())

    def _to_device(self, batch):
        device = self.device
        out = {}
        for key in ('users', 'pos_items', 'neg_items', 'items'):
            if key in batch:
                out[key] = torch.as_tensor(batch[key], dtype=torch.long, device=device)
        return out

    def _statistics_params(self):
        total_parameters = 0
        for param in self.parameters():
            variable_parameters = 1
            for dim in param.shape:
                variable_parameters *= dim
            total_parameters += variable_parameters
        if self.verbose > 0:
            print(f"#params: {total_parameters}")

    # Keep the original call surface: the (now unused) ``sess`` argument is
    # accepted so batch_test.py / helper.py / metrics.py stay untouched.
    def train(self, sess=None, feed_dict=None):
        batch = self._to_device(feed_dict)
        self.optimizer.zero_grad()
        loss, base_loss, kge_loss, reg_loss = self._forward_scores(batch)
        loss.backward()
        self.optimizer.step()
        return None, loss.item(), base_loss.item(), kge_loss.item(), reg_loss.item()

    def eval(self, sess=None, feed_dict=None):
        self.training = False
        with torch.no_grad():
            batch = self._to_device(feed_dict)
            batch_predictions = self.predict(batch)
        return batch_predictions.cpu().numpy()
