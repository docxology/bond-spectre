"""Matplotlib figures for the Spectre / NINE EYES package.

Publication-quality figures per analysed concept. Every generator is
deterministic (fixed seed, no random component) and writes a single PNG under
``output/figures/``. Depends only on ``numpy`` + ``matplotlib`` (plus the
domain core).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from spectre.surveillance_net import (
    SurveillanceNetwork,
    betweenness_centrality,
)

__all__ = ["plot_network_flow_centralization"]


def _project_root() -> Path:
    # .../spectre/src/spectre/figures/networks.py -> parents[3] == project root
    return Path(__file__).resolve().parents[3]


def plot_network_flow_centralization(
    network: SurveillanceNetwork,
    *,
    output_path: str | Path | None = None,
    dpi: int = 300,
    seed: int = 7,
) -> Path:
    """Render the directed agency network: node size ~ betweenness, arrows ~ flows.

    Draws the directed surveillance network on a seeded circular layout, sizes
    each node by its betweenness centrality, draws the directed data-sharing
    edges as arrows, and scales a node's radius by its measured betweenness so
    the pivotal agencies (the data hubs) are visually dominant.

    Args:
        network: The directed :class:`SurveillanceNetwork` to plot.
        output_path: Destination PNG; defaults to
            ``output/figures/network_flow_centralization.png``.
        dpi: Raster resolution.
        seed: Fixed numpy RNG seed for the deterministic layout jitter.

    Returns:
        The resolved output file path.
    """
    import matplotlib.pyplot as plt

    n = network.n
    if n < 1:
        raise ValueError("cannot plot an empty network")
    betweenness = betweenness_centrality(network).scores

    rng = np.random.default_rng(seed)
    angles = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    radius = 1.0
    positions: dict[str, tuple[float, float]] = {
        label: (
            float(radius * np.cos(angles[i]) + rng.normal(0, 0.02)),
            float(radius * np.sin(angles[i]) + rng.normal(0, 0.02)),
        )
        for i, label in enumerate(network.nodes)
    }

    path = (
        Path(output_path)
        if output_path is not None
        else (_project_root() / "output" / "figures" / "network_flow_centralization.png")
    )
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    label_index = {label: i for i, label in enumerate(network.nodes)}
    for source in network.nodes:
        for raw in np.flatnonzero(network.adjacency[label_index[source]]):
            target = network.nodes[int(raw)]
            ax.annotate(
                "",
                xy=positions[target],
                xytext=positions[source],
                arrowprops=dict(
                    arrowstyle="-|>",
                    color="#334155",
                    lw=0.8,
                    shrinkA=16,
                    shrinkB=16,
                ),
            )

    hub = max(betweenness, key=lambda label: betweenness[label]) if betweenness else ""
    max_betweenness = max(betweenness.values()) if betweenness else 0.0
    for label in network.nodes:
        size = 200 + 1600 * betweenness[label]
        ax.scatter(
            positions[label][0],
            positions[label][1],
            s=size,
            color="#0f766e",
            edgecolors="white",
            zorder=3,
        )
        ax.text(
            positions[label][0],
            positions[label][1] + 0.08,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
            zorder=4,
        )

    ax.set_title(
        f"NINE EYES agency network — hub {hub} (betweenness {max_betweenness:.2f})",
        fontsize=11,
    )
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path
