# tests/ — zero mocks, and the two gates that hold the boundaries

`conftest.py` and fifteen `test_*.py` modules: one per domain module, plus the cross-cutting gates.

## What each part holds

| Test module | Subject |
| --- | --- |
| `test_surveillance_net.py`, `test_org_intel.py`, `test_network_geometry.py` | The network and org models |
| `test_traffic_intel.py`, `test_infiltration.py`, `test_signal_cover.py` | The analysis modules |
| `test_manuscript_variables.py`, `test_figures.py` | Token hydration and figure rendering |
| `test_domain_isolation.py` | The gate on the pure core being importable standalone |
| `test_regeneration_determinism.py` | The gate on byte-identical regeneration |
| `test_claim_ledger.py` | The repository's own claims against the files |
| `test_sidecar_metadata.py` | The published sidecar metadata |
| `test_scripts_smoke.py` | Each CLI still runs |
| `test_mission.py` | The `bond_api` adapter — the integration surface |

## Rules

- **Zero mocks.** No `MagicMock`, `mocker.patch`, `unittest.mock` or `create_autospec` anywhere.
  A deterministic stand-in must implement the real protocol, as `_EmptyMission` in
  `test_manuscript_variables.py` does.
- **The gate is `uv run pytest tests/ --cov=src --cov-fail-under=90`** — 90% floor, line and branch.
- **`test_domain_isolation.py` is what keeps the core pure.** A new `bond_api` import outside
  `mission.py` fails here, so the rule is checked rather than trusted.
- **`test_regeneration_determinism.py` is the determinism gate**: re-running the generators must
  reproduce every `output/` file byte-identically.
- **`test_claim_ledger.py` reconciles the prose against the measured values.** A missing row, a stale
  row or a drifted number fails there; do not reconcile by eye.
- **No gate that cannot fail.** A validation branch unreachable from its only call site, or a test
  that asserts only that a call returned, is removed or made real. A new guard needs the test that
  fires it in the same pass.
- **`test_mission.py` is the module that needs the sibling `bond-api`.** The pure core's own tests run
  without it.
- **If the suite cannot import `bond_api` under `uv run pytest`,** run it as
  `uv run python -m pytest`: a stale console script left in `.venv/bin` by an earlier interpreter
  outlives that interpreter. Gate through the interpreter.
