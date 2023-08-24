from ..dataloader.dataset.dataset import Dataset

from ..utils import get_optional_argument

"""
    Recommender base class
"""
class Recommender:
    def __init__(self, config : dict = {}):
        if config is not None:
            self.save_weights = get_optional_argument(config, 'save_weights', False)
        pass

    def train(self, G_train, ratings_train, labels_train):
        raise NotImplementedError('Override train() method for your model subclass.')
    
    def get_recommendations(self, edges):
        raise NotImplementedError('Override get_recommendations() for your model subclass.')

    def get_single_recommendation(self, edge):
        raise NotImplementedError('Override get_single_recommendation_() for your model subclass.')
    
