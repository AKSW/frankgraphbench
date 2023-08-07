from .graph.graph import Graph

"""
    Loads data from data_config spec and return a NetworkX graph
    :arguments: 
        dataset: dict specifying the dataset configuration 
    :returns: Networkx graph (train, val, test)
"""
def load(**data_config):
    G = Graph(**data_config)
    