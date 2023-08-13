import importlib

from ..graph.graph import Graph

from tqdm import tqdm

def apply_method(G, **info):
    method2fun = {
        'binarize': binarize,
        'filter_by_rating': filter_by_rating,
        'filter_kcore': filter_kcore
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
    desc=f'Filtering by rate, where min={min} and max={max}'
    for (user, item) in tqdm(list(G.get_rating_edges()), desc=desc):
        edge_data = G.get_edge_data(user,item)
        
        rating = edge_data['rating']
        if not (rating >= min and rating <= max):
            G.remove_edge(user, item)

def filter_kcore(G: Graph, core: int, target: str, iterations: int = 1):
    print(f'K-core filtering (target={target}), where core={core} and {iterations} it.')
    for it in range(iterations):
        desc = f'K-core filtering {it+1} iteration over edges from each {target}'

        data = None
        if target == 'user':
            data = G.rating_edges.copy()
        elif target == 'item':
            data = G.rating_item2users.copy()

        n_total = len(list(data.keys()))

        count = 0
        for (u, vs) in tqdm(data.items(), total=n_total, desc=desc):
            if len(vs) < core:
                G.remove_node(u)
                count += 1
        if count == 0:
            break