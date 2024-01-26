from framework.dataloader.graph.graph import Graph
from framework.dataloader.graph.node import UserNode, ItemNode
from ...recommender import Recommender

from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
from pykeen.datasets import Dataset
from sklearn.neighbors import NearestNeighbors

from tqdm import tqdm

import pandas as pd
import numpy as np
import torch
import typing as t

"""
    Recommender base class
"""
class TransE(Recommender):
    def __init__(
            self, 
            config : dict,
            embedding_dim : int = 50, 
            scoring_fct_norm : int = 1, 
            entity_initializer = None, 
            entity_constrainer = None, 
            relation_initializer = None, 
            relation_constrainer = None, 
            regularizer = None, 
            regularizer_kwargs = None,
            epochs : int = 5,
            seed : int = 42,
            all_recs : bool = False,
            triples : str = 'all',
        ):
        super().__init__(config)
        self.embedding_dim = embedding_dim
        self.scoring_fct_norm = scoring_fct_norm
        self.entity_initializer = entity_initializer
        self.entity_constrainer = entity_constrainer
        self.relation_initializer = relation_initializer
        self.relation_constrainer = relation_constrainer
        self.regularizer = regularizer
        self.regularizer_kwargs = regularizer_kwargs
        self.epochs = epochs
        self.seed = seed
        self.all_recs = all_recs
        self.triples = triples
        self._triples = None
        self._model = None
        self._entity_to_id = None

    def name(self):
        text = 'TransE based model + cosine similarity'
        text += f';embedding_dim={self.embedding_dim}'
        return text

    def train(self, G_train, ratings_train):
        self.G_train = G_train
        if self.triples == 'all':
            self._triples = G_train.get_all_triples()
        elif self.triples == 'ratings':
            self._triples = G_train.get_ratings_triples()
        self.fit()
    
    def get_recommendations(self, k : int = 5) -> t.Dict[UserNode, t.List[ItemNode]]:
        """
        :param k: cutoff recommendation (int)
        :return dict of recommendations for each user
            of type {user1: [item1, item2]}
        """
        users = list(self.G_train.get_user_nodes())
        items = list(self.G_train.get_item_nodes())

        users_indices = [self._entity_to_id[user.__str__()] for user in users]
        users_indices = torch.LongTensor(users_indices)

        items_indices = [self._entity_to_id[item.__str__()] for item in items]
        items_indices = torch.LongTensor(items_indices)

        users_embeddings = self._model.entity_representations[0](indices=users_indices).detach().numpy()
        items_embeddings = self._model.entity_representations[0](indices=items_indices).detach().numpy()

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
        
    def get_user_recommendation(self, user : UserNode, k : int = 5):
        raise NotImplementedError('Override get_user_recommendation() for your model subclass.')
    
    def fit(self):
        triples = TriplesFactory.from_labeled_triples(self._triples[["head", "relation", "tail"]].values,
            create_inverse_triples=False,
            entity_to_id=None,
            relation_to_id=None,
            compact_id=False,
            filter_out_candidate_inverse_relations=True,
            metadata=None,
        )

        dataset = Dataset.from_tf(triples, ratios=[.95, .05, .0])
        self._entity_to_id = dataset.entity_to_id

        result = pipeline(
            dataset=dataset,
            model='TransE',
            model_kwargs=dict(
                embedding_dim=self.embedding_dim,
                scoring_fct_norm=self.scoring_fct_norm,
                entity_initializer=self.entity_initializer,
                entity_constrainer=self.entity_constrainer,
                relation_initializer=self.relation_initializer,
                relation_constrainer=self.relation_constrainer,
                regularizer=self.regularizer,
                regularizer_kwargs=self.regularizer_kwargs,
            ),
            epochs=self.epochs,
            random_seed=self.seed
        )
        self._model = result.model

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