'''
Created on Dec 18, 2018
Tensorflow Implementation of the Baseline Model, CKE, in:
Wang Xiang et al. KGAT: Knowledge Graph Attention Network for Recommendation. In KDD 2019.
@author: Xiang Wang (xiangwang@u.nus.edu)
@modifiedBy: Paulo do Carmo on Dec, 2025
@converted to PyTorch: Oct, 2026
'''
import torch
from torch import nn

from framework.recommender.utils.device import resolve_device
from framework.recommender.utils.initializers import variance_scaling


class CKE_model(nn.Module):
    def __init__(self, data_config, pretrain_data, args, device=None):
        super().__init__()
        self._parse_args(data_config, pretrain_data, args, device)
        self.weights = self._build_weights()
        # Optimization process (replaces tf.compat.v1.train.AdamOptimizer).
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        self._statistics_params()

    def _parse_args(self, data_config, pretrain_data, args, device):
        self.device = resolve_device(device)

        self.model_type = 'cke'
        self.pretrain_data = pretrain_data

        self.n_users = data_config['n_users']
        self.n_items = data_config['n_items']
        self.n_entities = data_config['n_entities']
        self.n_relations = data_config['n_relations']

        self.lr = args.lr
        # settings for CF part.
        self.emb_dim = args.embed_size
        self.batch_size = args.batch_size

        # settings for KG part.
        self.kge_dim = args.kge_size

        self.regs = args.regs

        self.verbose = args.verbose

    def _build_weights(self):
        all_weights = nn.ParameterDict()

        if self.pretrain_data is None:
            all_weights['user_embed'] = nn.Parameter(
                variance_scaling((self.n_users, self.emb_dim), distribution="uniform", scale=1.0, device=self.device))
            all_weights['item_embed'] = nn.Parameter(
                variance_scaling((self.n_items, self.emb_dim), distribution="uniform", scale=1.0, device=self.device))
            print('using xavier initialization')
        else:
            all_weights['user_embed'] = nn.Parameter(
                torch.as_tensor(self.pretrain_data['user_embed'], dtype=torch.float32, device=self.device))
            all_weights['item_embed'] = nn.Parameter(
                torch.as_tensor(self.pretrain_data['item_embed'], dtype=torch.float32, device=self.device))
            print('using pretrained initialization')

        all_weights['kg_entity_embed'] = nn.Parameter(
            variance_scaling((self.n_entities, 1, self.emb_dim), distribution="uniform", scale=1.0, device=self.device))
        all_weights['kg_relation_embed'] = nn.Parameter(
            variance_scaling((self.n_relations, self.kge_dim), distribution="uniform", scale=1.0, device=self.device))
        all_weights['trans_W'] = nn.Parameter(
            variance_scaling((self.n_relations, self.emb_dim, self.kge_dim), distribution="uniform", scale=1.0, device=self.device))

        return all_weights

    def _get_kg_inference(self, h, r, pos_t, neg_t):
        # head & tail entity embeddings: batch_size * 1 * emb_dim
        h_e = self.weights['kg_entity_embed'][h]
        pos_t_e = self.weights['kg_entity_embed'][pos_t]
        neg_t_e = self.weights['kg_entity_embed'][neg_t]

        # relation embeddings: batch_size * kge_dim
        r_e = self.weights['kg_relation_embed'][r]

        # relation transform weights: batch_size * kge_dim * emb_dim
        trans_M = self.weights['trans_W'][r]

        # batch_size * 1 * kge_dim -> batch_size * kge_dim
        h_e = torch.matmul(h_e, trans_M)
        pos_t_e = torch.matmul(pos_t_e, trans_M)
        neg_t_e = torch.matmul(neg_t_e, trans_M)

        # l2-normalize (epsilon=1e-12 matches tf.math.l2_normalize default)
        h_e = torch.nn.functional.normalize(h_e, p=2, dim=1, eps=1e-12)
        r_e = torch.nn.functional.normalize(r_e, p=2, dim=1, eps=1e-12)
        pos_t_e = torch.nn.functional.normalize(pos_t_e, p=2, dim=1, eps=1e-12)
        neg_t_e = torch.nn.functional.normalize(neg_t_e, p=2, dim=1, eps=1e-12)

        return h_e, r_e, pos_t_e, neg_t_e

    def _get_cf_inference(self, u, pos_i, neg_i):
        u_e = self.weights['user_embed'][u]
        pos_i_e = self.weights['item_embed'][pos_i]
        neg_i_e = self.weights['item_embed'][neg_i]

        pos_i_kg_e = self.weights['kg_entity_embed'][pos_i].reshape(-1, self.emb_dim)
        neg_i_kg_e = self.weights['kg_entity_embed'][neg_i].reshape(-1, self.emb_dim)

        return u_e, pos_i_e + pos_i_kg_e, neg_i_e + neg_i_kg_e

    def _get_kg_loss(self, h_e, r_e, pos_t_e, neg_t_e):
        def _get_kg_score(h_e, r_e, t_e):
            kg_score = torch.sum((h_e + r_e - t_e) ** 2, dim=1, keepdim=True)
            return kg_score

        pos_kg_score = _get_kg_score(h_e, r_e, pos_t_e)
        neg_kg_score = _get_kg_score(h_e, r_e, neg_t_e)

        # BPR hinge as ``-log(sigmoid(neg - pos))``. Written as
        # ``F.softplus(-(neg - pos))`` it is the exact same loss (since
        # ``-log(sigmoid(x)) == softplus(-x)``) but avoids the ``log(0)`` that
        # ``torch.log(torch.sigmoid(...))`` produces when the margin is large and
        # negative. Mirrors the KGAT / cFKG ports in this codebase.
        kg_loss = torch.nn.functional.softplus(-(neg_kg_score - pos_kg_score)).mean()
        kg_reg_loss = (h_e ** 2).sum() + (r_e ** 2).sum() + (pos_t_e ** 2).sum() + (neg_t_e ** 2).sum()

        return kg_loss, kg_reg_loss

    def _get_cf_loss(self, u_e, pos_i_e, neg_i_e):
        def _get_cf_score(u_e, i_e):
            cf_score = torch.sum(u_e * i_e, dim=1)
            return cf_score

        pos_cf_score = _get_cf_score(u_e, pos_i_e)
        neg_cf_score = _get_cf_score(u_e, neg_i_e)

        maxi = torch.log(1e-10 + torch.sigmoid(pos_cf_score - neg_cf_score))
        cf_loss = -maxi.mean()
        cf_reg_loss = (u_e ** 2).sum() + (pos_i_e ** 2).sum() + (neg_i_e ** 2).sum()

        return cf_loss, cf_reg_loss

    def _forward_loss(self, batch):
        u_e, pos_i_e, neg_i_e = self._get_cf_inference(batch['u'], batch['pos_i'], batch['neg_i'])
        h_e, r_e, pos_t_e, neg_t_e = self._get_kg_inference(batch['h'], batch['r'], batch['pos_t'], batch['neg_t'])

        kg_loss, kg_reg_loss = self._get_kg_loss(h_e, r_e, pos_t_e, neg_t_e)
        cf_loss, cf_reg_loss = self._get_cf_loss(u_e, pos_i_e, neg_i_e)

        base_loss = cf_loss
        kge_loss = kg_loss
        reg_loss = self.regs[0] * cf_reg_loss + self.regs[1] * kg_reg_loss
        loss = base_loss + kge_loss + reg_loss

        return loss, base_loss, kge_loss, reg_loss

    def predict(self, batch):
        u_e = self.weights['user_embed'][batch['u']]
        pos_i_e = self.weights['item_embed'][batch['pos_i']]
        pos_i_kg_e = self.weights['kg_entity_embed'][batch['pos_i']].reshape(-1, self.emb_dim)
        return torch.mm(u_e, (pos_i_e + pos_i_kg_e).t())

    def _statistics_params(self):
        total_parameters = 0
        for param in self.parameters():
            variable_parameters = 1
            for dim in param.shape:
                variable_parameters *= dim
            total_parameters += variable_parameters
        if self.verbose > 0:
            print("#params: %d" % total_parameters)

    def _to_device(self, batch):
        device = self.device
        out = {}
        for key in ('u', 'pos_i', 'neg_i', 'h', 'r', 'pos_t', 'neg_t'):
            if key in batch:
                out[key] = torch.as_tensor(batch[key], dtype=torch.long, device=device)
        return out

    # Keep the original call surface: the (now unused) ``sess`` argument is
    # accepted so batch_test.py / helper.py / metrics.py stay untouched.
    def train(self, sess=None, feed_dict=None):
        batch = self._to_device(feed_dict)
        self.optimizer.zero_grad()
        loss, base_loss, kge_loss, reg_loss = self._forward_loss(batch)
        loss.backward()
        self.optimizer.step()
        return None, loss.item(), base_loss.item(), kge_loss.item(), reg_loss.item()

    def eval(self, sess=None, feed_dict=None):
        self.training = False
        with torch.no_grad():
            batch = self._to_device(feed_dict)
            batch_predictions = self.predict(batch)
        return batch_predictions.cpu().numpy()
