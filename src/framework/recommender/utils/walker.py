# Code extracted from: https://raw.githubusercontent.com/benedekrozemberczki/karateclub/master/karateclub/utils/walker.py

import random
from functools import partial
from typing import List, Callable

import numpy as np
import networkx as nx
from tqdm import tqdm


def random_walks(graph, n_walks: int = 1, walk_len: int = 10, start_nodes=None,
                 p: float = 1.0, q: float = 1.0):
    """Run truncated random walks on ``graph``.

    This is a dependency-free replacement for the external ``graph-walker``
    library: it relies only on ``numpy`` / ``networkx`` / ``tqdm`` and returns
    native node ids -- whatever the graph uses as labels (integers, strings, or
    the framework's ``Node`` objects).

    :param graph: a NetworkX graph (undirected, weighted or unweighted)
    :param n_walks: number of walks to sample from each start node
    :param walk_len: number of *hops* per walk; a walk stops early at a dead
        end, so it may be shorter than ``walk_len``
    :param start_nodes: optional iterable of start nodes; defaults to every node
    :param p: return parameter of the Node2Vec second-order walk
    :param q: in-out parameter of the Node2Vec second-order walk
        (``p == q == 1`` -- the default -- yields a first-order uniform walk)
    :return: a list of walks, each a list of node ids beginning with its
        start node
    """
    if start_nodes is None:
        start_nodes = list(graph.nodes())

    biased = p != 1.0 or q != 1.0
    walks = []
    for node in tqdm(start_nodes, total=len(start_nodes), desc="running random walks"):
        for _ in range(n_walks):
            walks.append(_do_walk(graph, node, walk_len, p, q, biased))

    return walks


def _do_walk(graph, node, walk_len: int, p: float, q: float, biased: bool) -> list:
    """A single truncated random walk of up to ``walk_len`` hops at ``node``.

    With ``biased=False`` (``p == q == 1``) this is a first-order uniform walk.
    Otherwise it is a Node2Vec second-order walk with return probability ``1/p``
    and in-out probability ``1/q``.
    """
    walk = [node]
    if not biased:
        for _ in range(walk_len):
            neighbors = list(graph.neighbors(walk[-1]))
            if not neighbors:
                 # Dead end: stop early. Callers tolerate short walks.
                break
            walk.append(np.random.choice(neighbors))
        return walk

    edge_fn = _get_edge_fn(graph)
    weight_fn = _get_weight_fn(graph)
    previous_node = None
    previous_node_neighbors = []
    for _ in range(walk_len):
        current_node = walk[-1]
        edges = edge_fn(current_node)
        if not edges:
             # Dead end: stop early.
            break
        current_node_neighbors = np.array([edge[1] for edge in edges])
        weights = weight_fn(edges)
        probability = np.piecewise(
            weights,
            [
                current_node_neighbors == previous_node,
                np.isin(current_node_neighbors, previous_node_neighbors),
            ],
            [lambda w: w / p, lambda w: w, lambda w: w / q],
        )
        norm_probability = probability / sum(probability)
        walk.append(np.random.choice(current_node_neighbors, 1, p=norm_probability)[0])
        previous_node_neighbors = current_node_neighbors
        previous_node = current_node

    return walk


class RandomWalker:
    """
    Class to do fast first-order random walks.

    Args:
        walk_length (int): Number of random walks.
        walk_number (int): Number of nodes in truncated walk.
    """

    def __init__(self, walk_length: int, walk_number: int):
        self.walk_length = walk_length
        self.walk_number = walk_number

    def do_walk(self, node: int) -> List[str]:
        """
        Doing a single truncated random walk from a source node.

        Arg types:
            * **node** *(int)* - The source node of the random walk.

        Return types:
            * **walk** *(list of strings)* - A single truncated random walk.
        """
        walk: List[int] = [node]
        for _ in range(self.walk_length - 1):
            nebs = [node for node in self.graph.neighbors(walk[-1])]
            if len(nebs) > 0:
                walk = walk + random.sample(nebs, 1)
        walk = [str(w) for w in walk]
        return walk

    def do_walks(self, graph):
        """
        Doing a fixed number of truncated random walk from every node in the graph.

        Arg types:
            * **graph** *(NetworkX graph)* - The graph to run the random walks on.
        """
        self.walks: List[List[str]] = []
        self.graph = graph
        for node in tqdm(self.graph.nodes()):
            for _ in range(self.walk_number):
                walk_from_node = self.do_walk(node)
                self.walks.append(walk_from_node)


def _check_value(value, name):
    try:
        _ = 1 / value

    except ZeroDivisionError:
        raise ValueError(
            f"The value of {name} is too small " f"or zero to be used in 1/{name}."
        )


def _undirected(node, graph) -> List[tuple]:
    edges = graph.edges(node)

    return edges


def _directed(node, graph) -> List[tuple]:
    edges = graph.out_edges(node, data=True)

    return edges


def _get_edge_fn(graph) -> Callable:
    fn = _directed if nx.classes.function.is_directed(graph) else _undirected

    fn = partial(fn, graph=graph)
    return fn


def _unweighted(edges: List[tuple]) -> np.ndarray:
    return np.ones(len(edges))


def _weighted(edges: List[tuple]) -> np.ndarray:
    weights = map(lambda edge: edge[-1]["weight"], edges)

    return np.array([*weights])


def _get_weight_fn(graph) -> Callable:
    fn = _weighted if nx.classes.function.is_weighted(graph) else _unweighted

    return fn


class BiasedRandomWalker:
    """
    Class to do biased second order random walks.

    Args:
        walk_length (int): Number of random walks.
        walk_number (int): Number of nodes in truncated walk.
        p (float): Return parameter (1/p transition probability) to move towards previous node.
        q (float): In-out parameter (1/q transition probability) to move away from previous node.
    """

    walks: list
    graph: nx.classes.graph.Graph
    edge_fn: Callable
    weight_fn: Callable

    def __init__(self, walk_length: int, walk_number: int, p: float, q: float):
        self.walk_length = walk_length
        self.walk_number = walk_number

        _check_value(p, "p")
        self.p = p

        _check_value(q, "q")
        self.q = q

    def do_walk(self, node: int) -> List[str]:
        """
        Doing a single truncated second order random walk from a source node.

        Arg types:
            * **node** *(int)* - The source node of the random walk.

        Return types:
            * **walk** *(list of strings)* - A single truncated random walk.
        """
        walk = [node]
        previous_node = None
        previous_node_neighbors = []
        for _ in range(self.walk_length - 1):
            current_node = walk[-1]
            edges = self.edge_fn(current_node)
            current_node_neighbors = np.array([edge[1] for edge in edges])

            weights = self.weight_fn(edges)
            probability = np.piecewise(
                weights,
                [
                    current_node_neighbors == previous_node,
                    np.isin(current_node_neighbors, previous_node_neighbors),
                ],
                [lambda w: w / self.p, lambda w: w / 1, lambda w: w / self.q],
            )

            norm_probability = probability / sum(probability)
            selected = np.random.choice(current_node_neighbors, 1, p=norm_probability)[
                0
            ]
            walk.append(selected)

            previous_node_neighbors = current_node_neighbors
            previous_node = current_node

        walk = [str(w) for w in walk]
        return walk

    def do_walks(self, graph) -> None:
        """
        Doing a fixed number of truncated random walk from every node in the graph.

        Arg types:
            * **graph** *(NetworkX graph)* - The graph to run the random walks on.
        """
        self.walks = []
        self.graph = graph

        self.edge_fn = _get_edge_fn(graph)
        self.weight_fn = _get_weight_fn(graph)

        for node in tqdm(self.graph.nodes()):
            for _ in range(self.walk_number):
                walk_from_node = self.do_walk(node)
                self.walks.append(walk_from_node)