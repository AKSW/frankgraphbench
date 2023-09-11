from ..dataloader.graph.graph import Graph
from ..dataloader.graph.node import UserNode, ItemNode

from ..utils import get_optional_argument

import typing as t

"""
    Recommender base class
"""
class Recommender:
    def __init__(self, config : dict = {}):
        if config is not None:
            self.save_weights = get_optional_argument(config, 'save_weights', False)

    def train(self, G_train : Graph, ratings_train : t.Dict[UserNode, t.List[t.Tuple[ItemNode, float]]]):
        raise NotImplementedError('Override train() method for your model subclass.')
    
    def get_recommendations(self, k : int = 5):
        """
        :param k: cutoff recommendation (int)
        :return dict of recommendations for each user
            of type {user1: [item1, item2]}
        """
        raise NotImplementedError('Override get_recommendations() for your model subclass.')

    def get_user_recommendation(self, user : UserNode, k : int = 5):
        raise NotImplementedError('Override get_user_recommendation() for your model subclass.')
    
