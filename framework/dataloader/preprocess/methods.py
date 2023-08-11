import importlib

from ..graph.graph import Graph

from tqdm import tqdm

def apply_method(G, **info):
    method2fun = {
        'binarize': binarize,
        'filter_by_rating': filter_by_rating
    }

    try:
        f = method2fun[info['method']]
        f(G, **info['parameters'])
    except KeyError:
        raise KeyError(f'Preprocessing method {info["method"]} is not implemented.')

def binarize(G: Graph, threshold: int):
    desc='Binarizing user rating'
    for (user, item) in tqdm(list(G.get_rating_edges()), desc=desc):
        edge_data = G.get_edge_data(user,item)
        
        bin_rate = 0 # negative
        if edge_data['rating'] > threshold:
            bin_rate = 1

        G[user][item]['rating'] = bin_rate

def filter_by_rating(G: Graph, min: float, max: float):
    desc=f'Filtering by rate using, where min={min} and max={max}'
    count = 0
    for (user, item) in tqdm(list(G.get_rating_edges()), desc=desc):
        edge_data = G.get_edge_data(user,item)
        
        rating = edge_data['rating']
        if not (rating >= min and rating <= max):
            G.remove_edge(user, item)
            count += 1