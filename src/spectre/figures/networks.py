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
    out_degree_centrality,
)

__all__ = ["flow_figure_title", "plot_network_flow_centralization"]


def _project_root() -> Path:
    # .../spectre/src/spectre/figures/networks.py -> parents[3] == project root
    return Path(__file__).resolve().parents[3]


def flow_figure_title(network: SurveillanceNetwork) -> str:
    """Title naming *both* hub readings the figure encodes.

    Node area is betweenness, so the figure's largest node is the agency most
    often *in the middle* of a shortest path. That is not the same agency as
    the network's flow source: a pure source has no inbound edge, so no
    shortest path passes through it and its betweenness is exactly 0 — it is
    drawn at minimum size while dominating the out-degree. Naming only one of
    the two makes the picture contradict the text, so the title names both and
    says which channel each belongs to.

    Raises:
        ValueError: If the network has no agencies.
    """
    if network.n < 1:
        raise ValueError("cannot title an empty network")
    betweenness = betweenness_centrality(network).scores
    out_degree = out_degree_centrality(network).scores
    pivot = max(betweenness, key=lambda label: (betweenness[label], label))
    source = max(out_degree, key=lambda label: (out_degree[label], label))
    return (
        "NINE EYES agency network — node area is betweenness: "
        f"most pivotal {pivot} ({betweenness[pivot]:.2f}); "
        f"largest sender {source} (out-degree {out_degree[source]:.0f}, "
        f"betweenness {betweenness[source]:.2f})"
    )


def plot_network_flow_centralization(
    network: SurveillanceNetwork,
    *,
    output_path: str | Path | None = None,
    dpi: int = 300,
    seed: int = 7,
) -> Path:
    """Render the directed agency network: node size ~ betweenness, arrows ~ flows.

    Draws the directed surveillance network on a seeded circular layout, sizes
    each node by its betweenness centrality, and draws the directed
    data-sharing edges as arrows. Node area therefore encodes *path
    pivotality*, not sending volume: the largest sender may have betweenness 0
    and hence the smallest marker, so it is ringed and marked ``▸`` and named
    alongside the betweenness leader in the title (see
    :func:`flow_figure_title`).

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

    out_degree = out_degree_centrality(network).scores
    sender = max(out_degree, key=lambda label: (out_degree[label], label))
    for label in network.nodes:
        size = 200 + 1600 * betweenness[label]
        is_sender = label == sender
        ax.scatter(
            positions[label][0],
            positions[label][1],
            s=size,
            color="#0f766e",
            # The largest sender can have zero betweenness and therefore the
            # smallest marker; ring it so the figure does not read as if it
            # were peripheral.
            edgecolors="#b45309" if is_sender else "white",
            linewidths=2.2 if is_sender else 1.0,
            zorder=3,
        )
        ax.text(
            positions[label][0],
            positions[label][1] + 0.08,
            f"{label} ▸" if is_sender else label,
            ha="center",
            va="bottom",
            fontsize=9,
            zorder=4,
        )

    ax.set_title(flow_figure_title(network), fontsize=9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path
