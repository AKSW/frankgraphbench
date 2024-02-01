from framework.dataloader.graph.node import UserNode, ItemNode
from ...recommender import Recommender

from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
from pykeen.datasets import Dataset
from sklearn.neighbors import NearestNeighbors


import numpy as np
import torch
import typing as t

"""
    Recommender base class
"""


class TuckER(Recommender):
    def __init__(
        self,
        config: dict,
        embedding_dim: int = 200,
        relation_dim = None,
        dropout_0: float = 0.3,
        dropout_1: float = 0.4,
        dropout_2: float = 0.5,
        apply_batch_normalization: bool = True,
        entity_initializer=  None,
        relation_initializer = None,
        core_tensor_initializer = None,
        core_tensor_initializer_kwargs=None,
        epochs: int = 5,
        seed: int = 42,
        all_recs: bool = False,
        triples: str = "all",
    ):
        super().__init__(config)
        self.embedding_dim = embedding_dim
        self.entity_initializer = entity_initializer
        self.relation_dim = relation_dim
        self.dropout_0 = dropout_0
        self.dropout_1 = dropout_1
        self.dropout_2 = dropout_2
        self.apply_batch_normalization = apply_batch_normalization
        self.relation_initializer = relation_initializer
        self.core_tensor_initializer = core_tensor_initializer
        self.core_tensor_initializer_kwargs = core_tensor_initializer_kwargs
        self.epochs = epochs
        self.seed = seed
        self.all_recs = all_recs
        self.triples = triples
        self._triples = None
        self._model = None
        self._entity_to_id = None

    def name(self):
        text = "TuckER based model + cosine similarity"
        text += f";embedding_dim={self.embedding_dim}"
        return text

    def train(self, G_train, ratings_train):
        self.G_train = G_train
        if self.triples == "all":
            self._triples = G_train.get_all_triples()
        elif self.triples == "ratings":
            self._triples = G_train.get_ratings_triples()
        self.fit()

    def get_recommendations(self, k: int = 5) -> t.Dict[UserNode, t.List[ItemNode]]:
        """
        :param k: cutoff recommendation (int)
        :return dict of recommendations for each user
            of type {user1: [item1, item2]}
        """
        users_iter = self.G_train.get_user_nodes()
        items_iter = self.G_train.get_item_nodes()

        users = list(users_iter)
        items = list(items_iter)

        users_indices, users_no_embedding = [], []
        for user in users_iter:
            try:
                users_indices.append(self._entity_to_id[user.__str__()])
            except:
                users_no_embedding.append(user)
                users.remove(user)
                continue
        users_indices = torch.LongTensor(users_indices)

        items_indices, items_no_embedding = [], []
        for item in items_iter:
            try:
                items_indices.append(self._entity_to_id[item.__str__()])
            except:
                items_no_embedding.append(item)
                items.remove(item)
                continue
        items_indices = torch.LongTensor(items_indices)

        users_embeddings = (
            self._model.entity_representations[0](indices=users_indices)
            .detach()
            .cpu()
            .numpy()
        )
        items_embeddings = (
            self._model.entity_representations[0](indices=items_indices)
            .detach()
            .cpu()
            .numpy()
        )

        # complex data not supported by sklearn
        # users_embeddings = np.real(users_embeddings)
        # items_embeddings = np.real(items_embeddings)

        if len(users_no_embedding) > 0:
            users_embeddings = np.concatenate(
                (
                    users_embeddings,
                    np.zeros(
                        (len(users_no_embedding), self.embedding_dim),
                        dtype=users_embeddings.dtype,
                    ),
                ),
                axis=0,
            )
            users = users + users_no_embedding

        if len(items_no_embedding) > 0:
            items_embeddings = np.concatenate(
                (
                    items_embeddings,
                    np.zeros(
                        (len(items_no_embedding), self.embedding_dim),
                        dtype=items_embeddings.dtype,
                    ),
                ),
                axis=0,
            )
            items = items + items_no_embedding

        n_neighbors = self._get_n_neighbors(users, items, k)
        knn = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
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
        triples = TriplesFactory.from_labeled_triples(
            self._triples[["head", "relation", "tail"]].values,
            create_inverse_triples=False,
            entity_to_id=None,
            relation_to_id=None,
            compact_id=False,
            filter_out_candidate_inverse_relations=True,
            metadata=None,
        )

        dataset = Dataset.from_tf(triples, ratios=[0.95, 0.05, 0.0])
        self._entity_to_id = dataset.entity_to_id

        result = pipeline(
            dataset=dataset,
            model="TuckER",
            model_kwargs=dict(
                embedding_dim=self.embedding_dim,
                relation_dim=self.relation_dim,
                dropout_0=self.dropout_0,
                dropout_1=self.dropout_1,
                dropout_2=self.dropout_2,
                apply_batch_normalization=self.apply_batch_normalization,
                entity_initializer=self.entity_initializer,
                relation_initializer=self.relation_initializer,
                core_tensor_initializer=self.core_tensor_initializer,
                core_tensor_initializer_kwargs=self.core_tensor_initializer_kwargs,
            ),
            epochs=self.epochs,
            random_seed=self.seed,
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
