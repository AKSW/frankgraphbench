import random
import math
from copy import deepcopy
from collections import defaultdict

from ..graph.graph import Graph

import numpy as np
from sklearn.model_selection import KFold

class EdgeSplitter():
    def __init__(self, G: Graph, seed : int = 42):
        self.G = deepcopy(G)
        self.random_state = seed
        random.seed(seed)
        np.random.seed(seed)

        self.supported_methods = [
            'random_by_ratio',
            'timestamp_by_ratio',
            'fixed_timestamp',
            'k_fold'
        ]
    
    def split(self, **config):
        method = config['method']
        if method not in self.supported_methods:
            raise ValueError(f'Invalid split method provided. So far, the supported ones are:\n{self.supported_methods}')

        if method in ['random_by_ratio', 'timestamp_by_ratio']:
            p = config['p']
            level = config["level"]
            if p <= 0 or p >= 1:
                raise ValueError('The parameter p must be in the interval (0,1)')

            if level not in ['user', 'global']:
                raise ValueError('Invalid level parameter for splitting. Choose between user and global level.')
            
            print(f'Splitting data using {method} method at {level} level, where p={p} ...')
            
            if method == 'random_by_ratio':
                test = self._random_by_ratio(p, level)
            elif method == 'timestamp_by_ratio':
                test = self._timestamp_by_ratio(p, level)
            
            yield self._extract_dataset(test)

        elif method == 'fixed_timestamp':
            print(f'Splitting data using {method} method, where timestamp={config["timestamp"]} ...')

            test = []
            for (u,v) in self.G.get_rating_edges():
                data = self.G.get_edge_data(u,v)
                if data['timestamp'] > config['timestamp']:
                    test.append((u,v))
            yield self._extract_dataset(test)

        elif method == 'k_fold':
            k = config['k']
            if k < 2:
                raise ValueError('k parameter for K-fold must be at least 2.')
            
            level = config['level']
            if level not in ['user', 'global']:
                raise ValueError('Invalid level parameter for splitting. Choose between user and global level.')
            
            
            for test in self._kfold(k, level):
                yield self._extract_dataset(test)

    def _extract_dataset(self, test):
        # edges, labels = [], []
        ratings = defaultdict(list)
        for (u, v) in test:
            data = self.G.get_edge_data(u,v)
            self.G.remove_edge(u,v)
            ratings[u].append((v, data['rating']))

        return self.G, ratings 
    
    def _random_by_ratio(self, p: float, level: str) -> np.array:
        if level == 'global':
            ratings = np.array(list(self.G.get_rating_edges()))
            np.random.shuffle(ratings)
            n_test = math.ceil(ratings.shape[0] * p)

            return ratings[-n_test:]
        elif level == 'user':
            test = []
            for user, items in self.G.rating_edges.items():
                # Number of test items for user
                items = np.array(items)
                np.random.shuffle(items)
                n_test = math.ceil(items.shape[0] * p)
                test += [(user, item) for item in items[-n_test:]]

            return np.array(test)
        
    def _timestamp_by_ratio(self, p: float, level: str) -> np.array:
        if level == 'global':
            ratings = list(self.G.get_rating_edges())
            ratings = self._sort_by_timestamp(ratings)
            ratings = np.array(ratings)
            n_test = math.ceil(ratings.shape[0] * p)

            return ratings[-n_test:]
        elif level == 'user':
            test = []
            for user, items in self.G.rating_edges.items():
                ratings = [(user, item) for item in items]
                ratings = self._sort_by_timestamp(ratings)
                n_test = math.ceil(len(ratings) * p)    
                test += ratings[-n_test:]

            return np.array(test) 
        
    def _kfold(self, k : int, level : str):
        G_Copy = deepcopy(self.G)
        
        if level == 'global':
            ratings = list(self.G.get_rating_edges())
            ratings = np.array(ratings)
            np.random.shuffle(ratings)
            kfold = KFold(n_splits=k)
            for _, test_index in kfold.split(ratings):
                yield ratings[test_index]
                self.G = deepcopy(G_Copy)

        elif level == 'user':
            kfold_users, ratings_per_user = [], []
            for user, items in self.G.rating_edges.items():
                items = np.array(items)
                np.random.shuffle(items)
                kfold = KFold(n_splits=k).split(items)
                kfold_users.append(kfold)
                edges = np.array([(user, item) for item in items])
                ratings_per_user.append(edges)

            for _ in range(k):
                test = []
                for idx, kfold in enumerate(kfold_users):
                    _, test_index = next(kfold)
                    test_ratings = ratings_per_user[idx][test_index].tolist()
                    test += test_ratings
                test = np.array(test)
                yield test
                self.G = deepcopy(G_Copy)

    def _sort_by_timestamp(self, ratings: list) -> list:
        # globally sort the ratings by timestamp
        f = lambda edge: self.G.get_edge_data(edge[0], edge[1])['timestamp']
        return sorted(ratings, key=f)







