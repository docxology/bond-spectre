"""Tests for spectre.org_intel — SPECTRE hierarchy and cell compartmentalization."""

from __future__ import annotations

import pytest

from spectre.org_intel import (
    Brotherhood,
    HierarchyStats,
    build_org,
    cell_membership,
    command_reachability,
    compartmentalization,
    exposure,
    hierarchy_stats,
)

OPERATIVES = ("Blofeld", "White", "Madeleine", "Oberhauser", "Hinx", "Bautista", "C")
CELL_OF = {
    "White": "white",
    "Madeleine": "white",
    "Oberhauser": "white",
    "Hinx": "enforcer",
    "Bautista": "enforcer",
    "C": "shadow",
}
PARENT_OF = {
    "Oberhauser": "Blofeld",
    "White": "Blofeld",
    "Madeleine": "White",
    "Hinx": "Oberhauser",
    "Bautista": "Oberhauser",
    "C": "Oberhauser",
}
LEADERSHIP = ("Blofeld",)


def _org() -> Brotherhood:
    return build_org(OPERATIVES, CELL_OF, PARENT_OF, LEADERSHIP)


class TestBuildOrg:
    def test_valid(self) -> None:
        org = _org()
        assert isinstance(org, Brotherhood)
        assert "Blofeld" in org.leadership

    def test_duplicate_operatives_raises(self) -> None:
        with pytest.raises(ValueError):
            build_org(("A", "A"), {}, {})

    def test_empty_operatives_raises(self) -> None:
        with pytest.raises(ValueError):
            build_org((), {}, {})

    def test_unknown_in_cell_of_raises(self) -> None:
        with pytest.raises(ValueError):
            build_org(("A",), {"ZZ": "x"}, {})

    def test_empty_cell_id_raises(self) -> None:
        with pytest.raises(ValueError):
            build_org(("A",), {"A": "  "}, {})

    def test_unknown_in_parent_of_raises(self) -> None:
        with pytest.raises(ValueError):
            build_org(("A",), {}, {"A": "ZZ"})

    def test_unknown_superior_raises(self) -> None:
        with pytest.raises(ValueError):
            build_org(("A", "B"), {}, {"A": "ZZ"})

    def test_self_report_raises(self) -> None:
        with pytest.raises(ValueError):
            build_org(("A",), {}, {"A": "A"})

    def test_unknown_leadership_raises(self) -> None:
        with pytest.raises(ValueError):
            build_org(("A",), {}, {}, ("ZZ",))


class TestHierarchyStats:
    def test_depth_and_height(self) -> None:
        stats = hierarchy_stats(_org())
        assert isinstance(stats, HierarchyStats)
        assert stats.height == 2
        assert stats.depth["Blofeld"] == 0
        assert stats.depth["Madeleine"] == 2
        assert stats.total_members == 7
        assert stats.chain_complete is True

    def test_reachable_all(self) -> None:
        stats = hierarchy_stats(_org())
        assert stats.reachable_from_apex == 7


class TestCellMembership:
    def test_grouping(self) -> None:
        cells = cell_membership(_org())
        assert cells["white"] == ("White", "Madeleine", "Oberhauser")
        assert "shadow" in cells

    def test_skips_unassigned(self) -> None:
        # Blofeld has no cell; should not appear in any cell's membership.
        cells = cell_membership(_org())
        assert all("Blofeld" not in members for members in cells.values())


class TestCompartmentalization:
    def test_isolated_cells_high(self) -> None:
        # All cross-cell command edges removed -> perfect separation (1.0).
        org = build_org(("A", "B", "C", "D"), {"A": "1", "B": "1", "C": "2", "D": "2"}, {})
        assert compartmentalization(org) == pytest.approx(1.0)

    def test_single_cell_no_cross_pairs(self) -> None:
        org = build_org(("A", "B"), {"A": "x", "B": "x"}, {})
        assert compartmentalization(org) == pytest.approx(1.0)

    def test_cross_cell_command_edge_leaks(self) -> None:
        # C (cell 2) commands A (cell 1) -> one linked cross pair, separation < 1.
        org = build_org(
            ("A", "B", "C", "D"),
            {"A": "1", "B": "1", "C": "2", "D": "2"},
            {"A": "C"},
        )
        assert 0.0 < compartmentalization(org) < 1.0

    def test_real_org(self) -> None:
        value = compartmentalization(_org())
        assert 0.0 < value <= 1.0


class TestCommandReachability:
    def test_chain_from_apex(self) -> None:
        reached = command_reachability(_org())
        assert reached == set(OPERATIVES)


class TestExposure:
    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError):
            exposure(_org(), "ZZ")

    def test_cellmates_and_superiors(self) -> None:
        # Hinx is in enforcer cell, reports to Oberhauser (cross-cell).
        turned = exposure(_org(), "Hinx")
        assert "Hinx" in turned
        # Cellmates
        assert "Bautista" in turned
        # Direct superior
        assert "Oberhauser" in turned

    def test_apex_exposure(self) -> None:
        turned = exposure(_org(), "Blofeld")
        assert "Blofeld" in turned
        # Direct subordinates of the apex
        assert "Oberhauser" in turned or "White" in turned
