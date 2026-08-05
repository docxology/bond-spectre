# Spectre — NINE EYES

Mission codename **NINE EYES**: the BOND film package for *Spectre* (2015). It
takes the film's two central premises — the Nine Eyes global surveillance-sharing
programme and the SPECTRE brotherhood — and implements them as six pure,
deterministic analysis modules behind one frozen mission protocol.

## Film → software

| Film concept | Software payload |
| --- | --- |
| The Nine Eyes intelligence-sharing pact, with one agency at the centre | A directed agency graph, measured for hub dominance (Freeman centralization), flow concentration (Herfindahl), pivotal position (Brandes betweenness), and how far a signal seeded at the hub reaches |
| SPECTRE as a brotherhood of isolated cells under an apex | A cell partition over a command tree, measured for compartmentalization, command-chain completeness, and per-operative exposure |
| "Remove the coordinating hub and the reach collapses" | Undirected connectivity geometry: articulation points, global efficiency, and a greedy critical-node attack ordering |
| Watching the exchange with limited means | A volume-weighted traffic network and a budgeted greedy monitoring allocation with a provable approximation bound |
| One turned operative unravels the organisation | A round-based compromise cascade over the exposure relation, with expected damage and leadership-hit statistics |
| Placing surveillance capability over a target set | Sensor placement as set cover, plus a multi-sensor redundancy measure |

## Modules

| Module | What it computes |
| --- | --- |
| `src/spectre/surveillance_net.py` | Directed agency network (from an edge list or a validated adjacency matrix), out/in-degree centrality, Freeman group centralization, Brandes betweenness, Herfindahl flow concentration, inflow-share centrality, fixed-seed influence cascade, sweep coverage |
| `src/spectre/org_intel.py` | Brotherhood construction and validation, command depths/height, BFS apex reachability, cell membership, cross-cell compartmentalization, per-operative exposure |
| `src/spectre/network_geometry.py` | Connected components, articulation points (Tarjan), all-pairs BFS distances, Latora–Marchiori global efficiency, node-removal impact, robustness-under-attack curve, greedy critical-node ordering |
| `src/spectre/traffic_intel.py` | Volume-weighted traffic network, total volume, heavy-hitter links, interception coverage of a monitored set, greedy submodular monitoring-budget allocation with label-ordered tie-breaks |
| `src/spectre/infiltration.py` | Round-based compromise cascade through the brotherhood, expected-compromise fraction, leadership hit rate, mean rounds to leadership over fixed-seed trials |
| `src/spectre/signal_cover.py` | Agency × target coverage matrix, greedy set cover (Johnson), per-target coverage counts, uncovered targets, multi-sensor redundancy index |
| `src/spectre/mission.py` | The FROZEN `bond_api` `MissionProvider` adapter + the canonical dataset + gadget registration (the only module that imports `bond_api`) |
| `src/spectre/manuscript_variables.py` | Computes every manuscript token from `manuscript/config.yaml` plus the measured mission output |
| `src/spectre/figures/networks.py` | Deterministic matplotlib flow-centralization figure |

Every metric in the manuscript is **measured** — computed by the deterministic
NINE EYES mission provider and injected through
`src/spectre/manuscript_variables.py`; no number is hand-authored in prose, and
even the module and gadget counts are read from the code rather than typed.

## Mission provider

`src/spectre/mission.py` implements the FROZEN `bond_api.MissionProvider`
protocol over the canonical Nine Eyes network and SPECTRE brotherhood:

| Stage | Surface | Yields |
| --- | --- | --- |
| `brief()` | `MissionBrief` | Film, codename, objectives, assets, determinism/no-mock constraints |
| `recon(ReconRequest)` | `ReconReport` | Node, edge and cell counts plus the caller's goal |
| `plan(MissionBrief)` | `MissionPlan` | One step per domain module |
| `execute(MissionPlan)` | `MissionOutcome` | All measured results + `Provenance` (version, seed, SHA-256 `input_hash`, `wall_time_s = 0.0`) |
| `debrief(MissionOutcome)` | `Debrief` | Standing lessons over the outcome |

Also exported: `PROVIDER` (the pre-built instance discovery instantiates) and
`register_gadgets(registry)` (publishes the Q-branch callables). The pure
domain core does **not** import `bond_api`, so it remains importable
standalone; the protocol contract is isolated in the thin adapter.

## Quickstart

```bash
cd projects/working/bond/spectre
uv sync --extra dev                    # install deps + the frozen bond-api path dep
uv run pytest tests/ --cov=src --cov-fail-under=90

uv run python scripts/brief.py         # mission phase CLIs: brief/recon/plan/execute/debrief
uv run python scripts/execute.py
uv run python scripts/debrief.py       # full run; writes output/data/nine_eyes_debrief.json
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py   # hydrate manuscript tokens (last)
```

`uv` cannot write its cache under a restrictive sandbox; a
`Failed to initialize cache` error is an environment restriction, not a package
failure — re-run with the sandbox disabled.

## Science

- **Deterministic**: fixed seeds (cascade activation, compromise trials, figure
  layout), label-ordered tie-breaking in both greedy selections, no wall-clock
  in persisted artifacts (`Provenance.wall_time_s == 0.0`), canonical SHA-256
  `input_hash`. Two runs of `scripts/debrief.py` produce byte-identical records.
- **Zero mocks**: all tests use real data structures and real computation. Where
  a test needs an alternative implementation it writes a real object satisfying
  the real protocol.
- **Infrastructure-free core**: `numpy` + stdlib only in the six domain modules;
  safe to lift into any environment.
- **No gate that cannot fail**: validation branches unreachable from their call
  sites were removed or made reachable and tested.

## Gates

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90   # >=90% line+branch on src/
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

Achieved coverage and the live test count are recorded in
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md), regenerated from a
real run — this README states the gate, not a figure that can go stale.

## Documentation

- [`AGENTS.md`](AGENTS.md) — the package rulebook.
- [`docs/`](docs/README.md) — architecture, agent instructions, testing philosophy.
- [`manuscript/`](manuscript/README.md) — the publication surface and token protocol.
- [`TODO.md`](TODO.md) — build log and remaining work.
- [`data/claim_ledger.yaml`](data/claim_ledger.yaml) — every measured claim and its source.

Local-only working tree — this package is part of the BOND suite and is never
pushed to any remote.
