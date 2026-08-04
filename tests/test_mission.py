"""Tests for spectre.mission — the NINE EYES MissionProvider adapter."""

from __future__ import annotations

from bond_api.protocol import (
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    MissionProvider as Protocol,
    ReconReport,
    ReconRequest,
    run_mission,
)
from bond_api.registry import GadgetRegistry

from spectre.mission import (
    NINE_EYES_NETWORK,
    PROVIDER,
    SPECTRE_ORG,
    MissionProvider,
    register_gadgets,
)


def test_provider_satisfies_protocol() -> None:
    provider = MissionProvider()
    assert isinstance(provider, Protocol)


def test_prebuilt_provider_is_exported() -> None:
    assert isinstance(PROVIDER, MissionProvider)
    assert PROVIDER.film == "spectre"


class TestBrief:
    def test_brief(self) -> None:
        brief = PROVIDER.brief()
        assert isinstance(brief, MissionBrief)
        assert brief.film == "spectre"
        assert brief.codename == "NINE EYES"
        assert len(brief.objectives) == 3
        assert len(brief.assets) == 3
        assert len(brief.constraints) >= 1

    def test_recon(self) -> None:
        report = PROVIDER.recon(ReconRequest(goal="assess the programme"))
        assert isinstance(report, ReconReport)
        assert len(report.findings) >= 3

    def test_plan(self) -> None:
        plan = PROVIDER.plan(PROVIDER.brief())
        assert isinstance(plan, MissionPlan)
        names = [step.name for step in plan.steps]
        assert "flow_survey" in names and "geometry" in names

    def test_execute(self) -> None:
        outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
        assert isinstance(outcome, MissionOutcome)
        assert outcome.success is True

    def test_execute_results_keys(self) -> None:
        outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
        for key in (
            "centralization_index",
            "flow_concentration_hhi",
            "cascade_coverage",
            "compartmentalization",
            "network_efficiency",
            "critical_nodes",
        ):
            assert key in outcome.results

    def test_execute_deterministic(self) -> None:
        a = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
        b = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
        assert a.results == b.results
        assert a.provenance.input_hash == b.provenance.input_hash

    def test_debrief(self) -> None:
        outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
        debrief = PROVIDER.debrief(outcome)
        assert len(debrief.lessons) == 3

    def test_run_mission_flow(self) -> None:
        debrief = run_mission(PROVIDER, ReconRequest(goal="full flow"))
        assert debrief.outcome.success is True
        assert debrief.outcome.results["plan_steps"] == 3


class TestProvenance:
    def test_provenance_fields(self) -> None:
        outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
        prov = outcome.provenance
        assert prov.seed >= 0
        assert prov.package_version
        assert len(prov.input_hash) == 64
        assert prov.wall_time_s == 0.0


class TestRegistry:
    def test_register_gadgets(self) -> None:
        registry = register_gadgets(GadgetRegistry())
        assert registry.contains("spectre", "surveillance_centralization")
        assert registry.contains("spectre", "org_compartmentalization")
        assert registry.contains("spectre", "geometry_efficiency")
        assert "spectre" in registry.films()


class TestCanonicalData:
    def test_network_and_org_shapes(self) -> None:
        assert len(NINE_EYES_NETWORK["nodes"]) == 9
        assert len(SPECTRE_ORG["operatives"]) >= 5


def test_discovery_loads_provider() -> None:
    from pathlib import Path

    from bond_api.discovery import load_provider

    src = str(Path(__file__).resolve().parents[1] / "src")
    provider = load_provider("spectre", search_paths=[src])
    assert provider.film == "spectre"
    assert isinstance(provider, MissionProvider)
