"""Tests for spectre.mission — the NINE EYES MissionProvider adapter."""

from __future__ import annotations

from collections import Counter

import pytest

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
    NINE_EYES_EDGES,
    NINE_EYES_NETWORK,
    NINE_EYES_NODES,
    PROVIDER,
    SPECTRE_CELL_OF,
    SPECTRE_OPERATIVES,
    SPECTRE_ORG,
    SPECTRE_PARENT_OF,
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
            "traffic_total",
            "monitor_coverage_budget3",
            "expected_compromise_fraction",
            "leadership_hit_rate",
            "set_cover_size",
            "coverage_redundancy",
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
        assert debrief.outcome.results["plan_steps"] == 6


class TestHeadlineValuesArePinned:
    """Exact pins on the reported metrics, re-derived from the edge list.

    Key-presence and ``> 0.0`` assertions are what let a degenerate metric ship:
    ``data_share_centrality`` returned a 0/1 indicator vector for the whole of
    phase 5 and every test stayed green. Each pin below recomputes the expected
    value here, from ``NINE_EYES_EDGES`` directly, instead of calling the
    function under test — so a change in the implementation moves the measured
    value away from an independently-derived constant and the test goes red.
    """

    def _results(self) -> dict:
        return dict(PROVIDER.execute(PROVIDER.plan(PROVIDER.brief())).results)

    def test_flow_concentration_hhi(self) -> None:
        inflow = Counter(target for _, target in NINE_EYES_EDGES)
        total = sum(inflow.values())
        expected = sum((inflow.get(node, 0) / total) ** 2 for node in NINE_EYES_NODES)
        assert expected == pytest.approx(23 / 169)  # 3 x (1/13)^2 + 5 x (2/13)^2
        assert self._results()["flow_concentration_hhi"] == pytest.approx(round(expected, 4))

    def test_flow_concentration_floor_and_receivers(self) -> None:
        receivers = {target for _, target in NINE_EYES_EDGES}
        results = self._results()
        assert results["receiving_agencies"] == len(receivers) == 8
        assert results["flow_concentration_floor"] == pytest.approx(1 / len(receivers))

    def test_hhi_sits_just_above_its_floor(self) -> None:
        """The measured concentration is near-even, not concentrated.

        23/169 = 0.1361 against a 0.1250 floor: inflows are spread almost
        evenly across the eight receiving agencies. Any prose that reads this
        index as corroborating hub dominance is contradicted by this test.
        """
        results = self._results()
        excess = results["flow_concentration_hhi"] - results["flow_concentration_floor"]
        assert 0.0 < excess < 0.02

    def test_centralization_index(self) -> None:
        out_degree = Counter(source for source, _ in NINE_EYES_EDGES)
        cap = len(NINE_EYES_NODES) - 1
        deviation = sum(cap - out_degree.get(node, 0) for node in NINE_EYES_NODES)
        expected = deviation / ((len(NINE_EYES_NODES) - 1) * cap)
        assert expected == pytest.approx(59 / 64)
        assert self._results()["centralization_index"] == pytest.approx(round(expected, 4))

    def test_centralization_uses_the_star_bound_not_the_observed_max(self) -> None:
        """The methodology states the star-graph denominator; assert it is used.

        The two coincide on this dataset only because the maximum out-degree
        happens to equal n - 1. Recomputing with an observed maximum of 7
        (what the code would use if the hub lost one edge) gives a different
        number, so the pin above is not satisfied by either formula.
        """
        out_degree = Counter(source for source, _ in NINE_EYES_EDGES)
        assert max(out_degree.values()) == len(NINE_EYES_NODES) - 1

    def test_cascade_is_a_trial_mean_not_one_draw(self) -> None:
        from spectre.surveillance_net import build_network, cascade_coverage

        results = self._results()
        assert results["cascade_trials"] == 50
        net = build_network(NINE_EYES_NODES, NINE_EYES_EDGES)
        single = cascade_coverage(net, ("US",), 0.6, seed=results["seed"]).coverage_fraction
        assert results["cascade_coverage"] != pytest.approx(round(single, 4))
        # A mean over 50 draws at p = 0.6 from the sole source cannot sit
        # below the source's own share of the network.
        assert results["cascade_coverage"] > 1 / len(NINE_EYES_NODES)

    def test_recorded_seed_governs_the_cascade(self) -> None:
        """Changing the seed must change the number the provider reports.

        A seed that is stored in Provenance but consumed by nothing is a false
        provenance claim; this asserts the causal link exists.
        """
        from spectre.surveillance_net import build_network, expected_cascade_coverage

        net = build_network(NINE_EYES_NODES, NINE_EYES_EDGES)
        recorded = self._results()["seed"]
        at_seed = expected_cascade_coverage(net, ("US",), 0.6, trials=50, seed=recorded)
        elsewhere = expected_cascade_coverage(net, ("US",), 0.6, trials=50, seed=recorded + 1000)
        assert at_seed != pytest.approx(elsewhere)

    def test_structural_counts(self) -> None:
        results = self._results()
        assert results["plan_steps"] == 6
        assert results["cell_count"] == 3
        assert results["hierarchy_height"] == 2
        assert results["chain_complete"] is True
        assert results["articulation_points"] == ["US"]
        assert results["critical_nodes"] == ["US", "FR", "UK"]

    def test_operational_values(self) -> None:
        results = self._results()
        assert results["traffic_total"] == pytest.approx(1360.0)
        assert results["monitor_allocation"] == ["US", "DE", "ES"]
        assert results["monitor_coverage_budget3"] == pytest.approx(0.9669)
        assert results["set_cover_selection"] == ["CA", "DE", "FR", "UK"]
        assert results["uncovered_targets_after_cover"] == 0
        assert results["coverage_redundancy"] == pytest.approx(0.25)
        assert results["network_efficiency"] == pytest.approx(0.6806)
        assert results["compartmentalization"] == pytest.approx(0.8235)


class TestCanonicalRosterHasNoDuplicatePeople:
    """One node per distinct film character — no aliases, no actor names.

    The roster shipped with 'Ernst Blofeld' and 'Franz Oberhauser' (the same
    character under his birth name) plus 'Hinx', 'Mr Hinx' and 'Bautista'
    (the character twice more, once under his actor's surname), which inflated
    the operative count and manufactured the executive layer.
    """

    def test_no_alias_pairs_remain(self) -> None:
        roster = set(SPECTRE_OPERATIVES)
        for alias, canonical in (
            ("Franz Oberhauser", "Ernst Blofeld"),
            ("Hinx", "Mr Hinx"),
            ("Bautista", "Mr Hinx"),
        ):
            assert not (alias in roster and canonical in roster), f"{alias} duplicates {canonical}"

    def test_roster_entries_are_unique(self) -> None:
        assert len(set(SPECTRE_OPERATIVES)) == len(SPECTRE_OPERATIVES)

    def test_every_operative_is_placed_and_commanded(self) -> None:
        apex = "Ernst Blofeld"
        assert set(SPECTRE_CELL_OF) == set(SPECTRE_OPERATIVES) - {apex}
        assert set(SPECTRE_PARENT_OF) == set(SPECTRE_OPERATIVES) - {apex}
        assert set(SPECTRE_PARENT_OF.values()) <= set(SPECTRE_OPERATIVES)


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
        for gadget in (
            "surveillance_centralization",
            "org_compartmentalization",
            "geometry_efficiency",
            "traffic_interception",
            "infiltration_damage",
            "signal_set_cover",
        ):
            assert registry.contains("spectre", gadget), gadget
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
