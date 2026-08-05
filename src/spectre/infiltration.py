"""SPECTRE infiltration — compromise-cascade model.

The brotherhood's defining weakness is *infiltration*: turn one operative and
their cellmates, superior, and subordinates are exposed (see
:func:`spectre.org_intel.exposure`). This module models the resulting cascade
with a real, deterministic stochastic process:

* **compromise simulation** — round-based cascade seeded by a set of turned
  operatives: each round, every compromised operative exposes their cell,
  superior, and subordinates; each newly exposed operative turns with a fixed
  ``turn_probability`` (Bernoulli draw, fixed-seed RNG). Runs until the
  cascade stalls or the whole organisation is compromised;
* **damage metrics** — the fraction of the organisation compromised, whether
  leadership was reached, and the round at which leadership fell
  (``simulate_compromise``);
* **expected damage** — the mean of those metrics over a fixed number of
  deterministic trials, each driven by a distinct derived seed
  (``expected_damage``).

This is a percolation-style spread over the org graph (cf. Newman's epidemic
spread on networks), made deterministic by a fixed RNG seed and sorted
iteration order.

Pure and infrastructure-free: ``numpy`` + the standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from spectre.org_intel import Brotherhood, exposure

__all__ = [
    "CompromiseResult",
    "simulate_compromise",
    "expected_damage",
]


@dataclass(frozen=True)
class CompromiseResult:
    """Outcome of one compromise-cascade simulation."""

    compromised: frozenset[str]
    steps: int
    fraction: float
    leadership_hit: bool
    steps_to_leadership: int | None


def _validate_args(org: Brotherhood, seeds: Sequence[str], turn_probability: float) -> None:
    if not seeds:
        raise ValueError("at least one seed operative is required")
    known = set(org.operatives)
    unknown = [seed for seed in seeds if seed not in known]
    if unknown:
        raise ValueError(f"unknown seed operative(s): {sorted(unknown)}")
    if not 0.0 <= turn_probability <= 1.0:
        raise ValueError("turn_probability must be in [0, 1]")


def simulate_compromise(
    org: Brotherhood,
    seeds: Sequence[str],
    turn_probability: float,
    seed: int = 0,
) -> CompromiseResult:
    """Run a deterministic compromise cascade from ``seeds``.

    Args:
        org: The brotherhood to infiltrate.
        seeds: Operatives already turned at the start.
        turn_probability: Probability an exposed operative turns each round.
        seed: Fixed RNG seed (deterministic sequence).

    Raises:
        ValueError: If seeds are empty/unknown or ``turn_probability`` is
            outside ``[0, 1]``.
    """
    _validate_args(org, seeds, turn_probability)
    rng = np.random.default_rng(seed)
    compromised: set[str] = set(seeds)
    leadership = org.leadership or {m for m in org.operatives if org.parent_of.get(m) is None}
    leadership_hit = bool(compromised & leadership)
    steps_to_leadership = 0 if leadership_hit else None

    # Termination: every pass either breaks or adds at least one operative to
    # `compromised`, which is bounded by the organisation size — so the loop
    # runs at most len(org.operatives) times and needs no round cap.
    rounds = 0
    while True:
        rounds += 1
        new_turned: set[str] = set()
        for operative in sorted(compromised):
            for exposed in sorted(exposure(org, operative)):
                if exposed in compromised or exposed in new_turned:
                    continue
                if rng.random() < turn_probability:
                    new_turned.add(exposed)
        if not new_turned:
            break
        compromised.update(new_turned)
        if steps_to_leadership is None and (compromised & leadership):
            steps_to_leadership = rounds
        if len(compromised) == len(org.operatives):
            break

    return CompromiseResult(
        compromised=frozenset(compromised),
        steps=rounds,
        fraction=len(compromised) / len(org.operatives),
        leadership_hit=bool(compromised & leadership),
        steps_to_leadership=steps_to_leadership,
    )


def expected_damage(
    org: Brotherhood,
    seeds: Sequence[str],
    turn_probability: float,
    trials: int,
    seed: int = 0,
) -> dict[str, float]:
    """Mean compromise damage over ``trials`` deterministic simulations.

    Trial ``i`` uses derived seed ``seed + i``, so the whole estimate is
    reproducible.

    Args:
        org: The brotherhood to infiltrate.
        seeds: Operatives already turned at the start.
        turn_probability: Per-round turn probability.
        trials: Number of simulations to average over.
        seed: Base RNG seed.

    Raises:
        ValueError: If ``trials`` is not positive (or seeds/probability are
            invalid per :func:`simulate_compromise`).

    Returns:
        A mapping with ``mean_fraction``, ``mean_steps``, ``leadership_hit_rate``
        and ``mean_steps_to_leadership`` (the latter averaged only over trials
        that reached leadership; 0.0 when none did).
    """
    _validate_args(org, seeds, turn_probability)
    if trials <= 0:
        raise ValueError("trials must be positive")
    fractions: list[float] = []
    steps: list[int] = []
    leadership_hits = 0
    leadership_steps: list[int] = []
    for trial in range(trials):
        result = simulate_compromise(org, seeds, turn_probability, seed=seed + trial)
        fractions.append(result.fraction)
        steps.append(result.steps)
        # `steps_to_leadership is not None` is exactly `leadership_hit`
        # (simulate_compromise sets both together); using the optional as the
        # marker avoids a second branch that could never be False.
        if result.steps_to_leadership is not None:
            leadership_hits += 1
            leadership_steps.append(result.steps_to_leadership)
    mean_leadership_steps = sum(leadership_steps) / len(leadership_steps) if leadership_steps else 0.0
    return {
        "mean_fraction": float(np.mean(fractions)),
        "mean_steps": float(np.mean(steps)),
        "leadership_hit_rate": leadership_hits / trials,
        "mean_steps_to_leadership": mean_leadership_steps,
    }
