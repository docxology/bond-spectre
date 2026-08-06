"""Tests for spectre.surveillance_net — Nine Eyes data-flow centralization."""

from __future__ import annotations

import numpy as np
import pytest

from spectre.surveillance_net import (
    CascadeResult,
    CentralityResult,
    SurveillanceNetwork,
    betweenness_centrality,
    build_network,
    cascade_coverage,
    data_share_centrality,
    expected_cascade_coverage,
    group_centralization,
    herfindahl_index,
    in_degree_centrality,
    network_from_adjacency,
    out_degree_centrality,
    sweep_coverage,
    uniform_share_index,
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
    """Value assertions, not key assertions.

    The predecessor of this class asserted only that the score keys equalled
    the node labels, which passes identically whether the function returns
    shares, indicators or zeros — and it did in fact pass while the function
    returned a 0/1 indicator. Every test below inspects values.
    """

    def test_shares_are_inflow_fractions(self) -> None:
        # In-degrees on the fixture: US 0, UK 1, CA 1, DE 2 over 4 edges.
        net = build_network(NODES, EDGES)
        scores = data_share_centrality(net).scores
        assert scores["US"] == pytest.approx(0.0)
        assert scores["UK"] == pytest.approx(0.25)
        assert scores["CA"] == pytest.approx(0.25)
        assert scores["DE"] == pytest.approx(0.5)

    def test_shares_sum_to_one(self) -> None:
        net = build_network(NODES, EDGES)
        assert sum(data_share_centrality(net).scores.values()) == pytest.approx(1.0)

    def test_top_is_the_largest_receiver(self) -> None:
        net = build_network(NODES, EDGES)
        assert data_share_centrality(net).top[0] == "DE"

    def test_shares_are_not_indicators(self) -> None:
        """Two receivers of unequal inflow must not score the same.

        This is the assertion the shipped bug would have failed: under
        column-self-normalization every agency with any inflow scored exactly
        1.0, so UK (one inbound edge) and DE (two) were indistinguishable.
        """
        net = build_network(NODES, EDGES)
        scores = data_share_centrality(net).scores
        assert scores["DE"] > scores["UK"]
        assert scores["DE"] == pytest.approx(2 * scores["UK"])

    def test_edgeless_network_has_no_shares(self) -> None:
        net = build_network(NODES, ())
        assert set(data_share_centrality(net).scores.values()) == {0.0}


class TestUniformShareIndex:
    def test_floor_is_one_over_receiving_agencies(self) -> None:
        # UK, CA and DE receive; US does not -> floor 1/3.
        net = build_network(NODES, EDGES)
        assert uniform_share_index(net) == pytest.approx(1.0 / 3.0)

    def test_measured_hhi_is_at_or_above_the_floor(self) -> None:
        net = build_network(NODES, EDGES)
        shares = data_share_centrality(net).scores
        measured = herfindahl_index([shares[label] for label in NODES])
        assert measured >= uniform_share_index(net)

    def test_even_inflow_hits_the_floor_exactly(self) -> None:
        net = build_network(NODES, (("US", "UK"), ("US", "CA"), ("US", "DE")))
        shares = data_share_centrality(net).scores
        measured = herfindahl_index([shares[label] for label in NODES])
        assert measured == pytest.approx(uniform_share_index(net))

    def test_no_receiver_raises(self) -> None:
        with pytest.raises(ValueError, match="even-spread floor"):
            uniform_share_index(build_network(NODES, ()))


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


class TestCascadeSeedGovernsTheDraws:
    """The seed argument must change the realization, not merely be recorded."""

    def test_two_seeds_disagree_somewhere(self) -> None:
        net = build_network(NODES, EDGES)
        reached = {cascade_coverage(net, ("US",), 0.5, seed=s).activated for s in range(12)}
        assert len(reached) > 1, "seed does not influence the cascade"

    def test_same_seed_reproduces(self) -> None:
        net = build_network(NODES, EDGES)
        a = cascade_coverage(net, ("US",), 0.5, seed=7)
        b = cascade_coverage(net, ("US",), 0.5, seed=7)
        assert a.activated == b.activated

    def test_default_seed_is_zero(self) -> None:
        net = build_network(NODES, EDGES)
        assert cascade_coverage(net, ("US",), 0.5).activated == (cascade_coverage(net, ("US",), 0.5, seed=0).activated)


class TestExpectedCascadeCoverage:
    def test_mean_is_between_the_extreme_realizations(self) -> None:
        net = build_network(NODES, EDGES)
        draws = [cascade_coverage(net, ("US",), 0.5, seed=3 + i).coverage_fraction for i in range(40)]
        mean = expected_cascade_coverage(net, ("US",), 0.5, trials=40, seed=3)
        assert min(draws) <= mean <= max(draws)
        assert mean == pytest.approx(sum(draws) / len(draws))

    def test_mean_differs_from_a_single_draw(self) -> None:
        """The headline number must not be one Bernoulli sample dressed up."""
        net = build_network(NODES, EDGES)
        single = cascade_coverage(net, ("US",), 0.5, seed=11).coverage_fraction
        mean = expected_cascade_coverage(net, ("US",), 0.5, trials=50, seed=11)
        assert mean != pytest.approx(single)

    def test_certain_activation_reaches_everything(self) -> None:
        net = build_network(NODES, EDGES)
        assert expected_cascade_coverage(net, ("US",), 1.0, trials=5, seed=0) == pytest.approx(1.0)

    def test_seed_shifts_the_mean(self) -> None:
        net = build_network(NODES, EDGES)
        means = {expected_cascade_coverage(net, ("US",), 0.5, trials=5, seed=s) for s in range(8)}
        assert len(means) > 1

    def test_deterministic(self) -> None:
        net = build_network(NODES, EDGES)
        a = expected_cascade_coverage(net, ("US",), 0.6, trials=25, seed=11)
        b = expected_cascade_coverage(net, ("US",), 0.6, trials=25, seed=11)
        assert a == b

    def test_nonpositive_trials_raises(self) -> None:
        net = build_network(NODES, EDGES)
        with pytest.raises(ValueError, match="trials must be positive"):
            expected_cascade_coverage(net, ("US",), 0.5, trials=0)

    def test_generator_sources_survive_the_trial_loop(self) -> None:
        """A generator must be materialized once, not exhausted after trial 1."""
        net = build_network(NODES, EDGES)
        mean = expected_cascade_coverage(net, (label for label in ("US",)), 1.0, trials=3, seed=0)
        assert mean == pytest.approx(1.0)


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


class TestNetworkFromAdjacency:
    """The matrix constructor validates what build_network enforces by construction."""

    def test_valid_matrix_round_trips(self) -> None:
        built = build_network(NODES, EDGES)
        rebuilt = network_from_adjacency(NODES, built.adjacency)
        assert rebuilt.nodes == built.nodes
        assert np.array_equal(rebuilt.adjacency, built.adjacency)

    def test_matrix_is_copied(self) -> None:
        built = build_network(NODES, EDGES)
        rebuilt = network_from_adjacency(NODES, built.adjacency)
        built.adjacency[0, 1] = 0
        assert int(rebuilt.adjacency[0, 1]) == 1

    def test_wrong_shape_raises(self) -> None:
        with pytest.raises(ValueError, match="adjacency must be"):
            network_from_adjacency(NODES, np.zeros((3, 3), dtype=np.int64))

    def test_duplicate_labels_raise(self) -> None:
        with pytest.raises(ValueError, match="unique"):
            network_from_adjacency(("A", "A"), np.zeros((2, 2), dtype=np.int64))

    def test_self_loop_on_diagonal_raises(self) -> None:
        matrix = np.zeros((4, 4), dtype=np.int64)
        matrix[2, 2] = 1
        with pytest.raises(ValueError, match="self-loops"):
            network_from_adjacency(NODES, matrix)


class TestCascadeSourceHandling:
    def test_generator_sources_are_materialized(self) -> None:
        """A generator must not be consumed by the emptiness check."""
        net = build_network(NODES, EDGES)
        result = cascade_coverage(net, (label for label in ("US",)), 1.0)
        assert result.seeded == ("US",)
        assert result.coverage_fraction == pytest.approx(1.0)

    def test_empty_generator_raises(self) -> None:
        net = build_network(NODES, EDGES)
        with pytest.raises(ValueError, match="at least one source"):
            cascade_coverage(net, (label for label in ()), 1.0)


class TestBetweennessDegenerateSizes:
    def test_single_node_network(self) -> None:
        net = build_network(("US",), ())
        assert betweenness_centrality(net).scores == {"US": 0.0}

    def test_two_node_network_is_not_normalized(self) -> None:
        """With n == 2 the (n-1)(n-2) normalizer is 0, so raw scores stand."""
        net = build_network(("US", "UK"), (("US", "UK"),))
        scores = betweenness_centrality(net).scores
        assert scores == {"US": 0.0, "UK": 0.0}


class TestFiniteValidation:
    """NaN/inf must not propagate silently through the scalar metrics."""

    def test_group_centralization_rejects_nan(self) -> None:
        with pytest.raises(ValueError, match="finite"):
            group_centralization({"a": float("nan"), "b": 1.0})

    def test_group_centralization_rejects_inf(self) -> None:
        with pytest.raises(ValueError, match="finite"):
            group_centralization({"a": float("inf"), "b": 1.0})

    def test_group_centralization_rejects_nan_maximum(self) -> None:
        with pytest.raises(ValueError, match="finite"):
            group_centralization({"a": 1.0, "b": 0.0}, maximum_score=float("nan"))

    def test_herfindahl_rejects_nan(self) -> None:
        with pytest.raises(ValueError, match="finite"):
            herfindahl_index([1.0, float("nan")])

    def test_herfindahl_rejects_inf(self) -> None:
        with pytest.raises(ValueError, match="finite"):
            herfindahl_index([1.0, float("inf")])

    def test_valid_finite_inputs_still_work(self) -> None:
        assert group_centralization({"a": 1.0, "b": 0.0}) == pytest.approx(1.0)
        assert herfindahl_index([1.0, 1.0]) == pytest.approx(0.5)
