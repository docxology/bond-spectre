# docs — Spectre NINE EYES

Agent- and maintainer-facing documentation for the `spectre` BOND film package
(*Spectre*, 2015 — mission codename **NINE EYES**). Everything here describes
*this* package: the six pure domain modules, the frozen `bond_api` adapter, and
the measured-metrics discipline that keeps the manuscript honest.

| File | Purpose | Read it when |
| --- | --- | --- |
| [`AGENTS.md`](AGENTS.md) | How to work inside this package: change-routing table, the frozen `mission.py` surface, determinism rules, what gets a change rejected | Before any edit |
| [`agent_instructions.md`](agent_instructions.md) | Procedural layer: exact commands in order, environment setup, artifact regeneration, gates, commit discipline | While making the edit |
| [`architecture.md`](architecture.md) | Layer contract plus a module-by-module reference — every function in all six domain modules and what it computes; how `mission.py` implements the frozen `MissionProvider` | Before touching `src/` or `scripts/` |
| [`testing_philosophy.md`](testing_philosophy.md) | Zero-mock doctrine, real-data assertions, determinism as a tested property, the "no gate that cannot fail" rule, full test inventory | Before writing or changing a test |
| [`_generated/COUNTS.md`](_generated/COUNTS.md) | Live test count, achieved coverage, module/gadget/token inventories | To quote a number — regenerate it, never hand-edit |

Related documents outside this directory:

- [`../AGENTS.md`](../AGENTS.md) — the authoritative package rulebook.
- [`../README.md`](../README.md) — what the package is and how to run it.
- [`../TODO.md`](../TODO.md) — open work, accepted limitations, verification gates.
- [`../manuscript/AGENTS.md`](../manuscript/AGENTS.md) — the `{{TOKEN}}` protocol.
- [`../manuscript/SYNTAX.md`](../manuscript/SYNTAX.md) — citation, figure and token syntax.
- [`../data/claim_ledger.yaml`](../data/claim_ledger.yaml) — the recorded value of every measured claim.
