# src/ — six pure domain modules, one adapter, and the derivation layer

`src/spectre/`, the installable package. The split here is enforced, not stylistic.

## Layout

| Module | What it does |
| --- | --- |
| `surveillance_net.py` | The Nine Eyes surveillance network and its coverage |
| `org_intel.py` | The SPECTRE org cell model |
| `network_geometry.py` | Network geometry |
| `traffic_intel.py` | Traffic interception analysis |
| `infiltration.py` | Compromise cascades (imports the pure `org_intel`) |
| `signal_cover.py` | Sensor-placement cover |
| `figures/` | Matplotlib figure generators with a deterministic seed |
| `mission.py` | The **only** module importing `bond_api`; implements the frozen `MissionProvider` |
| `manuscript_variables.py` | Computes every `{{TOKEN}}` from config plus the measured mission results |

## Rules

- **The six domain modules import `numpy` and the standard library only.** No `bond_api`, no
  infrastructure, no hidden I/O. `grep -l bond_api src/spectre/*.py` must list `mission.py` alone.
- **The frozen provider surface must not be renamed or re-shaped** — `MissionProvider` with
  `film`, `brief()`, `recon()`, `plan()`, `execute()`, `debrief()`; the module-level `PROVIDER`;
  and `register_gadgets(registry)`. `bond-cli`, the coordinator's reconcile step and the orchestrator
  consume those names. Deepen inside them.
- **Determinism is a property of the code, not of a run.** Fixed seeds, label-ordered greedy
  tie-breaks, and no wall-clock in any persisted artifact — including the hydrated manuscript, whose
  date is the committed `paper.date`, never `datetime.now()`. `tests/test_regeneration_determinism.py`
  is the gate.
- **No hardcoded metrics in prose.** Every number flows from the measured mission `execute()` output
  through `generate_variables()`; even module and gadget inventories are measured from the code.
- **`output/` is disposable.** Change a generator, never a file under `output/`.
- **Type hints and docstrings throughout**; `ruff` and `mypy` are clean here.
