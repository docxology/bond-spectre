# LaTeX Preamble — Spectre NINE EYES

LaTeX packages and macros injected into the PDF build for this package. The
rendering pipeline extracts the fenced `latex` block below and combines it with
`config.yaml` before Pandoc runs; prose outside the block is documentation only
and is not compiled.

Package-specific additions for NINE EYES: `algorithm2e` for the greedy
selection pseudocode used in the methodology, and the `\Cindex` / `\HHI` /
`\Eff` macros so the centralization, concentration and efficiency symbols are
typeset identically everywhere they appear.

```latex
% Core mathematics
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{amsthm}

% Document layout
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{float}
\usepackage{graphicx}

% Tables
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}

% Algorithm typesetting (greedy monitoring allocation / greedy set cover)
\IfFileExists{algorithm2e.sty}{\usepackage[ruled,vlined,linesnumbered]{algorithm2e}}{}

% Code listings
\usepackage{listings}

% Typography
\usepackage{microtype}
\usepackage{xcolor}

% Cross-references and citations
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    allcolors=blue,
    pdftitle={Spectre: NINE EYES},
    pdfsubject={Surveillance-network centralization, criminal-org intelligence, and network geometry}
}
\IfFileExists{cleveref.sty}{\usepackage{cleveref}}{}

% NINE EYES notation
\newcommand{\Cindex}{C_{\mathrm{group}}}   % Freeman group centralization
\newcommand{\HHI}{H}                       % Herfindahl-Hirschman index
\newcommand{\Eff}{E_{\mathrm{glob}}}       % Latora-Marchiori global efficiency
\newcommand{\Cov}{\mathcal{C}}             % interception / sweep coverage
\newcommand{\Org}{\mathcal{O}}             % the brotherhood
\newcommand{\Net}{\mathcal{N}}             % the surveillance network
```

## Notation used in the sections

| Macro | Renders | Meaning |
| --- | --- | --- |
| `\Cindex` | $C_{\mathrm{group}}$ | Freeman group degree centralization, `[0, 1]` |
| `\HHI` | $H$ | Herfindahl–Hirschman flow concentration, `[1/n, 1]` |
| `\Eff` | $E_{\mathrm{glob}}$ | Latora–Marchiori global efficiency |
| `\Cov` | $\mathcal{C}$ | Coverage fraction (interception, cascade, or sweep) |
| `\Org` | $\mathcal{O}$ | The SPECTRE brotherhood (operatives, cells, command tree) |
| `\Net` | $\mathcal{N}$ | The Nine Eyes surveillance network |

Keep this table in step with the macro block above: a macro without a row here
is undocumented notation, and a row without a macro is a dangling reference.
