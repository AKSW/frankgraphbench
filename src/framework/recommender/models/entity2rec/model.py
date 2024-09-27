from typing import Dict, List, Tuple
from framework.dataloader.graph.graph import Graph
from framework.dataloader.graph.node import ItemNode, UserNode

from ...recommender import Recommender

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

    def name(self):
        text = "Entity2Rec"
        text += f";embedding_model={self.embedding_model};embedding_model_kwargs={self.embedding_model_kwargs};p={self.p};q={self.q};walk_length={self.walk_length};num_walks={self.num_walks};run_all={self.run_all};embedding_size={self.embedding_size};window_size={self.window_size};workers={self.workers};iterations={self.iterations};collab_only={self.collab_only};content_only={self.content_only}"
        return text
    
    def train(self, G_train: Graph, ratings_train: Dict[UserNode, List[Tuple[ItemNode, float]]]):
        return super().train(G_train, ratings_train)
    
    def get_recommendations(self, k: int = 5) -> Dict[UserNode, List[ItemNode]]:
        return super().get_recommendations(k)
    
    def fit(self):
        pass