'''
Created on Dec 18, 2018
Tensorflow Implementation of the Baseline Model, CFKG, in:
Wang Xiang et al. KGAT: Knowledge Graph Attention Network for Recommendation. In KDD 2019.
@author: Xiang Wang (xiangwang@u.nus.edu)
@modifiedBy: Paulo do Carmo on Dec, 2025
@converted to PyTorch: Oct, 2026
'''
import torch
from torch import nn

from framework.recommender.utils.device import resolve_device
from framework.recommender.utils.initializers import variance_scaling


class CFKG_model(nn.Module):
    def __init__(self, data_config, pretrain_data, args, device=None):
        super().__init__()

        self._parse_args(data_config, pretrain_data, args, device)

        self.weights = self._build_weights()

        # Optimization process (replaces tf.compat.v1.train.GradientDescentOptimizer).
        self.optimizer = torch.optim.SGD(self.parameters(), lr=self.lr)

        self._statistics_params()

    def _parse_args(self, data_config, pretrain_data, args, device):
        self.device = resolve_device(device)

        self.model_type = 'cfkg'

        self.pretrain_data = pretrain_data

        self.n_users = data_config['n_users']
        self.n_items = data_config['n_items']
        self.n_entities = data_config['n_entities']
        self.n_relations = data_config['n_relations']

        self.n_fold = 100

        self.margin = 1.0
        self.L1_flag = args.l1_flag

        self.lr = args.lr
        # settings for CF part.
        self.emb_dim = args.embed_size
        self.batch_size = args.batch_size

        # settings for KG part.
        self.kge_dim = args.kge_size

        self.weight_size = args.layer_size
        self.n_layers = len(self.weight_size)

        self.alg_type = args.alg_type
        self.model_type += '_%s_%s_%s_l%d' % (args.adj_type, args.adj_uni_type, args.alg_type, self.n_layers)

        self.regs = args.regs
        self.verbose = args.verbose

    def _build_weights(self):
        all_weights = nn.ParameterDict()

        if self.pretrain_data is None:
            all_weights['user_embed'] = nn.Parameter(
                variance_scaling((self.n_users, self.emb_dim), distribution="truncated_normal", scale=1.0, device=self.device))
            all_weights['entity_embed'] = nn.Parameter(
                variance_scaling((self.n_entities, self.emb_dim), distribution="truncated_normal", scale=1.0, device=self.device))
            print('using xavier initialization')
        else:
            user_embed = nn.Parameter(torch.as_tensor(self.pretrain_data['user_embed'], dtype=torch.float32, device=self.device))
            other_embed = variance_scaling((self.n_entities - self.n_items, self.emb_dim),
                                          distribution="truncated_normal", scale=1.0, device=self.device)
            all_weights['user_embed'] = user_embed
            all_weights['entity_embed'] = nn.Parameter(torch.cat([
                torch.as_tensor(self.pretrain_data['item_embed'], dtype=torch.float32, device=self.device),
                other_embed], dim=0))
            print('using pretrained initialization')

        all_weights['relation_embed'] = nn.Parameter(
            variance_scaling((self.n_relations, self.emb_dim), distribution="truncated_normal", scale=1.0, device=self.device))

        return all_weights

    def _get_kg_inference(self, h, r, pos_t, neg_t=None):
        embeddings = torch.cat([self.weights['user_embed'], self.weights['entity_embed']], dim=0)

        # head & tail entity embeddings: batch_size * emb_dim
        h_e = embeddings[h]
        pos_t_e = embeddings[pos_t]

        # relation embeddings: batch_size * emb_dim
        r_e = self.weights['relation_embed'][r]

        neg_t_e = embeddings[neg_t] if neg_t is not None else None

        return h_e, r_e, pos_t_e, neg_t_e

    def _forward_scores(self, batch):
        neg_t = batch.get('neg_t', None)
        h_e, r_e, pos_t_e, neg_t_e = self._get_kg_inference(batch['h'], batch['r'], batch['pos_t'], neg_t)

        if self.L1_flag:
            pos_kg_score = torch.sum(torch.abs(h_e + r_e - pos_t_e), dim=1, keepdim=True)
        else:
            pos_kg_score = torch.sum((h_e + r_e - pos_t_e) ** 2, dim=1, keepdim=True)

        batch_predictions = -pos_kg_score

        # At inference time (eval) only the positive triple is provided; the
        # triplet-margin loss and its regularizer are only meaningful at train time.
        if neg_t is not None:
            if self.L1_flag:
                neg_kg_score = torch.sum(torch.abs(h_e + r_e - neg_t_e), dim=1, keepdim=True)
            else:
                neg_kg_score = torch.sum((h_e + r_e - neg_t_e) ** 2, dim=1, keepdim=True)

            kg_loss = torch.mean(torch.clamp(pos_kg_score - neg_kg_score + self.margin, min=0.0))
        else:
            kg_loss = torch.zeros(1, dtype=torch.float32, device=self.device)

        reg_loss = torch.zeros(1, dtype=torch.float32, device=self.device)
        base_loss = torch.zeros(1, dtype=torch.float32, device=self.device)
        kge_loss = kg_loss
        loss = kge_loss + reg_loss

        return loss, base_loss, kge_loss, reg_loss, batch_predictions

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
        for key in ('h', 'r', 'pos_t', 'neg_t'):
            if key in batch:
                out[key] = torch.as_tensor(batch[key], dtype=torch.long, device=device)
        return out

    # Keep the original call surface: the (now unused) ``sess`` argument is
    # accepted so batch_test.py / helper.py / metrics.py stay untouched.
    def train(self, sess=None, feed_dict=None):
        batch = self._to_device(feed_dict)
        self.optimizer.zero_grad()
        loss, base_loss, kge_loss, reg_loss, _ = self._forward_scores(batch)
        loss.backward()
        self.optimizer.step()
        return None, loss.item(), base_loss.item(), kge_loss.item(), reg_loss.item()

    def eval(self, sess=None, feed_dict=None):
        self.training = False
        with torch.no_grad():
            batch = self._to_device(feed_dict)
            _, _, _, _, batch_predictions = self._forward_scores(batch)
        return batch_predictions.cpu().numpy()
