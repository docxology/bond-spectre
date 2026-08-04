# Testing philosophy — Spectre NINE EYES

## Zero-mock policy

All tests use **real data structures and computation** — no `unittest.mock`,
`MagicMock`, `@patch`, or `create_autospec`. Deterministic behavior comes from
real deterministic code, not fakes. The pure core is tested directly; the
`mission.py` adapter is tested through the real `bond_api` protocol types and a
live discovery test.

## Coverage

The enforced gate is **≥90% line+branch on `src/`**:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Live test count and achieved coverage are tracked in
`_generated/COUNTS.md`.

## Test inventory

| File | Covers |
| --- | --- |
| `test_surveillance_net.py` | centrality, centralization, HHI, betweenness, cascade, sweep + all error branches |
| `test_org_intel.py` | hierarchy, cells, compartmentalization, reachability, exposure + validation errors |
| `test_network_geometry.py` | connectivity, articulation points, efficiency, robustness, critical order + errors |
| `test_mission.py` | protocol compliance, determinism, provenance, gadgets, discovery |
| `test_manuscript_variables.py` | config loading, token map, live `{{TOKEN}}` cross-reference, tree resolution |
| `test_figures.py` | figure PNG writing + empty-network error |
| `test_scripts_smoke.py` | subprocess execution of every CLI with artifact assertions |

## Error-branch principle

Every `ValueError`/`FileNotFoundError` raised in `src/` is exercised by at
least one test — validation and boundary branches are first-class coverage, not
incidental.
