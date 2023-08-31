from ..dataloader.graph.graph import Graph
from ..dataloader.graph.node import UserNode, ItemNode

from ..utils import get_optional_argument

"""
    Recommender base class
"""
class Recommender:
    def __init__(self, config : dict = {}):
        if config is not None:
            self.save_weights = get_optional_argument(config, 'save_weights', False)

    def train(self, G_train : Graph, ratings_train : [(UserNode, ItemNode)], labels_train : [int]):
        raise NotImplementedError('Override train() method for your model subclass.')
    
    def get_recommendations(self, k : int = 5):
        raise NotImplementedError('Override get_recommendations() for your model subclass.')

    def get_user_recommendation(self, user : UserNode, k : int = 5):
        raise NotImplementedError('Override get_user_recommendation() for your model subclass.')
    
