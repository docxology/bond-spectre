"""Manuscript variable hydration for the Spectre / NINE EYES package.

Every ``{{TOKEN}}`` in ``manuscript/NN_*.md`` resolves through
:func:`generate_variables`, which reads ``manuscript/config.yaml`` plus the
*measured* output of the deterministic NINE EYES mission provider. Metrics are
never hand-authored in prose: they flow through this module (and the mission's
``execute`` step) so the manuscript cannot drift from the code it describes.

The consuming orchestrator is ``scripts/z_generate_manuscript_variables.py``
(thin wrapper); the live cross-reference gate lives in
``tests/test_manuscript_variables.py``.
"""

from __future__ import annotations

import platform
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from spectre import __version__
from spectre.mission import (
    NINE_EYES_EDGES,
    NINE_EYES_NODES,
    PROVIDER,
    SPECTRE_OPERATIVES,
)
from spectre.network_geometry import build_adjacency, articulation_points

__all__ = ["generate_variables", "load_manuscript_config", "resolve_manuscript_tree"]

# .../spectre/src/spectre/manuscript_variables.py -> parents[2] == project root
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"

_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def load_manuscript_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate ``manuscript/config.yaml`` (or an explicit path)."""
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"manuscript config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"manuscript config must be a top-level mapping, got {type(data).__name__}")
    return data


def _network_metrics() -> dict[str, Any]:
    """Run the deterministic mission and copy its measured results."""
    outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
    return dict(outcome.results)


def generate_variables(
    *,
    config_path: str | Path | None = None,
    require_outputs: bool = True,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` → value mapping for the manuscript.

    Args:
        config_path: Override for ``manuscript/config.yaml``.
        require_outputs: When True (default), verify the mission produced a
            success outcome — the strict-mode gate.
    """
    config = load_manuscript_config(config_path)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        raise ValueError("manuscript config 'paper' section must be a mapping")

    metrics = _network_metrics()
    if require_outputs and not metrics.get("plan_steps"):
        raise ValueError("mission produced no measured metrics — cannot hydrate manuscript")

    nodes, adjacency = build_adjacency(NINE_EYES_NODES, NINE_EYES_EDGES)
    articulation_labels = [nodes[i] for i in sorted(articulation_points(adjacency))]

    keywords = ", ".join(str(k) for k in config.get("keywords", []))
    critical = ", ".join(str(c) for c in metrics["critical_nodes"])

    return {
        "SPECTRE_IDENTITY": "SPECTRE",
        "SPECTRE_CODENAME": "NINE EYES",
        "SPECTRE_VERSION": str(paper.get("version", __version__)),
        "SPECTRE_TITLE": str(paper.get("title", "")),
        "SPECTRE_SUBTITLE": str(paper.get("subtitle", "")),
        "SPECTRE_KEYWORDS": keywords,
        "SPECTRE_NUM_NODES": str(len(NINE_EYES_NODES)),
        "SPECTRE_NUM_EDGES": str(len(NINE_EYES_EDGES)),
        "SPECTRE_NUM_OPERATIVES": str(len(SPECTRE_OPERATIVES)),
        "SPECTRE_NUM_CELLS": str(metrics["cell_count"]),
        "SPECTRE_CENTRALIZATION_INDEX": f"{metrics['centralization_index']:.4f}",
        "SPECTRE_FLOW_CONCENTRATION_HHI": f"{metrics['flow_concentration_hhi']:.4f}",
        "SPECTRE_CASCADE_COVERAGE": f"{metrics['cascade_coverage']:.4f}",
        "SPECTRE_HIERARCHY_HEIGHT": str(metrics["hierarchy_height"]),
        "SPECTRE_CHAIN_COMPLETE": str(metrics["chain_complete"]).lower(),
        "SPECTRE_COMPARTMENTALIZATION": f"{metrics['compartmentalization']:.4f}",
        "SPECTRE_NETWORK_EFFICIENCY": f"{metrics['network_efficiency']:.4f}",
        "SPECTRE_NUM_ARTICULATION_POINTS": str(len(articulation_labels)),
        "SPECTRE_ARTICULATION_NODES": ", ".join(articulation_labels),
        "SPECTRE_CRITICAL_NODES": critical,
        "SPECTRE_NUM_OBJECTIVES": str(len(PROVIDER.brief().objectives)),
        "PYTHON_VERSION": platform.python_version(),
        "PLATFORM": f"{platform.system()} {platform.machine()}",
        "GENERATION_TIMESTAMP": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def resolve_manuscript_tree(
    variables: dict[str, str],
    *,
    manuscript_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    strict: bool = True,
) -> tuple[Path, list[str]]:
    """Copy each manuscript section to ``output/manuscript/``, substituting tokens.

    Only ``NN_*.md`` section files are copied (not sidecars such as
    ``SYNTAX.md``). In strict mode any leftover ``{{TOKEN}}`` fails the
    resolution so the manuscript can never render with raw braces.

    Returns the output directory and the sorted list of resolved file names.
    """
    manuscript_dir = Path(manuscript_dir) if manuscript_dir is not None else PACKAGE_ROOT / "manuscript"
    output_dir = Path(output_dir) if output_dir is not None else PACKAGE_ROOT / "output" / "manuscript"
    resolved: list[str] = []
    for source in sorted(manuscript_dir.glob("[0-9][0-9]_*.md")):
        text = source.read_text(encoding="utf-8")
        for token, value in variables.items():
            text = text.replace("{{" + token + "}}", value)
        unresolved = sorted(set(_TOKEN_RE.findall(text)))
        if unresolved and strict:
            raise ValueError(f"unresolved manuscript tokens in {source.name}: {unresolved}")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / source.name).write_text(text, encoding="utf-8")
        resolved.append(source.name)
    return output_dir, resolved
