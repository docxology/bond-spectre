"""Tests for spectre.figures — figure generators."""

from __future__ import annotations

from pathlib import Path

import pytest

from spectre.figures import flow_figure_title, plot_network_flow_centralization
from spectre.mission import NINE_EYES_NETWORK
from spectre.surveillance_net import (
    SurveillanceNetwork,
    betweenness_centrality,
    build_network,
    out_degree_centrality,
)


def _nine_eyes() -> SurveillanceNetwork:
    return build_network(NINE_EYES_NETWORK["nodes"], NINE_EYES_NETWORK["edges"])


class TestNetworkFlowCentralization:
    def test_writes_png(self, tmp_path: Path) -> None:
        out = tmp_path / "fig.png"
        path = plot_network_flow_centralization(_nine_eyes(), output_path=out)
        assert path == out
        assert out.exists()
        assert out.stat().st_size > 0

    def test_default_path(self) -> None:
        path = plot_network_flow_centralization(_nine_eyes())
        assert path.name == "network_flow_centralization.png"
        assert path.exists()

    def test_empty_network_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            plot_network_flow_centralization(build_network((), ()), output_path=tmp_path / "x.png")


class TestFlowFigureTitle:
    """The title must not name one hub when the figure encodes two readings.

    The figure sizes nodes by betweenness. On the canonical network the largest
    sender (US, out-degree 8) has betweenness exactly 0 — it has no inbound
    edge, so no shortest path runs through it — and is drawn at minimum size.
    The shipped title read 'hub FR', contradicting the manuscript's US hub.
    """

    def test_the_source_and_the_pivot_differ_here(self) -> None:
        net = _nine_eyes()
        betweenness = betweenness_centrality(net).scores
        out_degree = out_degree_centrality(net).scores
        pivot = max(betweenness, key=lambda label: (betweenness[label], label))
        sender = max(out_degree, key=lambda label: (out_degree[label], label))
        assert sender == "US"
        assert pivot == "FR"
        assert betweenness["US"] == 0.0

    def test_title_names_both_readings(self) -> None:
        title = flow_figure_title(_nine_eyes())
        assert "FR" in title
        assert "US" in title
        assert "betweenness" in title
        assert "sender" in title

    def test_title_does_not_call_the_pivot_the_hub(self) -> None:
        assert "hub" not in flow_figure_title(_nine_eyes()).lower()

    def test_title_reports_the_source_betweenness_as_zero(self) -> None:
        assert "betweenness 0.00" in flow_figure_title(_nine_eyes())

    def test_empty_network_raises(self) -> None:
        with pytest.raises(ValueError, match="empty network"):
            flow_figure_title(build_network((), ()))
