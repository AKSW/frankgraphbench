from ..utils import get_optional_argument
from .graph.graph import Graph
from .preprocess.methods import apply_method
from .edge_splitter.edge_splitter import EdgeSplitter

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
    for method in methods:
        apply_method(G, **method)

def split(G, **split_config):
    seed = get_optional_argument(split_config, 'seed', 42)
    edge_splitter_test = EdgeSplitter(G, seed=seed)
    print(G.info())
    G_train, ratings_test, labels_test = edge_splitter_test.split(**split_config['test'])
    print(f'\tDisturbed graph info after splitting test data: {G_train.info()}')
    print(f'\tNumber of test instances: {ratings_test.shape[0]}')

    if get_optional_argument(split_config, 'validation', False):
        edge_splitter_val = EdgeSplitter(G_train, seed=seed)
        G_train, ratings_val, labels_val = edge_splitter_val.split(**split_config['validation'])
        print(f'\tGraph info after splitting validation data: {G_train.info()}')
        print(f'\tNumber of validation instances: {ratings_val.shape[0]}')

    ratings_train, labels_train = G_train.get_ratings_with_labels()
    print(ratings_train)
    print(f'Number of training instances: {ratings_train.shape[0]}')