# Introduction

The Nine Eyes programme — a global surveillance-sharing arrangement among a
handful of Western intelligence agencies — is the geometric setting of the
2015 film *Spectre*. The NINE EYES mission software package renders that
setting as a computational model answering three intelligence questions:

1. **How centralized are surveillance data flows?** If a single agency (the
   United States) sits at the hub of every sharing link, the network is highly
   centralized: a single compromised hub exposes the whole exchange, and the
   flow concentration is high.
2. **How is a criminal brotherhood structured?** SPECTRE is a
   compartmentalized organization: isolated cells whose members know only
   their own cell, underneath an apex leadership. The intelligence question is
   how "separable" the cells are and whether the command chain is complete.
3. **Which nodes are critical to the network's geometry?** Network geometry —
   connectivity, articulation points, and global efficiency — identifies the
   agencies whose removal most fragments the system. These are the priority
   targets for neutralization.

The package implements these as three pure, deterministic domain modules —
`spectre.surveillance_net` (data-flow centralization and cascade coverage),
`spectre.org_intel` (hierarchy and cell compartmentalization), and
`spectre.network_geometry` (connectivity and critical nodes) — exposed to the
BOND suite through a thin `MissionProvider` adapter (`spectre.mission`)
implementing the FROZEN `bond_api` protocol.
