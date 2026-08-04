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

## Traffic interception (deepening)

The traffic-intelligence model treats the surveillance network as carrying a
volume-weighted exchange (`spectre.traffic_intel`). A monitored agency
intercepts every link incident to it; the coverage of a monitored set is the
fraction of total traffic those links carry. Because a new agency's marginal
interception gain shrinks as coverage grows, allocating a monitoring budget is
a monotone submodular coverage-maximization problem; the greedy rule (pick the
agency adding the most new traffic, ties broken deterministically) carries the
Nemhauser–Wolsey–Fisher `(1 - 1/e)` guarantee.

## Compromise cascade (deepening)

The infiltration model (`spectre.infiltration`) simulates the brotherhood's
defining weakness: turn one operative and their cellmates, superior, and
subordinates are exposed. A round-based cascade compresses this through the
hierarchy, each exposed operative turning with a fixed probability — a
percolation process over the org graph (cf. epidemic spread on networks). We
report the expected fraction compromised, the rate at which leadership is
reached, and the mean cascade rounds to leadership, averaged over fixed-seed
deterministic trials.

## Sensor-placement cover (deepening)

The placement model (`spectre.signal_cover`) poses the surveillance programme
as a set-cover problem over agencies × targets: which agencies to place so that
the required fraction of targets is swept. The greedy set-cover heuristic
(Johnson) selects agencies by largest marginal gain and stays within a factor
`O(log n)` of the minimum cover; coverage redundancy measures the fraction of
targets swept by at least two agencies, a multi-sensor resilience metric.
