import random
from copy import deepcopy

from ..graph.graph import Graph

import numpy as np

class EdgeSplitter():
    def __init__(self, G: Graph, seed : int = 42):
        self.G = deepcopy(G)
        self.random_state = seed
        random.seed(seed)
        np.random.seed(seed)

        self.supported_methods = [
            'random_by_ratio',
            'timestamp_by_ratio',
            'fixed_timestamp'
        ]
    
    def split(self, **config):
        method = config['method']
        if method not in self.supported_methods:
            raise ValueError(f'Invalid split method provided. So far, the supported ones are:\n{self.supported_methods}')

        ratings = np.array(list(self.G.get_rating_edges()))

        if method in ['random_by_ratio', 'timestamp_by_ratio']:
            p = config['p']
            level = config["level"]
            if p <= 0 or p >= 1:
                raise ValueError('The parameter p must be in the interval (0,1)')
            
            print(f'Splitting data using {method} method at {level} level, where p={p} ...')
            
            if method == 'random_by_ratio' and level == 'global':
                np.random.shuffle(ratings)
            elif method == 'timestamp_by_ratio' and level == 'global':
                ratings = self._sort_by_timestamp(ratings)

            n_test = int(len(ratings) * p)
            test = ratings[-n_test:]

        elif method == 'fixed_timestamp':
            print(f'Splitting data using {method} method, where timestamp={config["timestamp"]} ...')

            test = []
            for (u,v) in self.G.get_rating_edges():
                data = self.G.get_edge_data(u,v)
                if data['timestamp'] > config['timestamp']:
                    test.append((u,v))


        edges, labels = [], []
        for (u, v) in test:
            data = self.G.get_edge_data(u,v)
            self.G.remove_edge(u,v)
            edges.append((u.get_id(), v.get_id()))
            labels.append(data['rating'])

        return self.G, np.array(edges), np.array(labels)

    def _sort_by_timestamp(self, ratings: list):
        # globally sort the ratings by timestamp
        f = lambda edge: self.G.get_edge_data(edge[0], edge[1])['timestamp']
        return sorted(ratings, key=f)







