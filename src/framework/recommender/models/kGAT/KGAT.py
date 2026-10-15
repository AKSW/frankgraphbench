'''
Created on Dec 18, 2018
Tensorflow Implementation of Knowledge Graph Attention Network (KGAT) model in:
Wang Xiang et al. KGAT: Knowledge Graph Attention Network for Recommendation. In KDD 2019.
@author: Xiang Wang (xiangwang@u.nus.edu)
@modifiedBy: Paulo do Carmo on Dec, 2025
@converted to PyTorch: Oct, 2026
@attentive-A re-plug (recompute per epoch): Oct, 2026
'''
import numpy as np
import scipy.sparse as sp
import torch
import torch.nn.functional as F
from torch import nn

from framework.recommender.utils.device import resolve_device, resolve_sparse_device
from framework.recommender.utils.initializers import variance_scaling


class KGAT_model(nn.Module):
    def __init__(self, data_config, pretrain_data, args, device=None):
        super().__init__()

        self._parse_args(data_config, pretrain_data, args, device)

        # The sparse attentive adjacency is consumed by ``torch.sparse.mm``. The
        # Apple Metal (MPS) backend has no sparse-matmul kernel, so when the model
        # runs on MPS the adjacency is kept on the CPU and the dense embedding is
        # shuttled across for the multiply; otherwise it shares the model device.
        self.sparse_device = resolve_sparse_device(self.device)

        """
        *********************************************************
        Create Model Parameters for CF & KGE parts.
        """
        self.weights = self._build_weights()

        """
        *********************************************************
        Compute Graph-based Representations of All Users & Items & KG Entities via
        Message-Passing Mechanism of Graph Neural Networks.

        Behaviour note:
        ``_A_sparse`` holds the sparse attentive adjacency consumed by the GNN
        message-passing (``_neighbor_embeddings``). It is (re)built from
        ``self.A_in`` at construction time, and ``update_attentive_A`` refreshes
        it at the end of every call so that the *next* forward pass runs on the
        newly recomputed attentive laplacian. This is the intended KGAT
        behaviour: the attentive matrix A is re-estimated each epoch from the
        current embeddings and fed back into the GNN.
        """
        self._A_sparse = self._to_torch_sparse(self.A_in, device=self.sparse_device)

        """
        Optimize Recommendation (CF) Part via BPR Loss.
        """
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)

        """
        Optimize KGE Part via BPR Loss.
        """
        self.optimizer2 = torch.optim.Adam(self.parameters(), lr=self.lr)

        self._statistics_params()

    def _parse_args(self, data_config, pretrain_data, args, device):
        self.device = resolve_device(device)

        # argument settings
        self.model_type = 'kgat'

        self.pretrain_data = pretrain_data

        self.n_users = data_config['n_users']
        self.n_items = data_config['n_items']
        self.n_entities = data_config['n_entities']
        self.n_relations = data_config['n_relations']

        self.n_fold = 100

        # initialize the attentive matrix A for phase I.
        self.A_in = data_config['A_in']

        self.all_h_list = data_config['all_h_list']
        self.all_r_list = data_config['all_r_list']
        self.all_t_list = data_config['all_t_list']
        self.all_v_list = data_config['all_v_list']

        self.adj_uni_type = args.adj_uni_type

        self.lr = args.lr

        # settings for CF part.
        self.emb_dim = args.embed_size
        self.batch_size = args.batch_size

        # settings for KG part.
        self.kge_dim = args.kge_size
        self.batch_size_kg = args.batch_size_kg

        self.weight_size = args.layer_size
        self.n_layers = len(self.weight_size)

        self.alg_type = args.alg_type
        self.model_type += '_%s_%s_%s_l%d' % (args.adj_type, args.adj_uni_type, args.alg_type, self.n_layers)

        self.regs = args.regs
        self.verbose = args.verbose

        self.mess_dropout = list(getattr(args, 'mess_dropout', [0.] * self.n_layers))
        self.node_dropout = list(getattr(args, 'node_dropout', [0.] * self.n_layers))

    def _build_weights(self):
        all_weights = nn.ParameterDict()

        if self.pretrain_data is None:
            all_weights['user_embed'] = nn.Parameter(
                variance_scaling((self.n_users, self.emb_dim), distribution="uniform", scale=1.0, device=self.device))
            all_weights['entity_embed'] = nn.Parameter(
                variance_scaling((self.n_entities, self.emb_dim), distribution="uniform", scale=1.0, device=self.device))
            print('using xavier initialization')
        else:
            user_embed = self.pretrain_data['user_embed']
            item_embed = self.pretrain_data['item_embed']
            other_embed = variance_scaling((self.n_entities - self.n_items, self.emb_dim),
                                          distribution="uniform", scale=1.0, device=self.device)
            all_weights['user_embed'] = nn.Parameter(torch.as_tensor(user_embed, dtype=torch.float32, device=self.device))
            all_weights['entity_embed'] = nn.Parameter(
                torch.cat([torch.as_tensor(item_embed, dtype=torch.float32, device=self.device), other_embed], dim=0))
            print('using pretrained initialization')

        all_weights['relation_embed'] = nn.Parameter(
            variance_scaling((self.n_relations, self.kge_dim), distribution="uniform", scale=1.0, device=self.device))
        all_weights['trans_W'] = nn.Parameter(
            variance_scaling((self.n_relations, self.emb_dim, self.kge_dim), distribution="uniform", scale=1.0, device=self.device))

        self.weight_size_list = [self.emb_dim] + self.weight_size

        for k in range(self.n_layers):
            all_weights['W_gc_%d' % k] = nn.Parameter(
                variance_scaling((self.weight_size_list[k], self.weight_size_list[k + 1]), distribution="uniform", scale=1.0, device=self.device))
            all_weights['b_gc_%d' % k] = nn.Parameter(
                variance_scaling((1, self.weight_size_list[k + 1]), distribution="uniform", scale=1.0, device=self.device))

            all_weights['W_bi_%d' % k] = nn.Parameter(
                variance_scaling((self.weight_size_list[k], self.weight_size_list[k + 1]), distribution="uniform", scale=1.0, device=self.device))
            all_weights['b_bi_%d' % k] = nn.Parameter(
                variance_scaling((1, self.weight_size_list[k + 1]), distribution="uniform", scale=1.0, device=self.device))

            all_weights['W_mlp_%d' % k] = nn.Parameter(
                variance_scaling((2 * self.weight_size_list[k], self.weight_size_list[k + 1]), distribution="uniform", scale=1.0, device=self.device))
            all_weights['b_mlp_%d' % k] = nn.Parameter(
                variance_scaling((1, self.weight_size_list[k + 1]), distribution="uniform", scale=1.0, device=self.device))

        return all_weights

    @staticmethod
    def _to_torch_sparse(A_in, device=None):
        coo = A_in.tocoo()
        coo = coo.asfptype()
        indices = torch.stack([
            torch.as_tensor(coo.row, dtype=torch.int64),
            torch.as_tensor(coo.col, dtype=torch.int64),
        ], dim=0)
        values = torch.as_tensor(np.asarray(coo.data, dtype=np.float32))
        shape = torch.Size((coo.shape[0], coo.shape[1]))
        sparse = torch.sparse_coo_tensor(indices, values, shape).coalesce()
        # The sparse adjacency is consumed by ``torch.sparse.mm`` against the
        # (device-resident) embeddings, so it must live on the same device as the
        # embeddings it multiplies. Without this, the CPU-built COO tensor would
        # be passed to an MPS/CUDA op, raising "Passed CPU tensor to MPS op".
        if device is not None:
            sparse = sparse.to(device)
        return sparse

    def _neighbor_embeddings(self, ego_embeddings):
        # The original folds A_in into self.n_fold row-partitions, matmuls each, and
        # concatenates the per-fold results. Concatenating row-partitioned matmul
        # outputs is identical to a single sparse matmul, so we use one for clarity.
        #
        # ``torch.sparse.mm`` is not available on the MPS backend, so when the
        # adjacency lives on a different device than the embedding (i.e. MPS), the
        # dense embedding is moved onto the adjacency device for the multiply and
        # the result is moved back to the model device.
        result_device = ego_embeddings.device
        if self._A_sparse.device != ego_embeddings.device:
            ego_embeddings = ego_embeddings.to(self._A_sparse.device)
            result_device = self.device
        return torch.sparse.mm(self._A_sparse, ego_embeddings).to(result_device)

    def _create_bi_interaction_embed(self):
        ego_embeddings = torch.cat([self.weights['user_embed'], self.weights['entity_embed']], dim=0)
        all_embeddings = [ego_embeddings]

        for k in range(0, self.n_layers):
            # sum messages of neighbors.
            side_embeddings = self._neighbor_embeddings(ego_embeddings)

            add_embeddings = ego_embeddings + side_embeddings

            # transformed sum messages of neighbors.
            sum_embeddings = F.leaky_relu(
                ego_embeddings @ self.weights['W_gc_%d' % k] + self.weights['b_gc_%d' % k])

            # bi messages of neighbors.
            bi_embeddings = ego_embeddings * side_embeddings
            # transformed bi messages of neighbors.
            bi_embeddings = F.leaky_relu(
                bi_embeddings @ self.weights['W_bi_%d' % k] + self.weights['b_bi_%d' % k])

            ego_embeddings = bi_embeddings + sum_embeddings

            # message dropout (rate == mess_dropout[k]; 0 during eval).
            p = self.mess_dropout[k] if k < len(self.mess_dropout) else 0.
            ego_embeddings = F.dropout(ego_embeddings, p=p, training=self.training)

            # normalize the distribution of embeddings.
            norm_embeddings = F.normalize(ego_embeddings, p=2, dim=1, eps=1e-12)

            all_embeddings += [norm_embeddings]

        all_embeddings = torch.cat(all_embeddings, dim=1)
        ua_embeddings, ea_embeddings = torch.split(all_embeddings, [self.n_users, self.n_entities], dim=0)
        return ua_embeddings, ea_embeddings

    def _create_gcn_embed(self):
        embeddings = torch.cat([self.weights['user_embed'], self.weights['entity_embed']], dim=0)
        all_embeddings = [embeddings]

        for k in range(0, self.n_layers):
            embeddings = self._neighbor_embeddings(embeddings)
            embeddings = F.leaky_relu(
                embeddings @ self.weights['W_gc_%d' % k] + self.weights['b_gc_%d' % k])

            p = self.mess_dropout[k] if k < len(self.mess_dropout) else 0.
            embeddings = F.dropout(embeddings, p=p, training=self.training)

            # normalize the distribution of embeddings.
            norm_embeddings = F.normalize(embeddings, p=2, dim=1, eps=1e-12)
            all_embeddings += [norm_embeddings]

        all_embeddings = torch.cat(all_embeddings, dim=1)
        ua_embeddings, ea_embeddings = torch.split(all_embeddings, [self.n_users, self.n_entities], dim=0)
        return ua_embeddings, ea_embeddings

    def _create_graphsage_embed(self):
        pre_embeddings = torch.cat([self.weights['user_embed'], self.weights['entity_embed']], dim=0)

        all_embeddings = [pre_embeddings]
        for k in range(self.n_layers):
            # line 1 in algorithm 1 [RM-GCN, KDD'2018], aggregator layer: weighted sum
            embeddings = self._neighbor_embeddings(pre_embeddings)

            # line 2 in algorithm 1 [RM-GCN, KDD'2018], aggregating the previous embeddings
            embeddings = torch.cat([pre_embeddings, embeddings], dim=1)
            pre_embeddings = F.relu(
                embeddings @ self.weights['W_mlp_%d' % k] + self.weights['b_mlp_%d' % k])

            p = self.mess_dropout[k] if k < len(self.mess_dropout) else 0.
            pre_embeddings = F.dropout(pre_embeddings, p=p, training=self.training)

            # normalize the distribution of embeddings.
            norm_embeddings = F.normalize(embeddings, p=2, dim=1, eps=1e-12)
            all_embeddings += [norm_embeddings]

        all_embeddings = torch.cat(all_embeddings, dim=1)
        ua_embeddings, ea_embeddings = torch.split(all_embeddings, [self.n_users, self.n_entities], dim=0)
        return ua_embeddings, ea_embeddings

    def _gcn_embeddings(self):
        if self.alg_type in ['bi', 'kgat']:
            return self._create_bi_interaction_embed()
        elif self.alg_type in ['gcn']:
            return self._create_gcn_embed()
        elif self.alg_type in ['graphsage']:
            return self._create_graphsage_embed()
        else:
            print('please check the the alg_type argument, which should be bi, kgat, gcn, or graphsage.')
            raise NotImplementedError

    def _get_kg_inference(self, h, r, pos_t, neg_t=None):
        embeddings = torch.cat([self.weights['user_embed'], self.weights['entity_embed']], dim=0)
        embeddings = embeddings.unsqueeze(1)

        # head & tail entity embeddings: batch_size *1 * emb_dim
        h_e = embeddings[h]
        pos_t_e = embeddings[pos_t]

        # relation embeddings: batch_size * kge_dim
        r_e = self.weights['relation_embed'][r]

        # relation transform weights: batch_size * kge_dim * emb_dim
        trans_M = self.weights['trans_W'][r]

        # ``h_e``/``pos_t_e``/``neg_t_e`` come out of the matmul as
        # (batch, 1, kge_dim) because ``embeddings`` was unsqueezed. The relation
        # embedding ``r_e`` is 2-D (batch, kge_dim), so without reshaping the
        # (h_e + r_e - t_e) term in ``_get_kg_score`` would broadcast the two
        # operands into (batch, batch, kge_dim) and materialise a batch^2 x kge_dim
        # intermediate (hundreds of GiB for this dataset). Collapse the spurious
        # middle dimension to (batch, kge_dim) so the transE score is computed
        # per-sample, matching ``_generate_transE_score`` and the original TF model.
        h_e = torch.reshape(torch.matmul(h_e, trans_M), [-1, self.kge_dim])
        pos_t_e = torch.reshape(torch.matmul(pos_t_e, trans_M), [-1, self.kge_dim])

        neg_t_e = None
        if neg_t is not None:
            neg_t_e = embeddings[neg_t]
            neg_t_e = torch.reshape(torch.matmul(neg_t_e, trans_M), [-1, self.kge_dim])

        return h_e, r_e, pos_t_e, neg_t_e

    def _forward_phase_I(self, batch):
        ua_embeddings, ea_embeddings = self._gcn_embeddings()

        u_e = ua_embeddings[batch['users']]
        pos_i_e = ea_embeddings[batch['pos_items']]
        neg_i_e = ea_embeddings[batch['neg_items']]

        pos_scores = torch.sum(u_e * pos_i_e, dim=1)
        neg_scores = torch.sum(u_e * neg_i_e, dim=1)

        regularizer = (u_e ** 2).sum() + (pos_i_e ** 2).sum() + (neg_i_e ** 2).sum()
        regularizer = regularizer / self.batch_size

        # Using the softplus as BPR loss to avoid the nan error.
        base_loss = F.softplus(-(pos_scores - neg_scores)).mean()
        kge_loss = torch.zeros(1, dtype=torch.float32, device=self.device)
        reg_loss = self.regs[0] * regularizer
        loss = base_loss + kge_loss + reg_loss

        return loss, base_loss, kge_loss, reg_loss

    def _forward_phase_II(self, batch):
        h_e, r_e, pos_t_e, neg_t_e = self._get_kg_inference(
            batch['h'], batch['r'], batch['pos_t'], batch['neg_t'])

        def _get_kg_score(h_e, r_e, t_e):
            kg_score = torch.sum((h_e + r_e - t_e) ** 2, dim=1, keepdim=True)
            return kg_score

        pos_kg_score = _get_kg_score(h_e, r_e, pos_t_e)
        neg_kg_score = _get_kg_score(h_e, r_e, neg_t_e)

        # Using the softplus as BPR loss to avoid the nan error.
        kg_loss = F.softplus(-(neg_kg_score - pos_kg_score)).mean()

        kg_reg_loss = (h_e ** 2).sum() + (r_e ** 2).sum() + (pos_t_e ** 2).sum() + (neg_t_e ** 2).sum()
        kg_reg_loss = kg_reg_loss / self.batch_size_kg

        kge_loss2 = kg_loss
        reg_loss2 = self.regs[1] * kg_reg_loss
        loss2 = kge_loss2 + reg_loss2

        return loss2, kge_loss2, reg_loss2

    def predict(self, batch):
        ua_embeddings, ea_embeddings = self._gcn_embeddings()
        u_e = ua_embeddings[batch['users']]
        pos_i_e = ea_embeddings[batch['pos_items']]
        return torch.mm(u_e, pos_i_e.t())

    def _generate_transE_score(self, h, r, t):
        embeddings = torch.cat([self.weights['user_embed'], self.weights['entity_embed']], dim=0)
        embeddings = embeddings.unsqueeze(1)

        h_e = embeddings[h]
        t_e = embeddings[t]

        # relation embeddings: batch_size * kge_dim
        r_e = self.weights['relation_embed'][r]

        # relation transform weights: batch_size * kge_dim * emb_dim
        trans_M = self.weights['trans_W'][r]

        # batch_size * 1 * kge_dim -> batch_size * kge_dim
        h_e = torch.reshape(torch.matmul(h_e, trans_M), [-1, self.kge_dim])
        t_e = torch.reshape(torch.matmul(t_e, trans_M), [-1, self.kge_dim])

        kg_score = torch.sum(t_e * torch.tanh(h_e + r_e), dim=1)
        return kg_score

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
        for key in ('users', 'pos_items', 'neg_items', 'h', 'r', 'pos_t', 'neg_t'):
            if key in batch:
                out[key] = torch.as_tensor(batch[key], dtype=torch.long, device=device)
        return out

    # Keep the original call surface: the (now unused) ``sess`` argument is
    # accepted so batch_test.py / helper.py / metrics.py stay untouched.
    #
    # ``train`` / ``eval`` shadow nn.Module.train()/eval(); we manage the
    # ``self.training`` flag ourselves so F.dropout switches on/off correctly.
    def train(self, sess=None, feed_dict=None):
        self.training = True
        batch = self._to_device(feed_dict)
        self.optimizer.zero_grad()
        loss, base_loss, kge_loss, reg_loss = self._forward_phase_I(batch)
        loss.backward()
        self.optimizer.step()
        return None, loss.item(), base_loss.item(), kge_loss.item(), reg_loss.item()

    def train_A(self, sess=None, feed_dict=None):
        self.training = True
        batch = self._to_device(feed_dict)
        self.optimizer2.zero_grad()
        loss2, kge_loss2, reg_loss2 = self._forward_phase_II(batch)
        loss2.backward()
        self.optimizer2.step()
        return None, loss2.item(), kge_loss2.item(), reg_loss2.item()

    def eval(self, sess=None, feed_dict=None):
        self.training = False
        with torch.no_grad():
            batch = self._to_device(feed_dict)
            batch_predictions = self.predict(batch)
        return batch_predictions.cpu().numpy()

    # Recompute the attentive laplacian matrix from the current embeddings and
    # re-plug it into the GNN: the freshly computed ``self.A_in`` is converted to
    # a sparse tensor and stored in ``self._A_sparse`` so that the subsequent
    # forward pass (``_gcn_embeddings`` -> ``_neighbor_embeddings``) operates on
    # the updated attentive adjacency. This is the intended KGAT behaviour.
    def update_attentive_A(self, sess=None):
        fold_len = len(self.all_h_list) // self.n_fold
        kg_score = []

        with torch.no_grad():
            for i_fold in range(self.n_fold):
                start = i_fold * fold_len
                if i_fold == self.n_fold - 1:
                    end = len(self.all_h_list)
                else:
                    end = (i_fold + 1) * fold_len

                if start == end:
                    continue

                h = torch.as_tensor(self.all_h_list[start:end], dtype=torch.long, device=self.device)
                r = torch.as_tensor(self.all_r_list[start:end], dtype=torch.long, device=self.device)
                pos_t = torch.as_tensor(self.all_t_list[start:end], dtype=torch.long, device=self.device)

                A_kg_score = self._generate_transE_score(h, r, pos_t)
                kg_score += list(A_kg_score.cpu().numpy())

        kg_score = np.array(kg_score)

        new_A_values = self._row_softmax(np.asarray(self.all_h_list, dtype=np.int64), kg_score)
        rows = np.asarray(self.all_h_list, dtype=np.int64)
        cols = np.asarray(self.all_t_list, dtype=np.int64)
        self.A_in = sp.coo_matrix((new_A_values, (rows, cols)),
                                  shape=(self.n_users + self.n_entities,
                                        self.n_users + self.n_entities))
        if self.alg_type in ['org', 'gcn']:
            self.A_in.setdiag(1.)

        # Re-plug the updated attentive adjacency into the GNN so the next
        # forward pass uses it.
        self._A_sparse = self._to_torch_sparse(self.A_in, device=self.sparse_device)

    @staticmethod
    def _row_softmax(rows, values):
        """Per-row softmax over a canonically-sorted sparse pattern.

        Reproduces ``tf.sparse.softmax`` on the (rows, values) pair: rows are
        assumed sorted ascending with contiguous per-row blocks (the loader sorts
        all_h_list / all_t_list for exactly this reason).
        """
        rows = np.asarray(rows, dtype=np.int64)
        values = np.asarray(values, dtype=np.float32)
        n = values.shape[0]
        if n == 0:
            return values
        uniq, inverse = np.unique(rows, return_inverse=True)
        row_max = np.full(uniq.shape[0], -np.inf, dtype=np.float64)
        np.maximum.at(row_max, inverse, values.astype(np.float64))
        shifted = np.exp((values.astype(np.float64) - row_max[inverse]))
        row_sum = np.zeros(uniq.shape[0], dtype=np.float64)
        np.add.at(row_sum, inverse, shifted)
        return (shifted / row_sum[inverse]).astype(np.float32)
