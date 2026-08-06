"""NINE EYES — figure generation CLI.

Renders the surveillance-network flow-centralization figure and the
brotherhood compromise-cascade figure to ``output/figures/`` for the canonical
Nine Eyes network and SPECTRE brotherhood, then mirrors both into
``output/manuscript/figures/`` so the embed paths in the manuscript (which
resolve relative to the resolved tree in ``output/manuscript/``) do not dangle.
"""

from __future__ import annotations

from pathlib import Path

import _boot  # noqa: E402,F401 (adds src/ to sys.path)

from spectre.figures import plot_brotherhood_cascade, plot_network_flow_centralization
from spectre.mission import (
    NINE_EYES_EDGES,
    NINE_EYES_NODES,
    SPECTRE_CELL_OF,
    SPECTRE_LEADERSHIP,
    SPECTRE_OPERATIVES,
    SPECTRE_PARENT_OF,
)
from spectre.org_intel import build_org
from spectre.surveillance_net import build_network


def _mirror(root: Path, path: Path, name: str) -> Path:
    manuscript_fig = root / "output" / "manuscript" / "figures" / name
    manuscript_fig.parent.mkdir(parents=True, exist_ok=True)
    manuscript_fig.write_bytes(path.read_bytes())
    return manuscript_fig


def main() -> None:
    network = build_network(NINE_EYES_NODES, NINE_EYES_EDGES)
    org = build_org(
        SPECTRE_OPERATIVES,
        SPECTRE_CELL_OF,
        SPECTRE_PARENT_OF,
        SPECTRE_LEADERSHIP,
    )
    root = Path(__file__).resolve().parents[1]

    flow_path = plot_network_flow_centralization(network)
    cascade_path = plot_brotherhood_cascade(org, "Mr White")
    print(f"Wrote figure -> {flow_path}")
    print(f"Wrote figure -> {cascade_path}")

    for path in (flow_path, cascade_path):
        mirrored = _mirror(root, path, path.name)
        print(f"Mirrored figure -> {mirrored}")


if __name__ == "__main__":
    main()
