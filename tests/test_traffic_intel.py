"""Tests for spectre.traffic_intel — interception coverage and monitor allocation."""

from __future__ import annotations

import pytest

from spectre.traffic_intel import (
    TrafficNetwork,
    build_traffic_network,
    canonical_traffic_network,
    heavy_hitters,
    interception_coverage,
    monitor_allocation,
    total_traffic,
)

NODES = ("US", "UK", "DE")
LINKS = (
    ("US", "UK", 100.0),
    ("US", "DE", 50.0),
    ("UK", "DE", 25.0),
)


class TestBuildTrafficNetwork:
    def test_valid(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        assert isinstance(net, TrafficNetwork)
        assert net.n == 3
        assert total_traffic(net) == pytest.approx(175.0)

    def test_duplicate_nodes_raises(self) -> None:
        with pytest.raises(ValueError):
            build_traffic_network(("A", "A"), ())

    def test_unknown_source_raises(self) -> None:
        with pytest.raises(ValueError):
            build_traffic_network(NODES, (("ZZ", "UK", 1.0),))

    def test_unknown_target_raises(self) -> None:
        with pytest.raises(ValueError):
            build_traffic_network(NODES, (("US", "ZZ", 1.0),))

    def test_self_loop_raises(self) -> None:
        with pytest.raises(ValueError):
            build_traffic_network(("A", "B"), (("A", "A", 1.0),))

    def test_negative_volume_raises(self) -> None:
        with pytest.raises(ValueError):
            build_traffic_network(("A", "B"), (("A", "B", -1.0),))

    def test_accumulates_duplicate_links(self) -> None:
        net = build_traffic_network(("A", "B"), (("A", "B", 10.0), ("A", "B", 5.0)))
        assert total_traffic(net) == pytest.approx(15.0)


class TestHeavyHitters:
    def test_top_links(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        top = heavy_hitters(net, 2)
        assert top == (("US", "UK", 100.0), ("US", "DE", 50.0))

    def test_k_exceeds_links(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        top = heavy_hitters(net, 10)
        assert len(top) == 3

    def test_nonpositive_k_raises(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        with pytest.raises(ValueError):
            heavy_hitters(net, 0)


class TestInterceptionCoverage:
    def test_single_hub(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        coverage = interception_coverage(net, ("US",))
        assert coverage == pytest.approx(150.0 / 175.0)

    def test_unknown_agency_raises(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        with pytest.raises(ValueError):
            interception_coverage(net, ("ZZ",))

    def test_empty_network_zero(self) -> None:
        net = build_traffic_network((), ())
        assert interception_coverage(net, ()) == 0.0


class TestMonitorAllocation:
    def test_budget_zero(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        selected, coverage = monitor_allocation(net, 0)
        assert selected == ()
        assert coverage == 0.0

    def test_negative_budget_raises(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        with pytest.raises(ValueError):
            monitor_allocation(net, -1)

    def test_greedy_picks_hub_first(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        selected, coverage = monitor_allocation(net, 1)
        assert selected == ("US",)
        assert coverage == pytest.approx(150.0 / 175.0)

    def test_budget_exceeds_nodes(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        selected, coverage = monitor_allocation(net, 10)
        assert all(node in NODES for node in selected)
        assert coverage == pytest.approx(1.0)

    def test_monotone_coverage(self) -> None:
        net = build_traffic_network(NODES, LINKS)
        _, one = monitor_allocation(net, 1)
        _, two = monitor_allocation(net, 2)
        _, three = monitor_allocation(net, 3)
        assert one <= two <= three

    def test_canonical_diminishing_returns(self) -> None:
        net = canonical_traffic_network()
        _, two = monitor_allocation(net, 2)
        _, three = monitor_allocation(net, 3)
        assert two < three < 1.0
        # Marginal gain shrinks: hub alone captures most of the traffic.
        _, one = monitor_allocation(net, 1)
        assert one > 0.7


class TestInterceptionOnInboundLinks:
    def test_monitoring_a_pure_sink_captures_its_inbound_traffic(self) -> None:
        """A leaf agency only has in-links; monitoring it must still intercept."""
        network = build_traffic_network(
            ("A", "B", "C"),
            (("A", "B", 30.0), ("A", "C", 70.0)),
        )
        assert interception_coverage(network, ("B",)) == pytest.approx(0.3)
        assert interception_coverage(network, ("C",)) == pytest.approx(0.7)
        assert interception_coverage(network, ("B", "C")) == pytest.approx(1.0)

    def test_ties_break_by_agency_label_not_node_order(self) -> None:
        """Two agencies with identical marginal gain: the lower label wins."""
        network = build_traffic_network(
            ("zulu", "alpha", "x", "y"),
            (("zulu", "x", 50.0), ("alpha", "y", 50.0)),
        )
        selected, coverage = monitor_allocation(network, budget=1)
        assert selected == ("alpha",)
        assert coverage == pytest.approx(0.5)
