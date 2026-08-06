"""Nine Eyes — global surveillance-network analysis.

The Nine Eyes program (``Spectre``, 2015 — mission codename NINE EYES) sweeps a
global surveillance network: intelligence agencies as nodes, data-sharing
links as directed edges. This module models the programme's geometric core:

* **data flow** — directed adjacency over agencies, in/out degree centrality;
* **centralization** — Freeman group centralization and the Herfindahl
  concentration of the inflow-share vector, read against its even-spread
  floor (:func:`uniform_share_index`) so the index is interpretable;
* **betweenness** — which agencies sit on the shortest data paths that carry
  the network's traffic (Brandes, unweighted);
* **cascade coverage** — an explicitly seeded Bernoulli influence cascade
  measuring how far a signal from a source propagates through sharing links,
  as one realization (:func:`cascade_coverage`) or as a trial-averaged
  expectation (:func:`expected_cascade_coverage`);
* **sweep coverage** — the fraction of a target population swept by at least
  one agency's signals.

The module is pure and infrastructure-free: ``numpy`` + the standard library
only, deterministic, and importable without ``bond-api``.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np

__all__ = [
    "SurveillanceNetwork",
    "CentralityResult",
    "CascadeResult",
    "build_network",
    "network_from_adjacency",
    "out_degree_centrality",
    "in_degree_centrality",
    "group_centralization",
    "betweenness_centrality",
    "herfindahl_index",
    "data_share_centrality",
    "uniform_share_index",
    "cascade_coverage",
    "expected_cascade_coverage",
    "sweep_coverage",
]


@dataclass(frozen=True)
class SurveillanceNetwork:
    """A directed agency network: node labels plus a square adjacency matrix.

    ``adjacency[i, j] != 0`` means agency ``i`` shares data with agency ``j``
    (a directed flow edge ``i -> j``). Self-loops are forbidden.
    """

    nodes: tuple[str, ...]
    adjacency: np.ndarray

    @property
    def n(self) -> int:
        """Number of agencies in the network."""
        return len(self.nodes)


@dataclass(frozen=True)
class CentralityResult:
    """Outcome of a centrality computation: per-node scores + ordering.

    ``scores`` maps node label -> numeric score; ``top`` lists node labels
    sorted by descending score (ties broken by insertion order).
    """

    scores: dict[str, float]
    top: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CascadeResult:
    """Outcome of a deterministic influence-cascade spread from a source set."""

    seeded: tuple[str, ...]
    activated: frozenset[str]
    coverage_fraction: float


def _validate_adjacency(adjacency: np.ndarray, nodes: Sequence[str]) -> None:
    """Validate a caller-supplied adjacency matrix against its node labels.

    Raises:
        ValueError: If the matrix is not square with one row per node, node
            labels repeat, or the matrix carries a self-loop on the diagonal.
    """
    n_nodes = len(nodes)
    if adjacency.shape != (n_nodes, n_nodes):
        raise ValueError(f"adjacency must be {n_nodes}x{n_nodes}, got {adjacency.shape}")
    if len(set(nodes)) != n_nodes:
        raise ValueError("node labels must be unique")
    if np.any(np.diag(adjacency)):
        raise ValueError("self-loops are not allowed in a surveillance network")


def network_from_adjacency(
    nodes: Sequence[str],
    adjacency: np.ndarray,
) -> SurveillanceNetwork:
    """Build a :class:`SurveillanceNetwork` from an existing adjacency matrix.

    The edge-list constructor :func:`build_network` enforces its invariants as
    it fills the matrix; this constructor accepts a matrix that was produced
    elsewhere (a slice, a transpose, a loaded artifact) and therefore has to
    validate it explicitly.

    Args:
        nodes: Unique agency labels, aligned with the matrix rows/columns.
        adjacency: Square matrix; ``adjacency[i, j] != 0`` is the flow
            ``i -> j``.

    Returns:
        A validated network (the matrix is copied, so the result is immutable
        with respect to the caller's array).

    Raises:
        ValueError: If the matrix is not square with one row per node, node
            labels repeat, or the diagonal carries a self-loop.
    """
    ordered = tuple(nodes)
    _validate_adjacency(adjacency, ordered)
    return SurveillanceNetwork(nodes=ordered, adjacency=np.array(adjacency, copy=True))


def build_network(
    nodes: Sequence[str],
    edges: Iterable[tuple[str, str]],
) -> SurveillanceNetwork:
    """Build a :class:`SurveillanceNetwork` from node labels and directed edges.

    Args:
        nodes: Unique agency labels.
        edges: Directed sharing links ``(source, target)``.

    Returns:
        A validated network with a square adjacency matrix.

    Raises:
        ValueError: If node labels are not unique or an edge references an
            unknown or self-loop pair.
    """
    ordered = tuple(nodes)
    index = {label: i for i, label in enumerate(ordered)}
    if len(index) != len(ordered):
        raise ValueError("node labels must be unique")
    n = len(ordered)
    adjacency = np.zeros((n, n), dtype=np.int64)
    for source, target in edges:
        if source not in index:
            raise ValueError(f"unknown source node {source!r}")
        if target not in index:
            raise ValueError(f"unknown target node {target!r}")
        if source == target:
            raise ValueError("self-loops are not allowed in a surveillance network")
        adjacency[index[source], index[target]] = 1
    # The loop above already enforces every invariant _validate_adjacency
    # checks (uniqueness, squareness, no self-loop), so re-checking here would
    # be a gate that cannot fail. Matrix-sourced networks go through
    # network_from_adjacency, which validates for real.
    return SurveillanceNetwork(nodes=ordered, adjacency=adjacency)


def _score_map(network: SurveillanceNetwork, values: Sequence[float]) -> dict[str, float]:
    return {label: float(values[i]) for i, label in enumerate(network.nodes)}


def _ordered(scores: dict[str, float]) -> tuple[str, ...]:
    return tuple(label for label, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0])))


def out_degree_centrality(network: SurveillanceNetwork) -> CentralityResult:
    """Out-degree centrality: volume of data each agency pushes downstream."""
    scores = _score_map(network, network.adjacency.sum(axis=1))
    return CentralityResult(scores=scores, top=_ordered(scores))


def in_degree_centrality(network: SurveillanceNetwork) -> CentralityResult:
    """In-degree centrality: volume of data each agency pulls upstream."""
    scores = _score_map(network, network.adjacency.sum(axis=0))
    return CentralityResult(scores=scores, top=_ordered(scores))


def group_centralization(scores: dict[str, float], *, maximum_score: float | None = None) -> float:
    """Freeman's group degree centralization in ``[0, 1]``.

    ``C = sum(max - score_i) / ((n - 1) * max)``, where ``max`` is the largest
    observed score (or an explicit ``maximum_score`` such as the star-graph
    bound). A value near 1 means a single agency dominates the flows; near 0
    means flows are evenly distributed. A single-node group returns 0.

    Args:
        scores: Per-node centrality scores.
        maximum_score: Optional theoretical maximum (e.g. ``n - 1`` for
            degree); defaults to the observed maximum.

    Raises:
        ValueError: If ``scores`` is empty or ``maximum_score`` is not positive.
    """
    if not scores:
        raise ValueError("scores must not be empty")
    values = [float(value) for value in scores.values()]
    for value in values:
        if not math.isfinite(value):
            raise ValueError("scores must all be finite")
    if maximum_score is not None and not math.isfinite(float(maximum_score)):
        raise ValueError("maximum_score must be finite")
    cap = maximum_score if maximum_score is not None else max(values)
    if cap <= 0:
        raise ValueError("maximum_score must be positive")
    n = len(values)
    if n < 2:
        return 0.0
    denominator = (n - 1) * cap
    return float(sum(cap - value for value in values) / denominator)


def _bfs_parents(adjacency: np.ndarray, source: int) -> tuple[dict[int, list[int]], list[int]]:
    """Return predecessors + BFS distances for every node reachable from ``source``.

    Reproduces the predecessor-list structure Brandes' algorithm expects.
    """
    n = len(adjacency)
    preds: dict[int, list[int]] = {i: [] for i in range(n)}
    dist: list[int] = [-1] * n
    dist[source] = 0
    queue: deque[int] = deque([source])
    while queue:
        node = queue.popleft()
        for raw in np.flatnonzero(adjacency[node]):
            nxt = int(raw)
            if dist[nxt] < 0:
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
            if dist[nxt] == dist[node] + 1:
                preds[nxt].append(node)
    return preds, dist


def betweenness_centrality(network: SurveillanceNetwork) -> CentralityResult:
    """Betweenness centrality via Brandes' algorithm (unweighted, directed).

    An agency's betweenness is the share of shortest data paths that pass
    through it — how pivotal it is to carrying the network's traffic.
    """
    n = network.n
    adj = network.adjacency
    centrality = np.zeros(n, dtype=np.float64)
    for source in range(n):
        preds, dist = _bfs_parents(adj, source)
        delta = np.zeros(n, dtype=np.float64)
        sigma: list[int] = [0] * n
        sigma[source] = 1
        reachable = [i for i in range(n) if dist[i] >= 0]
        for node in sorted(reachable, key=lambda i: dist[i]):
            for p in preds[node]:
                sigma[node] += sigma[p]
        for node in sorted(reachable, key=lambda i: dist[i], reverse=True):
            # Every node in `reachable` has at least one shortest path from
            # the source, so sigma[node] >= 1 — no zero-division guard here
            # (a guard that can never fire would only hide a real regression).
            for p in preds[node]:
                delta[p] += (sigma[p] / sigma[node]) * (1.0 + delta[node])
            if node != source:
                centrality[node] += delta[node]
    if n > 1:
        normalize = (n - 1) * (n - 2)
        if normalize > 0:
            centrality = centrality / normalize
    scores = _score_map(network, list(centrality))
    return CentralityResult(scores=scores, top=_ordered(scores))


def herfindahl_index(values: Sequence[float]) -> float:
    """Herfindahl–Hirschman concentration index over a normalized share vector.

    ``H = sum(share_i ** 2)`` for shares normalized to sum to 1. Values range
    from ``1/n`` (evenly spread) to ``1`` (monopoly). Used to measure how
    concentrated data flows are through a few hub agencies.

    Args:
        values: Non-negative flow quantities per agency.

    Raises:
        ValueError: If ``values`` is empty or sums to zero.
    """
    if not values:
        raise ValueError("values must not be empty")
    floats = [float(value) for value in values]
    for value in floats:
        if not math.isfinite(value):
            raise ValueError("values must all be finite")
    total = sum(floats)
    if total <= 0:
        raise ValueError("values must sum to a positive total")
    return float(sum((value / total) ** 2 for value in floats))


def data_share_centrality(network: SurveillanceNetwork) -> CentralityResult:
    """Each agency's share of all inbound data flows.

    ``share_j = inflow_j / sum_k inflow_k``, where ``inflow_j`` is agency
    ``j``'s in-degree. The scores are a probability vector: they sum to 1 on
    any network carrying at least one edge, and an agency that receives
    nothing scores 0. An edgeless network has no flow to share, so every score
    is 0 (and the vector sums to 0, not 1).

    This is the vector :func:`herfindahl_index` is meant to consume; feeding it
    anything that is not normalized to a total of 1 makes the resulting index
    meaningless.
    """
    inflow = network.adjacency.astype(np.float64).sum(axis=0)
    total = float(inflow.sum())
    shares = inflow / total if total > 0 else np.zeros_like(inflow)
    scores = _score_map(network, list(shares))
    return CentralityResult(scores=scores, top=_ordered(scores))


def uniform_share_index(network: SurveillanceNetwork) -> float:
    """The Herfindahl floor for this network's inflow-share vector.

    The HHI of a share vector spread as evenly as possible over the agencies
    that receive *anything* is ``1 / r``, where ``r`` is the number of agencies
    with non-zero in-degree. Reporting a measured HHI without this floor is
    uninterpretable: an index of 0.14 on nine agencies sounds concentrated
    until you know the floor is 0.125.

    Raises:
        ValueError: If no agency receives any flow (the floor is undefined).
    """
    inflow = network.adjacency.sum(axis=0)
    receiving = int(np.count_nonzero(inflow))
    if receiving == 0:
        raise ValueError("no agency receives flow — the even-spread floor is undefined")
    return 1.0 / receiving


def cascade_coverage(
    network: SurveillanceNetwork,
    sources: Iterable[str],
    activation_prob: float,
    *,
    seed: int = 0,
) -> CascadeResult:
    """One seeded realization of an influence cascade from a set of agencies.

    A seeded agency activates; each *active* agency then attempts to activate
    each downstream neighbour, and a neighbour activates with an independent
    Bernoulli draw at exactly ``activation_prob``, drawn from
    ``numpy.random.default_rng(seed)``.

    This returns a **single Bernoulli realization**, not an expectation: with
    ``0 < activation_prob < 1`` the coverage fraction of one draw can sit far
    from the mean. Use :func:`expected_cascade_coverage` when the quantity of
    interest is the expected reach.

    Args:
        network: The surveillance network.
        sources: Agencies seeded with the signal.
        activation_prob: Probability ``(0, 1]`` that an edge transmits a signal.
        seed: RNG seed governing every activation draw in this realization.

    Raises:
        ValueError: If ``activation_prob`` is outside ``(0, 1]``, sources are
            unknown, or no sources are given.
    """
    if not 0.0 < activation_prob <= 1.0:
        raise ValueError("activation_prob must be in (0, 1]")
    # Materialize first: `sources` is an Iterable, so a generator would be
    # emptied by the emptiness check and silently seed nothing.
    requested = tuple(sources)
    if not requested:
        raise ValueError("at least one source agency is required")
    index = network.nodes  # tuple of labels
    label_to_i = {label: i for i, label in enumerate(index)}
    rng = np.random.default_rng(seed)
    for label in requested:
        if label not in label_to_i:
            raise ValueError(f"unknown source agency {label!r}")
    seeds = tuple(sorted(set(requested)))
    frontier = [label_to_i[label] for label in seeds]
    activated: set[int] = set(frontier)
    while frontier:
        node = frontier.pop()
        for raw in np.flatnonzero(network.adjacency[node]):
            nxt = int(raw)
            if nxt in activated:
                continue
            if rng.random() < activation_prob:
                activated.add(nxt)
                frontier.append(nxt)
    reached = frozenset(index[i] for i in activated)
    return CascadeResult(
        seeded=seeds,
        activated=reached,
        coverage_fraction=len(activated) / network.n,
    )


def expected_cascade_coverage(
    network: SurveillanceNetwork,
    sources: Iterable[str],
    activation_prob: float,
    *,
    trials: int,
    seed: int = 0,
) -> float:
    """Mean cascade coverage over ``trials`` independently seeded realizations.

    :func:`cascade_coverage` is a single Bernoulli draw; this averages
    ``trials`` of them with per-trial seeds derived as ``seed + i`` (the same
    derivation :func:`spectre.infiltration.expected_damage` uses), so the
    reported reach is an estimate of the expectation rather than one sample.

    Args:
        network: The surveillance network.
        sources: Agencies seeded with the signal.
        activation_prob: Probability ``(0, 1]`` that an edge transmits a signal.
        trials: Number of realizations to average; must be positive.
        seed: Base seed; trial ``i`` runs at ``seed + i``.

    Raises:
        ValueError: If ``trials`` is not positive, or on any error
            :func:`cascade_coverage` raises.
    """
    if trials <= 0:
        raise ValueError("trials must be positive")
    requested = tuple(sources)
    total = 0.0
    for i in range(trials):
        total += cascade_coverage(network, requested, activation_prob, seed=seed + i).coverage_fraction
    return total / trials


def sweep_coverage(captured: int, total: int) -> float:
    """Fraction ``captured/total`` of a target population swept by agencies.

    Args:
        captured: Number of distinct targets captured by at least one agency.
        total: Total target population size.

    Raises:
        ValueError: If ``captured`` or ``total`` is negative, or ``captured``
            exceeds ``total``.
    """
    if captured < 0 or total < 0:
        raise ValueError("captured and total must be non-negative")
    if captured > total:
        raise ValueError("captured cannot exceed total")
    if total == 0:
        return 0.0
    return float(captured / total)
