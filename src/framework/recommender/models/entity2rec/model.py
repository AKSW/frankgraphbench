from typing import Dict, List, Tuple
from framework.dataloader.graph.graph import Graph
from framework.dataloader.graph.node import ItemNode, UserNode
from framework.recommender.models.entity2rec.entity2rec import Entity2RecD2K

from ...recommender import Recommender
from ...model2class import model2class

import importlib
import multiprocess
import pandas as pd
import networkx as nx
import numpy as np

from scipy.spatial.distance import cdist
from tqdm import tqdm

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
            social_only: bool = False,
            embedding_size: int = 64, 
            window_size: int = 3,
            workers: int = 4, 
            iterations: int = 1, 
            p: float = 1.0, 
            q: float = 1.0,
            relevance: float = 0.0,
            metric: str = "NDCG",
            k: int = 5,
            relation_template: dict = {'collab': 'rating', 'social': 'is', 'content': 'has'},
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
        self.social_only = social_only
        self.relevance = relevance
        self.metric = metric
        self.k = k
        self.relation_template = relation_template
        self._triples = None
        self._relations = []
        self._subgraphs = {}
        self._subgraphs_embedding = {}

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

        for relation in self._relations:
            # ratings_train is not actually used in the node2vec model
            model.train(self._subgraphs[relation], self.ratings_train)
            self._subgraphs_embedding[relation] = model._embedding

        x_train, y_train, qids_train, items_train = self._compute_features()
        
        e2rec = Entity2RecD2K('for_init', run_all=self.run_all, p=self.p, q=self.q,
                   feedback_file=self.feedback_file, walk_length=self.walk_length,
                   num_walks=self.num_walks, dimensions=self.embedding_size, window_size=self.window_size,
                   workers=self.workers, iterations=self.iterations, collab_only=self.collab_only,
                   content_only=self.content_only, social_only=self.social_only)
        
        e2rec.fit(x_train, y_train, qids_train,
            optimize=self.metric, N=self.k)

    def entity2rel(self):
        # needs to get an embedding that relates to a property
        pass

    def _generate_subgraphs(self):
        self._relations = self._triples['relation'].unique()
        filter_temp = {}
        for relation in self._relations:
            filter_temp[relation] = pd.concat([self._triples['head'][self._triples['relation'] == relation], self._triples['tail'][self._triples['relation'] == relation]])

        # joining rating properties according to collab, content, social properties, and relevant score delimitations
        new_filter_temp = {}
        for rel in self.relation_template.values():
            new_filter_temp[rel] = pd.Series()
            for relation in self._relations:
                if rel in relation:
                    new_filter_temp[rel] = pd.concat([new_filter_temp[rel], filter_temp[relation]])

        for rel, df in new_filter_temp.items():
            self._subgraphs[rel] = nx.subgraph(self.G_train, df)
        
        # make relations same as template
        self._relations = list(self.relation_template.values())

    def _compute_features(self, n_jobs=-1):
        def process(users, return_dict, i):
            TX, Ty, Tqids, Titems = [], [], [], []

            desc = f"Computing features for user-item ratings (thread: {i})"
            for user in tqdm(users, desc=desc):
                candidate_items = self.__get_candidate_items(user, train=True)
                for item in candidate_items:
                    items_liked_by_user = self.__items_liked_by_user(user)
                    users_liking_an_item = self.__users_liking_an_item(item)

                    TX.append(self.__compute_user_item_features(user, item, items_liked_by_user, users_liking_an_item))
                    Ty.append(self.__get_relevance(user, item))
                    Tqids.append(user)
                    Titems.append(item)

            return_dict[f"{i}"] = (TX, Ty, Tqids, Titems)
        
        def split_processing(n_jobs, return_dict):
            users = list(self.G_train.get_user_nodes())
            split_size = round(len(users) / n_jobs)
            threads = []                                                                
            for i in range(n_jobs):                                                 
                # determine the indices of the list this thread will handle             
                start = i * split_size                                                  
                # special case on the last chunk to account for uneven splits           
                end = len(users) if i+1 == n_jobs else (i+1) * split_size                
                # create the thread
                threads.append(                                                         
                    multiprocess.Process(target=process, args=(users[start:end], return_dict, i)))
                threads[-1].start() # start the thread we just created                  

            # wait for all threads to finish                                            
            for t in threads:
                t.join()
        
        if n_jobs == -1:
            n_jobs = multiprocess.cpu_count()

        return_dict = multiprocess.Manager().dict()
        TX, Ty, Tqids, Titems = [], [], [], []

        split_processing(n_jobs, return_dict)
        return_dict = dict(return_dict)
        for t in range(n_jobs):
            TX += return_dict[f"{t}"][0]
            Ty += return_dict[f"{t}"][1]
            Tqids += return_dict[f"{t}"][2]
            Titems += return_dict[f"{t}"][3]
        return TX, Ty, Tqids, Titems

    def __get_relevance(self, user, item):
        ratings = self.G_train.get_ratings_with_labels()
        for i, relevance in ratings[user]:
            if i == item:
                return relevance

    def __get_candidate_items(self, user, train=False):
        items = list(self.G_train.get_item_nodes())

        rated_items = []
        for u, i in self.G_train.get_rating_edges():
            if u == user:
                rated_items.append(i)
        
        unrated_items = [item for item in items if item not in rated_items]

        if train:
            return rated_items
        else:
            return unrated_items

    def __users_liking_an_item(self, item):
        users_liked = []
        for u, i in self.G_train.get_rating_edges():
            if i == item:
                users_liked.append(u)
        return users_liked

    def __items_liked_by_user(self, user):
        liked_items = []
        for u, i in self.G_train.get_rating_edges():
            if u == user:
                liked_items.append(i)
        return liked_items
    
    def __compute_user_item_features(self, user, item, items_liked_by_user, users_liking_an_item):
        collab_scores, content_scores, social_scores = self.__compute_scores(user, item, items_liked_by_user, users_liking_an_item)

        if self.collab_only:
            return collab_scores
        elif self.content_only:
            return content_scores
        elif self.social_only:
            return social_scores
        else:
            return collab_scores + content_scores + social_scores
        
    def __compute_scores(self, user, item, items_liked_by_user, users_liking_an_item):
        collaborative_score = [self.__relatedness_score('collab', user, item)]

        content_scores = []
        for past_item in items_liked_by_user:
            content_scores.append(self.__relatedness_score('content', past_item, item))
        content_score = np.mean(content_scores)

        social_scores = []
        for past_user in users_liking_an_item:
            social_scores.append(self.__relatedness_score('social', past_user, user))
        social_score = np.mean(social_scores)

        return collaborative_score, content_score, social_score
        

    def __relatedness_score(self, relation, node1, node2):
        try:
            score = 1. - (cdist(self._subgraphs_embedding[relation][node1], self._subgraphs_embedding[relation][node2], 'cosine'))
        except KeyError:
            score = 0.

        return score