"""Tests for spectre.network_geometry — connectivity and critical nodes."""

from __future__ import annotations

import numpy as np
import pytest

from spectre.network_geometry import (
    RobustnessPoint,
    all_pairs_shortest_paths,
    articulation_points,
    build_adjacency,
    connected_components,
    critical_node_order,
    is_connected,
    network_efficiency,
    node_removal_impact,
    robustness_curve,
)


class TestBuildAdjacency:
    def test_valid_returns_nodes_and_matrix(self) -> None:
        nodes, adj = build_adjacency(("A", "B"), (("A", "B"),))
        assert nodes == ("A", "B")
        assert adj.shape == (2, 2)
        assert int(adj.sum()) == 2  # symmetric

    def test_duplicate_raises(self) -> None:
        with pytest.raises(ValueError):
            build_adjacency(("A", "A"), ())

    def test_unknown_node_raises(self) -> None:
        with pytest.raises(ValueError):
            build_adjacency(("A", "B"), (("A", "C"),))

    def test_self_loop_raises(self) -> None:
        with pytest.raises(ValueError):
            build_adjacency(("A", "B"), (("A", "A"),))


class TestConnectivity:
    def test_disconnected_components(self) -> None:
        _, adj = build_adjacency(("A", "B", "C"), (("A", "B"),))
        comps = connected_components(adj)
        assert len(comps) == 2
        assert {0, 1} in comps
        assert {2} in comps

    def test_is_connected_true(self) -> None:
        _, adj = build_adjacency(("A", "B", "C"), (("A", "B"), ("B", "C")))
        assert is_connected(adj) is True

    def test_is_connected_false(self) -> None:
        _, adj = build_adjacency(("A", "B"), ())
        assert is_connected(adj) is False


class TestArticulationPoints:
    def test_path_middle_is_critical(self) -> None:
        # A - B - C : removing B disconnects.
        _, adj = build_adjacency(("A", "B", "C"), (("A", "B"), ("B", "C")))
        assert articulation_points(adj) == {1}

    def test_cycle_has_none(self) -> None:
        _, adj = build_adjacency(("A", "B", "C"), (("A", "B"), ("B", "C"), ("C", "A")))
        assert articulation_points(adj) == set()

    def test_star_root_children_rule(self) -> None:
        # Root 'US' with two children is an articulation point.
        nodes, adj = build_adjacency(("US", "UK", "DE"), (("US", "UK"), ("US", "DE")))
        assert articulation_points(adj) == {0}


class TestShortestPaths:
    def test_path_lengths(self) -> None:
        _, adj = build_adjacency(("A", "B", "C"), (("A", "B"), ("B", "C")))
        lengths = all_pairs_shortest_paths(adj)
        assert lengths[0][2] == 2
        assert lengths[1][0] == 1

    def test_disconnected_unreachable(self) -> None:
        _, adj = build_adjacency(("A", "B"), ())
        lengths = all_pairs_shortest_paths(adj)
        assert 1 not in lengths[0]


class TestNetworkEfficiency:
    def test_single_node_zero(self) -> None:
        adj = np.zeros((1, 1), dtype=int)
        assert network_efficiency(adj) == 0.0

    def test_connected_pair(self) -> None:
        _, adj = build_adjacency(("A", "B"), (("A", "B"),))
        assert network_efficiency(adj) == pytest.approx(1.0)

    def test_path_three(self) -> None:
        _, adj = build_adjacency(("A", "B", "C"), (("A", "B"), ("B", "C")))
        eff = network_efficiency(adj)
        # pairs: A-B d=1, A-C d=2, B-A d=1, B-C d=1, C-A d=2, C-B d=1
        assert eff == pytest.approx((1 + 0.5 + 1 + 1 + 0.5 + 1) / 6)


class TestNodeRemovalImpact:
    def test_bridge_removal_disconnects(self) -> None:
        _, adj = build_adjacency(("A", "B", "C"), (("A", "B"), ("B", "C")))
        impact = node_removal_impact(adj, 1)  # B is a bridge
        assert impact > 0.0

    def test_empty_adjacency_zero(self) -> None:
        adj = np.zeros((0, 0), dtype=int)
        assert node_removal_impact(adj, 0) == 0.0


class TestRobustnessCurve:
    def test_removal_sequence(self) -> None:
        nodes, adj = build_adjacency(("A", "B", "C", "D"), (("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("C", "A")))
        points = robustness_curve(adj, nodes, ["A", "B", "C"])
        assert len(points) == 3
        last = points[-1]
        assert isinstance(last, RobustnessPoint)
        assert last.removed_count == 3
        assert last.component_count >= 1

    def test_unknown_node_raises(self) -> None:
        nodes, adj = build_adjacency(("A", "B"), (("A", "B"),))
        with pytest.raises(ValueError):
            robustness_curve(adj, nodes, ["ZZ"])

    def test_already_removed_raises(self) -> None:
        nodes, adj = build_adjacency(("A", "B"), (("A", "B"),))
        with pytest.raises(ValueError):
            robustness_curve(adj, nodes, ["A", "A"])


class TestCriticalNodeOrder:
    def test_hub_first(self) -> None:
        nodes, adj = build_adjacency(
            ("US", "UK", "DE", "FR"),
            (("US", "UK"), ("US", "DE"), ("US", "FR")),
        )
        order = critical_node_order(adj)
        assert order[0] == 0  # US, the only hub

    def test_k_limit(self) -> None:
        _, adj = build_adjacency(("A", "B", "C", "D"), (("A", "B"), ("B", "C"), ("C", "D")))
        order = critical_node_order(adj, k=2)
        assert len(order) == 2

    def test_k_zero(self) -> None:
        _, adj = build_adjacency(("A", "B"), (("A", "B"),))
        assert critical_node_order(adj, k=0) == []


class TestBuildAdjacencyErrorBranches:
    def test_unknown_first_endpoint_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown node 'Z'"):
            build_adjacency(("A", "B"), (("Z", "A"),))

    def test_unknown_second_endpoint_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown node 'Z'"):
            build_adjacency(("A", "B"), (("A", "Z"),))


class TestEfficiencyOnDisconnectedGraph:
    def test_unreachable_pairs_contribute_nothing(self) -> None:
        """Two isolated dyads: only within-dyad pairs are reachable."""
        _, adj = build_adjacency(("A", "B", "C", "D"), (("A", "B"), ("C", "D")))
        # 4 reachable ordered pairs at distance 1, out of n*(n-1) = 12.
        assert network_efficiency(adj) == pytest.approx(4.0 / 12.0)

    def test_fully_isolated_graph_has_zero_efficiency(self) -> None:
        _, adj = build_adjacency(("A", "B", "C"), ())
        assert network_efficiency(adj) == 0.0

    def test_out_of_range_index_raises(self) -> None:
        _, adj = build_adjacency(("A", "B"), (("A", "B"),))
        with pytest.raises(ValueError, match="out of range"):
            node_removal_impact(adj, 5)

    def test_negative_index_raises(self) -> None:
        _, adj = build_adjacency(("A", "B"), (("A", "B"),))
        with pytest.raises(ValueError, match="out of range"):
            node_removal_impact(adj, -1)

    def test_valid_index_still_works(self) -> None:
        _, adj = build_adjacency(("A", "B", "C"), (("A", "B"), ("B", "C")))
        assert node_removal_impact(adj, 1) > 0.0
