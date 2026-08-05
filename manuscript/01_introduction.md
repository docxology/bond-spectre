# Introduction

The Nine Eyes programme — a global surveillance-sharing arrangement among a
handful of Western intelligence agencies — is the geometric setting of the
2015 film *Spectre*. The NINE EYES mission software package renders that
setting as a computational model answering six intelligence questions, three
structural and three operational.

The structural questions ask what the network and the organisation *are*:

1. **How centralized are surveillance data flows?** If a single agency sits at
   the hub of every sharing link, the network is highly centralized and a
   single compromised hub exposes the whole exchange. Sending and receiving
   are separate readings and need not agree: a lone source can dominate the
   out-degree while its recipients each receive a comparable trickle, so an
   out-degree centralization index and an inflow-share concentration index are
   two measurements, not one measurement corroborated twice.
2. **How is a criminal brotherhood structured?** SPECTRE is a compartmentalized
   organization: isolated cells whose members know only their own cell,
   underneath an apex leadership. The intelligence question is how "separable"
   the cells are and whether the command chain is complete.
3. **Which nodes are critical to the network's geometry?** Connectivity,
   articulation points, and global efficiency identify the agencies whose
   removal most fragments the system. These are the priority targets for
   neutralization.

The operational questions ask what can be *done* with that structure:

4. **Where should a limited monitoring budget go?** Interception coverage is
   monotone and submodular in the monitored set, so a greedy allocation carries
   a provable approximation guarantee — and the diminishing returns are exactly
   what makes the hub's dominance actionable.
5. **What does one turned operative cost the brotherhood?** Exposure propagates
   through cellmates and command links; the cascade quantifies how often a
   single breach reaches the apex, and how quickly.
6. **Where should sensors be placed to sweep every target?** Placement is a set
   cover, and the residual multi-sensor redundancy measures whether the sweep
   survives losing one agency.

The package implements these as {{SPECTRE_NUM_DOMAIN_MODULES}} pure,
deterministic domain modules — `spectre.surveillance_net` (data-flow
centralization, betweenness, cascade coverage), `spectre.org_intel` (hierarchy
and cell compartmentalization), `spectre.network_geometry` (connectivity,
articulation points, critical nodes), `spectre.traffic_intel` (volume-weighted
interception and budgeted monitoring), `spectre.infiltration` (compromise
cascade and expected damage), and `spectre.signal_cover` (sensor-placement set
cover and redundancy) — exposed to the BOND suite through a thin
`MissionProvider` adapter (`spectre.mission`) implementing the FROZEN
`bond_api` protocol. The adapter holds no mathematics of its own: it selects
the canonical data, calls the pure core, and records provenance, which is why
the protocol can stay frozen while the domain keeps deepening.
