# Spectre — NINE EYES build log & roadmap

## Built

### Pure, deterministic domain core

- **`src/spectre/surveillance_net.py`** — Nine Eyes data-flow centralization:
  `build_network`, `network_from_adjacency`, `out/in_degree_centrality`,
  `group_centralization` (Freeman), `betweenness_centrality` (Brandes),
  `herfindahl_index`, `data_share_centrality` (normalized inflow shares),
  `uniform_share_index` (that index's even-spread floor), `cascade_coverage`
  (one seeded independent-cascade realization), `expected_cascade_coverage`
  (trial-averaged expectation), `sweep_coverage`.
- **`src/spectre/org_intel.py`** — SPECTRE criminal-org intelligence:
  `build_org`, `hierarchy_stats` (BFS apex reachability), `cell_membership`,
  `compartmentalization`, `command_reachability`, `exposure`.
- **`src/spectre/network_geometry.py`** — connectivity & critical nodes:
  `build_adjacency`, `connected_components`, `is_connected`,
  `articulation_points` (Tarjan), `all_pairs_shortest_paths`,
  `network_efficiency` (Latora–Marchiori), `node_removal_impact`,
  `robustness_curve`, `critical_node_order`.
- **`src/spectre/traffic_intel.py`** — traffic interception:
  `build_traffic_network`, `canonical_traffic_network`, `total_traffic`,
  `heavy_hitters`, `interception_coverage`, `monitor_allocation` (greedy
  submodular budget allocation, Nemhauser–Wolsey–Fisher, label-ordered
  tie-breaks).
- **`src/spectre/infiltration.py`** — compromise cascade:
  `simulate_compromise` (round-based percolation through cells + hierarchy,
  terminating without a round cap), `expected_damage` (fixed-seed trials: mean
  fraction, leadership hit rate, rounds to leadership).
- **`src/spectre/signal_cover.py`** — sensor-placement set cover:
  `build_coverage`, `canonical_coverage_problem`, `greedy_set_cover`
  (Johnson), `coverage_counts`, `uncovered_targets`, `redundancy_index`.

### Protocol, hydration, figures, scripts

- **`src/spectre/mission.py`** — FROZEN `bond_api.MissionProvider` adapter
  (brief/recon/plan/execute/debrief) over the canonical datasets; one plan step
  per domain module; measured results for all six analyses; gadget table
  published through `register_gadgets` with a `gadget_names()` reader;
  deterministic provenance (SHA-256 `input_hash`, `wall_time_s = 0.0`). Public
  protocol surface unchanged since phase 2.
- **`src/spectre/manuscript_variables.py`** — token hydration from config +
  measured mission output, with an injectable provider so the strict
  measured-metrics gate is exercisable, and `domain_module_names()` /
  `gadget_names()` so inventory counts in prose are measured, not typed.
- **`src/spectre/figures/networks.py`** — deterministic matplotlib
  flow-centralization figure.
- **`scripts/`** — thin per-phase CLIs: `brief.py`, `recon.py`, `plan.py`,
  `execute.py`, `debrief.py`, `generate_figures.py`,
  `z_generate_manuscript_variables.py`.

### Documentation & manuscript

- Root `README.md` (film→software mapping, every module, working commands,
  MissionProvider surface), `AGENTS.md` (rules + verify recipe), this file.
- `docs/`: `README.md` (index), `AGENTS.md` (change routing + frozen surface),
  `agent_instructions.md` (procedures), `architecture.md` (module-by-module),
  `testing_philosophy.md` (doctrine + inventory), `_generated/COUNTS.md`.
- `manuscript/`: sections `00`–`07` and `99`, plus `README.md`, `AGENTS.md`,
  `SYNTAX.md`, `preamble.md`, `config.yaml`, `references.bib` (real sources
  only: Freeman, Newman, Brandes, Tarjan, Hopcroft–Tarjan, Latora–Marchiori,
  Albert–Jeong–Barabási, Borgatti, Hirschman, Kempe–Kleinberg–Tardos,
  Nemhauser–Wolsey–Fisher, Leskovec et al., Johnson, Feige).

## Declared integration points

1. **Provenance persistence** — `scripts/debrief.py` writes a plain JSON
   record (`output/data/nine_eyes_debrief.json`). When `bond-utilities` is a
   declared dependency, delegate to
   `bond_utilities.mission_io.record_provenance_outcome(...)`.
   Acceptance: the written record carries `input_hash`, `schema_version`, and
   derived `seed`, and round-trips through `mission_io.load_record`.
2. **Fleet discovery** — the provider is discoverable via
   `bond_api.discovery.load_provider("spectre")` with `src/` on the search
   path; the orchestrator discovers the fleet automatically. No action needed.

## Remaining work

- [ ] **Wire `bond-utilities.mission_io`** for provenance persistence (point 1
      above). Blocked only on declaring the dependency; the record shape is
      already compatible.
- [ ] **Second figure** — the org cell structure and the compromise cascade are
      currently text-only in the results. A cell/cascade figure would need a new
      generator in `src/spectre/figures/`, a thin call in
      `scripts/generate_figures.py`, a test in `tests/test_figures.py`, and a
      figure reference row in `manuscript/SYNTAX.md`.
- [ ] **Weighted geometry** — the connectivity layer is unweighted while the
      traffic layer carries volumes; a volume-weighted efficiency and a
      volume-weighted critical-node score would let the two layers be compared
      rather than only reported side by side. Noted as a scope limit in
      `manuscript/07_scope_and_related_work.md`.
- [ ] **Adaptive adversary** — `critical_node_order` and `monitor_allocation`
      both optimize against a static structure. A rewiring response model would
      make the attack/defence results sequential rather than one-shot.
- [ ] **PDF render** — `manuscript/config.yaml` has every render format toggled
      off; the sections and `preamble.md` are render-ready but a build has not
      been exercised from this package.

## Gate history

- [x] Phase-2 gate: coverage ≥90%, ruff check+format, mypy, zero mocks, no
      exemplar leftovers, git clean, path-scoped commit.
- [x] Phase-4 deepen: three additional pure modules (traffic_intel,
      infiltration, signal_cover) + mission/token/manuscript/bib extension;
      protocol surface unchanged; gates re-verified.
- [x] Phase-5 docs/manuscript truth pass: full `docs/` baseline, manuscript
      sections `07` + `README`/`SYNTAX`/`preamble` added, prose reconciled with
      the deepened code, seven further real references, dead/unreachable
      branches removed or made testable, coverage raised to full line+branch on
      `src/`.
- [x] Phase-6 adversarial remediation: five SEVERE + six MODERATE verifier
      findings resolved. `data_share_centrality` was returning a 0/1 indicator
      (column self-normalization) — fixed to real inflow shares, which moved
      the reported HHI from 0.1250 to 0.1361 and exposed that the index sits
      just above its even-spread floor rather than corroborating hub dominance;
      the prose now says so. The figure title named the betweenness leader as
      "hub" while the text named the sending hub — both readings are now named
      and the sender is ringed. The cascade seed is plumbed through instead of
      recorded-but-ignored, and the cascade figure is a 50-trial mean rather
      than one Bernoulli draw. The brotherhood roster lost three alias nodes
      (Oberhauser = Blofeld; Hinx = Bautista = Mr Hinx). Hollow tests replaced
      with value pins re-derived from the edge list; the tautological inventory
      gate pinned to literals; the claim ledger extended from 11 rows to one
      per measured token and made an enforced gate.
