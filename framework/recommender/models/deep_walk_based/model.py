from framework.dataloader.graph.node import UserNode
from ...recommender import Recommender
from ...utils.walker import BiasedRandomWalker

import walker
import numpy as np
import networkx as nx
from gensim.models.word2vec import Word2Vec
from sklearn.neighbors import NearestNeighbors
from copy import deepcopy

from ....dataloader.graph.node import ItemNode

class DeepWalkBased(Recommender):
    def __init__(
            self, 
            config : dict, 
            walk_len : int, 
            n_walks : int, 
            p : float = 1.0,
            q : float = 1.0,
            embedding_size : int = 64,
            workers : int = 4,
            window_size : int = 3,
            epochs: int = 1,
            learning_rate : float = 0.05,
            min_count : int = 1,
            seed : int = 42,
            all_recs : bool = False 
        ):
        super().__init__(config)
        self.walk_len = walk_len
        self.n_walks = n_walks
        self.embedding_size = embedding_size
        self.p, self.q = p, q
        self.workers = workers
        self.window_size = window_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.min_count = min_count
        self.seed = seed
        self.all_recs = all_recs
        self._embedding = {}

    def name(self):
        text = 'Node2Vec based model + cosine similarity'
        text += f';q={self.q};p={self.p};embedding_size={self.embedding_size}'
        return text

    def train(self, G_train, ratings_train):
        self.G_train = G_train
        self.fit()

    def get_recommendations(self, k: int = 5):
        # Set doesnt guarantee the order of set elements
        users = list(self.G_train.get_user_nodes())
        items = list(self.G_train.get_item_nodes())

        users_embeddings = np.array([self._embedding[user] for user in users])
        items_embeddings = np.array([self._embedding[item] for item in items])

        n_neighbors = self._get_n_neighbors(users, items, k)
        knn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        knn.fit(items_embeddings)
        rec_indices = knn.kneighbors(users_embeddings, return_distance=False)

        recommendations = {}
        for user_idx, user in enumerate(users):
            rated_items = self.G_train.get_user_rated_items(user)
            recs = []
            for item_idx in rec_indices[user_idx]:
                item = items[item_idx]
                if item not in rated_items:
                    recs.append(item)
                    if not self.all_recs and len(recs) == k:
                        break
            
            recommendations[user] = recs
        
        return recommendations

    def get_user_recommendation(self, user: UserNode, k: int = 5):
        items = self.G_train.get_item_nodes()
        rated_items = self.G_train.get_user_rated_items(user)
        unrated_items = list(items - rated_items)
        user_embedding = self._embedding[user].reshape(1, -1)
        items_embeddings = np.array([self._embedding[item] for item in unrated_items])
        n_neighbors = k if not self.all_recs else len(unrated_items)
        knn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        knn.fit(items_embeddings)
        rec_indices = knn.kneighbors(user_embedding, return_distance=False)

        recs = []
        for idx in rec_indices[0]:
            recs.append(unrated_items[idx])

        return recs


    def fit(self):
        graph = self.G_train.convert_node_labels_to_integer()
        self.walks = walker.random_walks(
            graph, n_walks=self.n_walks, walk_len=self.walk_len
        )
        print(f'Random walk shape: {self.walks.shape}')
        self.walks = self.walks.tolist()

        model = Word2Vec(
            self.walks,
            sg=1,
            hs=1,
            alpha=self.learning_rate,
            epochs=self.epochs,
            vector_size=self.embedding_size,
            window=self.window_size,
            min_count=self.min_count,
            workers=self.workers,
            seed=self.seed
        )

        for node in graph.nodes():
            self._embedding[graph.nodes[node]['old_label']] = model.wv[node]
        
        # self.G_train.convert_back()
    
    # def _convert_node_labels_to_integer(self, G):
    #     N = G.number_of_nodes()
    #     mapping = dict(zip(G.nodes(), range(0, N)))
    #     nx.relabel_nodes(G, mapping, copy=False)
    #     nx.set_node_attributes(G, {v: k for k, v in mapping.items()}, 'old_label')

    def _convert_back(self, G):
        mapping = {node: G.nodes[node]['old_label'] for node in G.nodes()}
        nx.relabel_nodes(G, mapping, copy=False)
        nx.set_node_attributes(G, {v: k for k, v in mapping.items()}, 'old_label')

    def _get_n_neighbors(self, users, items, top_k):
        n_neighbors = 0
        if self.all_recs:
            n_neighbors = len(items)
        else:
            max_recs = 0
            for user in users:
                rated_items = self.G_train.get_user_rated_items(user)
                if len(rated_items) > max_recs:
                    max_recs = len(rated_items)
            n_neighbors = min(max_recs + top_k, len(items))
        
        return n_neighbors


           
    
