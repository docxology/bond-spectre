# Methodology

All analysis is deterministic and computed over a fixed, canonical dataset. The
only stochastic components — the influence cascade and the compromise cascade —
draw from explicitly seeded generators, and no wall-clock value enters a
persisted artifact. The package exposes {{SPECTRE_NUM_DOMAIN_MODULES}} pure
domain modules ({{SPECTRE_DOMAIN_MODULES}}); the mission's `execute` stage runs
them as a {{SPECTRE_PLAN_STEPS}}-step plan and reports the measured results
below.

## Surveillance-network centralization

The NINE EYES network is a directed graph whose nodes are agencies and whose
edges are data-sharing links. Out-degree centrality counts the data volume an
agency pushes downstream; in-degree centrality counts the volume it pulls in.
Freeman's group centralization index [@Freeman1979]

$$
\Cindex = \frac{\sum_i (s_{\max} - s_i)}{(n - 1)\, s_{\max}}
$$ {#eq:group_centralization}

measures how concentrated the flows are, from 0 (evenly spread) to 1 (a single
hub dominates); the normalizing denominator is the total deviation of the
star graph on `n` nodes. The Herfindahl–Hirschman index [@Hirschman1964] of
inflow shares,

$$
\HHI = \sum_i \left( \frac{f_i}{\sum_j f_j} \right)^{\!2},
$$ {#eq:hhi}

measures flow concentration independently of the degree distribution's shape.
Betweenness centrality — the share of shortest data paths passing through each
agency — is computed with Brandes' predecessor accumulation [@Brandes2001] and
drives the node sizing in @fig:network_flow_centralization. Cascade coverage
runs an independent-cascade process [@Kempe2003] from a seeding agency at a
fixed activation probability and reports the fraction of the network reached —
the surveillance footprint of that seed.

Networks are constructed either from an edge list, where every invariant is
enforced as the matrix is filled, or from an existing adjacency matrix, which
is validated explicitly (shape, label uniqueness, zero diagonal) because it was
produced elsewhere.

## Criminal-org cell model

The brotherhood assigns each operative to a cell and to a single superior.
Command depth is the number of links from an operative to the nearest apex; the
chain is complete when every operative is reachable from leadership by a
breadth-first walk down the `superior → subordinate` edges. Reachability is
computed by that walk rather than inferred from the depth assignment, so a
malformed organisation with a command cycle and no apex is correctly reported
as *incomplete* rather than silently accepted.

Compartmentalization is the fraction of cross-cell operative pairs that are
*not* directly linked by a command edge — 1.0 on a perfectly separated cell
structure, and lower when cells leak command links. Exposure of an operative is
their cellmates plus their direct superior and direct subordinates: the set that
falls if that operative is turned.

## Network geometry

Connectivity is assessed by connected-component flood fill; articulation points
(nodes whose removal disconnects the graph) are found with Tarjan's low-link
depth-first search [@Tarjan1972; @HopcroftTarjan1973]. Global efficiency is the
Latora–Marchiori mean inverse shortest-path length [@Latora2001]

$$
\Eff = \frac{1}{n(n-1)} \sum_{i \neq j} \frac{1}{d(i, j)},
$$ {#eq:efficiency}

with unreachable pairs contributing nothing. Critical-node ordering greedily
removes, at each step, the node whose removal most reduces the *current*
graph's pairwise connectivity — the targeted-attack simulation of Albert, Jeong
and Barabási [@Albert2000], scored as a key-player problem [@Borgatti2006].

## Traffic interception

The traffic-intelligence model treats the surveillance network as carrying a
volume-weighted exchange. A monitored agency intercepts every link incident to
it — inbound as well as outbound — and the coverage of a monitored set is the
fraction of total traffic those links carry. Because a new agency's marginal
interception gain shrinks as coverage grows, allocating a monitoring budget is
a monotone submodular coverage-maximization problem; the greedy rule carries
the Nemhauser–Wolsey–Fisher `(1 - 1/e)` guarantee [@Nemhauser1978], and the
same structure underlies submodular sensor placement for outbreak detection
[@Leskovec2007]. Candidate agencies are scanned in sorted label order, so ties
break by label rather than by however the network's node tuple happens to be
ordered — a determinism that survives reordering the input.

## Compromise cascade

The infiltration model simulates the brotherhood's defining weakness: turn one
operative and their cellmates, superior, and subordinates are exposed. A
round-based cascade propagates this through the organisation, each exposed
operative turning with a fixed probability — an independent-cascade process
[@Kempe2003] read as percolation on the org graph [@Newman2002]. Every
non-terminal round adds at least one operative to the compromised set, which is
bounded by the organisation's size, so the process terminates without an
imposed round cap. We report the expected fraction compromised, the rate at
which leadership is reached, and the mean number of rounds to leadership,
averaged over fixed-seed trials whose per-trial seeds are derived from one base
seed.

## Sensor-placement cover

The placement model poses the surveillance programme as a set-cover problem
over agencies × targets: which agencies to place so that the required fraction
of targets is swept. The greedy set-cover heuristic [@Johnson1974] selects
agencies by largest marginal gain and stays within a factor `O(log n)` of the
minimum cover, which is essentially the best any polynomial-time algorithm can
guarantee [@Feige1998]; the search stops when no remaining agency adds a target,
so an unreachable target is reported as a gap rather than looped over. Coverage
redundancy measures the fraction of targets swept by at least two selected
agencies — a multi-sensor resilience metric.
