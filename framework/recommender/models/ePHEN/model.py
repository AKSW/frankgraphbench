from framework.dataloader.graph.node import UserNode, ItemNode
from ...recommender import Recommender

from ...model2class import model2class

from sklearn.neighbors import NearestNeighbors
from sentence_transformers import SentenceTransformer

import numpy as np
import pandas as pd
import random
import importlib

from tqdm import tqdm
from copy import deepcopy

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

"""
    Recommender base class
"""

class EPHEN(Recommender):
    def __init__(
        self,
        config: dict,
        embedding_model: str = "sentence-transformers/distiluse-base-multilingual-cased-v2",
        embedding_model_kwargs: dict = None,
        embed_with: str = "movie_title", # 'graph' for graph embedding model or column for text embedding model
        iterations: int = 30,
        mi: float = 0.85,
        seed: int = 42,
        all_recs: bool = False,
    ):
        super().__init__(config)
        self.embedding_model = embedding_model
        self.embedding_model_kwargs = embedding_model_kwargs
        self.embed_with = embed_with
        self.iterations = iterations
        self.mi = mi
        self.seed = seed
        self.all_recs = all_recs
        self._embedding = {}

    def name(self):
        text = "EPHEN based model + cosine similarity"
        text += f";embedding_model={self.embedding_model};embed_with={self.embed_with};iterations={self.iterations};mi={self.mi}."
        return text

    def train(self, G_train, ratings_train):
        self.G_train = G_train
        self.ratings_train = ratings_train
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
        raise NotImplementedError(
            "Override get_user_recommendation() for your model subclass."
        )

    def fit(self):
        if self.embed_with == "graph":
            self._generate_graph_init_embeddings()
        else:
            self._generate_text_init_embeddings()
        self._regularization()

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
    
    def _generate_text_init_embeddings(self):
        model = SentenceTransformer(self.embedding_model)
        item_properties = pd.DataFrame(self.G_train.get_item_property_edges())
        filtered_properties = item_properties[1][item_properties[1].apply(lambda x: x.get_property_type() == self.embed_with)].reset_index(drop=True)
        self.init_embeddings = {}
        for property in tqdm(filtered_properties):
            self.init_embeddings[property] = model.encode(property.id)

    def _generate_graph_init_embeddings(self):
        module_name = f'framework.recommender.models.{model2class[self.embedding_model]["submodule"]}'
        class_name = model2class[self.embedding_model]['class']

        model = getattr(importlib.import_module(module_name), class_name)
        model = model(self.embedding_model_kwargs['config'], **self.embedding_model_kwargs['parameters'])

        model.train(self.G_train, self.ratings_train)

        self.init_embeddings = model._embedding

    def _regularization(self):
        dim = len(self.init_embeddings[list(self.init_embeddings.keys())[0]])
        self._embedding = deepcopy(self.init_embeddings)
        for node in self.G_train.nodes():
            if node not in self._embedding:
                self._embedding[node] = np.array([0.0] * dim)
        nodes = list(self.G_train.nodes())
        pbar = tqdm(range(0, self.iterations))
        for iteration in pbar:
            random.shuffle(nodes)
            energy = 0.0
            for node in nodes:
                f_new = np.array([0.0] * dim)
                f_old = np.array(self._embedding[node])
                sum_w = 0.0
                for neighbor in self.G_train.neighbors(node):
                    w = 1.0
                    if 'weight' in self.G_train[node][neighbor]:
                        w = self.G_train[node][neighbor]['weight']
                    w /= np.sqrt(self.G_train.degree[neighbor])
                    f_new = f_new + w * f_old
                    sum_w = sum_w + w
                if sum_w == 0.0: 
                    sum_w = 1.0
                f_new /= sum_w
                self._embedding[node] = f_new
                if node in self.init_embeddings:
                    self._embedding[node] = self.init_embeddings[node] * \
                        self.mi + self._embedding[node] * (1.0 - self.mi)
                energy = energy + np.linalg.norm(f_new-f_old)
            iteration = iteration + 1
            message = f"Iteration {iteration} | Energy = {energy}"
            pbar.set_description(message)