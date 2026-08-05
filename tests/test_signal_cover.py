"""Tests for spectre.signal_cover — sensor-placement set cover and redundancy."""

from __future__ import annotations

import pytest

from spectre.signal_cover import (
    CoverageProblem,
    build_coverage,
    canonical_coverage_problem,
    coverage_counts,
    greedy_set_cover,
    redundancy_index,
    uncovered_targets,
)

AGENCIES = ("A", "B", "C")
TARGETS = ("t1", "t2", "t3")
COVERAGE = {
    "A": ("t1", "t2"),
    "B": ("t2", "t3"),
    "C": ("t3",),
}


class TestBuildCoverage:
    def test_valid(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        assert isinstance(problem, CoverageProblem)
        assert problem.matrix.shape == (3, 3)

    def test_duplicate_agencies_raises(self) -> None:
        with pytest.raises(ValueError):
            build_coverage(("A", "A"), TARGETS, {"A": ("t1",)})

    def test_duplicate_targets_raises(self) -> None:
        with pytest.raises(ValueError):
            build_coverage(AGENCIES, ("t1", "t1"), {"A": ("t1",)})

    def test_unknown_agency_raises(self) -> None:
        with pytest.raises(ValueError):
            build_coverage(AGENCIES, TARGETS, {"ZZ": ("t1",)})

    def test_unknown_target_raises(self) -> None:
        with pytest.raises(ValueError):
            build_coverage(AGENCIES, TARGETS, {"A": ("t9",)})


class TestGreedySetCover:
    def test_three_agencies_cover_all(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        selected, covered = greedy_set_cover(problem)
        assert set(covered) == set(TARGETS)
        # Two agencies (A+B) already cover all three targets.
        assert "A" in selected and "B" in selected
        assert len(selected) <= 3

    def test_fraction_cover(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        selected, covered = greedy_set_cover(problem, required_fraction=1 / 3)
        assert len(covered) >= 1

    def test_required_fraction_zero_raises(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        with pytest.raises(ValueError):
            greedy_set_cover(problem, required_fraction=0.0)

    def test_required_fraction_above_one_raises(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        with pytest.raises(ValueError):
            greedy_set_cover(problem, required_fraction=1.5)

    def test_empty_targets_returns_empty(self) -> None:
        problem = build_coverage(AGENCIES, (), {})
        selected, covered = greedy_set_cover(problem)
        assert selected == ()
        assert covered == frozenset()

    def test_deterministic_tie_break(self) -> None:
        # Two agencies covering disjoint-but-equal sets; greedy picks alphabetically.
        problem = build_coverage(("B", "A"), ("t1", "t2"), {"A": ("t1",), "B": ("t2",)})
        selected, _ = greedy_set_cover(problem, required_fraction=0.5)
        assert selected == ("A",)


class TestCoverageCounts:
    def test_counts(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        counts = coverage_counts(problem)
        assert counts["t1"] == 1
        assert counts["t2"] == 2


class TestUncoveredTargets:
    def test_partial_selection_leaves_gaps(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        assert uncovered_targets(problem, ("A",)) == ("t3",)

    def test_full_selection_none(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        assert uncovered_targets(problem, ("A", "B")) == ()

    def test_unknown_agency_raises(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        with pytest.raises(ValueError):
            uncovered_targets(problem, ("ZZ",))


class TestRedundancyIndex:
    def test_full_selection_redundancy(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        # A covers t1,t2; B covers t2,t3 -> only t2 is doubly-swept -> 1/3.
        assert redundancy_index(problem, ("A", "B")) == pytest.approx(1 / 3)

    def test_single_agency_zero_redundancy(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        assert redundancy_index(problem, ("A",)) == 0.0

    def test_unknown_agency_raises(self) -> None:
        problem = build_coverage(AGENCIES, TARGETS, COVERAGE)
        with pytest.raises(ValueError):
            redundancy_index(problem, ("ZZ",))

    def test_empty_targets_zero(self) -> None:
        problem = build_coverage(AGENCIES, (), {})
        assert redundancy_index(problem, ("A",)) == 0.0


class TestCanonical:
    def test_canonical_cover(self) -> None:
        problem = canonical_coverage_problem()
        selected, covered = greedy_set_cover(problem)
        assert set(covered) == set(problem.targets)
        assert len(selected) <= 4
        assert 0.0 < redundancy_index(problem, selected) < 1.0


class TestGreedyCoverExhaustion:
    def test_stops_when_no_agency_adds_a_target(self) -> None:
        """An unreachable target cannot be covered: greedy must stop, not spin."""
        problem = build_coverage(
            ("A", "B"),
            ("t1", "t2", "unreachable"),
            {"A": ("t1",), "B": ("t2",)},
        )
        selected, covered = greedy_set_cover(problem)
        assert selected == ("A", "B")
        assert covered == frozenset({"t1", "t2"})
        assert uncovered_targets(problem, selected) == ("unreachable",)

    def test_agency_covering_nothing_is_never_selected(self) -> None:
        problem = build_coverage(("A", "idle"), ("t1",), {"A": ("t1",), "idle": ()})
        selected, covered = greedy_set_cover(problem)
        assert selected == ("A",)
        assert covered == frozenset({"t1"})


class TestGreedyBreaksOnZeroGain:
    def test_break_when_remaining_agencies_add_nothing(self) -> None:
        """Agencies remain, but none can add a target: greedy breaks out."""
        problem = build_coverage(
            ("A", "idle"),
            ("t1", "unreachable"),
            {"A": ("t1",), "idle": ()},
        )
        selected, covered = greedy_set_cover(problem)
        assert selected == ("A",)
        assert covered == frozenset({"t1"})
        assert uncovered_targets(problem, selected) == ("unreachable",)
