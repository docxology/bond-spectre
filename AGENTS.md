# Spectre — NINE EYES (agent instructions)

## Scope & identity

- **Package**: `spectre` — BOND film package for *Spectre* (2015), mission
  codename **NINE EYES**.
- **Scope**: exactly this repository. Never touch sibling BOND packages, the
  suite root files, or the template repo.
- **Published snapshot**: `origin` is `github.com/docxology/bond-spectre`, the
  public snapshot of this suite package; the suite's own working tree stays
  local-only. Commits here are path-scoped (rule 9) and pushed normally —
  never force-pushed, never history-rewritten.

## Layout contract

| Surface | Rule |
| --- | --- |
| `src/spectre/surveillance_net.py`, `org_intel.py`, `network_geometry.py`, `traffic_intel.py`, `infiltration.py`, `signal_cover.py` (pure domain core) | `numpy` + stdlib only (`infiltration` also imports the pure `org_intel`); **no** `bond_api` import; deterministic; importable standalone |
| `src/spectre/mission.py` | The only module that imports `bond_api`; implements the FROZEN `MissionProvider`; publishes gadgets via `register_gadgets` |
| `src/spectre/manuscript_variables.py` | Computes every `{{TOKEN}}` from config + the measured mission results |
| `src/spectre/figures/` | Matplotlib figure generators (deterministic seed) |
| `scripts/` | Thin orchestrators (sys.path bootstrap via `_boot`); no business logic |
| `tests/` | Zero mocks; real data + computation; the standalone-importable core tested separately |

## Non-negotiable rules

1. **No mock framework** — no `MagicMock` / `mocker.patch` / `unittest.mock` /
   `create_autospec` anywhere. A deterministic stand-in must implement the real
   protocol (see `_EmptyMission` in `tests/test_manuscript_variables.py`).
2. **≥90% line+branch coverage on `src/`**:
   `uv run pytest tests/ --cov=src --cov-fail-under=90`.
3. **Pure core is bond_api-free** — the six domain modules import only `numpy`
   + stdlib. The protocol adapter lives only in `mission.py`.
4. **Determinism** — fixed seeds, label-ordered greedy tie-breaks, no wall-clock
   in *any* persisted artifact (the hydrated manuscript included: the date is
   the committed `paper.date`, never `datetime.now()`), no untracked RNG.
   Within one software environment, re-running the three generator scripts
   reproduces every `output/` file byte-identically;
   `tests/test_regeneration_determinism.py` is the gate.
5. **No hardcoded metrics in prose** — every number flows through
   `manuscript_variables.generate_variables()` from the measured mission
   `execute()` output. Never hand-author a metric in `manuscript/*.md`. This
   includes counts of the package's own parts: module and gadget inventories are
   measured from the code.
6. **No gate that cannot fail** — a validation branch unreachable from its only
   call site, an `except` that swallows, or a test that asserts only that a call
   returned, must be removed or made real. If you add a guard, add the test that
   fires it in the same pass.
7. **`output/` is disposable** — regenerable, git-ignored; change generators,
   never `output/` files.
8. **Thin scripts** — `scripts/*.py` only bootstrap sys.path and delegate to
   `src/`; no mathematical expressions that determine outputs.
9. **Path-scoped commits** — `git add -A` inside this repo only.

## Frozen cross-package surface

`bond-cli`, the coordinator's reconcile step, and the orchestrator consume
these names. Deepen inside them; never rename or re-shape them:

- `MissionProvider` with `film`, `brief()`, `recon()`, `plan()`, `execute()`,
  `debrief()`;
- `PROVIDER` — the module-level pre-built instance;
- `register_gadgets(registry)` — the Q-branch registration hook.

## Build & verify

```bash
# Install (bond-api is a local path dependency declared in pyproject.toml; the
# pinned path lives in the BOND suite monorepo, so a standalone clone cannot
# resolve it — the pure core still imports and tests without it)
uv sync --extra dev

# 1. Tests + coverage gate (line AND branch on src/)
uv run pytest tests/ --cov=src --cov-fail-under=90

# 2. Zero mocks
grep -rnE "MagicMock|@patch|create_autospec|unittest\.mock" tests/ || echo Clean

# 3. Pure core is bond-api-free (must list only mission.py)
grep -l "bond_api" src/spectre/*.py

# 4. Ruff + mypy
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# 5. Regenerate measured artifacts (hydration LAST)
uv run python scripts/debrief.py
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py
#    Ledger reconciliation is enforced by tests/test_claim_ledger.py (part of
#    step 1), not by eye: a missing row, a stale row, or a drifted value fails
#    there. The script step above only regenerates the artifacts it compares.

# 6. Determinism spot-check
uv run python scripts/debrief.py && cp output/data/nine_eyes_debrief.json /tmp/run1.json
uv run python scripts/debrief.py && diff /tmp/run1.json output/data/nine_eyes_debrief.json

# 7. Lineage — no leftover exemplar scaffold strings
grep -rn "template_code_project" . --exclude-dir=.git --exclude-dir=.venv --exclude=uv.lock || echo Clean

# 8. git status clean after your commit(s)
```

If a `uv` command reports `Failed to initialize cache` or
`Operation not permitted`, that is a sandbox restriction rather than a package
failure — re-run it with the sandbox disabled.

## Reading order

1. This file (governs all modifications).
2. `docs/AGENTS.md` — change routing, frozen surface, rejection criteria.
3. `docs/architecture.md` — module-by-module boundaries, before touching `src/`.
4. `docs/testing_philosophy.md` — before writing or modifying any test file.
5. `manuscript/AGENTS.md` and `manuscript/SYNTAX.md` — before editing prose.

## Declared integration point

Provenance record persistence currently writes a plain JSON record from
`scripts/debrief.py`. When `bond-utilities.mission_io.record_provenance_outcome`
is wired as a dependency, `scripts/debrief.py` should delegate persistence to it
(the contract is documented in the BOND suite's bond-utilities phase-1 build).
