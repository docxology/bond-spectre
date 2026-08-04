# Spectre — NINE EYES

Mission codename **NINE EYES**: a BOND film package (Spectre, 2015) modelling the
global surveillance programme with three pure, deterministic analytic concepts.

## Concepts

| Module | Concept | What it computes |
| --- | --- | --- |
| `src/spectre/surveillance_net.py` | Data-flow centralization | Directed agency network, out/in-degree centrality, Freeman group centralization, Herfindahl flow concentration, deterministic cascade coverage, sweep coverage |
| `src/spectre/org_intel.py` | Criminal-org cell model | SPECTRE hierarchy depths/height, cell membership, compartmentalization (cross-cell leak), command-chain reachability, per-operative exposure |
| `src/spectre/network_geometry.py` | Connectivity & critical nodes | Connected components, articulation points (Tarjan), global efficiency, node-removal impact, robustness-under-attack curve, greedy critical-node ordering |
| `src/spectre/traffic_intel.py` | Traffic interception | Volume-weighted traffic network, heavy-hitter links, interception coverage from monitored agencies, greedy submodular monitoring-budget allocation |
| `src/spectre/infiltration.py` | Compromise cascade | Round-based compromise cascade through the brotherhood, expected-compromise damage, leadership hit rate, steps to leadership |
| `src/spectre/signal_cover.py` | Sensor-placement cover | Agency × target coverage matrix, greedy set cover, per-target coverage counts, uncovered targets, multi-sensor coverage redundancy |

Every metric in the manuscript is **measured** — computed by the deterministic
NINE EYES mission provider and injected through
`src/spectre/manuscript_variables.py`; no number is hand-authored in prose.

## Mission provider

`src/spectre/mission.py` implements the FROZEN `bond_api.MissionProvider`
protocol (brief → recon → plan → execute → debrief) over the canonical Nine
Eyes network and SPECTRE brotherhood, and registers NINE EYES analysis gadgets
with the `bond_api.GadgetRegistry`. The pure domain core does **not** import
`bond_api`, so it remains importable standalone; the protocol contract is
isolated in the thin adapter.

## Quickstart

```bash
cd projects/working/bond/spectre
uv sync --extra dev                    # install deps + the frozen bond-api path dep
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/brief.py         # mission phase CLIs: brief/recon/plan/execute/debrief
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py   # hydrate manuscript tokens (last)
```

## Science

- **Deterministic**: fixed seed, fixed layout seed, no wall-clock in persisted
  artifacts (`Provenance.wall_time_s == 0.0`), canonical SHA-256 `input_hash`.
- **Zero mocks**: all tests use real data structures and computation.
- **Infrastructure-free core**: `numpy` + stdlib only in the three domain
  modules; safe to lift into any environment.

## Gates

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90   # >=90% line+branch on src/
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

Local-only working tree — this package is part of the BOND suite and is never
pushed to any remote.
