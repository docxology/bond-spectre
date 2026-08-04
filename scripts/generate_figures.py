"""NINE EYES — figure generation CLI.

Renders the surveillance-network flow-centralization figure to
``output/figures/`` for the canonical Nine Eyes network.
"""

from __future__ import annotations

import _boot  # noqa: E402,F401 (adds src/ to sys.path)

from spectre.figures import plot_network_flow_centralization
from spectre.mission import NINE_EYES_EDGES, NINE_EYES_NODES
from spectre.surveillance_net import build_network


def main() -> None:
    network = build_network(NINE_EYES_NODES, NINE_EYES_EDGES)
    path = plot_network_flow_centralization(network)
    print(f"Wrote figure -> {path}")


if __name__ == "__main__":
    main()
