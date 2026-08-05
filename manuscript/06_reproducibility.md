# Reproducibility

## Deterministic regeneration

The entire artifact set regenerates byte-identical from a clean tree:

```bash
uv run python scripts/debrief.py              # runs the full mission
uv run python scripts/generate_figures.py     # writes the network figure
uv run python scripts/z_generate_manuscript_variables.py  # hydrates tokens (runs LAST)
```

Each script recomputes its results from the fixed canonical dataset; there is
no stored intermediate that could drift from the code. The mission record and
figure are written under `output/` (git-ignored, regenerable). Running
`scripts/debrief.py` twice and diffing
`output/data/nine_eyes_debrief.json` is the determinism check — any difference
is a defect, not a tolerance.

## Provenance

Execution provenance records the package version, the deterministic seed, and
the SHA-256 ``input_hash`` of the mission inputs — a canonical, key-sorted JSON
serialization of the agency network and the brotherhood — so any outcome can be
reproduced solely from its persisted record. `data/claim_ledger.yaml` carries
the current value of every measured claim alongside the function that produced
it, and is reconciled against `output/data/manuscript_variables.json` whenever
a metric changes.

## No hand-authored numbers

Every quantity in this manuscript is an injected token resolved by
`src/spectre/manuscript_variables.py` from the measured mission output. Two
tests keep that honest: a live cross-reference test fails if any token used in
prose is missing from the generator, and strict resolution fails if any token
survives substitution. Even the package's own inventories — module count,
gadget count, plan length — are measured from the code rather than typed.

## Gates

* `uv run pytest tests/ --cov=src --cov-fail-under=90` — the coverage gate
  (line **and** branch, enforced on `src/`)
* `uv run ruff check src/ scripts/ tests/` and `uv run ruff format --check`
* `uv run mypy src/ scripts/`
* zero mocks anywhere in `tests/`; the pure domain core has no `bond_api`
  import, proven by a subprocess import test

The achieved coverage and test count from the last real run are recorded in
`docs/_generated/COUNTS.md`; this manuscript deliberately does not restate them,
because a number quoted in prose is a number that can go stale.

Generated at {{GENERATION_TIMESTAMP}} on {{PLATFORM}} with Python
{{PYTHON_VERSION}}.
