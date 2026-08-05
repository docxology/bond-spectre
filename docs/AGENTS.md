# docs/AGENTS.md — how to work inside the Spectre NINE EYES package

This file is the operating manual for an agent (or human) making changes to the
`spectre` BOND film package. The root [`../AGENTS.md`](../AGENTS.md) is the
authoritative rulebook; this file tells you *how to actually do the work* —
which surface to touch for a given kind of change, in what order, and what to
re-run afterwards.

## What this package is

`spectre` models the *Spectre* (2015) premises — the Nine Eyes global
surveillance-sharing programme and the SPECTRE brotherhood — as six pure,
deterministic analysis modules plus a thin adapter that publishes them to the
BOND fleet through the FROZEN `bond_api` `MissionProvider` protocol. Mission
codename: **NINE EYES**.

Nothing in this package is a stub. Every module computes a real quantity from a
real algorithm over the canonical dataset defined in `src/spectre/mission.py`.

## Change routing — where does my edit go?

| I want to… | Edit | Then re-run |
| --- | --- | --- |
| Change or add an algorithm | `src/spectre/<domain module>.py` | tests, then `scripts/z_generate_manuscript_variables.py` |
| Change what the mission *measures* | `src/spectre/mission.py` `execute()` | `scripts/debrief.py`, token gate, `data/claim_ledger.yaml` |
| Add a number to the manuscript | `src/spectre/manuscript_variables.py` (add the token) **then** the prose | `scripts/z_generate_manuscript_variables.py` |
| Add a gadget | `_GADGETS` in `src/spectre/mission.py` | `tests/test_mission.py` |
| Add a figure | `src/spectre/figures/` + a thin call in `scripts/generate_figures.py` | `scripts/generate_figures.py`, `tests/test_figures.py` |
| Add a CLI phase | `scripts/*.py` (thin only) | `tests/test_scripts_smoke.py` |
| Fix prose | `manuscript/NN_*.md` | the token cross-reference test |

Never invert that table. Business logic in `scripts/` and hand-authored metrics
in prose are the two failure modes this package is built to make impossible.

## The frozen surface — do not change its shape

`src/spectre/mission.py` is consumed *across packages* by `bond-cli`, the
coordinator's reconcile step, and the orchestrator. These names are frozen:

- `MissionProvider` (class name is fixed by the discovery contract) with
  `film`, `brief()`, `recon()`, `plan()`, `execute()`, `debrief()`;
- `PROVIDER` — the pre-built module-level instance discovery instantiates;
- `register_gadgets(registry)` — the Q-branch registration hook.

You may deepen freely *inside* these (more measured results, more plan steps,
more gadgets in `_GADGETS`). You may not rename them, change their arity, or
move them to another module. `tests/test_mission.py` asserts protocol
compliance and live discovery; if you break the shape, that test tells you
before the fleet does.

## Determinism rules

1. Every RNG is explicitly seeded (`_SEED` in `mission.py`, the `seed`
   parameter of `simulate_compromise`/`expected_damage`, the layout seed in
   `figures/networks.py`, the fixed cascade seed in `cascade_coverage`).
2. No wall-clock in persisted artifacts: `Provenance.wall_time_s` is `0.0` by
   construction. `GENERATION_TIMESTAMP` exists only in the hydrated manuscript,
   never in the mission record.
3. Iteration over sets is sorted before it can affect a result (see the
   cascade's `sorted(compromised)` and the greedy tie-breaks).
4. Re-running `scripts/debrief.py` twice must produce byte-identical
   `output/data/nine_eyes_debrief.json`. If it does not, you introduced
   non-determinism — find it before doing anything else.

## Working order for a substantive change

```bash
# 1. Change src/ (algorithm or mission) and extend tests/ in the same pass.
uv run pytest tests/ --cov=src --cov-fail-under=90

# 2. Re-measure: the mission is the only source of manuscript numbers.
uv run python scripts/debrief.py
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py

# 3. Reconcile the recorded claims with what was just measured.
#    data/claim_ledger.yaml values must match output/data/manuscript_variables.json.

# 4. Gates.
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# 5. Commit inside THIS repo only.
git add -A && git commit -m "spectre: <what changed>"
```

## Things that will get a change rejected

- A mock framework anywhere in `tests/` (`unittest.mock`, `MagicMock`,
  `mocker.patch`, `create_autospec`). A deterministic stand-in must implement
  the real protocol — see `_EmptyMission` in `tests/test_manuscript_variables.py`
  for the sanctioned pattern.
- A `bond_api` import in any of the six domain modules. `tests/test_domain_isolation.py`
  proves the core imports in a subprocess without `bond_api` on the path.
- A hand-typed number in `manuscript/*.md` prose.
- A guard or assertion that cannot fail (a validation branch unreachable from
  its only call site, a `try/except` that swallows, a test asserting only that
  a function returned). If you find one, delete it or make it reachable and
  test it — do not leave decoration behind.
- Editing anything under `output/` by hand. It is regenerated, git-ignored, and
  disposable.

## Reading order

1. [`../AGENTS.md`](../AGENTS.md) — the rulebook.
2. [`architecture.md`](architecture.md) — module-by-module boundaries.
3. [`testing_philosophy.md`](testing_philosophy.md) — before writing a test.
4. [`../manuscript/AGENTS.md`](../manuscript/AGENTS.md) — before editing prose.
