# Manuscript syntax — Spectre NINE EYES

Package-specific syntax reference: the `{{TOKEN}}` table, the figure registry,
equation labelling, and citation keys for the `spectre` manuscript. Read
[`AGENTS.md`](AGENTS.md) first for the token *protocol*; this file is the
*syntax*.

## Tokens

Tokens are written `{{UPPER_SNAKE}}` and resolved by
`src/spectre/manuscript_variables.py::generate_variables()`. Anything else —
including a single-brace `{TOKEN}` — is left untouched and will read as literal
text.

### Identity and metadata

| Token | Source |
| --- | --- |
| `{{SPECTRE_IDENTITY}}` | Constant `SPECTRE` |
| `{{SPECTRE_CODENAME}}` | Constant `NINE EYES` |
| `{{SPECTRE_TITLE}}`, `{{SPECTRE_SUBTITLE}}`, `{{SPECTRE_VERSION}}` | `config.yaml` → `paper` |
| `{{SPECTRE_KEYWORDS}}` | `config.yaml` → `keywords`, comma-joined |

### Package inventory (measured, not typed)

| Token | Source |
| --- | --- |
| `{{SPECTRE_NUM_DOMAIN_MODULES}}`, `{{SPECTRE_DOMAIN_MODULES}}` | `domain_module_names()` — a listing of the package directory |
| `{{SPECTRE_NUM_GADGETS}}` | `mission.gadget_names()` — the registration table |
| `{{SPECTRE_PLAN_STEPS}}` | `execute()` result `plan_steps` |
| `{{SPECTRE_NUM_OBJECTIVES}}` | `brief().objectives` |

### Dataset scale

| Token | Source |
| --- | --- |
| `{{SPECTRE_NUM_NODES}}`, `{{SPECTRE_NUM_EDGES}}` | `NINE_EYES_NODES` / `NINE_EYES_EDGES` |
| `{{SPECTRE_NUM_OPERATIVES}}`, `{{SPECTRE_NUM_CELLS}}` | `SPECTRE_OPERATIVES`; measured `cell_count` |

### Measured results

| Token | Computed by |
| --- | --- |
| `{{SPECTRE_CENTRALIZATION_INDEX}}` | `surveillance_net.group_centralization` (star bound `n − 1`) |
| `{{SPECTRE_FLOW_CONCENTRATION_HHI}}` | `surveillance_net.herfindahl_index` over `data_share_centrality` |
| `{{SPECTRE_FLOW_CONCENTRATION_FLOOR}}`, `{{SPECTRE_NUM_RECEIVING_AGENCIES}}` | `surveillance_net.uniform_share_index` — never quote the HHI without its floor |
| `{{SPECTRE_CASCADE_COVERAGE}}`, `{{SPECTRE_CASCADE_TRIALS}}` | `surveillance_net.expected_cascade_coverage` (trial mean, not one draw) |
| `{{SPECTRE_HIERARCHY_HEIGHT}}`, `{{SPECTRE_CHAIN_COMPLETE}}` | `org_intel.hierarchy_stats` |
| `{{SPECTRE_COMPARTMENTALIZATION}}` | `org_intel.compartmentalization` |
| `{{SPECTRE_NUM_ARTICULATION_POINTS}}`, `{{SPECTRE_ARTICULATION_NODES}}` | `network_geometry.articulation_points` |
| `{{SPECTRE_NETWORK_EFFICIENCY}}` | `network_geometry.network_efficiency` |
| `{{SPECTRE_CRITICAL_NODES}}` | `network_geometry.critical_node_order` |
| `{{SPECTRE_TRAFFIC_TOTAL}}`, `{{SPECTRE_TRAFFIC_TOP_LINK}}` | `traffic_intel.total_traffic` / `heavy_hitters` |
| `{{SPECTRE_MONITOR_ALLOCATION}}`, `{{SPECTRE_MONITOR_COVERAGE}}` | `traffic_intel.monitor_allocation` |
| `{{SPECTRE_COMPROMISE_FRACTION}}`, `{{SPECTRE_LEADERSHIP_HIT_RATE}}`, `{{SPECTRE_MEAN_STEPS_TO_LEADERSHIP}}` | `infiltration.expected_damage` |
| `{{SPECTRE_SET_COVER_SIZE}}`, `{{SPECTRE_SET_COVER_SELECTION}}`, `{{SPECTRE_COVER_REDUNDANCY}}`, `{{SPECTRE_UNCOVERED_AFTER_COVER}}` | `signal_cover.greedy_set_cover` / `redundancy_index` / `uncovered_targets` |

### Environment

| Token | Source |
| --- | --- |
| `{{PYTHON_VERSION}}`, `{{PLATFORM}}` | `platform` module at hydration time — the only environment-dependent values in the artifact set |
| `{{SPECTRE_RELEASE_DATE}}` | `paper.date` in `manuscript/config.yaml` — a committed input, validated as `YYYY-MM-DD`. There is **no** wall-clock value anywhere in the artifacts: hydration never calls `datetime.now()`, which is what makes the byte-identical regeneration claim true |

## Citations

```markdown
[@Freeman1979]                 <!-- single -->
[@Tarjan1972; @Latora2001]     <!-- multiple -->
@Nemhauser1978 proved ...      <!-- narrative -->
```

Every key must exist in [`references.bib`](references.bib). Never write a raw
`\cite{}` in Markdown. Current keys:

`Freeman1979`, `Newman2010`, `Brandes2001`, `Tarjan1972`, `HopcroftTarjan1973`,
`Latora2001`, `Albert2000`, `Borgatti2006`, `Hirschman1964`, `Kempe2003`,
`Newman2002`, `Nemhauser1978`, `Leskovec2007`, `Johnson1974`, `Feige1998`.

**Do not invent a reference.** If you are not certain a source exists as
described, remove it rather than ship it.

## Figures

```markdown
![Caption text.](figures/network_flow_centralization.png){#fig:network_flow_centralization}
![Caption text.](figures/brotherhood_cascade.png){#fig:brotherhood_cascade}
```

| Figure | Generator | Referenced in |
| --- | --- | --- |
| `network_flow_centralization.png` | `src/spectre/figures/networks.py::plot_network_flow_centralization` | `03_results.md` |
| `brotherhood_cascade.png` | `src/spectre/figures/networks.py::plot_brotherhood_cascade` | `03_results.md` |

Paths are relative to the resolved manuscript in `output/manuscript/`; the
figure must be generated before rendering or the reference dangles.  Both
PNGs are mirrored into `output/manuscript/figures/` by
`scripts/generate_figures.py`, and a test resolves every embedded path from the
resolved tree to prove it.

## Equations

```markdown
$$
\Cindex = \frac{\sum_i (s_{\max} - s_i)}{(n - 1)\, s_{\max}}
$$ {#eq:group_centralization}
```

Macros such as `\Cindex`, `\HHI` and `\Eff` are defined in
[`preamble.md`](preamble.md); use them instead of respelling the symbols.
Reference an equation as `[@eq:group_centralization]`.

## What the resolver touches

Only `NN_*.md` section files are copied to `output/manuscript/` with tokens
substituted. `README.md`, `AGENTS.md`, `SYNTAX.md`, `preamble.md`,
`config.yaml` and `references.bib` are sidecars: they are read by the build or
by humans, never token-resolved. Strict mode (the default) fails the resolution
if any `{{TOKEN}}` survives substitution.
