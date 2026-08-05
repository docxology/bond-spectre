# Architecture — Spectre NINE EYES

## Layer contract

| Layer | Modules | Imports allowed |
| --- | --- | --- |
| Pure core | `surveillance_net.py`, `org_intel.py`, `network_geometry.py`, `traffic_intel.py`, `infiltration.py`, `signal_cover.py` | `numpy`, stdlib, and (for `infiltration`) the sibling `org_intel` — **no** `bond_api`, **no** `infrastructure` |
| Adapter | `mission.py` | `bond_api.*` + the pure core |
| Hydration | `manuscript_variables.py` | config, `spectre.mission`, pure core |
| Figures | `figures/networks.py` | `matplotlib`, `numpy`, pure core |
| Scripts | `scripts/*.py` | `spectre.*`, `bond_api.*` (via the `_boot` sys.path bootstrap) |
| Tests | `tests/*.py` | everything above, pytest only |

The dependency arrow is one-directional: scripts → src, tests → src; nothing
imports upward. The pure core is the load-bearing freedom — it can be lifted
into any Python environment without `bond-api` or the rest of the BOND suite,
and `tests/test_domain_isolation.py` proves it in a subprocess.

## The six domain modules, and what each one actually computes

### `surveillance_net.py` — data-flow shape of the Nine Eyes exchange

Models the sharing programme as a **directed** graph of agencies.

| Function | Computes |
| --- | --- |
| `build_network(nodes, edges)` | Validated `SurveillanceNetwork` from an edge list (rejects duplicate labels, unknown endpoints, self-loops) |
| `network_from_adjacency(nodes, matrix)` | The same network from a caller-supplied matrix; validates shape, label uniqueness and the diagonal, and copies the array |
| `out_degree_centrality` / `in_degree_centrality` | Volume each agency pushes downstream / pulls upstream |
| `group_centralization(scores)` | Freeman's group degree centralization `Σ(max − sᵢ) / ((n−1)·max)` in `[0, 1]` |
| `betweenness_centrality` | Brandes' algorithm (unweighted, directed): the share of shortest data paths through each agency |
| `herfindahl_index(values)` | HHI concentration `Σ shareᵢ²` over the normalized flow vector |
| `data_share_centrality` | Column-normalized inflow share per agency |
| `cascade_coverage(net, sources, p)` | Fixed-seed Bernoulli influence cascade from seed agencies; returns the reached set and the covered fraction |
| `sweep_coverage(captured, total)` | Fraction of a target population swept by at least one agency |

### `org_intel.py` — the SPECTRE brotherhood as a compartmentalized org

Models the criminal organisation as a cell partition plus a command tree.

| Function | Computes |
| --- | --- |
| `build_org(...)` | Validated `Brotherhood` (unique operatives, known superiors, no self-reporting, known leadership) |
| `hierarchy_stats` | Per-operative command depth, tree height, and how many operatives are reachable from the apex — reachability is a real BFS from leadership, so `chain_complete` means what it says even for a malformed, apex-less org |
| `cell_membership` | Cell id → ordered member tuple |
| `compartmentalization` | Fraction of cross-cell operative pairs with no direct command link (`1.0` = perfect separation) |
| `command_reachability` | BFS over `parent → subordinate` edges from the leadership apex |
| `exposure(org, operative)` | Who falls if one operative is turned: cellmates + direct superior + direct subordinates |

### `network_geometry.py` — bare connectivity and critical nodes

Treats the same network as **undirected** and asks what breaks it.

| Function | Computes |
| --- | --- |
| `build_adjacency` | Symmetric adjacency matrix from labelled edges |
| `connected_components` / `is_connected` | BFS flood-fill components |
| `articulation_points` | Tarjan low-link DFS: nodes whose removal disconnects the graph |
| `all_pairs_shortest_paths` | BFS all-pairs distances (unit weights) |
| `network_efficiency` | Latora–Marchiori global efficiency: mean inverse shortest-path length over ordered pairs |
| `node_removal_impact` | Fractional pairwise-connectivity loss when one node is deleted |
| `robustness_curve` | Giant-component fraction and component count after each step of a cumulative attack |
| `critical_node_order(adj, k)` | Greedy attack ordering — repeatedly delete the node that costs the *current* graph the most pairwise connectivity |

### `traffic_intel.py` — interception under a monitoring budget

Puts volumes on the links and asks how much of the exchange can be captured.

| Function | Computes |
| --- | --- |
| `build_traffic_network` | Volume-weighted directed matrix (accumulates repeated pairs; rejects negatives and self-loops) |
| `canonical_traffic_network` | The canonical Nine Eyes volume scenario used by the mission |
| `total_traffic` / `heavy_hitters(k)` | Total carried volume; top-`k` links by volume with deterministic tie-breaks |
| `interception_coverage(net, monitored)` | Fraction of traffic on links incident to any monitored agency |
| `monitor_allocation(net, budget)` | Greedy monotone-submodular maximization (Nemhauser–Wolsey–Fisher `1 − 1/e`): candidates scanned in sorted label order, so ties break by label |

### `infiltration.py` — the compromise cascade

The only domain module that composes another: it runs `org_intel.exposure`
round after round.

| Function | Computes |
| --- | --- |
| `simulate_compromise(org, seeds, p, seed)` | Round-based percolation: each round every compromised operative exposes their cell/superior/subordinates and each newly exposed operative turns with probability `p`. Returns the compromised set, rounds, fraction, whether leadership fell, and in which round. Terminates without a round cap because every non-terminal pass strictly grows the compromised set |
| `expected_damage(org, seeds, p, trials, seed)` | Mean fraction compromised, mean rounds, leadership-hit rate, and mean rounds-to-leadership over `trials` runs at derived seeds `seed + i` |

### `signal_cover.py` — sensor placement as set cover

| Function | Computes |
| --- | --- |
| `build_coverage` | Binary agency × target coverage matrix |
| `canonical_coverage_problem` | The canonical eight-target / six-agency placement scenario |
| `greedy_set_cover(problem, required_fraction)` | Johnson's greedy heuristic (`O(log n)` of optimum), label-ordered tie-breaks, stops when no remaining agency adds a target |
| `coverage_counts` | Per-target number of covering agencies |
| `uncovered_targets(problem, selected)` | The residual gaps of a placement |
| `redundancy_index(problem, selected)` | Fraction of targets swept by ≥ 2 selected agencies — resilience to losing one agency |

## How the pieces compose

```
surveillance_net ──┐                     (flows, centralization, cascade)
org_intel ─────────┼──> mission.execute() ──> MissionOutcome.results
network_geometry ──┤                            │
traffic_intel ─────┤                            ├──> manuscript_variables ──> {{TOKEN}}
infiltration ──────┤ (uses org_intel.exposure)  └──> scripts/debrief.py ──> output/data/*.json
signal_cover ──────┘
surveillance_net ──> figures/networks.py ──> output/figures/*.png
```

The domain modules are mutually independent with one deliberate exception:
`infiltration` builds on `org_intel.exposure`, because a compromise cascade is
literally the transitive closure of exposure. Everything else meets only in
`mission.execute()`.

## How `mission.py` implements the frozen `bond_api` MissionProvider

`mission.py` is the *only* module that imports `bond_api`. It holds the
canonical dataset (the nine agencies and their sharing links; the brotherhood
operatives, their cells, their command edges, and the apex), and it implements
the five frozen stages:

| Stage | Signature | What it does here |
| --- | --- | --- |
| `brief` | `() -> MissionBrief` | Declares film `spectre`, codename `NINE EYES`, three objectives (centralization, compartmentalization, critical nodes), three assets, and the determinism/no-mock constraints |
| `recon` | `(ReconRequest) -> ReconReport` | Surveys scale: node count, edge count, cell count, and echoes the caller's goal |
| `plan` | `(MissionBrief) -> MissionPlan` | Six steps — `flow_survey`, `org_intel`, `geometry`, `traffic_intel`, `infiltration`, `signal_cover` — each carrying the objective it serves |
| `execute` | `(MissionPlan) -> MissionOutcome` | Runs all six analyses over the canonical data and returns a JSON-serializable `results` dict plus `Provenance(package_version, seed, input_hash, wall_time_s=0.0)` |
| `debrief` | `(MissionOutcome) -> Debrief` | Three lessons summarizing centralization + interception, compartmentalization + mole risk, and critical nodes + cover size |

Supporting surface:

- `PROVIDER` — a module-level pre-built instance. `bond_api.discovery.load_provider("spectre")`
  finds `spectre.mission` and instantiates the exported `MissionProvider`.
- `register_gadgets(registry)` — publishes the Q-branch callables
  (`surveillance_centralization`, `org_compartmentalization`,
  `geometry_efficiency`, `traffic_interception`, `infiltration_damage`,
  `signal_set_cover`) from the private `_GADGETS` table.
- `gadget_names()` — the same table, sorted, so a documented gadget count is
  measured rather than typed.
- `_input_hash()` — canonical `json.dumps(..., sort_keys=True)` SHA-256 over the
  network and org definitions, recorded on every outcome.

The adapter contains no mathematics of its own: it selects data, calls the pure
core, and rounds for serialization. That is why the protocol can stay frozen
while the domain keeps deepening.

## Hydration path

`manuscript_variables.generate_variables()` drives the provider once, reads
`manuscript/config.yaml`, and returns the full `{{TOKEN}}` map. Two of its
inventories are *measured*, not typed: `domain_module_names()` lists the
package directory (minus `__init__`, `mission`, `manuscript_variables`), and
`gadget_names()` reads the registration table. The strict measured-metrics gate
is exercisable because the provider is injectable — a test passes a real
alternative runner that measures nothing and asserts the gate fires.

## Forbidden patterns

- Any `bond_api` import inside the pure core modules.
- Mathematical logic in `scripts/` (that belongs in `src/`).
- Mock objects in tests.
- Hand-authoring a numeric metric in manuscript prose.
- Validation branches unreachable from their only call site, or `except`
  blocks that swallow an error and continue.
