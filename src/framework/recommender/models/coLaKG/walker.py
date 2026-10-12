"""
    Self-contained random-walk helper for CoLaKG's user-centered prompts.

    Provides ``random_walks`` with a ``start_nodes`` argument, which is not
    offered by the karateclub walker the original code imported. A first-order
    (uniform, unweighted) walk is sufficient here: the purpose is only to build
    a short, diverse neighborhood context for each user node to feed into the LLM
    prompt, so no biased (node2vec p/q) sampling is needed.
"""
import numpy as np
import networkx as nx

from tqdm import tqdm


def random_walks(graph, n_walks: int = 1, walk_len: int = 10, start_nodes=None):
    """Run truncated first-order random walks on ``graph``.

    :param graph: a (NetworkX) graph whose nodes are integer ids
    :param n_walks: number of walks to sample from each start node
    :param walk_len: number of *hops* per walk (the returned walk therefore has
        ``walk_len + 1`` nodes, the start node plus ``walk_len`` steps)
    :param start_nodes: optional iterable of start nodes; defaults to every node
    :return: a list of walks, each walk a list of integer node ids beginning
        with its start node
    """
    if start_nodes is None:
        start_nodes = list(graph.nodes())

    walks = []
    for node in tqdm(start_nodes, total=len(start_nodes), desc="running random walks"):
        for _ in range(n_walks):
            walks.append(_do_walk(graph, node, walk_len))

    return walks


def _do_walk(graph, node, walk_len: int):
    """A single truncated random walk of ``walk_len`` hops starting at ``node``."""
    walk = [node]
    for _ in range(walk_len):
        current = walk[-1]
        neighbors = list(graph.neighbors(current))
        if len(neighbors) == 0:
             # Dead end: stop early. The caller tolerates short walks.
            break
        current = np.random.choice(neighbors)
        walk.append(current)

    return walk
