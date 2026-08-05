# Testing philosophy — Spectre NINE EYES

## Zero-mock policy

All tests use **real data structures and real computation** — no
`unittest.mock`, `MagicMock`, `@patch`, `mocker.patch`, or `create_autospec`
anywhere in `tests/`. This is not stylistic: a mocked collaborator makes a test
assert the shape of a call instead of the truth of a result, and every metric in
this package's manuscript is a result.

Where a test needs an alternative implementation, it writes a **real object
that satisfies the real contract**. The sanctioned example is `_EmptyMission`
in `tests/test_manuscript_variables.py`: a small class implementing
`brief/plan/execute` and returning genuine `bond_api` protocol instances whose
`results` dict is empty. It is not a mock — it is a mission that measures
nothing, which is exactly the condition the strict hydration gate exists to
reject. The frozen protocol validates it on construction, so the stand-in
cannot drift from the contract it stands in for.

## Real data, not fixtures-of-convenience

Domain tests build small networks and brotherhoods by hand and check numbers
that can be derived on paper:

- a small star network gives an exactly computable Freeman centralization;
- two disjoint dyads give a global efficiency of `4 / 12` — four ordered pairs
  at distance one out of `n(n−1)` — which the test asserts as a closed form,
  not as "whatever the code returned";
- a two-agency traffic split of 30/70 makes the interception coverage of each
  monitored endpoint exact.

Tests that only assert "a float came back" do not earn their place here.

## Determinism as a tested property, not a claim

- `cascade_coverage` runs on a fixed seed; the tests assert the same seeded
  cascade reproduces its reached set and that coverage is monotone in the
  activation probability.
- `simulate_compromise` / `expected_damage` take an explicit seed and derive
  per-trial seeds; the tests assert repeat runs are identical.
- Greedy tie-breaks are asserted directly: `test_ties_break_by_agency_label_not_node_order`
  builds a traffic network whose node order (`zulu`, `alpha`, …) contradicts
  its label order and requires the label-ordered winner. A determinism claim
  that holds only because of incidental input ordering is not determinism.
- `Provenance.wall_time_s == 0.0` and the canonical SHA-256 `input_hash` are
  asserted in `tests/test_mission.py`, so no wall-clock can leak into a
  persisted artifact unnoticed.

## Coverage

The enforced gate is **≥90% line + branch on `src/`**:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Branch coverage is on (`[tool.coverage.run] branch = true`), which is the
point: line coverage alone would let a validation `if` be entered but never
taken. The achieved figure and test count are recorded in
[`_generated/COUNTS.md`](_generated/COUNTS.md) from a real run — regenerate it,
never hand-edit it, and never quote a coverage number in prose that a command
did not just print.

## Error-branch principle

Every `ValueError` / `FileNotFoundError` raised in `src/` is exercised by at
least one test, matched on message where the message distinguishes two nearby
branches (`unknown node 'Z'` on the first endpoint versus the second, `unknown
operative … in parent_of` versus `unknown superior …`). Validation and boundary
branches are first-class coverage, not incidental.

## No gate that cannot fail

A branch that cannot be reached from any call site is worse than no branch: it
reads as protection and provides none. Where this package found such branches
they were either deleted (a re-validation of a matrix the constructor had just
built element by element; a `sigma > 0` guard in Brandes' accumulation where
every reachable node has at least one shortest path; a round cap on a cascade
that provably terminates) or made reachable and tested (matrix-sourced networks
now go through `network_from_adjacency`, which validates for real; the strict
hydration gate is reachable because the provider is injectable).

When you add a guard, write the test that makes it fire in the same pass. If
you cannot make it fire, the guard is decoration — remove it.

## Test inventory

| File | Covers |
| --- | --- |
| `test_surveillance_net.py` | edge-list and matrix constructors, degree/betweenness/share centrality, Freeman centralization, HHI, seeded cascade (incl. generator sources), sweep coverage, degenerate 1- and 2-node networks, all error branches |
| `test_org_intel.py` | build validation (unknown operative, unknown superior, self-report), depth/height, apex reachability, cell membership, compartmentalization, exposure, command cycles, explicit `None` parents |
| `test_network_geometry.py` | components, connectivity, articulation points, all-pairs distances, efficiency on connected/disconnected/isolated graphs, removal impact, robustness curve, greedy critical ordering, error branches |
| `test_traffic_intel.py` | traffic build/validation, totals, heavy hitters, interception on out- and in-links, budgeted greedy allocation, label-ordered tie-breaks, error branches |
| `test_infiltration.py` | cascade spread and determinism, damage aggregation, leadership-hit accounting, seed/probability/trials validation |
| `test_signal_cover.py` | coverage build/validation, greedy set cover incl. tie-breaks and zero-gain termination, counts, uncovered gaps, redundancy |
| `test_mission.py` | frozen protocol compliance, five-stage flow, six-step plan, measured results, provenance, gadget registration, live discovery |
| `test_manuscript_variables.py` | config loading and validation, token map, measured inventories, strict metrics gate via a real stand-in runner, live `{{TOKEN}}` cross-reference, tree resolution |
| `test_figures.py` | figure PNG writing + empty-network error |
| `test_scripts_smoke.py` | subprocess execution of every CLI with artifact assertions |
| `test_domain_isolation.py` | subprocess proof that the six pure modules import without `bond_api` |

## The live cross-reference gate

`test_manuscript_variables.py::TestLiveReference` reads every
`manuscript/NN_*.md`, extracts every `{{TOKEN}}`, and fails if any of them is
absent from `generate_variables()`. That is what makes "no hand-authored
metrics" enforceable rather than aspirational: a number added to prose without
a backing computation cannot be spelled as a token, and a token without a
computation fails the suite.
