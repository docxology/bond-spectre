# Spectre — NINE EYES build log & roadmap

## Built

### Pure, deterministic domain core (phase 2 — three concepts)

- **`src/spectre/surveillance_net.py`** — Nine Eyes data-flow centralization:
  `build_network`, `out/in_degree_centrality`, `group_centralization`
  (Freeman), `betweenness_centrality` (Brandes), `herfindahl_index`,
  `data_share_centrality`, `cascade_coverage` (deterministic influence
  cascade), `sweep_coverage`.
- **`src/spectre/org_intel.py`** — SPECTRE criminal-org intelligence:
  `build_org`, `hierarchy_stats`, `cell_membership`, `compartmentalization`,
  `command_reachability`, `exposure`.
- **`src/spectre/network_geometry.py`** — connectivity & critical nodes:
  `build_adjacency`, `connected_components`, `is_connected`,
  `articulation_points` (Tarjan), `all_pairs_shortest_paths`,
  `network_efficiency`, `node_removal_impact`, `robustness_curve`,
  `critical_node_order`.

### Deepened analysis (phase 4 — three more algorithms)

- **`src/spectre/traffic_intel.py`** — traffic interception:
  `build_traffic_network`, `canonical_traffic_network`, `total_traffic`,
  `heavy_hitters`, `interception_coverage`, `monitor_allocation` (greedy
  submodular budget allocation, Nemhauser–Wolsey–Fisher).
- **`src/spectre/infiltration.py`** — compromise cascade:
  `simulate_compromise` (round-based percolation through cells + hierarchy),
  `expected_damage` (fixed-seed trials: mean fraction, leadership hit rate,
  steps to leadership).
- **`src/spectre/signal_cover.py`** — sensor-placement set cover:
  `build_coverage`, `canonical_coverage_problem`, `greedy_set_cover`
  (Johnson), `coverage_counts`, `uncovered_targets`, `redundancy_index`.

- **`src/spectre/mission.py`** — FROZEN `bond_api.MissionProvider` adapter
  (brief/recon/plan/execute/debrief) over the canonical datasets; 6-step plan;
  deepened measured results (interception coverage, compromise damage, cover
  redundancy); 6 registered gadgets; deterministic provenance. Public protocol
  surface unchanged.
- **`src/spectre/manuscript_variables.py`** — `{{TOKEN}}` hydration (35 tokens)
  from config + measured mission output; strict cross-reference gate.
- **`src/spectre/figures/networks.py`** — deterministic matplotlib
  flow-centralization figure.
- **`scripts/`** — thin per-phase CLIs: `brief.py`, `recon.py`, `plan.py`,
  `execute.py`, `debrief.py`, `generate_figures.py`,
  `z_generate_manuscript_variables.py`.
- **`manuscript/references.bib`** — real sources: Freeman 1979, Newman 2010,
  Brandes 2001, Tarjan 1972, Nemhauser 1978, Johnson 1974, Feige 1998,
  Newman 2002.

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

## Roadmap

- [x] Phase-2 gate: pytest `--cov-fail-under=90`, ruff check+format, mypy, zero
      mocks, `template[_]code_project` rg → zero, git clean, path-scoped commit.
- [x] Phase-4 deepen: three new pure modules (traffic_intel, infiltration,
      signal_cover) + mission/token/manuscript/bib extension; protocol surface
      unchanged; gates re-verified.
- [ ] (optional) Wire `bond-utilities.mission_io` provenance per point 1.
- [ ] (optional) Add a second figure (org cell-structure / compromise cascade).
