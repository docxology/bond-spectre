# Spectre — NINE EYES build log & roadmap

## Built (phase 2)

Pure, deterministic domain core modelling the three Spectre (2015) concepts:

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
- **`src/spectre/mission.py`** — FROZEN `bond_api.MissionProvider` adapter
  (brief/recon/plan/execute/debrief), canonical NINE EYES dataset, gadget
  registration, deterministic provenance.
- **`src/spectre/manuscript_variables.py`** — `{{TOKEN}}` hydration from
  config + measured mission output; strict cross-reference gate.
- **`src/spectre/figures/networks.py`** — deterministic PyPI-free
  (matplotlib-only) network flow-centralization figure.
- **`scripts/`** — thin per-phase CLIs: `brief.py`, `recon.py`, `plan.py`,
  `execute.py`, `debrief.py`, `generate_figures.py`,
  `z_generate_manuscript_variables.py`.

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
- [ ] (optional) Wire `bond-utilities.mission_io` provenance per point 1.
- [ ] (optional) Add a second figure (org cell-structure visualization).
