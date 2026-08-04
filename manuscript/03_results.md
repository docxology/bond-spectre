# Results

## Surveillance-network centralization

The NINE EYES network comprises {{SPECTRE_NUM_NODES}} agencies and
{{SPECTRE_NUM_EDGES}} directed data-sharing links. The measured group
centralization index is {{SPECTRE_CENTRALIZATION_INDEX}}, indicating that the
flows concentrate strongly around a hub agency; the independent Herfindahl
flow-concentration measure is {{SPECTRE_FLOW_CONCENTRATION_HHI}}. A signal
seeded at the hub propagates to {{SPECTRE_CASCADE_COVERAGE}} of the network in
the fixed cascade model — the surveillance footprint of a single hub.

![The Nine Eyes agency network: node size is betweenness centrality, arrows are data flows.](figures/network_flow_centralization.png){#fig:network_flow_centralization}

## Criminal-org cell model

The {{SPECTRE_NUM_OPERATIVES}} brotherhood operatives are partitioned into
{{SPECTRE_NUM_CELLS}} cells. The organization's command chain is complete
({{SPECTRE_CHAIN_COMPLETE}}) with a hierarchy height of
{{SPECTRE_HIERARCHY_HEIGHT}} links. Cell compartmentalization measures
{{SPECTRE_COMPARTMENTALIZATION}}: the brotherhood keeps a high (but
imperfect) degree of separation between its cells.

## Network geometry

The canonical network is connected and has {{SPECTRE_NUM_ARTICULATION_POINTS}}
articulation points ({{SPECTRE_ARTICULATION_NODES}}) whose removal would
disconnect it, and a global efficiency of {{SPECTRE_NETWORK_EFFICIENCY}}. The
greedy critical-node ordering identifies
{{SPECTRE_CRITICAL_NODES}} as the agencies whose neutralization most fragments
the network. In the film, removing exactly this coordinating hub collapses the
brotherhood's reach — the model reproduces that dependence quantitatively.

## Traffic interception (deepening)

The canonical exchange carries {{SPECTRE_TRAFFIC_TOTAL}} volume units; the
single largest flow is {{SPECTRE_TRAFFIC_TOP_LINK}}, confirming the hub's
dominance. Greedy budgeted monitoring selects {{SPECTRE_MONITOR_ALLOCATION}},
and monitors {{SPECTRE_MONITOR_COVERAGE}} of all traffic with just three
agencies — a demonstration of diminishing marginal returns that motivates the
submodular formulation.

## Compromise cascade (deepening)

Turning a single cell operative causes an expected
{{SPECTRE_COMPROMISE_FRACTION}} of the brotherhood to fall within the cascade;
leadership is reached with probability {{SPECTRE_LEADERSHIP_HIT_RATE}} after a
mean of {{SPECTRE_MEAN_STEPS_TO_LEADERSHIP}} rounds. The model quantifies why a
compartmentalized brotherhood guards its cells: any cell breach is a vector
straight to the apex.

## Sensor-placement cover (deepening)

The greedy set cover places {{SPECTRE_SET_COVER_SIZE}} agencies
({{SPECTRE_SET_COVER_SELECTION}}) to sweep the full target set, leaving
{{SPECTRE_UNCOVERED_AFTER_COVER}} targets uncovered. The resulting multi-sensor
redundancy is {{SPECTRE_COVER_REDUNDANCY}} — the fraction of targets swept by at
least two agencies, i.e. the resilience of the sweep to the loss of a single
agency.
