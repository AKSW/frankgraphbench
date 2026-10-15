"""
    Random-walk helper for CoLaKG's user-centered prompts.

    This module re-exports the shared, dependency-free walk helpers from
    ``framework.recommender.utils.walker`` -- a drop-in replacement for the
    external ``graph-walker`` library. The shared implementation supports the
    ``start_nodes`` argument CoLaKG needs and, unlike a first-order-only walker,
    also accepts the Node2Vec ``p``/``q`` parameters. A first-order (uniform,
    unweighted) walk -- the default -- is sufficient for CoLaKG's purpose: it
    only needs a short, diverse neighborhood context per user node to feed into
    the LLM prompt, so the uniform default (``p == q == 1``) is used.

    ``parallel_random_walks`` runs the same walks across multiple processes
    (default: one quarter of the available CPU cores) and is what CoLaKG's
    prompt-building phase uses.
"""
from ...utils.walker import parallel_random_walks, random_walks

__all__ = ["parallel_random_walks", "random_walks"]
