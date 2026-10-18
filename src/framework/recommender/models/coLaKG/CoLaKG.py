import multiprocessing

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn

from .dataloader import Loader


def _move_graph(graph, device):
    """Move a sparse LightGCN adjacency tensor (or a list of split tensors) to ``device``."""
    if isinstance(graph, (list, tuple)):
        return [g.to(device) for g in graph]
    return graph.to(device) if graph is not None else graph


class BasicModel(nn.Module):    
    def __init__(self):
        super(BasicModel, self).__init__()
    
    def getUsersRating(self, users):
        raise NotImplementedError

class PairWiseModel(BasicModel):
    def __init__(self):
        super(PairWiseModel, self).__init__()
    def bpr_loss(self, users, pos, neg):
        """
        Parameters:
            users: users list 
            pos: positive items for corresponding users
            neg: negative items for corresponding users
        Return:
            (log-loss, l2-loss)
        """
        raise NotImplementedError

class CoLaKG_model(BasicModel):
    def __init__(self, 
               config: dict,
               dataset: Loader,
               adj_matrix=None, 
               semantic_emb=None, 
               user_semantic_emb=None,
               device=None,):
        super(CoLaKG_model, self).__init__()

        self.config = config
        self.dataset = dataset
        self.device = device if device is not None else torch.device("cpu")
        self.adj_matrix = adj_matrix
        self.semantic_emb = semantic_emb
        self.user_semantic_emb = user_semantic_emb
        self.semantic_dim = semantic_emb.shape[1] if semantic_emb is not None else 1024
        self.semantic_hid = self.config.get('semantic_hid_dim', 32)
        self.dropout_i = self.config['dropout_i']
        self.dropout_u = self.config['dropout_u']
        self.dropout_neighbor = self.config['dropout_n']
        self.__init_weight()
          # Put every parameter, buffer, and prebuilt tensor on the same device.
        self.to(self.device)
        if self.adj_matrix is not None:
            self.adj_matrix = self.adj_matrix.to(self.device)

    def __init_weight(self):
        self.num_users  = self.dataset.n_users # get a graph and info object here
        self.num_items  = self.dataset.m_items
        print("num_items", self.num_items)
        self.latent_dim = self.config['latent_dim_rec']
        self.n_layers = self.config['lightGCN_n_layers']
        self.keep_prob = self.config['keep_prob']
        self.A_split = self.config['A_split']
        self.embedding_user = torch.nn.Embedding(
            num_embeddings=self.num_users, embedding_dim=self.latent_dim)
        self.embedding_item = torch.nn.Embedding(
            num_embeddings=self.num_items, embedding_dim=self.latent_dim)

        nn.init.normal_(self.embedding_user.weight, std=0.1)
        nn.init.normal_(self.embedding_item.weight, std=0.1)
        print("use NORMAL distribution initilizer")
   
        self.f = nn.Sigmoid()
        self.Graph = self.dataset.getSparseGraph()
        self.Graph = _move_graph(self.Graph, self.device)
        self.semantic_map = nn.Linear(self.semantic_dim, self.latent_dim)
        self.user_semantic_map = nn.Linear(self.semantic_dim, self.latent_dim)
        print(f"lgn is already to go(drop_edge:{self.config['use_drop_edge']})")
        self.W = nn.Parameter(torch.empty(size=(self.semantic_dim, self.semantic_hid)))
        nn.init.xavier_uniform_(self.W.data, gain=1.414)
        self.a = nn.Parameter(torch.empty(size=(2*self.semantic_hid, 1)))
        nn.init.xavier_uniform_(self.a.data, gain=1.414)

        self.W_u = nn.Parameter(torch.empty(size=(self.semantic_dim, self.semantic_hid)))
        nn.init.xavier_uniform_(self.W_u.data, gain=1.414)
        self.a_u = nn.Parameter(torch.empty(size=(2*self.semantic_hid, 1)))
        nn.init.xavier_uniform_(self.a_u.data, gain=1.414)
        self.alpha=0.2
        self.leakyrelu = nn.LeakyReLU(self.alpha)

    def __dropout_x(self, x, keep_prob):
        size = x.size()
        index = x.indices().t()
        values = x.values()
        random_index = torch.rand(len(values)) + keep_prob
        random_index = random_index.int().bool()
        index = index[random_index]
        values = values[random_index]/keep_prob
        g = torch.sparse.FloatTensor(index.t(), values, size)
        return g
    
    def __dropout(self, keep_prob):
        if self.A_split:
            graph = []
            for g in self.Graph:
                graph.append(self.__dropout_x(g, keep_prob))
        else:
            graph = self.__dropout_x(self.Graph, keep_prob)
        return graph
    
    def _align_semantic(self, learned_emb, semantic_emb):
        """Reconcile a semantic embedding tensor with a learned embedding table.

        The learned table (e.g. ``embedding_item.weight``) and the semantic
        embedding are expected to share the same 0-based entity id space, but a
        k-fold split can leave a node disconnected: that node contributes a
        semantic row yet no rating triple, so the two tensors can end up with
        different row counts. Instead of letting the elementwise add below raise
        a ``RuntimeError`` on a size mismatch, pad the shorter side with a
        neutral (zero) base tensor and, if a semantic tensor is empty, replace it
        entirely with a neutral tensor. This keeps a single disconnected node
        from breaking the run.
        """
        target = learned_emb.shape[0]
        semantic_dim = self.latent_dim
        base = torch.zeros(target, semantic_dim, device=self.device)

        if semantic_emb is None:
            return base

        if semantic_emb.shape[0] != target:
            base = base.clone()
            n = min(semantic_emb.shape[0], target)
            base[:n] = semantic_emb[:n]
            semantic_emb = base

        return semantic_emb

    def computer(self):
        """
        propagate methods for lightGCN
        """
        users_emb = self.embedding_user.weight
        items_emb = self.embedding_item.weight

        items_semantic_emb = F.dropout(self.semantic_emb, self.dropout_i, training=self.training)
        items_semantic_emb = self.semantic_map(items_semantic_emb)
        items_semantic_emb = F.elu(items_semantic_emb)
        items_semantic_emb = F.dropout(items_semantic_emb, self.dropout_i, training=self.training)
        items_semantic_emb = self._align_semantic(items_emb, items_semantic_emb)
        items_emb_merged = (items_emb + items_semantic_emb) / 2

        user_semantic_emb = F.dropout(self.user_semantic_emb, self.dropout_u, training=self.training)
        user_semantic_emb = self.user_semantic_map(user_semantic_emb)
        user_semantic_emb = F.elu(user_semantic_emb)
        user_semantic_emb = F.dropout(user_semantic_emb, self.dropout_u, training=self.training)
        user_semantic_emb = self._align_semantic(users_emb, user_semantic_emb)
        users_emb_merged = (users_emb + user_semantic_emb) / 2
        
        
        neighbor_emb = items_emb_merged[self.adj_matrix]
        items_semantic_emb0 = self.semantic_emb
        neighbor_semantic_emb = self.semantic_emb[self.adj_matrix]  # N,L,d1

        # x = self.attentions(neighbor_semantic_emb, neighbor_emb, items_semantic_emb0)
        h, value_emb, semantic_emb = neighbor_semantic_emb, neighbor_emb, items_semantic_emb0
        
        Wh = torch.matmul(h, self.W)  # N,L,d
        h0 = semantic_emb.unsqueeze(1).repeat(1, h.shape[1],1)  # N,L,d1
        Wh0 = torch.matmul(h0, self.W)  # N,L,d
        
        W_concat = torch.cat((Wh, Wh0), dim=-1) # N,L,2d
        
        attention = torch.matmul(W_concat, self.a).squeeze(-1) # N,L
        attention = self.leakyrelu(attention)
        attention = F.softmax(attention, dim=1) # N,L
    
        attention = F.dropout(attention, self.dropout_neighbor, training=self.training) # N,L
        attention = attention.unsqueeze(-1)
     
        h_prime = attention * value_emb

        h_prime = torch.sum(h_prime, dim=1)
        
        h_prime = F.elu(h_prime)
      

        items_emb_merged = (items_emb_merged + h_prime ) / 2
        
        # items_emb = F.elu(items_emb)
       
        all_emb = torch.cat([users_emb_merged, items_emb_merged])
        embs = [all_emb]
        
        if self.config['use_drop_edge']:
            if self.training:
                # print("droping")
                g_droped = self.__dropout(self.keep_prob)
            else:
                g_droped = self.Graph        
        else:
            g_droped = self.Graph    
        
        for layer in range(self.n_layers):
            if self.A_split:
                temp_emb = []
                for f in range(len(g_droped)):
                    temp_emb.append(torch.sparse.mm(g_droped[f], all_emb))
                side_emb = torch.cat(temp_emb, dim=0)
                all_emb = side_emb
            else:
                all_emb = torch.sparse.mm(g_droped, all_emb)
            embs.append(all_emb)
        embs = torch.stack(embs, dim=1)
        #print(embs.size())
        light_out = torch.mean(embs, dim=1)
        users, items = torch.split(light_out, [self.num_users, self.num_items])
        return users, items
    
    def getUsersRating(self, users):
        all_users, all_items = self.computer()
        users_emb = all_users[users.long()]
        items_emb = all_items
        rating = self.f(torch.matmul(users_emb, items_emb.t()))
        return rating

    def getEmbedding(self, users, pos_items, neg_items):
        all_users, all_items = self.computer()
        users_emb = all_users[users]
        pos_emb = all_items[pos_items]
        neg_emb = all_items[neg_items]
        users_emb_ego = self.embedding_user(users)
        pos_emb_ego = self.embedding_item(pos_items)
        neg_emb_ego = self.embedding_item(neg_items)
        
        users_emb_ego0 = self.user_semantic_map(self.user_semantic_emb)[users]
        pos_emb_ego0 = self.semantic_map(self.semantic_emb)[pos_items]
        neg_emb_ego0 = self.semantic_map(self.semantic_emb)[neg_items]
        return users_emb, pos_emb, neg_emb, users_emb_ego, pos_emb_ego, neg_emb_ego, pos_emb_ego0, neg_emb_ego0, users_emb_ego0
    
    def bpr_loss(self, users, pos, neg):
        # getEmbedding returns, in order: propagated (users, pos, neg) embeddings
        # followed by their ego embeddings (users, pos, neg) and the semantic
        # ego embeddings (pos, neg, users).
        (users_emb, pos_emb, neg_emb,
        users_emb_ego, pos_emb_ego, neg_emb_ego,
        pos_emb_sem, neg_emb_sem, users_emb_sem) = self.getEmbedding(users.long(), pos.long(), neg.long())
        reg_loss = (1/2) * (
           users_emb_ego.norm(2).pow(2) +
           pos_emb_ego.norm(2).pow(2) +
           neg_emb_ego.norm(2).pow(2) +
           pos_emb_sem.norm(2).pow(2) +
           neg_emb_sem.norm(2).pow(2) +
           users_emb_sem.norm(2).pow(2)
        ) / float(len(users))
        pos_scores = torch.mul(users_emb, pos_emb)
        pos_scores = torch.sum(pos_scores, dim=1)
        neg_scores = torch.mul(users_emb, neg_emb)
        neg_scores = torch.sum(neg_scores, dim=1)

        loss = torch.mean(torch.nn.functional.softplus(neg_scores - pos_scores))

        return loss, reg_loss
       
    def forward(self, users, items):
        # compute embedding
        all_users, all_items = self.computer()
        # print('forward')
        #all_users, all_items = self.computer()
        users_emb = all_users[users]
        items_emb = all_items[items]
        inner_pro = torch.mul(users_emb, items_emb)
        gamma     = torch.sum(inner_pro, dim=1)
        return gamma
