# Scope and Related Work

## What this package claims

NINE EYES is a *modelling* package, not an intelligence product. It claims
exactly three things, each verifiable by running the code:

1. The film's premises — a hub-dominated surveillance-sharing exchange and a
   compartmentalized brotherhood — admit precise, standard formalizations:
   directed-graph centralization, a cell partition over a command tree,
   undirected connectivity geometry, weighted interception coverage,
   percolation on the org graph, and set cover.
2. Under those formalizations the canonical dataset yields the measured values
   reported in §3, deterministically, from a fixed seed and a fixed input whose
   SHA-256 is recorded on every outcome.
3. Every number in this manuscript is produced by that computation and injected
   as a token; none is typed by hand.

It claims nothing about any real surveillance arrangement. The canonical
network is a fictional construction sized to the film's conceit
({{SPECTRE_NUM_NODES}} agencies, {{SPECTRE_NUM_EDGES}} directed links), chosen
so that each algorithm has something non-trivial to find. The brotherhood
roster is one node per distinct film character, but its cell partition and
command edges are chosen rather than observed (§5): the organisational
*structure* is a modelling construct, and no claim of canonical fidelity is
made for it.

## Out of scope

- **Empirical validation.** There is no ground-truth dataset for the modelled
  quantities, so no accuracy claim is made or implied. The results are
  properties of a stated model over stated inputs.
- **Weighted or temporal graph dynamics.** The geometry and centrality layers
  are unweighted and static; only the traffic layer carries volumes, and no
  layer carries time.
- **Adversarial reaction.** The critical-node ordering and the monitoring
  allocation are one-shot optimizations against a fixed structure; the modelled
  organisation does not rewire in response.
- **Optimality.** Two of the six analyses use greedy heuristics with known
  approximation bounds rather than exact solvers (see below); the reported
  selections are the greedy ones.

## Related work by module

**Centralization and centrality.** Freeman's group centralization index
[@Freeman1979] is the standard measure of how concentrated a network's degree
distribution is around a single actor; the general treatment of degree,
connectivity, and efficiency measures follows Newman [@Newman2010]. Betweenness
is computed with Brandes' shortest-path accumulation [@Brandes2001]. Flow
concentration reuses the Herfindahl–Hirschman index from industrial
organization [@Hirschman1964] on the inflow-share vector, which gives a
concentration reading independent of the Freeman index — and, on this dataset,
a contradicting one (§3). Because the index is bounded below by `1/r` rather
than by 0, it is reported alongside that floor; quoting an HHI without its
floor invites reading an evenly-spread vector as a concentrated one, which is
exactly what an earlier revision of this report did.

**Connectivity geometry.** Articulation points come from Tarjan's low-link
depth-first search [@Tarjan1972; @HopcroftTarjan1973]. Global efficiency is the
Latora–Marchiori mean inverse shortest-path length [@Latora2001]. The
node-removal impact and robustness curve follow the error-and-attack-tolerance
framing of Albert, Jeong and Barabási [@Albert2000]: fragmenting a
hub-dominated network takes few targeted removals and many random ones. The
greedy critical-node ordering is a key-player problem in the sense of Borgatti
[@Borgatti2006], scored by pairwise-connectivity loss.

**Cascades.** The surveillance cascade and the infiltration cascade are both
independent-cascade processes in the sense of Kempe, Kleinberg and Tardos
[@Kempe2003], which is also where the submodularity of coverage-style influence
objectives is established. The infiltration model's percolation reading — a
contagion spreading over a fixed contact structure — follows Newman's treatment
of epidemic spread on networks [@Newman2002]; here the contact structure is the
brotherhood's exposure relation (cellmates, superior, subordinates) rather than
a social contact graph.

**Budgeted monitoring.** Interception coverage is monotone and submodular in
the monitored set, so the greedy rule carries the classic `(1 − 1/e)` guarantee
of Nemhauser, Wolsey and Fisher [@Nemhauser1978]. The same structure underlies
sensor placement for outbreak detection [@Leskovec2007], which is the closest
published analogue of the monitoring-allocation problem posed here.

**Placement as set cover.** The sensor-placement layer is minimum set cover,
solved with Johnson's greedy heuristic [@Johnson1974] at its `O(log n)` factor;
Feige's threshold [@Feige1998] establishes that no substantially better
polynomial-time approximation exists unless `NP` has quasi-polynomial-time
algorithms, which is why the greedy solution is reported rather than an exact
one.

## Position within the BOND suite

The suite's other packages model other films' concepts; this one owns
surveillance-network and criminal-organisation intelligence. Cross-package
reuse happens through `bond-api`, never by importing another film's `src/`. The
package exposes {{SPECTRE_NUM_DOMAIN_MODULES}} pure domain modules
({{SPECTRE_DOMAIN_MODULES}}) behind one frozen `MissionProvider` and
{{SPECTRE_NUM_GADGETS}} registered Q-branch gadgets, and its `execute` stage
runs a {{SPECTRE_PLAN_STEPS}}-step plan. Anything a sibling package needs from
NINE EYES it obtains through those interfaces.

## Threats to validity

- **Canonical-dataset dependence.** All reported values are properties of one
  fixed input. A different agency network or brotherhood would give different
  numbers; the algorithms, not the numbers, are the reusable contribution.
- **Greedy selection.** The monitoring allocation and the placement cover are
  approximations. Their guarantees are stated above, but a reported selection
  is not proof of optimality.
- **Cascade parameterization.** Cascade coverage and expected damage depend on
  the activation and turn probabilities, which are stated design choices rather
  than estimates. The models are used comparatively (which node, which agency,
  how much worse) rather than as absolute forecasts.
- **Cascade sampling error.** Both cascade figures are means over
  {{SPECTRE_CASCADE_TRIALS}} seeded realizations, not closed-form
  expectations. No confidence interval is reported, so the trailing digits of
  those two numbers should not be read as significant; they would move under a
  different base seed or trial count.
- **Unweighted geometry.** Treating the sharing graph as unweighted for the
  connectivity layer discards the volume information the traffic layer uses. The
  two layers deliberately answer different questions and their results should
  not be pooled.
