"""Network geometry — connectivity and critical-node analysis.

Where :mod:`spectre.surveillance_net` measures *flows* and
:mod:`spectre.org_intel` measures *hierarchy*, this module measures the bare
*geometry* of an undirected intelligence network: how connected it is, which
nodes are load-bearing, and how it fragments when operatives are neutralized.
Algorithms (all real and deterministic):

* **connectivity** — connected components, connectivity of the whole graph;
* **articulation points** — nodes whose removal disconnects the graph (Tarjan's
  DFS low-link algorithm);
* **global efficiency** — the average inverse shortest-path length, a standard
  small-world measure of how efficiently the network routes contact;
* **critical-node impact** — the pairwise-connectivity loss when a single node
  is removed; a priority ordering of the most load-bearing nodes, and a
  robustness curve under cumulative removal (attack simulation).

Pure and infrastructure-free: ``numpy`` + the standard library only.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

__all__ = [
    "build_adjacency",
    "connected_components",
    "is_connected",
    "articulation_points",
    "all_pairs_shortest_paths",
    "network_efficiency",
    "node_removal_impact",
    "robustness_curve",
    "critical_node_order",
]


@dataclass(frozen=True)
class RobustnessPoint:
    """One step of a cumulative-removal attack: removed set + largest component."""

    removed: tuple[str, ...]
    removed_count: int
    giant_component_fraction: float
    component_count: int


def build_adjacency(
    nodes: Sequence[str],
    edges: Iterable[tuple[str, str]],
) -> tuple[tuple[str, ...], np.ndarray]:
    """Build an undirected adjacency matrix from node labels and edge pairs.

    Returns ``(ordered_nodes, adjacency)`` where ``adjacency[i, j] == 1`` iff
    ``i`` and ``j`` share an edge.

    Raises:
        ValueError: If node labels are not unique, an edge references an
            unknown node, or an edge is a self-loop.
    """
    ordered = tuple(nodes)
    if len(set(ordered)) != len(ordered):
        raise ValueError("node labels must be unique")
    index = {label: i for i, label in enumerate(ordered)}
    n = len(ordered)
    adjacency = np.zeros((n, n), dtype=np.int64)
    for a, b in edges:
        if a not in index:
            raise ValueError(f"unknown node {a!r}")
        if b not in index:
            raise ValueError(f"unknown node {b!r}")
        if a == b:
            raise ValueError("self-loops are not allowed")
        i, j = index[a], index[b]
        adjacency[i, j] = 1
        adjacency[j, i] = 1
    return ordered, adjacency


def connected_components(adjacency: np.ndarray) -> list[set[int]]:
    """Connected components as sets of node indices (BFS flood fill)."""
    n = len(adjacency)
    visited: set[int] = set()
    components: list[set[int]] = []
    for start in range(n):
        if start in visited:
            continue
        component: set[int] = set()
        queue: deque[int] = deque([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            component.add(node)
            for raw in np.flatnonzero(adjacency[node]):
                nxt = int(raw)
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        components.append(component)
    return components


def is_connected(adjacency: np.ndarray) -> bool:
    """True when the graph has exactly one connected component."""
    return len(connected_components(adjacency)) == 1


def articulation_points(adjacency: np.ndarray) -> set[int]:
    """Articulation (critical) points via Tarjan's DFS low-link algorithm.

    A node is an articulation point if its removal disconnects the
    (traversed) component containing it. Returns the set of node indices.
    """
    n = len(adjacency)
    visited: set[int] = set()
    disc: dict[int, int] = {}
    low: dict[int, int] = {}
    parent: dict[int, int | None] = {}
    out: set[int] = set()
    timer = 0
    child_counts: dict[int, int] = {}

    def dfs(node: int) -> None:
        nonlocal timer
        visited.add(node)
        disc[node] = low[node] = timer
        timer += 1
        children = 0
        for raw in np.flatnonzero(adjacency[node]):
            nxt = int(raw)
            if nxt not in visited:
                children += 1
                parent[nxt] = node
                dfs(nxt)
                low[node] = min(low[node], low[nxt])
                if parent.get(node) is None and children > 1:
                    out.add(node)
                if parent.get(node) is not None and low[nxt] >= disc[node]:
                    out.add(node)
            elif nxt != parent.get(node):
                low[node] = min(low[node], disc[nxt])
        child_counts[node] = children

    for start in range(n):
        if start not in visited:
            dfs(start)
    return out


def all_pairs_shortest_paths(adjacency: np.ndarray) -> dict[int, dict[int, int]]:
    """BFS all-pairs shortest-path lengths (unit edge weights)."""
    n = len(adjacency)
    lengths: dict[int, dict[int, int]] = {}
    for source in range(n):
        dist = [-1] * n
        dist[source] = 0
        queue: deque[int] = deque([source])
        while queue:
            node = queue.popleft()
            for raw in np.flatnonzero(adjacency[node]):
                nxt = int(raw)
                if dist[nxt] < 0:
                    dist[nxt] = dist[node] + 1
                    queue.append(nxt)
        lengths[source] = {i: d for i, d in enumerate(dist) if d >= 0}
    return lengths


def _pairwise_connectivity(adjacency: np.ndarray) -> float:
    """Total number of connected (source, target) pairs across all components."""
    total = 0
    for component in connected_components(adjacency):
        size = len(component)
        total += size * (size - 1)
    return float(total)


def network_efficiency(adjacency: np.ndarray) -> float:
    """Global efficiency: mean inverse shortest-path length over all pairs.

    ``E = (1 / (n*(n-1))) * sum_{i != j} 1 / d(i, j)`` over *reachable* pairs.
    Returns 0 for fewer than two nodes.
    """
    n = len(adjacency)
    if n < 2:
        return 0.0
    lengths = all_pairs_shortest_paths(adjacency)
    total = 0.0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = lengths[i].get(j)
            if d is not None and d > 0:
                total += 1.0 / d
    return float(total / (n * (n - 1)))


def node_removal_impact(adjacency: np.ndarray, node: int) -> float:
    """Pairwise-connectivity loss when ``node`` is removed, normalized by baseline.

    Removes the node (and its incident edges), recomputes pairwise
    connectivity, and returns the fractional loss ``1 - reduced/baseline``.
    """
    n = len(adjacency)
    baseline = _pairwise_connectivity(adjacency)
    if n == 0:
        return 0.0
    mask = np.arange(n) != node
    reduced = adjacency[np.ix_(mask, mask)]
    post = _pairwise_connectivity(reduced)
    if baseline <= 0:
        return 0.0
    return float(1.0 - post / baseline)


def robustness_curve(
    adjacency: np.ndarray,
    nodes: Sequence[str],
    removal_order: Iterable[str],
) -> list[RobustnessPoint]:
    """Simulate cumulative removal and track the giant-component fraction.

    Args:
        adjacency: Undirected adjacency matrix.
        nodes: Node labels aligned with ``adjacency`` rows.
        removal_order: Nodes to remove, in attack order.

    Returns:
        One :class:`RobustnessPoint` per removal step, recording the largest
        connected component fraction and component count after that removal.
    """
    index = {label: i for i, label in enumerate(nodes)}
    remaining = set(range(len(nodes)))
    points: list[RobustnessPoint] = []
    removed_labels: list[str] = []
    for label in removal_order:
        if label not in index:
            raise ValueError(f"unknown node {label!r} in removal_order")
        node = index[label]
        if node not in remaining:
            raise ValueError(f"node {label!r} already removed")
        remaining.discard(node)
        removed_labels.append(label)
        mask = np.array(sorted(remaining), dtype=int)
        sub = adjacency[np.ix_(mask, mask)]
        comps = connected_components(sub)
        largest = max((len(c) for c in comps), default=0)
        points.append(
            RobustnessPoint(
                removed=tuple(removed_labels),
                removed_count=len(removed_labels),
                giant_component_fraction=largest / len(nodes) if nodes else 0.0,
                component_count=len(comps),
            )
        )
    return points


def critical_node_order(adjacency: np.ndarray, k: int | None = None) -> list[int]:
    """Rank nodes by descending pairwise-connectivity removal impact.

    A greedy attack ordering: at each step remove the node whose removal
    reduces the *current* graph's pairwise connectivity the most. ``k`` limits
    the number of nodes returned (default: all ``n``).
    """
    n = len(adjacency)
    remaining = list(range(n))
    order: list[int] = []
    cap = n if k is None else max(0, min(k, n))
    for _ in range(cap):
        if len(remaining) <= 1:
            break
        mask = np.array(remaining, dtype=int)
        current = adjacency[np.ix_(mask, mask)]
        position = {orig: i for i, orig in enumerate(remaining)}
        impacts = {orig: node_removal_impact(current, position[orig]) for orig in remaining}
        victim = max(remaining, key=lambda orig: impacts[orig])
        order.append(victim)
        remaining.remove(victim)
    return order
