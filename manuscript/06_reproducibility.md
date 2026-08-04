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
figure are written under `output/` (git-ignored, regenerable).

## Provenance

Execution provenance records the package version, the deterministic seed, and
the SHA-256 ``input_hash`` of the mission inputs, so any outcome can be
reproduced solely from its persisted record.

## Gates

* `uv run pytest tests/ --cov=src --cov-fail-under=90` — the coverage gate
* `uv run ruff check src/ scripts/ tests/` and `uv run ruff format --check`
* `uv run mypy src/ scripts/`
* zero mocks anywhere in `tests/`; pure domain core has no `bond_api` import

Generated at {{GENERATION_TIMESTAMP}} on {{PLATFORM}} with Python
{{PYTHON_VERSION}}.
