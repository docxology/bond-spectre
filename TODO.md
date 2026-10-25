# TODO — spectre (NINE EYES)

`spectre` is the BOND film package for *Spectre* (2015). It formalizes the film's
two premises — the Nine Eyes surveillance-sharing pact and the SPECTRE
brotherhood — as six pure, deterministic domain modules (`surveillance_net`,
`org_intel`, `network_geometry`, `traffic_intel`, `infiltration`, `signal_cover`)
behind one frozen `bond_api.MissionProvider` adapter in `src/spectre/mission.py`,
with every manuscript number hydrated from the measured `execute()` output and
reconciled against `data/claim_ledger.yaml`.

**Verified state at phase-6** (measured 2026-08-05, macOS arm64 / CPython 3.14.6;
superseded by the Round-2 re-measurement at the end of this file):
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **246 passed**, coverage
**100.00%** line+branch on `src/` (928 statements, 358 branches, 0 missed).
`ruff check`, `ruff format --check`, and `mypy src/ scripts/` are all clean.

**Closed 2026-08-05 — the byte-identical claim was false.**
`manuscript_variables.generate_variables()` emitted `GENERATION_TIMESTAMP` from
`datetime.now(timezone.utc)` and rendered it into
`output/manuscript/06_reproducibility.md`, so every regeneration produced
different persisted bytes while `README.md`, `AGENTS.md` and the manuscript all
claimed byte-identical regeneration — and 236 green tests never touched it.
Reproduced before fixing: two consecutive hydrations hashed
`b5c21873bfd87c06abd20912410b29f0` then `98ef6eb7b315b93c1f1736479ae1ae67`.
The claim was **made true**, not softened: the token is now
`SPECTRE_RELEASE_DATE`, read from the committed `paper.date` in
`manuscript/config.yaml` and validated as `YYYY-MM-DD` with no clock fallback,
and `tests/test_regeneration_determinism.py` binds it — it regenerates the whole
artifact set twice, more than a wall-clock tick apart, and compares SHA-256
digests file by file (proven able to fail: re-introducing `datetime.now()` turns
5 of its tests red, including all three byte-identity assertions). The claim's
scope is now stated in words in `manuscript/06_reproducibility.md`: identity
holds within one software environment, with `{{PLATFORM}}` / `{{PYTHON_VERSION}}`
the only environment-dependent values.

**Audit position:** all 11 findings in
`../output/verify/spectre.json` (5 SEVERE, 6 MODERATE) were resolved in phase-6
and I re-verified each against the live tree this session — the degenerate
`data_share_centrality`, the false HHI, the mis-titled figure, the two hollow
gates, the ignored cascade seed, the single-draw cascade, the alias-inflated
roster, the 11-row ledger, the unpinned headline metrics, and the
normalization/prose mismatch are all closed and pinned by tests that can fail.
`spectre` has **no** entry in `../output/verify/_unresolved.json` and no
`spectre.unresolved.json` file exists, so **zero items below are carried-over
unresolved audit findings**. Everything below was found by reading the tree
today.

---

## Open work

> Superseded in part: the Round-2 section at the end of this file closes C1,
> C2, C3, E2, V3, D2 and the V1 sort-key half, and V2 carries its own closure
> note (2026-08-05). The rows below keep the original finding text; the closure
> evidence lives in that section's table. The verification block further down
> has been re-measured — its live counts are 271 passed / 100.00%.

### Correctness

| # | Item |
| --- | --- |
| C1 | **The manuscript's only figure reference dangles in the resolved tree.** `manuscript/03_results.md:31` embeds `figures/network_flow_centralization.png`, and `manuscript/SYNTAX.md:96` states paths resolve relative to the resolved manuscript in `output/manuscript/`. From there the relative path resolves to `output/manuscript/figures/network_flow_centralization.png`, which does not exist — `scripts/generate_figures.py:16-19` writes to `output/figures/` (via `src/spectre/figures/networks.py:102-106`). It has never bitten because no render has been exercised (see D3). **Done:** either the embed path is `../figures/...` (updated in `manuscript/03_results.md:31` and the registry rows at `manuscript/SYNTAX.md:86,91`), or `scripts/generate_figures.py` also writes/copies into `output/manuscript/figures/`; plus a test in `tests/test_scripts_smoke.py` that resolves the embedded path from `output/manuscript/` and asserts the file exists. **Command:** `uv run python scripts/generate_figures.py && uv run python scripts/z_generate_manuscript_variables.py && uv run python -c "import re,pathlib; d=pathlib.Path('output/manuscript'); [print(p, (d/m).resolve().exists()) for p in d.glob('*.md') for m in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', p.read_text())]"` — every line must print `True`. |
| C2 | **Three metadata sidecars describe a three-module package that has not existed since phase-4.** `.zenodo.json:3`, `codemeta.json:6`, and `CITATION.cff:4-9` all say the package "Models surveillance-network data-flow centralization, criminal-organisation cell structure (SPECTRE), and network geometry" — omitting `traffic_intel`, `infiltration`, and `signal_cover`, three of the six shipped domain modules. All three also carry the keyword `"active inference"` (`.zenodo.json:20`, `codemeta.json:25`, `CITATION.cff:21`), a scaffold leftover from the exemplar this package was forked from: nothing in `src/`, `tests/`, or `manuscript/` concerns active inference. **Done:** all three descriptions name the six domain areas that `domain_module_names()` returns, and the off-topic keyword is gone from all three. **Command:** `uv run python -c "import sys; sys.path.insert(0,'src'); from spectre.manuscript_variables import domain_module_names; print(domain_module_names())"` then `grep -n "active inference" .zenodo.json codemeta.json CITATION.cff \|\| echo Clean` (must print `Clean`) and read the three descriptions against that module list. |
| C3 | **`manuscript/config.yaml:24-25` claims a GitHub repository this package does not have.** `github_repository: "docxology/spectre"` / `repository_url: "https://github.com/docxology/spectre"` sit two lines under a comment that reads "Local-only working tree: no remote, no DOI" — and `README.md:117-118` plus `AGENTS.md:9` both state the package is never pushed to any remote. Neither field is consumed by any token (`grep -rn "repository_url\|github_repository" src/ manuscript/*.md` returns nothing), so this is an unread but false declaration. **Done:** the two keys are removed, or replaced with a value that is true of a local-only tree. **Command:** `grep -n "github_repository\|repository_url" manuscript/config.yaml` returns nothing, and `uv run pytest tests/test_manuscript_variables.py -q` still passes (proving nothing consumed them). |

### Verification

| # | Item |
| --- | --- |
| V1 | **The byte-identical-determinism claim is not bound by any test.** `README.md:79` states "Two runs of `scripts/debrief.py` produce byte-identical records" and `AGENTS.md:84-86` lists the diff as a *manual* spot-check (verify step 6). The closest test, `tests/test_scripts_smoke.py:51-58`, runs `debrief.py` once and asserts only that the record exists, `success is True`, and `input_hash` is truthy. `tests/test_mission.py:88-92` compares two in-process `execute()` calls but never touches the persisted JSON bytes, so a non-determinism introduced by the serializer (key order, float repr, trailing newline) would ship green. **Done:** a test runs `scripts/debrief.py` twice into a temp location and asserts the two files are byte-identical, and it fails if the writer at `scripts/debrief.py:20-24` drops `sort_keys=True`. **Command:** `uv run pytest tests/test_scripts_smoke.py -q -k determinis` shows the new test passing; then temporarily remove `sort_keys=True` from `scripts/debrief.py:23` and confirm it goes red (positive control), and restore. **Partly closed 2026-08-05:** `tests/test_regeneration_determinism.py::test_full_pipeline_is_byte_identical_across_runs` runs all three generators twice and compares SHA-256 digests of every `output/` file, so `nine_eyes_debrief.json` is now bound run-to-run. What remains open is the *serializer-canonicality* half: dropping `sort_keys=True` would not make two runs of identical code differ (dict order is insertion order), so that specific positive control still has no gate. A test that asserts the persisted record equals a canonically re-serialized round-trip would close it. |
| V2 | **The same gap applies to figure determinism.** `README.md:76-77` claims a fixed seed for "figure layout". `tests/test_figures.py:24-35` asserts only that the PNG is written and non-empty. Nothing asserts two renders of the same network produce the same bytes, so a matplotlib default or an unseeded jitter change would pass. **Done:** a test renders the canonical network twice to two temp paths and compares SHA-256 digests. **Closed 2026-08-05:** the PNG is inside the digest set compared by `tests/test_regeneration_determinism.py::test_full_pipeline_is_byte_identical_across_runs`, which re-renders it via `scripts/generate_figures.py` on both passes; an unseeded jitter or a run-varying metadata field now fails the suite. **Command:** `uv run pytest tests/test_regeneration_determinism.py -q`. |
| V3 | **`tests/test_domain_isolation.py:17-24` hand-maintains the module list it guards.** `_IMPORTS` is a literal 6-tuple. AGENTS.md rule 3 ("the pure core is `bond_api`-free") is only enforced for modules someone remembered to add here — a seventh domain module added tomorrow is silently unguarded, while `manuscript_variables.domain_module_names()` reads the same set off disk and would notice. **Done:** the test derives its import list from `domain_module_names()` (or asserts `set(_IMPORTS)` equals the derived names, so a divergence fails loudly). **Command:** `uv run pytest tests/test_domain_isolation.py -q`, then add an empty `src/spectre/scratch_probe.py`, confirm the suite goes red, and delete it. |
| V4 | **Two AGENTS.md rules are enforced only by a grep a human has to remember to run.** Rule 1 (no mock framework) is verify step 2 at `AGENTS.md:69`; the lineage rule is verify step 7 at `AGENTS.md:89`. Neither is a test, so neither fires in `uv run pytest`. Every *other* rule in that file has been made a gate (isolation, coverage, claim ledger, live token cross-reference). **Done:** a `tests/test_repo_hygiene.py` scans `tests/` for `MagicMock\|@patch\|create_autospec\|unittest\.mock` and the tree for `template_code_project`, failing on any hit — with a positive control proving the scanner matches a planted string in a temp tree (an empty scan set is the failure mode this class of gate has; see the sibling packages' notes). **Command:** `uv run pytest tests/test_repo_hygiene.py -q` and confirm the scan set is asserted non-empty. |

### Documentation

| # | Item |
| --- | --- |
| D1 | **`docs/_generated/COUNTS.md` is regenerated by hand from a real run and can silently age.** Its header tells you which commands to read the numbers off, but nothing fails when the file drifts. Today its rows are accurate (re-measured 2026-08-05: 246 tests, 100.00%, 928/358, 34 ledger rows). The inventory rows *are* pinned live by `tests/test_manuscript_variables.py::TestMeasuredInventories`; the test count, coverage percentage, and statement/branch counts are not. **Done:** either a script regenerates the file from a coverage run, or the header states plainly which rows are gated and which are a hand-recorded snapshot with the date of the run. **Command:** `uv run pytest tests/ --cov=src --cov-fail-under=90 -q \| tail -5` and compare against `docs/_generated/COUNTS.md`. |
| D2 | **`AGENTS.md:78-82` (verify step 5) still describes ledger reconciliation as a manual eyeball.** It reads "`data/claim_ledger.yaml` values must equal `output/data/manuscript_variables.json`" — but `tests/test_claim_ledger.py` has made that an enforced gate with positive controls since phase-6, and `README.md:91-94` already says so. The rulebook understates its own machinery. **Done:** step 5 names `tests/test_claim_ledger.py` as the enforcement and keeps only the regeneration commands as manual. **Command:** `uv run pytest tests/test_claim_ledger.py -q` (11 tests, all green) and read `AGENTS.md:78-82`. |
| D3 | **No render has ever been exercised from this package.** `manuscript/config.yaml:53-58` toggles `pdf`, `html`, `slides`, `docx`, and `epub` all to `false`. Sections `00`–`07` + `99`, `preamble.md`, and `references.bib` (15 entries) are render-ready but unproven — and C1 above is exactly the class of defect a first render would have caught. **Done:** one format is toggled on and a build produces a document with no `??` cross-references, no unresolved `{{TOKEN}}`, and the figure visible on the page (raster-read it; `pdftotext` hides mangled figures and math). **Command:** hydrate first (`uv run python scripts/debrief.py && uv run python scripts/generate_figures.py && uv run python scripts/z_generate_manuscript_variables.py`), then run the chosen renderer over `output/manuscript/` and inspect the artifact. |

### Extension

| # | Item |
| --- | --- |
| E1 | **Wire `bond_utilities.mission_io` for provenance persistence.** `scripts/debrief.py:20-24` hand-rolls the JSON write and `:34-44` hand-builds the record dict. The counterpart exists and is compatible: `../bond-utilities/src/bond_utilities/mission_io.py:153` `record_provenance_outcome(...)`, with `validate_record`, `save_record`, `load_record`, and `verify_provenance` alongside. Blocked only on declaring `bond-utilities` in `pyproject.toml` `[project.dependencies]` + `[tool.uv.sources]` (mirroring the `bond-api` path dep at `pyproject.toml:37-38`). **Done:** `scripts/debrief.py` delegates persistence, and the written record carries `input_hash`, `schema_version`, and the derived `seed` and round-trips through `mission_io.load_record`. **Command:** `uv sync --all-extras && uv run python scripts/debrief.py && uv run python -c "import sys; sys.path.insert(0,'src'); from bond_utilities.mission_io import load_record, verify_provenance; r=load_record('output/data/nine_eyes_debrief.json'); print(r['schema_version'], r['provenance']['seed'], verify_provenance(r))"`. |
| E2 | **Second figure — the org/cascade layer is text-only.** `src/spectre/figures/networks.py` holds the sole generator; `manuscript/SYNTAX.md:91` has one registry row. The cell partition (`org_intel.cell_membership`) and the compromise cascade (`infiltration.expected_damage`) are reported only as numbers in `03_results.md`. **Done:** a new generator in `src/spectre/figures/`, a call in `scripts/generate_figures.py`, a test in `tests/test_figures.py` (including the byte-determinism check from V2), a registry row in `manuscript/SYNTAX.md`, and an embed in `03_results.md` whose path resolves (C1). **Command:** `uv run python scripts/generate_figures.py && ls output/figures/` shows two PNGs, and `uv run pytest tests/test_figures.py -q` passes. |
| E3 | **Volume-weighted geometry.** `network_geometry.py` is unweighted while `traffic_intel.py` carries volumes, so the two layers answer different questions and their results cannot be pooled — recorded today as an accepted scope note (`manuscript/07_scope_and_related_work.md`, "Out of scope" and "Threats to validity"). A volume-weighted `network_efficiency` and a volume-weighted `critical_node_order` would let them be compared rather than only reported side by side. **Done:** the weighted variants exist with value-pinned tests re-derived by hand from the traffic edge list, the scope note is narrowed to what remains unweighted, and any new manuscript number has a claim-ledger row. **Command:** `uv run pytest tests/test_network_geometry.py tests/test_traffic_intel.py tests/test_claim_ledger.py -q`. |
| E4 | **Adaptive adversary.** `network_geometry.critical_node_order` and `traffic_intel.monitor_allocation` both optimize one-shot against a fixed structure; the modelled organisation never rewires (stated as a scope limit in `manuscript/07_scope_and_related_work.md`). A rewiring-response model would make the attack/defence results sequential. **Done:** a sequential model with a stated rewiring rule, deterministic under a declared seed, tested for seed *sensitivity* as well as reproducibility (the pattern already used for the cascade at `tests/test_mission.py:174`). **Command:** `uv run pytest tests/ --cov=src --cov-fail-under=90`. |

---

## Known limitations (not bugs)

- **The Herfindahl flow-concentration index does not corroborate hub dominance —
  it nearly contradicts it.** The adversarial pass forced this claim to be
  softened, and the honest scope is now stated in
  `manuscript/07_scope_and_related_work.md` and pinned by
  `tests/test_mission.py:132` (`test_hhi_sits_just_above_its_floor`): the
  measured HHI of 0.1361 sits barely above its 0.1250 even-spread floor. The
  index is reported *with* its floor precisely so it cannot be read as
  corroborating the Freeman centralization of 0.9219. Do not re-frame it as
  supporting evidence.
- **The SPECTRE cell partition and command edges are a modelling construct, not
  film canon.** The roster is one node per distinct character (aliases removed
  in phase-6 — Oberhauser = Blofeld, Hinx = Mr Hinx), but the film publishes no
  org chart. `src/spectre/mission.py:124-138` and
  `manuscript/07_scope_and_related_work.md` both say so explicitly. Structural
  results (`hierarchy_height`, compartmentalization, cascade damage) are
  properties of the stated model, not claims about the film.
- **No empirical validation.** There is no ground truth for any modelled
  quantity, so no accuracy claim is made. The reusable contribution is the
  algorithms, not the numbers.
- **Cascade figures carry unreported sampling error.** Both cascade quantities
  are means over 50 seeded realizations, not closed-form expectations, and no
  confidence interval is reported — the trailing digits would move under a
  different base seed. Stated in `manuscript/07_scope_and_related_work.md`.
- **Two of the six analyses are greedy approximations, not exact solvers**
  (`monitor_allocation` at the Nemhauser–Wolsey–Fisher `1 − 1/e` bound;
  `greedy_set_cover` at Johnson's `O(log n)`, with Feige's threshold as the
  reason not to chase an exact solver). The reported selections are the greedy
  ones.
- **No DOI, and no repository URL in the manuscript config.**
  `manuscript/config.yaml` drops DOI fields by the BOND fork contract, and the
  exemplar's invented repository URL was removed outright (C3). This repository
  is the published snapshot of the package
  (`github.com/docxology/bond-spectre`), not the DOI surface of record.
- **`output/` is disposable and git-ignored.** Everything under it is
  regenerable from `scripts/`. Never edit an artifact to make a gate pass.

---

## Verification

Run from the repository root — this standalone clone *is* the package (in the
BOND suite it lives at `projects/working/bond/spectre`). With no suite checkout
next to it, the `bond-api` path pin cannot resolve, so `uv run pytest` is only
available in an environment where `bond_api` is importable. If `uv` reports
`Failed to initialize cache` or `Operation not permitted`, that is a sandbox
restriction — re-run with the sandbox disabled. If you touch `pyproject.toml`,
sync with `uv sync --all-extras` (a bare `uv sync` prunes pytest).

```bash
# 1. Tests + coverage gate — expect 271 passed, 100.00% line+branch on src/
uv run pytest tests/ --cov=src --cov-fail-under=90

# 2. Zero mocks — expect "Clean"
grep -rnE "MagicMock|@patch|create_autospec|unittest\.mock" tests/ || echo Clean

# 3. Pure core is bond-api-free — must list ONLY src/spectre/mission.py
grep -l "bond_api" src/spectre/*.py

# 4. Lint + types — expect "All checks passed!", "32 files already formatted",
#    "Success: no issues found in 19 source files"
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# 5. Regenerate measured artifacts, hydration LAST
uv run python scripts/debrief.py
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py
#    Ledger reconciliation is enforced by tests/test_claim_ledger.py (step 1),
#    not by eye: a missing row, a stale row, or a drifted value fails there.

# 6. Determinism spot-check (V1 is now a gate — tests/test_regeneration_determinism.py)
uv run python scripts/debrief.py && cp output/data/nine_eyes_debrief.json /tmp/run1.json
uv run python scripts/debrief.py && diff /tmp/run1.json output/data/nine_eyes_debrief.json

# 7. Lineage — expect "Clean"
grep -rn "template_code_project" . --exclude-dir=.git --exclude-dir=.venv --exclude=uv.lock || echo Clean

# 8. git status clean after your commit
git status --porcelain
```


---

## Round-2 (2026-08-06)

**Verified state today** (measured 2026-08-06, macOS arm64 / CPython 3.14.6):
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **271 passed**, coverage
**100.00%** line+branch on `src/` (999 statements, 396 branches, 0 missed).
`ruff check`, `ruff format --check` (34 files) and `mypy src/ scripts/`
(19 files) are all clean. The byte-identical regeneration gate
(`tests/test_regeneration_determinism.py`) still passes with the new figure in
the pipeline.

### Closed this round (each with a regression/negative-control test)

| Ref | Finding | Fix + test evidence |
| --- | --- | --- |
| C1 | **The manuscript's only figure reference dangled.** `03_results.md` embedded `figures/network_flow_centralization.png`, which — resolved relative to `output/manuscript/` — did not exist (figures were written to `output/figures/`). | `scripts/generate_figures.py` now mirrors every figure into `output/manuscript/figures/`; `tests/test_scripts_smoke.py::TestFigureDeployment` resolves every embedded image path from the resolved tree and asserts it exists (refs asserted non-empty, so it cannot pass vacuously). |
| C2 | **Metadata sidecars described a three-module package and carried the scaffold keyword.** `.zenodo.json`, `codemeta.json`, `CITATION.cff` named only surveillance/cell/geometry and listed `"active inference"`. | All three rewritten to name the six shipped domain areas; the keyword is gone. `tests/test_sidecar_metadata.py` checks the keyword arrays (so the legitimate "Active Inference Institute" affiliation does not trip it) and that all six area terms appear. |
| C3 | **Config falsely declared a remote repository on a local-only tree.** `manuscript/config.yaml` carried `github_repository`/`repository_url` for a tree that is never pushed. | Keys removed; `tests/test_sidecar_metadata.py::TestC3Config` asserts the config declares no such remote. |
| V1 (half) | **`sort_keys=True` in the debrief writer was not load-bearing.** Dropping it would not change two identical runs (insertion order is stable), so the run-to-run determinism test could never catch it. | `tests/test_scripts_smoke.py::TestRecordCanonicality` asserts the persisted record equals its key-sorted re-serialization, so the flag is now pinned. |
| V3 | **`test_domain_isolation.py` hand-maintained its 6-module import list** — a seventh domain module would be silently unguarded. | The import list is now derived from `domain_module_names()`; `test_import_list_is_derived_and_nonempty` asserts the derivation is live and the scan set non-empty. |
| Edge | **`node_removal_impact` silently no-op'd on an out-of-range index** (removed nothing, returned 0.0). | Now raises `ValueError`; tests for out-of-range and negative indices in `tests/test_network_geometry.py`. |
| Edge | **`herfindahl_index` / `group_centralization` propagated NaN/inf silently.** | Both reject non-finite inputs; NaN/inf regression tests in `tests/test_surveillance_net.py::TestFiniteValidation`. |
| E2 | **The org/cascade layer was text-only; the package had one figure.** | Added `plot_brotherhood_cascade` (command tree, cells as colours, live exposure set of the seeded operative), exported from `spectre.figures`, wired into `generate_figures.py`, embedded in `03_results.md`, registered in `manuscript/SYNTAX.md`; byte-determinism + empty/unknown-seed/cycle branch tests in `tests/test_figures.py`. |
| D2 | **AGENTS.md step 5 described ledger reconciliation as a manual eyeball.** | Now names `tests/test_claim_ledger.py` as the enforcement (it already was the real gate). |

### Manuscript deepened

- Added a **live-bound summary results table** at the top of `03_results.md`; every
  cell is an injected `{{TOKEN}}` from the measured mission output (no new
  tokens → no ledger churn).
- Added the **brotherhood compromise-cascade figure** (E2) so the org layer is
  visual, not text-only.
- Abstract, methodology, results, limitations (07 "Threats to validity"),
  reproducibility and 15-entry bibliography were already in place and verified
  to hydrate (no leftover `{{TOKEN}}` in the resolved tree).

### Known open for a future round

- **E1** — wire `bond_utilities.mission_io.record_provenance_outcome` into
  `scripts/debrief.py` (blocked on declaring the `bond-utilities` path dep in
  `pyproject.toml`).
- **E3** — volume-weighted `network_efficiency` / `critical_node_order` so the
  geometry layer pools with the traffic layer.
- **E4** — an adaptive (rewiring) adversary for the one-shot greedy optimizations.
- **D1** — `docs/_generated/COUNTS.md` test-count/coverage rows are still a
  hand-recorded snapshot (inventory rows remain pinned live); a generator
  remains the clean fix.
- **D3** — no render format has been exercised; all `render.formats` toggles are
  still off, so a first render could still surface a cross-reference or
  layout defect the figure-path test (C1) now pre-empts for embeds only.
