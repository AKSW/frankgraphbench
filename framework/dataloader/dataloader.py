import importlib

from .graph.graph import Graph
from .preprocess.methods import apply_method

"""
    Loads, preprocess, filter and split dataset, then return a NetworkX graph
    :arguments: 
        dataset: dict specifying the dataset configuration 
    :returns: Networkx graph (train, val, test)
"""
def load(**data_config):
    G = Graph(**data_config)
    return G

def preprocess(G, methods: list):
    print(len(list(G.get_rating_edges())))
    print(len(list(G.get_rating_edges(key_type='item'))))
    for method in methods:
        apply_method(G, **method)
    print(len(list(G.get_rating_edges())))
    print(len(list(G.get_rating_edges(key_type='item'))))
        
    