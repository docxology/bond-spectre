"""NINE EYES — the Spectre (2015) mission provider for BOND-API.

This is the thin adapter between the pure domain core
(:mod:`spectre.surveillance_net`, :mod:`spectre.org_intel`,
:mod:`spectre.network_geometry`) and the FROZEN ``bond_api``
``MissionProvider`` protocol. The domain modules do **not** import
``bond_api`` and remain impportable standalone; this module is the only place
where the protocol contract is wired in.

The provider is deterministic: a fixed seed, no wall-clock in persisted
artifacts (``wall_time_s = 0.0``), and every result is measured from real
computation over the canonical Nine Eyes surveillance network and the SPECTRE
brotherhood structure defined below.
"""

from __future__ import annotations

import hashlib
import json

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from spectre import __version__
from spectre.network_geometry import (
    articulation_points,
    build_adjacency,
    critical_node_order,
    network_efficiency,
)
from spectre.org_intel import (
    Brotherhood,
    build_org,
    cell_membership,
    compartmentalization,
    hierarchy_stats,
)
from spectre.surveillance_net import (
    SurveillanceNetwork,
    build_network,
    cascade_coverage,
    data_share_centrality,
    group_centralization,
    herfindahl_index,
    out_degree_centrality,
)

__all__ = [
    "MissionProvider",
    "PROVIDER",
    "NINE_EYES_NETWORK",
    "NINE_EYES_NODES",
    "NINE_EYES_EDGES",
    "SPECTRE_ORG",
    "SPECTRE_OPERATIVES",
    "SPECTRE_CELL_OF",
    "SPECTRE_PARENT_OF",
    "SPECTRE_LEADERSHIP",
    "register_gadgets",
]

#: Deterministic RNG seed for any stochastic component (cascade activation).
_SEED = 11

#: Canonical Nine Eyes agency labels.
NINE_EYES_NODES: tuple[str, ...] = ("UK", "US", "CA", "AU", "NZ", "DE", "FR", "ES", "SE")
#: Canonical directed data-sharing edges among the Nine Eyes agencies.
NINE_EYES_EDGES: tuple[tuple[str, str], ...] = (
    ("US", "UK"),
    ("US", "CA"),
    ("US", "AU"),
    ("US", "NZ"),
    ("US", "DE"),
    ("US", "FR"),
    ("US", "ES"),
    ("US", "SE"),
    ("UK", "DE"),
    ("DE", "FR"),
    ("AU", "NZ"),
    ("ES", "SE"),
    ("FR", "ES"),
)
#: Serializable canonical network (kept for provenance input hashing).
NINE_EYES_NETWORK: dict[str, object] = {
    "nodes": NINE_EYES_NODES,
    "edges": NINE_EYES_EDGES,
}

#: Canonical SPECTRE brotherhood operatives.
SPECTRE_OPERATIVES: tuple[str, ...] = (
    "Ernst Blofeld",
    "Madeleine Swann",
    "Mr White",
    "Franz Oberhauser",
    "Hinx",
    "Guerrin",
    "Bautista",
    "C",
    "Mr Hinx",
)
#: Operative -> cell id.
SPECTRE_CELL_OF: dict[str, str] = {
    "Madeleine Swann": "white",
    "Mr White": "white",
    "Franz Oberhauser": "white",
    "Hinx": "enforcer",
    "Guerrin": "enforcer",
    "Bautista": "enforcer",
    "C": "shadow",
    "Mr Hinx": "enforcer",
}
#: Operative -> superior (None marks an apex).
SPECTRE_PARENT_OF: dict[str, str | None] = {
    "Franz Oberhauser": "Ernst Blofeld",
    "Madeleine Swann": "Mr White",
    "Mr White": "Ernst Blofeld",
    "Hinx": "Franz Oberhauser",
    "Guerrin": "Franz Oberhauser",
    "Bautista": "Franz Oberhauser",
    "C": "Franz Oberhauser",
    "Mr Hinx": "Franz Oberhauser",
}
#: Apex leadership.
SPECTRE_LEADERSHIP: tuple[str, ...] = ("Ernst Blofeld",)
#: Serializable canonical brotherhood (kept for provenance input hashing).
SPECTRE_ORG: dict[str, object] = {
    "operatives": SPECTRE_OPERATIVES,
    "cell_of": SPECTRE_CELL_OF,
    "parent_of": SPECTRE_PARENT_OF,
    "leadership": SPECTRE_LEADERSHIP,
}


def _network() -> SurveillanceNetwork:
    """Build the canonical Nine Eyes surveillance network."""
    return build_network(NINE_EYES_NODES, NINE_EYES_EDGES)


def _org() -> Brotherhood:
    """Build the canonical SPECTRE brotherhood."""
    return build_org(
        SPECTRE_OPERATIVES,
        SPECTRE_CELL_OF,
        SPECTRE_PARENT_OF,
        SPECTRE_LEADERSHIP,
    )


def _input_hash() -> str:
    """Stable SHA-256 fingerprint of the canonical mission inputs."""
    payload = {"network": NINE_EYES_NETWORK, "org": SPECTRE_ORG}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class MissionProvider:  # noqa: N801 — class name is fixed by the discovery contract
    """Deterministic NINE EYES mission provider implementing the BOND-API protocol."""

    film = "spectre"

    def __init__(self) -> None:
        self._network = _network()
        self._org = _org()

    def brief(self) -> MissionBrief:
        """Declare the NINE EYES mission: three objectives over the three concepts."""
        return MissionBrief(
            film=self.film,
            codename="NINE EYES",
            objectives=(
                "measure surveillance-network centralization and data flow",
                "assess the SPECTRE brotherhood's hierarchy and cell separation",
                "identify critical nodes in the network's geometry",
            ),
            assets=(
                Asset(kind="graph", name="nine_eyes_network", payload={"nodes": len(self._network.nodes)}),
                Asset(kind="graph", name="spectre_brotherhood", payload={"operatives": len(self._org.operatives)}),
                Asset(kind="kernel", name="geometry", payload={"seed": _SEED}),
            ),
            constraints=(
                Constraint(kind="determinism", detail="fixed seed, no wall-clock in results"),
                Constraint(kind="data", detail="real computation only, no mocks"),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the canonical networks: scale, connectivity, cell layout."""
        return ReconReport(
            findings=(
                Finding(label="nine_eyes_nodes", detail=str(len(self._network.nodes))),
                Finding(label="nine_eyes_edges", detail=str(int(self._network.adjacency.sum()))),
                Finding(label="spectre_cells", detail=str(len(cell_membership(self._org)))),
                Finding(label="request_goal", detail=request.goal),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the three deterministic analysis steps."""
        return MissionPlan(
            steps=(
                Step(name="flow_survey", action="centralize", params={"objective": brief.objectives[0]}),
                Step(name="org_intel", action="compartmentalize", params={"objective": brief.objectives[1]}),
                Step(name="geometry", action="find_critical_nodes", params={"objective": brief.objectives[2]}),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the analysis over the canonical networks and report measured metrics."""
        net = self._network
        org = self._org

        out_degree = out_degree_centrality(net).scores
        centrality = group_centralization(out_degree)
        shares = data_share_centrality(net)
        shares_list = [shares.scores[label] for label in net.nodes]
        concentration = herfindahl_index(shares_list)
        cascade = cascade_coverage(net, ("US",), 0.6)

        hierarchy = hierarchy_stats(org)
        separation = compartmentalization(org)
        cells = cell_membership(org)

        # Geometry is inherently undirected: build the symmetric adjacency.
        geometry_nodes, geometry_adj = build_adjacency(NINE_EYES_NODES, NINE_EYES_EDGES)
        articulations = sorted(articulation_points(geometry_adj))
        efficiency = network_efficiency(geometry_adj)
        critical = critical_node_order(geometry_adj, k=3)

        results = {
            "plan_steps": len(plan.steps),
            "centralization_index": round(centrality, 4),
            "flow_concentration_hhi": round(concentration, 4),
            "cascade_coverage": round(cascade.coverage_fraction, 4),
            "hierarchy_height": hierarchy.height,
            "chain_complete": bool(hierarchy.chain_complete),
            "compartmentalization": round(separation, 4),
            "cell_count": len(cells),
            "articulation_points": [geometry_nodes[i] for i in articulations],
            "network_efficiency": round(efficiency, 4),
            "critical_nodes": [geometry_nodes[i] for i in critical],
            "seed": _SEED,
        }
        return MissionOutcome(
            success=True,
            results=results,
            provenance=Provenance(
                package_version=__version__,
                seed=_SEED,
                input_hash=_input_hash(),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarize the mission and record standing lessons."""
        results = outcome.results
        return Debrief(
            outcome=outcome,
            lessons=(
                f"centralization index {results['centralization_index']}, "
                f"concentration HHI {results['flow_concentration_hhi']}",
                f"brotherhood compartmentalization {results['compartmentalization']}, "
                f"chain complete: {results['chain_complete']}",
                f"critical nodes carry the network: {', '.join(results['critical_nodes'])}",
            ),
        )


def register_gadgets(registry: GadgetRegistry) -> GadgetRegistry:
    """Register the NINE EYES analysis gadgets with a ``bond_api`` registry.

    Args:
        registry: A :class:`GadgetRegistry` to register into.

    Returns:
        The same registry (for chaining).
    """
    registry.register(
        "spectre",
        {
            "surveillance_centralization": group_centralization,
            "org_compartmentalization": compartmentalization,
            "geometry_efficiency": network_efficiency,
        },
    )
    return registry


#: Pre-built provider instance exposed at module top level (discovery loads
#: ``spectre.mission`` and instantiates the exported ``MissionProvider``).
PROVIDER = MissionProvider()
