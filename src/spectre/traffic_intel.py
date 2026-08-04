"""Nine Eyes traffic intelligence — interception coverage and monitoring allocation.

Where :mod:`spectre.surveillance_net` measures the *shape* of data flows, this
module models the operational interception problem: how much of the network's
traffic a monitoring agency can actually capture, and how to spend a limited
monitoring budget to maximize interception.

Models (all real, deterministic):

* **traffic network** — a directed volume matrix over agency pairs
  (``build_traffic_network``);
* **heavy hitters** — the top-``k`` links by carried volume
  (``heavy_hitters``);
* **interception coverage** — the fraction of total traffic intercepted when a
  set of agencies is monitored, where monitoring an agency captures every link
  incident to it (``interception_coverage``);
* **budgeted monitor allocation** — a greedy submodular-maximization heuristic
  (Nemhauser–Wolsey–Fisher style) that picks the ``budget`` agencies with the
  largest marginal interception gain, with deterministic tie-breaking
  (``monitor_allocation``). The greedy rule carries the classic
  ``(1 - 1/e)`` approximation guarantee for monotone submodular coverage.

Pure and infrastructure-free: ``numpy`` + the standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

__all__ = [
    "TrafficNetwork",
    "build_traffic_network",
    "canonical_traffic_network",
    "total_traffic",
    "heavy_hitters",
    "interception_coverage",
    "monitor_allocation",
]


@dataclass(frozen=True)
class TrafficNetwork:
    """A directed traffic volume matrix over agency pairs.

    ``traffic[i, j]`` is the data volume flowing from agency ``i`` to agency
    ``j`` (0 for absent links; self-loops are forbidden).
    """

    nodes: tuple[str, ...]
    traffic: np.ndarray

    @property
    def n(self) -> int:
        """Number of agencies in the traffic network."""
        return len(self.nodes)


def build_traffic_network(
    nodes: Sequence[str],
    links: Iterable[tuple[str, str, float]],
) -> TrafficNetwork:
    """Build a :class:`TrafficNetwork` from agency labels and volume links.

    Args:
        nodes: Unique agency labels.
        links: ``(source, target, volume)`` triples; volumes are accumulated
            when a pair repeats.

    Raises:
        ValueError: If node labels are not unique, a link references an
            unknown agency, a link is a self-loop, or a volume is negative.
    """
    ordered = tuple(nodes)
    index = {label: i for i, label in enumerate(ordered)}
    if len(index) != len(ordered):
        raise ValueError("node labels must be unique")
    n = len(ordered)
    traffic = np.zeros((n, n), dtype=np.float64)
    for source, target, volume in links:
        if source not in index:
            raise ValueError(f"unknown source agency {source!r}")
        if target not in index:
            raise ValueError(f"unknown target agency {target!r}")
        if source == target:
            raise ValueError("self-loops are not allowed in a traffic network")
        if volume < 0:
            raise ValueError(f"traffic volume must be non-negative, got {volume!r}")
        traffic[index[source], index[target]] += volume
    return TrafficNetwork(nodes=ordered, traffic=traffic)


def canonical_traffic_network() -> TrafficNetwork:
    """The canonical Nine Eyes traffic scenario: the hub carries the load.

    Volumes are chosen so the United States hub dominates carried traffic and
    the interception problem is non-trivial (no single agency sees the whole
    exchange).
    """
    return build_traffic_network(
        ("UK", "US", "CA", "AU", "NZ", "DE", "FR", "ES", "SE"),
        (
            ("US", "UK", 200.0),
            ("US", "CA", 150.0),
            ("US", "AU", 140.0),
            ("US", "NZ", 130.0),
            ("US", "DE", 180.0),
            ("US", "FR", 120.0),
            ("US", "ES", 110.0),
            ("US", "SE", 100.0),
            ("UK", "DE", 60.0),
            ("DE", "FR", 50.0),
            ("AU", "NZ", 45.0),
            ("ES", "SE", 40.0),
            ("FR", "ES", 35.0),
        ),
    )


def total_traffic(network: TrafficNetwork) -> float:
    """Sum of all carried traffic volumes."""
    return float(network.traffic.sum())


def heavy_hitters(network: TrafficNetwork, k: int) -> tuple[tuple[str, str, float], ...]:
    """The top-``k`` links by carried volume, descending.

    Ties break by agency label (source, then target) so the result is
    byte-deterministic.

    Args:
        network: The traffic network.
        k: Number of links to return.

    Raises:
        ValueError: If ``k`` is not positive.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    entries: list[tuple[str, str, float]] = []
    for i, source in enumerate(network.nodes):
        for raw in np.flatnonzero(network.traffic[i]):
            target_index = int(raw)
            entries.append(
                (
                    source,
                    network.nodes[target_index],
                    float(network.traffic[i, target_index]),
                )
            )
    entries.sort(key=lambda entry: (-entry[2], entry[0], entry[1]))
    return tuple(entries[:k])


def _link_set_of(network: TrafficNetwork, monitored: Iterable[str]) -> set[tuple[int, int]]:
    """Directed link index pairs intercepted by a monitored agency set.

    Monitoring an agency captures every link incident to it (in or out).
    """
    index = {label: i for i, label in enumerate(network.nodes)}
    links: set[tuple[int, int]] = set()
    for label in monitored:
        if label not in index:
            raise ValueError(f"unknown monitored agency {label!r}")
        node = index[label]
        for raw in np.flatnonzero(network.traffic[node]):
            links.add((node, int(raw)))
        for raw in np.flatnonzero(network.traffic[:, node]):
            links.add((int(raw), node))
    return links


def interception_coverage(network: TrafficNetwork, monitored: Iterable[str]) -> float:
    """Fraction of total traffic intercepted when ``monitored`` agencies watch.

    A link is intercepted when at least one of its endpoints is monitored.

    Args:
        network: The traffic network.
        monitored: Agencies performing interception.

    Raises:
        ValueError: If ``monitored`` names an unknown agency.
    """
    total = total_traffic(network)
    if total <= 0:
        return 0.0
    captured = 0.0
    for i, j in _link_set_of(network, monitored):
        captured += float(network.traffic[i, j])
    return float(captured / total)


def monitor_allocation(network: TrafficNetwork, budget: int) -> tuple[tuple[str, ...], float]:
    """Greedy budgeted allocation of monitoring agencies.

    At each step picks the not-yet-chosen agency whose addition intercepts the
    most *new* traffic (marginal gain); ties break by agency label. This is the
    classic greedy heuristic for monotone submodular coverage maximization
    (Nemhauser–Wolsey–Fisher), so for a budget of ``b`` agencies the achieved
    coverage is at least ``(1 - 1/e)`` of the optimal ``b``-agency coverage.

    Args:
        network: The traffic network.
        budget: Number of agencies that can be monitored.

    Raises:
        ValueError: If ``budget`` is negative.

    Returns:
        ``(selected_agencies, coverage_fraction)`` — the agencies chosen in
        selection order and the resulting interception coverage.
    """
    if budget < 0:
        raise ValueError("budget must be non-negative")
    nodes = network.nodes
    total = total_traffic(network)
    if total <= 0 or budget == 0 or not nodes:
        return (), 0.0
    remaining = list(nodes)
    selected: list[str] = []
    covered: set[tuple[int, int]] = set()
    index = {label: i for i, label in enumerate(nodes)}
    for _ in range(min(budget, len(nodes))):
        best: str | None = None
        best_gain = -1.0
        for label in remaining:
            node = index[label]
            gain = 0.0
            for raw in np.flatnonzero(network.traffic[node]):
                link = (node, int(raw))
                if link not in covered:
                    gain += float(network.traffic[link])
            for raw in np.flatnonzero(network.traffic[:, node]):
                link = (int(raw), node)
                if link not in covered:
                    gain += float(network.traffic[link])
            if gain > best_gain:
                best_gain = gain
                best = label
        if best is None or best_gain <= 0:
            break
        selected.append(best)
        remaining.remove(best)
        node = index[best]
        for raw in np.flatnonzero(network.traffic[node]):
            covered.add((node, int(raw)))
        for raw in np.flatnonzero(network.traffic[:, node]):
            covered.add((int(raw), node))
    captured = sum(float(network.traffic[i, j]) for i, j in covered)
    return tuple(selected), float(captured / total)
