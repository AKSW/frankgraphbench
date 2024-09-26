from typing import Dict, List, Tuple
from framework.dataloader.graph.graph import Graph
from framework.dataloader.graph.node import ItemNode, UserNode

from ...recommender import Recommender

class Entity2Rec(Recommender):
    def __init__(self, config: dict = ...):
        super().__init__(config)

    def name(self):
        text = "Entity2Rec"
        text += f";"
        return text
    
    def train(self, G_train: Graph, ratings_train: Dict[UserNode, List[Tuple[ItemNode, float]]]):
        return super().train(G_train, ratings_train)
    
    def get_recommendations(self, k: int = 5) -> Dict[UserNode, List[ItemNode]]:
        return super().get_recommendations(k)
    
    def fit(self):
        pass