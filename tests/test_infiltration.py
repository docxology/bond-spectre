"""Tests for spectre.infiltration — compromise cascade through the brotherhood."""

from __future__ import annotations

import pytest

from spectre.infiltration import (
    CompromiseResult,
    expected_damage,
    simulate_compromise,
)
from spectre.mission import (
    SPECTRE_CELL_OF,
    SPECTRE_LEADERSHIP,
    SPECTRE_OPERATIVES,
    SPECTRE_PARENT_OF,
)
from spectre.org_intel import build_org


def _org():
    return build_org(
        SPECTRE_OPERATIVES,
        SPECTRE_CELL_OF,
        SPECTRE_PARENT_OF,
        SPECTRE_LEADERSHIP,
    )


class TestSimulateCompromise:
    def test_seed_always_compromised(self) -> None:
        org = _org()
        result = simulate_compromise(org, ("Mr White",), 0.0, seed=0)
        assert isinstance(result, CompromiseResult)
        assert "Mr White" in result.compromised
        assert result.steps >= 1

    def test_zero_probability_no_spread(self) -> None:
        org = _org()
        result = simulate_compromise(org, ("Mr White",), 0.0, seed=0)
        assert result.fraction == pytest.approx(1 / len(org.operatives))

    def test_full_spread_at_probability_one(self) -> None:
        org = _org()
        result = simulate_compromise(org, ("Mr White",), 1.0, seed=0)
        assert result.fraction == pytest.approx(1.0)
        assert result.leadership_hit is True

    def test_deterministic(self) -> None:
        org = _org()
        a = simulate_compromise(org, ("Mr White",), 0.5, seed=11)
        b = simulate_compromise(org, ("Mr White",), 0.5, seed=11)
        assert a.compromised == b.compromised
        assert a.fraction == b.fraction

    def test_leadership_seed_hits_at_step_zero(self) -> None:
        org = _org()
        result = simulate_compromise(org, ("Ernst Blofeld",), 0.5, seed=0)
        assert result.leadership_hit is True
        assert result.steps_to_leadership == 0

    def test_unknown_seed_raises(self) -> None:
        org = _org()
        with pytest.raises(ValueError):
            simulate_compromise(org, ("ZZ",), 0.5)

    def test_empty_seed_raises(self) -> None:
        org = _org()
        with pytest.raises(ValueError):
            simulate_compromise(org, (), 0.5)

    def test_probability_out_of_range_raises(self) -> None:
        org = _org()
        with pytest.raises(ValueError):
            simulate_compromise(org, ("Mr White",), 1.5)
        with pytest.raises(ValueError):
            simulate_compromise(org, ("Mr White",), -0.1)


class TestExpectedDamage:
    def test_returns_metric_keys(self) -> None:
        org = _org()
        damage = expected_damage(org, ("Mr White",), 0.5, trials=10, seed=11)
        for key in ("mean_fraction", "mean_steps", "leadership_hit_rate", "mean_steps_to_leadership"):
            assert key in damage
        assert 0.0 <= damage["leadership_hit_rate"] <= 1.0
        assert 0.0 <= damage["mean_fraction"] <= 1.0

    def test_deterministic(self) -> None:
        org = _org()
        a = expected_damage(org, ("Mr White",), 0.5, trials=20, seed=3)
        b = expected_damage(org, ("Mr White",), 0.5, trials=20, seed=3)
        assert a == b

    def test_zero_probability_minimal_damage(self) -> None:
        org = _org()
        damage = expected_damage(org, ("Mr White",), 0.0, trials=5, seed=0)
        assert damage["mean_fraction"] == pytest.approx(1 / len(org.operatives))
        assert damage["leadership_hit_rate"] == 0.0

    def test_nonpositive_trials_raises(self) -> None:
        org = _org()
        with pytest.raises(ValueError):
            expected_damage(org, ("Mr White",), 0.5, trials=0)
