# Agent instructions — Spectre NINE EYES

This file mirrors the authoritative rules in the root `../AGENTS.md`; read
that one first. Abridged architecture section:

## Layer boundaries

```
src/spectre/
  surveillance_net.py   -- PURE (numpy+stdlib, no bond_api)  data-flow centralization
  org_intel.py          -- PURE                                 criminal-org cells
  network_geometry.py   -- PURE                                 connectivity & critical nodes
  mission.py            -- ADAPTER (imports bond_api)           FROZEN MissionProvider + gadgets
  manuscript_variables.py -- reads config + measured mission    {{TOKEN}} hydration
  figures/networks.py   -- matplotlib figure generator (seeded)
scripts/*.py            -- thin orchestrators (sys.path bootstrap)
tests/*.py              -- zero mocks, real data + computation
```

**Purity rule**: `surveillance_net.py`, `org_intel.py`, `network_geometry.py`
must import only `numpy` + the standard library. The `bond_api` contract is
confined to `mission.py` (and the tests that exercise it). The pure modules
must remain importable without `bond-api` installed.

**Determinism**: fixed seed for cascade activation and figure layout; no
wall-clock in persisted artifacts (`Provenance.wall_time_s == 0.0`); canonical
SHA-256 `input_hash` over the canonical dataset.

## Required maintenance commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

When you modify a metric that appears in the manuscript, re-run
`scripts/z_generate_manuscript_variables.py` and update
`data/claim_ledger.yaml` to keep measured values current.
