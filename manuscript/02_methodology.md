# Methodology

All analysis is deterministic and computed over a fixed, canonical dataset; no
randomness is relied upon beyond a fixed-seed activation draw, and no
wall-clock enters persisted artifacts.

## Surveillance-network centralization

The NINE EYES network is a directed graph whose nodes are agencies and whose
edges are data-sharing links. Out-degree centrality counts the data volume an
agency pushes downstream; in-degree centrality counts the volume it pulls in.
Freeman's group centralization index

$$\text{C} = \frac{\sum_i(\max s - s_i)}{n \cdot \max s}$$

measures how concentrated the flows are, from 0 (evenly spread) to 1 (a single
hub dominates). The Herfindahl–Hirschman index (HHI) of inflow shares measures
flow concentration independently. Cascade coverage runs a deterministic
influence cascade from a seeding agency and reports the fraction of the
network reached — the surveillance footprint.

## Criminal-org cell model

The brotherhood assigns each operative to a cell and to a single superior.
Command depth is the number of links from an operative to the apex; the chain
is complete when every operative is reachable from leadership via the command
tree. Compartmentalization is the fraction of cross-cell operative pairs that
are *not* directly linked by a command edge — 1.0 on a perfectly separated
cell structure, and lower when cells leak command links.

## Network geometry

Connectivity is assessed by connected-component flood fill; articulation
points (nodes whose removal disconnects the graph) are found with Tarjan's
low-link DFS. Global efficiency is the mean inverse shortest-path length.
Critical-node ordering greedily removes, at each step, the node whose removal
most reduces pairwise connectivity — an attack simulation of network
fragmentation.
