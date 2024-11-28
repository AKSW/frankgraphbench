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

from scipy.spatial.distance import cosine
from tqdm import tqdm

class Entity2Rec(Recommender):
    def __init__(
            self, 
            config: dict,
            feedback_file: str = None, 
            embedding_model: str = "deepwalk_based",
            embedding_model_kwargs: dict = None,
            run_all: bool = False, 
            collab_only: bool = False,
            content_only: bool = False,
            social_only: bool = False,
            workers: int = -1,
            frac_negative_candidates: float = 0.1,
            seed: int = 42,
            iterations: int = 1, 
            relevance: float = 0.0,
            metric: str = "NDCG",
            k: int = 5,
            relation_template: dict = {'collab': 'rating', 'social': 'is', 'content': 'has'},
        ):
        super().__init__(config)
        self.feedback_file = feedback_file
        self.embedding_model = embedding_model
        self.embedding_model_kwargs = embedding_model_kwargs
        self.run_all = run_all
        self.workers = workers
        self.frac_negative_candidates = frac_negative_candidates
        self.seed = seed
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
        self._e2rec = None

    def name(self):
        text = "Entity2Rec"
        text += f";embedding_model={self.embedding_model};embedding_model_kwargs={self.embedding_model_kwargs};run_all={self.run_all};"
        text += f"workers={self.workers};iterations={self.iterations};collab_only={self.collab_only};content_only={self.content_only}"
        return text
    
    def train(self, G_train: Graph, ratings_train: Dict[UserNode, List[Tuple[ItemNode, float]]]):
        self.G_train = G_train
        self.ratings_train = ratings_train
        self._triples = G_train.get_all_triples(return_type="obj")
        self.fit()
    
    def get_recommendations(self, k: int = 5) -> Dict[UserNode, List[ItemNode]]:
        x_test, y_test, qids_test, items_test = self._compute_features('test', n_jobs=self.workers)
        recs = self._e2rec.predict(x_test, qids_test)

        groups = {}
        for idx, user in enumerate(qids_test):
            if user in groups:
                groups[user].append((items_test[idx], recs[idx]))
            else:
                groups[user] = [(items_test[idx], recs[idx])]

        for user in groups.keys():
            groups[user] = sorted(groups[user], key = lambda x: x[1], reverse=True)
            groups[user] = [tuple_rec[0] for tuple_rec in groups[user]]
        
        return groups

    
    def fit(self):
        self.entity2rec()

    def entity2rec(self):
        self.entity2vec()

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

        x_train, y_train, qids_train, items_train = self._compute_features('train', n_jobs=self.workers)
        
        self._e2rec = Entity2RecD2K('for_init', run_all=self.run_all, feedback_file=self.feedback_file, 
                   workers=self.workers, iterations=self.iterations, collab_only=self.collab_only,
                   content_only=self.content_only, social_only=self.social_only)
        
        self._e2rec.fit(x_train, y_train, qids_train,
            optimize=self.metric, N=self.k)

    def _generate_subgraphs(self):
        self._relations = self._triples['relation'].unique()
        filter_temp = {}
        for relation in self._relations:
            filter_temp[relation] = pd.concat([self._triples['head'][self._triples['relation'] == relation], self._triples['tail'][self._triples['relation'] == relation]])

        # joining rating properties according to collab, content, social properties, and relevant score delimitations
        new_filter_temp = {}
        for temp, rel in self.relation_template.items():
            new_filter_temp[temp] = pd.Series()
            for relation in self._relations:
                if rel in relation:
                    new_filter_temp[temp] = pd.concat([new_filter_temp[temp], filter_temp[relation]])

        for rel, df in new_filter_temp.items():
            self._subgraphs[rel] = nx.subgraph(self.G_train, df)
        
        # make relations same as template
        self._relations = list(self.relation_template.keys())

    def _compute_features(self, data, n_jobs=-1):
        def process(data, users, return_dict, i):
            TX, Ty, Tqids, Titems = [], [], [], []

            desc = f"Computing features for user-item ratings (thread: {i})"
            for user in tqdm(users, desc=desc):
                if data == 'train':
                    candidate_items = self.__get_candidate_items(user, train=True, frac_negative_candidates=self.frac_negative_candidates)
                else:
                    candidate_items = self.__get_candidate_items(user)
                for item in candidate_items:
                    items_liked_by_user = self.__items_liked_by_user(user)
                    users_liking_an_item = self.__users_liking_an_item(item)

                    features = self.__compute_user_item_features(user, item, items_liked_by_user, users_liking_an_item)
                    
                    if features:
                        TX.append(features)
                        Ty.append(self.__get_relevance(user, item))
                        Tqids.append(user)
                        Titems.append(item)
                    else:
                        continue

            return_dict[f"{i}"] = (TX, Ty, Tqids, Titems)
        
        def split_processing(data, n_jobs, return_dict):
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
                    multiprocess.Process(target=process, args=(data, users[start:end], return_dict, i)))
                threads[-1].start() # start the thread we just created                  

            # wait for all threads to finish                                            
            for t in threads:
                t.join()
        
        if n_jobs == -1:
            n_jobs = multiprocess.cpu_count()

        return_dict = multiprocess.Manager().dict()
        TX, Ty, Tqids, Titems = [], [], [], []

        split_processing(data, n_jobs, return_dict)
        return_dict = dict(return_dict)
        for t in range(n_jobs):
            TX += return_dict[f"{t}"][0]
            Ty += return_dict[f"{t}"][1]
            Tqids += return_dict[f"{t}"][2]
            Titems += return_dict[f"{t}"][3]
        return TX, Ty, Tqids, Titems

    def __get_relevance(self, user, item):
        ratings = self.G_train.get_ratings_with_labels()
        relevance = 0
        for i, r in ratings[user]:
            if i == item:
                relevance = r
                break
        
        return relevance

    def __get_candidate_items(self, user, train=False, frac_negative_candidates=0.1):
        items = list(self.G_train.get_item_nodes())

        rated_items = []
        for u, i in self.G_train.get_rating_edges():
            if u == user:
                rated_items.append(i)
        
        unrated_items = [item for item in items if item not in rated_items]

        if train:
            return pd.Series(rated_items + unrated_items[:round(len(unrated_items)*frac_negative_candidates)]).sample(frac=1, random_state=self.seed).to_list()
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
        if content_scores:
            content_score = np.mean(content_scores)
        else:
            content_score = []

        social_scores = []
        for past_user in users_liking_an_item:
            social_scores.append(self.__relatedness_score('social', past_user, user))
        if social_scores:
            social_score = np.mean(social_scores)
        else:
            social_score = []

        return collaborative_score, content_score, social_score
        

    def __relatedness_score(self, relation, node1, node2):
        try:
            score = 1. - (cosine(self._subgraphs_embedding[relation][node1], self._subgraphs_embedding[relation][node2]))
        except KeyError:
            score = 0.

        return score