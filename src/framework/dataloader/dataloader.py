from ..utils import get_optional_argument
from .graph.graph import Graph
from .preprocess.methods import apply_method
from .edge_splitter.edge_splitter import EdgeSplitter
from .dataset.dataset import Dataset

"""
    Loads, preprocess, filter and split dataset, then return a dataset
    :arguments: 
        dataset: dict specifying the dataset configuration 
    :returns: Networkx graph (train, val, test)
"""
def load(**data_config):
    # G = Graph(**data_config)
    G = Graph()
    G.build(**data_config)
    return G

def preprocess(G, methods: list):
    for method in methods:
        apply_method(G, **method)

def split(G, **split_config):
    seed = get_optional_argument(split_config, 'seed', 42)
    edge_splitter_test = EdgeSplitter(G, seed=seed)
    for (G_train, ratings_test) in edge_splitter_test.split(**split_config['test']):
        dataset = Dataset()
        dataset.set_test_data(ratings_test)
        print(f'\tDisturbed graph info after splitting test data: {G_train.info()}')
        print(f'\tNumber of test instances: {len_instances(ratings_test)}')

        if get_optional_argument(split_config, 'validation', False):
            if split_config['test']['method'] == 'k_fold' and split_config['validation']['method'] == 'k_fold':
                raise ValueError("Validation split does not support k_fold method.")
            
            edge_splitter_val = EdgeSplitter(G_train, seed=seed)
            for G_train, ratings_val in edge_splitter_val.split(**split_config['validation']):
                dataset.set_val_data(ratings_val)
                print(f'\tGraph info after splitting validation data: {G_train.info()}')
                print(f'\tNumber of validation instances: {len_instances(ratings_val)}')

        ratings_train = G_train.get_ratings_with_labels()
        # Attach the split technique + seed that produced this disturbed graph so
        # models building user-side artefacts from it (e.g. coLaKG's random-walk
        # prompts) can key their cache on it and avoid cross-split leakage.
        G_train._split_signature = build_split_signature(split_config, seed)
        dataset.set_train_data(G_train, ratings_train)
        print(f'Number of training instances: {len_instances(ratings_train)}')

        yield dataset

def build_split_signature(split_config, seed):
    """Return the technique signature of a split.

    The signature captures everything that determines the *disturbed* training
    graph -- i.e. which rating edges are held out -- from the split technique
    (the ``test`` method and its parameters, plus the optional ``validation``
    split) together with the top-level ``seed``. It is attached to ``G_train`` so
    a model that builds user-side artefacts from the training graph (e.g. coLaKG's
    random-walk prompts) can key its cache on it and avoid serving a cache built
    under a different split. Item-side artefacts do not depend on the split and
    are intentionally excluded.

    The returned object is plain and JSON-serializable so it can be stored in a
    cache file and rendered into a cache filename.
    """
    return {
        'seed': seed,
        'test': dict(split_config.get('test', {}) or {}),
        'validation': dict(split_config.get('validation', {}) or {}),
    }

def len_instances(data):
    return sum([len(items) for items in data.values()])


    
