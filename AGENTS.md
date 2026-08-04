# Spectre — NINE EYES (agent instructions)

## Scope & identity

- **Package**: `spectre` — BOND film package for *Spectre* (2015), mission
  codename **NINE EYES**.
- **Scope**: exactly this directory. Never touch sibling BOND packages, bond
  root files, or the template repo.
- **Local-only**: no remote, never push.

## Layout contract

| Surface | Rule |
| --- | --- |
| `src/spectre/surveillance_net.py`, `org_intel.py`, `network_geometry.py`, `traffic_intel.py`, `infiltration.py`, `signal_cover.py` (pure domain core) | `numpy` + stdlib only; **no** `bond_api` import; deterministic; importable standalone |
| `src/spectre/mission.py` | The only module that imports `bond_api`; implements the FROZEN `MissionProvider`. Registered gadgets via `register_gadgets`. |
| `src/spectre/manuscript_variables.py` | Computes every `{{TOKEN}}` from config + the measured mission results |
| `src/spectre/figures/` | Matplotlib figure generators (deterministic seed) |
| `scripts/` | Thin orchestrators (sys.path bootstrap via `_boot`); no business logic |
| `tests/` | Zero mocks; real data + computation; standalone importable core tested separately |

## Non-negotiable rules

1. **No mock framework** — `MagicMock` / `mocker.patch` / `unittest.mock` /
   `create_autospec` anywhere. Deterministic fake behavior implements the real
   protocol or nothing.
2. **≥90% line+branch coverage on `src/`**:
   `uv run pytest tests/ --cov=src --cov-fail-under=90`.
3. **Pure core is bond_api-free** — the six domain modules must import only
   `numpy` + stdlib. The protocol adapter lives only in `mission.py`.
4. **Determinism** — fixed seed, no wall-clock in persisted artifacts, no
   untracked RNG. Re-runs reproduce byte-identical results.
5. **No hardcoded metrics in prose** — every number flows through
   `manuscript_variables.generate_variables()` from the measured mission
   `execute()` output. Never hand-author a metric in `manuscript/*.md`.
6. **`output/` is disposable** — regenerable, git-ignored; change generators,
   never `output/` files.
7. **Thin scripts** — `scripts/*.py` only bootstrap sys.path and delegate to
   `src/`; no mathematical expressions that determine outputs.
8. **Path-scoped commits** — `git add -A` inside this repo only.

## Verification checklist (before "done")

```bash
# 1. Tests + coverage gate
uv run pytest tests/ --cov=src --cov-fail-under=90

# 2. Zero mocks
grep -rnE "MagicMock|@patch|create_autospec|unittest\\.mock" tests/ || echo Clean

# 3. Pure core is bond-api-free
grep -rln "bond_api" src/spectre/surveillance_net.py src/spectre/org_intel.py src/spectre/network_geometry.py || echo Clean

# 4. Ruff + mypy
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# 5. Lineage — no leftover template scaffold strings
rg -n "template[_]code_project" . --glob '!.git/**' --glob '!uv.lock' || echo Clean

# 6. git status clean after your commit(s)
```

## Reading order

1. This file (governs all modifications).
2. `docs/architecture.md` — boundary rules before touching `src/`/`scripts`.
3. `docs/testing_philosophy.md` — before writing or modifying any test file.
4. `manuscript/AGENTS.md` — before editing any manuscript section.

## Declared integration point

Provenance record persistence currently writes a plain JSON record from
`scripts/debrief.py`. When `bond-utilities.mission_io.record_provenance_outcome`
is wired as a dependency, `scripts/debrief.py` should delegate persistence to it
(the contract is documented in the BOND suite's bond-utilities phase-1 build).
