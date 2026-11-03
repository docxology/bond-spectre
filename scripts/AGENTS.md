# scripts/ — the NINE EYES phase CLIs and the generator that runs last

`_boot.py`, the five phase CLIs `brief.py`, `recon.py`, `plan.py`, `execute.py`, `debrief.py`,
`generate_figures.py`, and `z_generate_manuscript_variables.py`.

## Rules

- **Thin orchestrators.** Every CLI bootstraps `sys.path` through `_boot.py` and dispatches into
  `src/spectre/`. No business logic belongs here.
- **`_boot.py` is the single bootstrap.** A new script imports it rather than repeating a path
  calculation; a second copy of that logic is a defect.
- **`z_generate_manuscript_variables.py` runs LAST**, after the mission has produced the results it
  derives tokens from. Running it first yields tokens from stale or absent measurements.
- **`generate_figures.py` writes deterministic figures.** Same inputs, same bytes.
- **Exit codes are the report.** A phase that failed exits non-zero; never describe it as done.
- **Scope is this repository.** Never write into sibling BOND packages, the bond root, or the
  template repository.
- `ruff` and `mypy` are clean on this directory, as on `src/`.
