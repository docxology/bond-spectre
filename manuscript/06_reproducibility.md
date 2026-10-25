# Reproducibility

## Deterministic regeneration

The entire artifact set regenerates byte-identical from a clean tree:

```bash
uv run python scripts/debrief.py              # runs the full mission
uv run python scripts/generate_figures.py     # writes both figures
uv run python scripts/z_generate_manuscript_variables.py  # hydrates tokens (runs LAST)
```

Each script recomputes its results from the fixed canonical dataset; there is
no stored intermediate that could drift from the code. The mission record,
figures and hydrated manuscript are written under `output/` (git-ignored,
regenerable).

The claim is scoped precisely. **Within one software environment**, two full
regenerations produce byte-identical `output/` artifacts — mission record,
figure PNGs, `manuscript_variables.json` and every hydrated section — because
hydration is a pure function of the committed tree: no wall clock, no untracked
RNG, no run counter. The single environment-dependent value is the interpreter
stamp printed at the end of this section (`{{PLATFORM}}`, `{{PYTHON_VERSION}}`),
which by construction is what changes when the environment changes; the
manuscript's date is `paper.date` from `manuscript/config.yaml`, a committed
input, not the time of the run. `tests/test_regeneration_determinism.py`
enforces the claim by regenerating the whole artifact set twice in one test
run, more than a wall-clock tick apart, and comparing SHA-256 digests file by
file — a re-introduced `datetime.now()` anywhere in the pipeline turns it red.

## Provenance

Execution provenance records the package version, the deterministic seed, and
the SHA-256 ``input_hash`` of the mission inputs — a canonical, key-sorted JSON
serialization of the agency network and the brotherhood — so any outcome can be
reproduced solely from its persisted record. `data/claim_ledger.yaml` carries
one row per measured manuscript token — the recorded value alongside the
function that produced it — and that coverage is enforced rather than asserted:
`tests/test_claim_ledger.py` compares the ledger against
`measured_tokens(generate_variables())` and fails on a measured token with no
row, a row for a token that is no longer measured, or a recorded value the code
no longer produces. The token partition is an exclusion list (only
configuration prose and the environment stamp are exempt), so a newly added
metric is covered automatically and exempting one takes a deliberate edit.

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

Release {{SPECTRE_VERSION}}, dated {{SPECTRE_RELEASE_DATE}} (from
`manuscript/config.yaml`), hydrated on {{PLATFORM}} with Python
{{PYTHON_VERSION}}.
