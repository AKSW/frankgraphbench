from typing import Dict, List, Tuple
from framework.dataloader.graph.graph import Graph
from framework.dataloader.graph.node import ItemNode, UserNode

from ...recommender import Recommender

class KGAT(Recommender):
    def __init__(
                    self, 
                    config : dict, 
                    embed_size: int = 64,
                 ):
        super().__init__(config)
        self.embed_size = embed_size

    def name(self):
        text = "KGAT"
        return text
    
    def train(self, G_train: Graph, ratings_train: Dict[UserNode, List[Tuple[ItemNode, float]]]):
        self.G_train = G_train
        self.ratings_train = ratings_train
        self._triples = G_train.get_all_triples() # gotta change this method: create the properties properly as relations before doing the transformations. this will also change how all translation models perform, hopefully better
        print(self._triples["head"].unique())
        print(self._triples["relation"].unique())
        print(self._triples["tail"].unique())
    
    def get_recommendations(self, k : int = 5) -> Dict[UserNode, List[ItemNode]]:
        """
        :param k: cutoff recommendation (int)
        :return dict of recommendations for each user
            of type {user1: [item1, item2]}
        """
        raise NotImplementedError('Override get_recommendations() for your model subclass.')

    def get_user_recommendation(self, user : UserNode, k : int = 5):
        raise NotImplementedError('Override get_user_recommendation() for your model subclass.')
        
    def _transform_ratings_to_ids(self):
        pass