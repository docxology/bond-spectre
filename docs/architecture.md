# Architecture — Spectre NINE EYES

## Layer contract

| Layer | Modules | Imports allowed |
| --- | --- | --- |
| Pure core | `surveillance_net.py`, `org_intel.py`, `network_geometry.py`, `traffic_intel.py`, `infiltration.py`, `signal_cover.py` | `numpy`, stdlib only — **no** `bond_api`, **no** `infrastructure` |
| Adapter | `mission.py` | `bond_api.*` + the pure core |
| Hydration | `manuscript_variables.py` | config, `spectre.mission`, pure core |
| Figures | `figures/networks.py` | `matplotlib`, `numpy`, pure core |
| Scripts | `scripts/*.py` | `spectre.*`, `bond_api.*` (via sys.path bootstrap `_boot`) |
| Tests | `tests/*.py` | everything above, pytest-only |

Dependency arrow is one-directional: scripts → src; tests → src; nothing
imports upward. The pure core is the load-bearing freedom: it can be lifted
into any Python environment without `bond-api` or the BOND suite.

## Mission flow

`spectre.mission.MissionProvider` implements the FROZEN `bond_api` protocol:

```
brief() -> MissionBrief
recon(ReconRequest) -> ReconReport
plan(MissionBrief) -> MissionPlan
execute(MissionPlan) -> MissionOutcome   (measured results + Provenance)
debrief(MissionOutcome) -> Debrief
```

`execute()` runs the three concept analyses over the canonical dataset and
returns measured, JSON-serializable metrics with full provenance. Discovery
via `bond_api.discovery.load_provider("spectre")`.

## Forbidden patterns

- Any `bond_api` import inside the pure core modules.
- Mathematical logic in `scripts/` (that belongs in `src/`).
- Mock objects in tests.
- Hand-authoring a numeric metric in manuscript prose.
