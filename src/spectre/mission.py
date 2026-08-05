"""NINE EYES — the Spectre (2015) mission provider for BOND-API.

This is the thin adapter between the pure domain core
(:mod:`spectre.surveillance_net`, :mod:`spectre.org_intel`,
:mod:`spectre.network_geometry`, :mod:`spectre.traffic_intel`,
:mod:`spectre.infiltration`, :mod:`spectre.signal_cover`) and the FROZEN
``bond_api`` ``MissionProvider`` protocol. The domain modules do **not** import
``bond_api`` and remain importable standalone; this module is the only place
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
from spectre.infiltration import expected_damage
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
from spectre.signal_cover import (
    canonical_coverage_problem,
    greedy_set_cover,
    redundancy_index,
    uncovered_targets,
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
from spectre.traffic_intel import (
    canonical_traffic_network,
    heavy_hitters,
    monitor_allocation,
    total_traffic,
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
    "gadget_names",
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
                Step(name="traffic_intel", action="intercept", params={"objective": brief.objectives[0]}),
                Step(name="infiltration", action="cascade", params={"objective": brief.objectives[1]}),
                Step(name="signal_cover", action="place_sensors", params={"objective": brief.objectives[0]}),
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

        # Deepened analyses: traffic interception, compromise cascade, sensor cover.
        traffic = canonical_traffic_network()
        traffic_total = total_traffic(traffic)
        top_links = heavy_hitters(traffic, 3)
        monitor_selected, monitor_coverage = monitor_allocation(traffic, budget=3)

        damage = expected_damage(org, ("Mr White",), turn_probability=0.5, trials=50, seed=_SEED)

        cover = canonical_coverage_problem()
        cover_selected, cover_covered = greedy_set_cover(cover)
        cover_redundancy = redundancy_index(cover, cover_selected)
        cover_gaps = uncovered_targets(cover, cover_selected)

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
            "traffic_total": round(traffic_total, 1),
            "traffic_top_link": f"{top_links[0][0]}->{top_links[0][1]} ({top_links[0][2]:.1f})",
            "monitor_allocation": list(monitor_selected),
            "monitor_coverage_budget3": round(monitor_coverage, 4),
            "expected_compromise_fraction": round(damage["mean_fraction"], 4),
            "leadership_hit_rate": round(damage["leadership_hit_rate"], 4),
            "mean_steps_to_leadership": round(damage["mean_steps_to_leadership"], 4),
            "set_cover_size": len(cover_selected),
            "set_cover_selection": list(cover_selected),
            "coverage_redundancy": round(cover_redundancy, 4),
            "uncovered_targets_after_cover": len(cover_gaps),
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
                f"centralization {results['centralization_index']}, "
                f"monitoring 3 agencies intercepts {results['monitor_coverage_budget3']} of traffic",
                f"brotherhood compartmentalization {results['compartmentalization']}; "
                f"a mole reaches leadership with probability {results['leadership_hit_rate']}",
                f"critical nodes carry the network: {', '.join(results['critical_nodes'])}; "
                f"set cover needs {results['set_cover_size']} agencies",
            ),
        )


#: Q-branch gadget table: gadget name -> the pure-core callable it exposes.
#: Private so the package's public registration surface stays exactly
#: ``register_gadgets`` (what the coordinator and CLI consume).
_GADGETS: dict[str, object] = {
    "surveillance_centralization": group_centralization,
    "org_compartmentalization": compartmentalization,
    "geometry_efficiency": network_efficiency,
    "traffic_interception": monitor_allocation,
    "infiltration_damage": expected_damage,
    "signal_set_cover": greedy_set_cover,
}


def gadget_names() -> tuple[str, ...]:
    """Sorted names of the gadgets :func:`register_gadgets` publishes.

    Measured from the same table the registration uses, so a manuscript or doc
    count of gadgets cannot drift from what is actually registered.
    """
    return tuple(sorted(_GADGETS))


def register_gadgets(registry: GadgetRegistry) -> GadgetRegistry:
    """Register the NINE EYES analysis gadgets with a ``bond_api`` registry.

    Args:
        registry: A :class:`GadgetRegistry` to register into.

    Returns:
        The same registry (for chaining).
    """
    registry.register("spectre", dict(_GADGETS))
    return registry


#: Pre-built provider instance exposed at module top level (discovery loads
#: ``spectre.mission`` and instantiates the exported ``MissionProvider``).
PROVIDER = MissionProvider()
