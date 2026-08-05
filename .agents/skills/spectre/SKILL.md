---
name: spectre
description: BOND film package (Spectre 2015) — Nine Eyes surveillance-network centralization, SPECTRE org cell model, network geometry, traffic interception, compromise cascades, sensor-placement cover.
version: 0.1.0
author: docxology
license: MIT
tags: [bond, spectre, nine-eyes, surveillance-network, org-intel, network-geometry, traffic-intel, infiltration, signal-cover]
---

# spectre

Project-scoped skill for the BOND film package at
`projects/working/bond/spectre/` (mission codename **NINE EYES**). Load this
when working inside the project.

## When to Use

- Working inside `projects/working/bond/spectre/` — running mission CLIs,
  editing domain modules, regenerating outputs.
- Implementing or inspecting the FROZEN `bond_api.MissionProvider`
  (`src/spectre/mission.py`).
- Validating the package contracts (pure bond_api-free core, zero-mock
  testing, determinism, ≥90% coverage) after changes.

## Quick Reference

```bash
cd projects/working/bond/spectre
uv sync --extra dev                       # install deps incl. the bond-api path dep
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/debrief.py          # run the full deterministic mission
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py   # hydrate tokens (last)
```

## Structure

- **Pure core (numpy+stdlib, no bond_api), six modules:**
  `src/spectre/surveillance_net.py` (data-flow centralization, betweenness,
  cascade coverage), `src/spectre/org_intel.py` (hierarchy + cell
  compartmentalization + exposure), `src/spectre/network_geometry.py`
  (connectivity, articulation points, critical nodes),
  `src/spectre/traffic_intel.py` (volume-weighted interception, greedy
  submodular monitoring budget), `src/spectre/infiltration.py` (compromise
  cascade, expected damage), `src/spectre/signal_cover.py` (greedy set cover,
  coverage redundancy).
- **Adapter:** `src/spectre/mission.py` — FROZEN `MissionProvider`, canonical
  NINE EYES dataset, `register_gadgets`.
- **Hydration:** `src/spectre/manuscript_variables.py` — `{{TOKEN}}`s from
  config + measured mission output.
- **Figures:** `src/spectre/figures/networks.py` (matplotlib only).
- **Scripts:** thin per-phase CLIs (`brief/recon/plan/execute/debrief`),
  `generate_figures.py`, `z_generate_manuscript_variables.py`.

## Pitfalls

- **Keep the pure core bond_api-free.** Only `mission.py` imports `bond_api`;
  the six domain modules must stay importable standalone
  (`tests/test_domain_isolation.py` proves it in a subprocess).
- **No mocks.** All tests use real data structures and computation.
- **Deterministic.** Fixed seeds, label-ordered greedy tie-breaks, no
  wall-clock in persisted artifacts (`Provenance.wall_time_s == 0.0`).
- **Frozen surface.** `MissionProvider`, `PROVIDER` and `register_gadgets` are
  consumed across packages — deepen inside them, never re-shape them.
- **Metrics flow, never hardcode.** Every number in the manuscript comes from
  `manuscript_variables.generate_variables()` reading the measured mission
  `execute()` output — do not hand-author metrics in prose.
- **`output/` is disposable** (git-ignored); edit generators, not `output/`.
- **Scripts are thin.** `_boot.py` adds `src/` to `sys.path` (`# noqa: E402`).

## Cross-refs

- Root `AGENTS.md` — authoritative agent rulebook.
- `docs/AGENTS.md`, `docs/architecture.md`, `docs/testing_philosophy.md`,
  `docs/agent_instructions.md`.
- `TODO.md` — build log + declared integration points.
