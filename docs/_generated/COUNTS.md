# Spectre NINE EYES — live counts

Regenerate from the project root (do not hand-edit); read the values off the
real output of these commands:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 -q          # test count + coverage
uv run python scripts/z_generate_manuscript_variables.py       # token + section counts
uv run python -c "import sys; sys.path.insert(0,'src'); from spectre.manuscript_variables import domain_module_names; from spectre.mission import gadget_names, PROVIDER; print(len(domain_module_names()), len(gadget_names()), len(PROVIDER.plan(PROVIDER.brief()).steps))"
```

| Metric | Value |
| --- | --- |
| Test count | 189 |
| Coverage (line+branch on `src/`) | 100.00% |
| Statements / branches measured | 877 / 338 |
| Domain modules | 6 (infiltration, network_geometry, org_intel, signal_cover, surveillance_net, traffic_intel) |
| Mission stages | 5 (brief, recon, plan, execute, debrief) |
| Plan steps | 6 |
| Registered gadgets | 6 |
| Manuscript tokens | 40 |
| Manuscript sections resolved | 9 (00–07, 99) |
| Bibliography entries | 15 |

Measured on the run that produced the coverage table above. The module, gadget,
plan-step and token counts are additionally asserted live by
`tests/test_manuscript_variables.py::TestMeasuredInventories`, so drift between
the code and those rows fails the suite rather than sitting here quietly.
