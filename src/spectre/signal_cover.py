"""Nine Eyes signal cover — sensor-placement set cover and coverage redundancy.

The surveillance programme must *place* its monitoring capability: a set of
agencies, each able to cover a subset of targets (regions, networks,
personnel). This module models the placement problem with real combinatorial
algorithms:

* **coverage problem** — an agency × target binary coverage matrix
  (``build_coverage``);
* **greedy set cover** — the classic Johnson greedy heuristic that selects
  agencies by largest marginal gain until the required fraction of targets is
  covered (``greedy_set_cover``); for covering everything it stays within a
  factor ``O(log n)`` of the minimum set cover;
* **coverage counts and redundancy** — how many agencies cover each target
  (``coverage_counts``) and the fraction of targets swept by at least two
  agencies (``redundancy_index``) — a multi-sensor resilience measure;
* **uncovered targets** — the residual gaps of any placement
  (``uncovered_targets``).

Pure and infrastructure-free: ``numpy`` + the standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np

__all__ = [
    "CoverageProblem",
    "build_coverage",
    "canonical_coverage_problem",
    "greedy_set_cover",
    "coverage_counts",
    "uncovered_targets",
    "redundancy_index",
]


@dataclass(frozen=True)
class CoverageProblem:
    """A binary agency × target coverage matrix.

    ``matrix[a, t] == 1`` means agency ``a`` can cover target ``t``.
    """

    agencies: tuple[str, ...]
    targets: tuple[str, ...]
    matrix: np.ndarray


def build_coverage(
    agencies: Sequence[str],
    targets: Sequence[str],
    coverage: Mapping[str, Iterable[str]],
) -> CoverageProblem:
    """Build a :class:`CoverageProblem` from an agency → targets mapping.

    Args:
        agencies: Unique agency labels.
        targets: Unique target labels.
        coverage: Which targets each agency can cover (keys must be agencies;
            values must name targets).

    Raises:
        ValueError: If labels are not unique, a coverage key is an unknown
            agency, or a covered target is unknown.
    """
    ordered_agencies = tuple(agencies)
    ordered_targets = tuple(targets)
    if len(set(ordered_agencies)) != len(ordered_agencies):
        raise ValueError("agency labels must be unique")
    if len(set(ordered_targets)) != len(ordered_targets):
        raise ValueError("target labels must be unique")
    agency_index = {label: i for i, label in enumerate(ordered_agencies)}
    target_index = {label: i for i, label in enumerate(ordered_targets)}
    matrix = np.zeros((len(ordered_agencies), len(ordered_targets)), dtype=np.int64)
    for agency, covered in coverage.items():
        if agency not in agency_index:
            raise ValueError(f"unknown agency {agency!r} in coverage")
        row = agency_index[agency]
        for target in covered:
            if target not in target_index:
                raise ValueError(f"unknown target {target!r} covered by {agency!r}")
            matrix[row, target_index[target]] = 1
    return CoverageProblem(agencies=ordered_agencies, targets=ordered_targets, matrix=matrix)


def canonical_coverage_problem() -> CoverageProblem:
    """The canonical Nine Eyes placement scenario.

    Eight sweep targets over six agencies, with deliberate cross-coverage
    (every region reachable by more than one agency where physically
    plausible) so the greedy set cover is non-trivial: it needs multiple
    agencies AND retains multi-sensor redundancy (``redundancy_index > 0``).
    """
    return build_coverage(
        ("UK", "US", "CA", "AU", "DE", "FR"),
        (
            "north_atlantic",
            "europe_central",
            "europe_west",
            "mediterranean",
            "baltic",
            "black_sea",
            "pacific_west",
            "pacific_east",
        ),
        {
            "UK": ("north_atlantic", "europe_central", "europe_west"),
            "US": ("north_atlantic", "pacific_west", "pacific_east"),
            "CA": ("pacific_west", "pacific_east", "europe_west"),
            "AU": ("pacific_west", "pacific_east"),
            "DE": ("europe_central", "baltic", "europe_west"),
            "FR": ("mediterranean", "black_sea", "europe_west"),
        },
    )


def greedy_set_cover(
    problem: CoverageProblem, required_fraction: float = 1.0
) -> tuple[tuple[str, ...], frozenset[str]]:
    """Greedy set cover: agencies by marginal gain until targets are covered.

    Args:
        problem: The coverage problem.
        required_fraction: Fraction of targets that must be covered (default
            1.0 = cover everything reachable).

    Raises:
        ValueError: If ``required_fraction`` is outside ``(0, 1]``.

    Returns:
        ``(selected_agencies, covered_targets)`` — the agencies chosen in
        selection order and the target set they cover.
    """
    if not 0.0 < required_fraction <= 1.0:
        raise ValueError("required_fraction must be in (0, 1]")
    n_targets = len(problem.targets)
    if n_targets == 0:
        return (), frozenset()
    required_count = int(np.ceil(required_fraction * n_targets))
    covered: set[int] = set()
    remaining = sorted(range(len(problem.agencies)), key=lambda i: problem.agencies[i])
    selected: list[str] = []

    def marginal_gain(agency_index: int) -> int:
        return sum(1 for target in np.flatnonzero(problem.matrix[agency_index]) if int(target) not in covered)

    while len(covered) < required_count and remaining:
        # `remaining` is non-empty (loop condition), so max() always has a
        # candidate; ties break by agency label because `remaining` is sorted
        # by label and max() keeps the first maximal element.
        gains = {agency_index: marginal_gain(agency_index) for agency_index in remaining}
        best_index = max(remaining, key=lambda agency_index: gains[agency_index])
        if gains[best_index] <= 0:
            break
        selected.append(problem.agencies[best_index])
        remaining.remove(best_index)
        for target in np.flatnonzero(problem.matrix[best_index]):
            covered.add(int(target))
    covered_targets = frozenset(problem.targets[i] for i in covered)
    return tuple(selected), covered_targets


def coverage_counts(problem: CoverageProblem) -> dict[str, int]:
    """Per-target number of agencies that can cover it."""
    return {problem.targets[t]: int(problem.matrix[:, t].sum()) for t in range(len(problem.targets))}


def uncovered_targets(problem: CoverageProblem, selected: Iterable[str]) -> tuple[str, ...]:
    """Targets covered by *none* of ``selected``, sorted by label.

    Raises:
        ValueError: If ``selected`` names an unknown agency.
    """
    index = {label: i for i, label in enumerate(problem.agencies)}
    covered: set[int] = set()
    for label in selected:
        if label not in index:
            raise ValueError(f"unknown agency {label!r} in selected")
        for target in np.flatnonzero(problem.matrix[index[label]]):
            covered.add(int(target))
    return tuple(problem.targets[t] for t in range(len(problem.targets)) if t not in covered)


def redundancy_index(problem: CoverageProblem, selected: Iterable[str]) -> float:
    """Fraction of targets swept by at least two of ``selected`` agencies.

    A value near 1 means every target has multi-sensor redundancy (removing
    one agency loses no coverage); near 0 means coverage is single-string.

    Raises:
        ValueError: If ``selected`` names an unknown agency.
    """
    if len(problem.targets) == 0:
        return 0.0
    index = {label: i for i, label in enumerate(problem.agencies)}
    counts = np.zeros(len(problem.targets), dtype=np.int64)
    for label in selected:
        if label not in index:
            raise ValueError(f"unknown agency {label!r} in selected")
        counts += problem.matrix[index[label]]
    redundant = int((counts >= 2).sum())
    return float(redundant / len(problem.targets))
