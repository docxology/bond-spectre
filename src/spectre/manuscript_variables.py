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
from typing import Any, Protocol

import yaml

from spectre import __version__
from spectre.mission import (
    NINE_EYES_EDGES,
    NINE_EYES_NODES,
    PROVIDER,
    SPECTRE_OPERATIVES,
    gadget_names,
)
from spectre.network_geometry import build_adjacency, articulation_points

__all__ = [
    "MissionRunner",
    "domain_module_names",
    "generate_variables",
    "load_manuscript_config",
    "resolve_manuscript_tree",
]

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


class MissionRunner(Protocol):
    """The slice of the FROZEN ``MissionProvider`` this module actually drives.

    Declaring it as a Protocol keeps the strict measured-metrics gate below
    *testable*: a test can pass a real alternative runner that returns an empty
    result set, instead of the gate being green by construction because the
    canonical provider can never fail it.
    """

    def brief(self) -> Any:
        """Return the mission brief."""

    def plan(self, brief: Any) -> Any:
        """Return the mission plan for a brief."""

    def execute(self, plan: Any) -> Any:
        """Return the mission outcome for a plan."""


#: Modules of the pure, bond-api-free domain core (everything in the package
#: except the protocol adapter, the hydration layer and the figures subpackage).
_NON_DOMAIN_MODULES = frozenset({"__init__", "mission", "manuscript_variables"})


def domain_module_names() -> tuple[str, ...]:
    """Names of the pure domain modules, measured from the installed package.

    Derived by listing the package directory rather than from a hand-kept
    constant, so the manuscript's module count cannot drift from the code.
    """
    package_dir = Path(__file__).resolve().parent
    return tuple(sorted(path.stem for path in package_dir.glob("*.py") if path.stem not in _NON_DOMAIN_MODULES))


def _network_metrics(provider: MissionRunner) -> dict[str, Any]:
    """Run the deterministic mission and copy its measured results."""
    outcome = provider.execute(provider.plan(provider.brief()))
    return dict(outcome.results)


def generate_variables(
    *,
    config_path: str | Path | None = None,
    require_outputs: bool = True,
    provider: MissionRunner | None = None,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` → value mapping for the manuscript.

    Args:
        config_path: Override for ``manuscript/config.yaml``.
        require_outputs: When True (default), verify the mission produced
            measured metrics — the strict-mode gate.
        provider: Mission runner to measure; defaults to the canonical NINE
            EYES ``PROVIDER``. Injectable so the strict gate can be exercised.

    Raises:
        ValueError: If the config ``paper`` section is not a mapping, or (in
            strict mode) the mission produced no measured metrics.
    """
    config = load_manuscript_config(config_path)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        raise ValueError("manuscript config 'paper' section must be a mapping")

    runner: MissionRunner = PROVIDER if provider is None else provider
    metrics = _network_metrics(runner)
    if require_outputs and not metrics.get("plan_steps"):
        raise ValueError("mission produced no measured metrics — cannot hydrate manuscript")

    nodes, adjacency = build_adjacency(NINE_EYES_NODES, NINE_EYES_EDGES)
    articulation_labels = [nodes[i] for i in sorted(articulation_points(adjacency))]

    keywords = ", ".join(str(k) for k in config.get("keywords", []))
    critical = ", ".join(str(c) for c in metrics["critical_nodes"])
    monitor_allocation = ", ".join(str(a) for a in metrics["monitor_allocation"])
    set_cover_selection = ", ".join(str(a) for a in metrics["set_cover_selection"])

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
        "SPECTRE_NUM_OBJECTIVES": str(len(runner.brief().objectives)),
        "SPECTRE_NUM_DOMAIN_MODULES": str(len(domain_module_names())),
        "SPECTRE_DOMAIN_MODULES": ", ".join(domain_module_names()),
        "SPECTRE_NUM_GADGETS": str(len(gadget_names())),
        "SPECTRE_PLAN_STEPS": str(metrics["plan_steps"]),
        "SPECTRE_TRAFFIC_TOTAL": f"{metrics['traffic_total']:.1f}",
        "SPECTRE_TRAFFIC_TOP_LINK": str(metrics["traffic_top_link"]),
        "SPECTRE_MONITOR_ALLOCATION": monitor_allocation,
        "SPECTRE_MONITOR_BUDGET": str(len(metrics["monitor_allocation"])),
        "SPECTRE_MONITOR_COVERAGE": f"{metrics['monitor_coverage_budget3']:.4f}",
        "SPECTRE_COMPROMISE_FRACTION": f"{metrics['expected_compromise_fraction']:.4f}",
        "SPECTRE_LEADERSHIP_HIT_RATE": f"{metrics['leadership_hit_rate']:.2f}",
        "SPECTRE_MEAN_STEPS_TO_LEADERSHIP": f"{metrics['mean_steps_to_leadership']:.2f}",
        "SPECTRE_SET_COVER_SIZE": str(metrics["set_cover_size"]),
        "SPECTRE_SET_COVER_SELECTION": set_cover_selection,
        "SPECTRE_COVER_REDUNDANCY": f"{metrics['coverage_redundancy']:.4f}",
        "SPECTRE_UNCOVERED_AFTER_COVER": str(metrics["uncovered_targets_after_cover"]),
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
