# Agent instructions — Spectre NINE EYES

Concrete operating instructions for this package. The authoritative rules are
in the root [`../AGENTS.md`](../AGENTS.md); the change-routing table and the
frozen-surface contract are in [`AGENTS.md`](AGENTS.md); the module-by-module
reference is in [`architecture.md`](architecture.md). This file is the
*procedural* layer: exact commands, in order, with what each one proves.

## 0. Environment

```bash
uv sync --extra dev      # installs numpy/matplotlib/pyyaml + the local bond-api path dep
```

Run from the repository root: this standalone clone *is* the package (in the
BOND suite it lives at `projects/working/bond/spectre`).

`bond-api` is a **path dependency** pinned in `pyproject.toml` under
`[tool.uv.sources]`, and the pinned path is inside the suite monorepo, so a
standalone clone cannot resolve it. If the sibling `bond-api` package moves,
`uv sync` fails loudly — that is intended; do not vendor a copy to work around
it, and do not repoint the pin at a registry or a non-existent repository. The
six domain modules never import it, so tests on the pure core keep working even
while the protocol package is being rebuilt.

Without a suite checkout that pin cannot resolve, and the gates are still
runnable: create a throwaway env **outside** the repo, install
`numpy matplotlib pyyaml pytest pytest-cov ruff mypy` into it, put `<repo>/src`
plus a `bond_api` (from the suite checkout or the uv cache) on `PYTHONPATH`, and
run the commands below from the repository root. Re-measured that way on
2026-10-25 (CPython 3.14.9, numpy 2.4.2, mypy 2.3.0, ruff 0.16.1): **271
passed**, 100.00% line+branch (999 statements, 396 branches), mypy clean on 19
files, `ruff format --check --line-length 120` clean on 34 files.

If a `uv` command fails with `Failed to initialize cache` or
`Operation not permitted`, that is a sandbox restriction, not a package
failure. Re-run the same command with the sandbox disabled.

## 1. Layer boundaries (enforced, not advisory)

```
src/spectre/
  surveillance_net.py   -- PURE  flows, centrality, centralization, cascade, sweep
  org_intel.py          -- PURE  hierarchy, cells, compartmentalization, exposure
  network_geometry.py   -- PURE  components, articulation points, efficiency, critical nodes
  traffic_intel.py      -- PURE  volume network, heavy hitters, interception, budgeted monitoring
  infiltration.py       -- PURE  compromise cascade, expected damage  (composes org_intel.exposure)
  signal_cover.py       -- PURE  coverage matrix, greedy set cover, redundancy, gaps
  mission.py            -- ADAPTER (the only bond_api importer)  FROZEN MissionProvider + gadgets
  manuscript_variables.py -- config + measured mission -> {{TOKEN}} map
  figures/networks.py   -- matplotlib figure generator (seeded layout)
scripts/*.py            -- thin orchestrators (sys.path bootstrap via _boot)
tests/*.py              -- zero mocks, real data + computation
```

**Purity rule**: the six domain modules import only `numpy` + the standard
library (`infiltration` additionally imports `org_intel`, which is itself
pure). The `bond_api` contract is confined to `mission.py` and the tests that
exercise it. Verify with:

```bash
uv run python -c "import sys; sys.path.insert(0, 'src'); import spectre.signal_cover; print('pure core imports clean')"
grep -l "bond_api" src/spectre/*.py     # must print only src/spectre/mission.py
```

`tests/test_domain_isolation.py` makes the same proof in a subprocess with
`bond_api` unavailable — do not weaken it.

## 2. Adding an algorithm

1. Write it in the relevant domain module (or a new pure module) with full type
   hints, a docstring naming the algorithm and its guarantee, and an explicit
   `Raises:` section for every validation branch.
2. Export it in that module's `__all__`.
3. Add tests in the matching `tests/test_<module>.py`, including every error
   branch and at least one degenerate-size case (empty, single element,
   disconnected).
4. If the mission should *report* it, add the call in `mission.execute()` and a
   key in the `results` dict — round floats there, not in the pure core.
5. If it appears in the manuscript, add a token in
   `manuscript_variables.generate_variables()` and reference `{{TOKEN}}` in prose.

New pure module? `domain_module_names()` picks it up from the directory
listing automatically, so `{{SPECTRE_NUM_DOMAIN_MODULES}}` stays correct with
no edit — that is deliberate.

## 3. Regenerating measured artifacts

Order matters: hydration runs **last**, because it re-measures the mission.

```bash
uv run python scripts/brief.py        # mission declaration
uv run python scripts/recon.py        # survey findings
uv run python scripts/plan.py         # the six planned steps
uv run python scripts/execute.py      # measured results + provenance
uv run python scripts/debrief.py      # full run; writes output/data/nine_eyes_debrief.json
uv run python scripts/generate_figures.py                 # output/figures/*.png
uv run python scripts/z_generate_manuscript_variables.py  # tokens + output/manuscript/
```

Then reconcile `data/claim_ledger.yaml`: every `value:` there must equal the
corresponding entry in `output/data/manuscript_variables.json`. The ledger is
the human-readable record of what the package currently claims; a stale ledger
is a silent lie, so update it in the same commit as the metric change.

## 4. Required gates before calling anything done

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90   # ≥90% line+branch on src/
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
grep -rnE "MagicMock|@patch|create_autospec|unittest\.mock" tests/ || echo "no mocks"
git status --short                                   # clean after your commit
```

The achieved coverage and test count are recorded in
[`_generated/COUNTS.md`](_generated/COUNTS.md) — regenerate that file from a
real run rather than editing the numbers.

`ruff` is the one gate this repo does not fully declare: there is no
`[tool.ruff]` table here, so the rule selection and line length come from the
BOND suite root. A standalone clone must pass the shared line length explicitly
(`ruff check --line-length 120 src/ scripts/ tests/` — the default rule set then
reports findings that root's narrower `select` excludes, such as `RUF100` on the
required `# noqa: E402` bootstrap lines). `ruff format --check --line-length 120
src/ scripts/ tests/` is portable as-is — it is clean across `src/`, `scripts/`
and `tests/`, and it prints its own file count rather than quoting one here.

## 5. Determinism checks

```bash
uv run python scripts/debrief.py && cp output/data/nine_eyes_debrief.json /tmp/run1.json
uv run python scripts/debrief.py && diff /tmp/run1.json output/data/nine_eyes_debrief.json && echo "deterministic"
```

Any difference is a defect. The usual causes are an unseeded RNG, iteration
over an unsorted set that reaches a result, or a wall-clock value leaking into
a persisted artifact.

## 6. Commit discipline

Path-scoped, inside this repository only:

```bash
git add -A && git commit -m "spectre: <what changed and why>"
```

This repository is the **published snapshot** of the suite package
(`github.com/docxology/bond-spectre`), so commits here are pushed normally —
never force-pushed and never history-rewritten. The BOND suite's own working
tree is the local-only one. Never touch a sibling BOND package, the suite root
files, or the template repository.
