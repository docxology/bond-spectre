"""Tests for spectre.figures — figure generators."""

from __future__ import annotations

from pathlib import Path

import pytest

from spectre.figures import plot_network_flow_centralization
from spectre.mission import NINE_EYES_NETWORK
from spectre.surveillance_net import (
    SurveillanceNetwork,
    build_network,
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
