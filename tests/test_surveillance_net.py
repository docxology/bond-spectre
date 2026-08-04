"""Tests for spectre.surveillance_net — Nine Eyes data-flow centralization."""

from __future__ import annotations

import pytest

from spectre.surveillance_net import (
    CascadeResult,
    CentralityResult,
    SurveillanceNetwork,
    betweenness_centrality,
    build_network,
    cascade_coverage,
    data_share_centrality,
    group_centralization,
    herfindahl_index,
    in_degree_centrality,
    out_degree_centrality,
    sweep_coverage,
)

NODES = ("US", "UK", "CA", "DE")
# US feeds everyone; UK -> DE.
EDGES = (
    ("US", "UK"),
    ("US", "CA"),
    ("US", "DE"),
    ("UK", "DE"),
)


class TestBuildNetwork:
    def test_valid(self) -> None:
        net = build_network(NODES, EDGES)
        assert isinstance(net, SurveillanceNetwork)
        assert net.n == 4
        assert int(net.adjacency.sum()) == 4

    def test_duplicate_nodes_raises(self) -> None:
        with pytest.raises(ValueError):
            build_network(("A", "A"), ())

    def test_unknown_source_raises(self) -> None:
        with pytest.raises(ValueError):
            build_network(NODES, (("ZZ", "UK"),))

    def test_unknown_target_raises(self) -> None:
        with pytest.raises(ValueError):
            build_network(NODES, (("US", "ZZ"),))

    def test_self_loop_raises(self) -> None:
        with pytest.raises(ValueError):
            build_network(("A", "B"), (("A", "A"),))


class TestDegreeCentrality:
    def test_out_degree(self) -> None:
        net = build_network(NODES, EDGES)
        result = out_degree_centrality(net)
        assert result.scores["US"] == 3.0
        assert result.scores["UK"] == 1.0
        assert result.top[0] == "US"

    def test_in_degree(self) -> None:
        net = build_network(NODES, EDGES)
        result = in_degree_centrality(net)
        assert result.scores["DE"] == 2.0
        assert result.top[0] == "DE"


class TestGroupCentralization:
    def test_star_is_highly_centralized(self) -> None:
        score = group_centralization({"hub": 3.0, "a": 0.0, "b": 0.0, "c": 0.0})
        assert score == pytest.approx(1.0)

    def test_even_is_zero(self) -> None:
        score = group_centralization({"a": 1.0, "b": 1.0, "c": 1.0})
        assert score == pytest.approx(0.0)

    def test_explicit_maximum(self) -> None:
        score = group_centralization({"a": 1.0, "b": 0.0}, maximum_score=1.0)
        assert score == pytest.approx(1.0)

    def test_single_node_zero(self) -> None:
        assert group_centralization({"a": 1.0}) == pytest.approx(0.0)

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            group_centralization({})

    def test_nonpositive_maximum_raises(self) -> None:
        with pytest.raises(ValueError):
            group_centralization({"a": 1.0}, maximum_score=0.0)


class TestBetweenness:
    def test_path_middle_is_between(self) -> None:
        # A - B - C : B sits on the only A-C path.
        net = build_network(("A", "B", "C"), (("A", "B"), ("B", "C")))
        result = betweenness_centrality(net)
        assert result.scores["B"] > result.scores["A"]
        assert result.scores["B"] > result.scores["C"]
        assert result.top[0] == "B"

    def test_ordered_top(self) -> None:
        net = build_network(NODES, EDGES)
        result = betweenness_centrality(net)
        assert isinstance(result, CentralityResult)
        assert isinstance(result.top, tuple)
        assert any(label in result.top for label in ("US", "UK", "CA", "DE"))


class TestHerfindahl:
    def test_uniform_share(self) -> None:
        value = herfindahl_index([1.0, 1.0, 1.0, 1.0])
        assert value == pytest.approx(0.25)

    def test_monopoly(self) -> None:
        assert herfindahl_index([1.0, 0.0, 0.0]) == pytest.approx(1.0)

    def test_normalizes_totals(self) -> None:
        assert herfindahl_index([2.0, 2.0, 2.0]) == pytest.approx(1.0 / 3.0)

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            herfindahl_index([])

    def test_zero_total_raises(self) -> None:
        with pytest.raises(ValueError):
            herfindahl_index([0.0, 0.0])


class TestDataShare:
    def test_shares_present(self) -> None:
        net = build_network(NODES, EDGES)
        result = data_share_centrality(net)
        assert set(result.scores.keys()) == set(NODES)


class TestCascadeCoverage:
    def test_probability_out_of_range_low(self) -> None:
        net = build_network(NODES, EDGES)
        with pytest.raises(ValueError):
            cascade_coverage(net, ("US",), 0.0)

    def test_probability_too_high(self) -> None:
        net = build_network(NODES, EDGES)
        with pytest.raises(ValueError):
            cascade_coverage(net, ("US",), 1.5)

    def test_no_sources_raises(self) -> None:
        net = build_network(NODES, EDGES)
        with pytest.raises(ValueError):
            cascade_coverage(net, (), 0.5)

    def test_unknown_source_raises(self) -> None:
        net = build_network(NODES, EDGES)
        with pytest.raises(ValueError):
            cascade_coverage(net, ("ZZ",), 0.5)

    def test_deterministic(self) -> None:
        net = build_network(NODES, EDGES)
        a = cascade_coverage(net, ("US",), 0.99)
        b = cascade_coverage(net, ("US",), 0.99)
        assert isinstance(a, CascadeResult)
        assert a.activated == b.activated
        assert 0.0 < a.coverage_fraction <= 1.0
        assert a.seeded == ("US",)

    def test_low_probability_reaches_less(self) -> None:
        net = build_network(NODES, EDGES)
        high = cascade_coverage(net, ("US",), 0.99)
        low = cascade_coverage(net, ("US",), 0.01)
        assert low.coverage_fraction <= high.coverage_fraction


class TestSweepCoverage:
    def test_normal(self) -> None:
        assert sweep_coverage(3, 10) == pytest.approx(0.3)

    def test_zero_total(self) -> None:
        assert sweep_coverage(0, 0) == 0.0

    def test_negative_captured_raises(self) -> None:
        with pytest.raises(ValueError):
            sweep_coverage(-1, 5)

    def test_captured_exceeds_total_raises(self) -> None:
        with pytest.raises(ValueError):
            sweep_coverage(6, 5)


class TestNumpyTypes:
    def test_scores_are_floats(self) -> None:
        net = build_network(NODES, EDGES)
        result = out_degree_centrality(net)
        for value in result.scores.values():
            assert isinstance(value, float)
