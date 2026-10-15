# Code extracted from: https://raw.githubusercontent.com/benedekrozemberczki/karateclub/master/karateclub/utils/walker.py

import random
from functools import partial
from typing import List, Callable

import numpy as np
import networkx as nx
from tqdm import tqdm


# Parent-side globals used by the copy-on-write fast path of
# :func:`parallel_random_walks`. On ``fork`` start methods the worker processes
# inherit these without copying the (potentially large) graph object.
_SHARED_GRAPH = None
_SHARED_START_NODES = None


def random_walks(graph, n_walks: int = 1, walk_len: int = 10, start_nodes=None,
                 p: float = 1.0, q: float = 1.0, seed=None):
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
    :param seed: optional integer that seeds a *local* ``numpy`` Generator so
        the walks are reproducible. When ``None`` (the default) the numpy global
        RNG is used unchanged, preserving prior behavior.
    :return: a list of walks, each a list of node ids beginning with its
        start node
    """
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random
    if start_nodes is None:
        start_nodes = list(graph.nodes())

    biased = p != 1.0 or q != 1.0
    walks = []
    for node in tqdm(start_nodes, total=len(start_nodes), desc="running random walks"):
        for _ in range(n_walks):
            walks.append(_do_walk(graph, node, walk_len, p, q, biased, rng))

    return walks


def parallel_random_walks(graph, n_walks: int = 1, walk_len: int = 10, start_nodes=None,
                          p: float = 1.0, q: float = 1.0, seed=None, workers=None):
    """Run truncated random walks on ``graph`` across multiple processes.

    This is the multi-process counterpart of :func:`random_walks`, intended for
    the DeepWalk / Node2Vec and CoLaKG pipelines where the walk phase dominates
    training time. It fans the start nodes out over worker processes with
    :mod:`multiprocess`, so the CPU-bound walk phase runs in parallel.

    The default worker count is **one quarter of the available CPU cores**
    (``multiprocess.cpu_count() // 4``); pass ``workers`` to override it. When the
    resolved count is below 2 or there are fewer than two start nodes the call runs
    in the main process instead, so this function is always safe to call.

    Why this is fast: ``multiprocess`` uses the ``fork`` start method by default,
    so the (potentially large) graph is published to the workers through a
    parent-side global and read by every child **copy-on-write** rather than being
    pickled and copied into each process through the IPC pipe. The per-worker task
    arguments are therefore just small integer ranges. If the platform cannot fork,
    the function degrades to the slower-but-correct pickled-argument path.

    Reproducibility: when ``seed`` is given, each start node derives its own RNG
    from the pair ``(seed, node_index)`` (see :func:`_node_rng`), where
    ``node_index`` is the node's position in ``start_nodes``. Because a node's
    walks depend only on that position -- not on which worker or chunk processed
    it -- the output is **identical regardless of the number of workers**
    (including the in-process fallback). Note this per-node seeding scheme
    differs from the legacy single-RNG stream of :func:`random_walks`, so a
    parallel run is not byte-for-byte identical to a legacy sequential run for
    the same seed; it is fully reproducible and worker-count independent instead.
    With ``seed is None`` the walk order is left nondeterministic.

    The arguments ``graph``, ``n_walks``, ``walk_len``, ``start_nodes``, ``p``,
    ``q`` and ``seed`` otherwise have the same meaning as in :func:`random_walks`.

    :param workers: number of worker processes; defaults to
        ``multiprocess.cpu_count() // 4``
    :return: a list of walks, each a list of node ids beginning with its
        start node, in the same order as the (sequential) ``start_nodes``
    """
    global _SHARED_GRAPH, _SHARED_START_NODES
    if start_nodes is None:
        start_nodes = list(graph.nodes())
    start_nodes = list(start_nodes)

    if workers is None:
        import multiprocess  # lazy: keeps the module importable without the dep
        workers = multiprocess.cpu_count() // 4

    biased = p != 1.0 or q != 1.0

    # Fewer than two workers or fewer than two start nodes: nothing to parallelise,
    # so run the same per-node-seeded loop in the main process. This keeps the
    # result worker-count independent even in the fallback.
    if workers < 2 or len(start_nodes) < 2:
        return _walks_for_nodes(graph, list(start_nodes), n_walks, walk_len,
                                p, q, biased, seed, 0)

    import multiprocess  # lazy: keeps the module importable without the dependency

    n = len(start_nodes)
    chunk_size = max((n + workers - 1) // workers, 1)
    tasks = [
        (i * chunk_size, min((i + 1) * chunk_size, n), n_walks, walk_len,
         p, q, biased, seed, i * chunk_size)
        for i in range(workers)
    ]

    start_method = multiprocess.get_start_method(allow_none=True)
    if start_method == "fork" or start_method is None:
        # Copy-on-write fast path: the large graph is published as a parent-side
        # global that ``fork`` children inherit without copying. Task args carry
        # only the integer ranges.
        _SHARED_GRAPH = graph
        _SHARED_START_NODES = start_nodes
        worker = _cow_walk_worker
    else:
        # Non-fork start method: children do not inherit the parent's address
        # space, so ship the graph in the (pickled) task args. Correct everywhere,
        # just less memory-efficient.
        _SHARED_GRAPH = None
        _SHARED_START_NODES = None
        tasks = [(graph, start_nodes, *task) for task in tasks]
        worker = _pickled_walk_worker

    with multiprocess.Pool(workers) as pool:
        chunk_walks = list(
            tqdm(pool.map(worker, tasks), total=len(tasks),
                 desc="running random walks (parallel)")
        )

    walks = []
    for result in chunk_walks:
        walks.extend(result)

    # Drop the shared references so the graph can be garbage-collected after the
    # pool is torn down.
    _SHARED_GRAPH = None
    _SHARED_START_NODES = None
    return walks


def _cow_walk_worker(task) -> list:
    """Copy-on-write worker body for :func:`parallel_random_walks`.

    Reads the graph and start nodes from the parent-side globals
    ``_SHARED_GRAPH`` / ``_SHARED_START_NODES`` (inherited by ``fork`` children
    copy-on-write) and only the integer range from the task. This is the fast
    path used on ``fork``-capable platforms.
    """
    start, end, n_walks, walk_len, p, q, biased, seed, offset = task
    nodes = _SHARED_START_NODES[start:end]
    return _walks_for_nodes(_SHARED_GRAPH, nodes, n_walks, walk_len,
                            p, q, biased, seed, offset)


def _pickled_walk_worker(task) -> list:
    """Pickled-argument worker body for :func:`parallel_random_walks`.

    Fallback for non-``fork`` start methods, where children do not inherit the
    parent address space: the graph and start-node list arrive inside the task
    tuple instead of via the shared globals.
    """
    graph, start_nodes, start, end, n_walks, walk_len, p, q, biased, seed, offset = task
    return _walks_for_nodes(graph, start_nodes[start:end], n_walks, walk_len,
                            p, q, biased, seed, offset)


def _walks_for_nodes(graph, nodes, n_walks: int, walk_len: int, p: float, q: float,
                     biased: bool, seed, offset) -> list:
    """Run ``n_walks`` walks for each node in ``nodes``.

    Shared by the in-process fallback and every parallel worker body. ``nodes`` is
    a slice of the start-node sequence and ``offset`` is the index of ``nodes[0]``
    within that sequence. Each node gets a reproducible RNG derived from
    ``(seed, its absolute index)`` via :func:`_node_rng`, so the walks do not
    depend on how the nodes were split across workers.
    """
    walks = []
    for local, node in enumerate(nodes):
        rng = _node_rng(seed, offset + local)
        for _ in range(n_walks):
            walks.append(_do_walk(graph, node, walk_len, p, q, biased, rng))
    return walks


def _node_rng(seed, node_index):
    """Return a per-node numpy Generator.

    With a given integer ``seed`` the Generator is derived deterministically from
    ``(seed, node_index)`` via :class:`numpy.random.SeedSequence`, so a node's
    walks are reproducible and independent of the worker / chunk layout. With
    ``seed is None`` an unseeded Generator is returned, matching the
    non-reproducible default of :func:`random_walks`.
    """
    if seed is None:
        return np.random.default_rng()
    spawned = np.random.SeedSequence([int(seed), int(node_index)]).spawn(1)
    return np.random.default_rng(spawned[0])


def _do_walk(graph, node, walk_len: int, p: float, q: float, biased: bool, rng) -> list:
    """A single truncated random walk of up to ``walk_len`` hops at ``node``.

    With ``biased=False`` (``p == q == 1``) this is a first-order uniform walk.
    Otherwise it is a Node2Vec second-order walk with return probability ``1/p``
    and in-out probability ``1/q``. ``rng`` is a numpy Generator (or the global
    ``np.random`` module) that provides the random draws.
    """
    walk = [node]
    if not biased:
        for _ in range(walk_len):
            neighbors = list(graph.neighbors(walk[-1]))
            if not neighbors:
                 # Dead end: stop early. Callers tolerate short walks.
                break
            walk.append(rng.choice(neighbors))
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
        walk.append(rng.choice(current_node_neighbors, size=1, p=norm_probability)[0])
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