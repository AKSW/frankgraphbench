from typing import Dict, List, Tuple
from framework.dataloader.graph.graph import Graph
from framework.dataloader.graph.node import ItemNode, UserNode

from ...recommender import Recommender
from ...model2class import model2class

import importlib
import pandas as pd
import networkx as nx

class Entity2Rec(Recommender):
    def __init__(
            self, 
            config: dict,
            feedback_file: str = None, 
            embedding_model: str = "deepwalk_based",
            embedding_model_kwargs: dict = None,
            walk_length: int = 100,
            num_walks: int = 50, 
            run_all: bool = False, 
            collab_only: bool = False,
            content_only: bool = False,
            embedding_size: int = 64, 
            window_size: int = 3,
            workers: int = 4, 
            iterations: int = 1, 
            p: float = 1.0, 
            q: float = 1.0,
        ):
        super().__init__(config)
        self.feedback_file = feedback_file
        self.embedding_model = embedding_model
        self.embedding_model_kwargs = embedding_model_kwargs
        self.p = p
        self.q = q
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.run_all = run_all
        self.embedding_size = embedding_size 
        self.window_size = window_size
        self.workers = workers
        self.iterations = iterations
        self.collab_only = collab_only
        self.content_only = content_only
        self._triples = None
        self._embedding = {}
        self._subgraphs = {}

    def name(self):
        text = "Entity2Rec"
        text += f";embedding_model={self.embedding_model};embedding_model_kwargs={self.embedding_model_kwargs};p={self.p};q={self.q};"
        text += f"walk_length={self.walk_length};num_walks={self.num_walks};run_all={self.run_all};embedding_size={self.embedding_size};"
        text += f"window_size={self.window_size};workers={self.workers};iterations={self.iterations};collab_only={self.collab_only};"
        text += f"content_only={self.content_only}"
        return text
    
    def train(self, G_train: Graph, ratings_train: Dict[UserNode, List[Tuple[ItemNode, float]]]):
        self.G_train = G_train
        self.ratings_train = ratings_train
        self._triples = G_train.get_all_triples(return_type="obj")
        self.fit()
    
    def get_recommendations(self, k: int = 5) -> Dict[UserNode, List[ItemNode]]:
        return super().get_recommendations(k)
    
    def fit(self):
        self.entity2rec()

    def entity2rec(self):
        self.entity2vec()
        self.entity2rel()

    def entity2vec(self):
        module_name = f'framework.recommender.models.{model2class[self.embedding_model]["submodule"]}'
        class_name = model2class[self.embedding_model]['class']

        model = getattr(importlib.import_module(module_name), class_name)
        model = model(self.embedding_model_kwargs['config'], **self.embedding_model_kwargs['parameters'])

        self._generate_subgraphs()
        for index, value in self._subgraphs.items():
            print(f'{index}: {value}')

        # model.train(self.G_train, self.ratings_train)
        # self.init_embeddings = model._embedding

    def entity2rel(self):
        pass

    def _generate_subgraphs(self):
        for relation in self._triples['relation'].unique():
            filter_temp = pd.concat([self._triples['head'][self._triples['relation'] == relation], self._triples['tail'][self._triples['relation'] == relation]])
            self._subgraphs[relation] = nx.subgraph(self.G_train, filter_temp)