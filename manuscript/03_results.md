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
