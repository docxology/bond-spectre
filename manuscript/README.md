# manuscript — Spectre NINE EYES

The publication surface of the `spectre` BOND film package. Prose lives here;
every number in it is computed elsewhere and injected as a `{{TOKEN}}`.

## Contents

| File | Role |
| --- | --- |
| `00_abstract.md` | What the package models and the headline measured results |
| `01_introduction.md` | The Nine Eyes / SPECTRE setting and the intelligence questions asked |
| `02_methodology.md` | The six models: centralization, cell structure, geometry, interception, cascade, cover |
| `03_results.md` | Measured values over the canonical dataset, plus the network figure |
| `04_conclusion.md` | What the measurements mean and what carries over |
| `05_experimental_setup.md` | The canonical dataset, determinism guarantees, software environment |
| `06_reproducibility.md` | Exact regeneration commands, provenance, gates |
| `07_scope_and_related_work.md` | What is and is not claimed; related work per module; threats to validity |
| `99_references.md` | Human-readable reference list mirroring `references.bib` |
| `references.bib` | BibTeX entries — real, checkable sources only |
| `config.yaml` | Paper metadata, authors, keywords, render toggles, testing tolerances |
| `preamble.md` | LaTeX packages and the NINE EYES notation macros |
| `AGENTS.md` | The token protocol and how to add a token |
| `SYNTAX.md` | Citation, figure, equation and token syntax for this package |

## The one rule

**Never type a metric into prose.** Add it to
`src/spectre/manuscript_variables.py::generate_variables()`, reference it as
`{{TOKEN}}`, and let the hydration step fill it in. The live cross-reference
test fails on any token without a backing computation, and strict resolution
fails on any token left unsubstituted — together they make the rule
enforceable rather than aspirational.

## Building

```bash
# From the package root, in this order:
uv run python scripts/debrief.py                          # measure (writes the mission record)
uv run python scripts/generate_figures.py                 # figures -> output/figures/
uv run python scripts/z_generate_manuscript_variables.py  # tokens + resolved tree -> output/manuscript/
```

The resolved, token-substituted copies land in `output/manuscript/` — that
directory is generated and git-ignored, so edit the sources here, never the
output.

## Adding a section

Name it `NN_title.md` with a two-digit prefix; the resolver picks up
`[0-9][0-9]_*.md` in sorted order and ignores sidecars such as this README,
`AGENTS.md`, `SYNTAX.md` and `preamble.md`. Keep the canonical numbering
(`00`–`07`, `99`) so the section order matches the rest of the BOND fleet.
