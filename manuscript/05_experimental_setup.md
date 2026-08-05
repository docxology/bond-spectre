# Experimental Setup

## Dataset

The analysis runs over a fixed canonical dataset declared in
`src/spectre/mission.py`:

* **NINE EYES surveillance network** — {{SPECTRE_NUM_NODES}} agencies
  (``UK, US, CA, AU, NZ, DE, FR, ES, SE``) with {{SPECTRE_NUM_EDGES}} directed
  data-sharing links, the United States at the hub;
* **SPECTRE brotherhood** — {{SPECTRE_NUM_OPERATIVES}} operatives across
  {{SPECTRE_NUM_CELLS}} cells, an apex leader, and one executive layer. The
  roster is a *distinct-person* roster: exactly one node per film character.
  An earlier revision of this dataset carried "Franz Oberhauser" (Blofeld's
  birth name — the same character) and both "Hinx" and "Bautista" (Mr Hinx
  again, the latter under his actor's surname) as separate operatives, which
  inflated the operative count and manufactured the executive layer that the
  hierarchy height then reported. Those aliases are gone;
* **Brotherhood edges are a modelling construct.** The film establishes
  Blofeld at the apex, Mr Hinx as an enforcer, Mr White as a former member,
  Madeleine Swann as his daughter and C as an inside collaborator, but it
  publishes no org chart. The cell assignment and the `superior → subordinate`
  edges are therefore chosen, not observed; the only fidelity claim made is
  that no two nodes are the same person;
* **Traffic scenario** — the same agency set carrying volume-weighted links
  (`spectre.traffic_intel.canonical_traffic_network`), sized so that no single
  agency observes the whole exchange and the interception problem is
  non-trivial;
* **Placement scenario** — an agency × target coverage matrix over eight sweep
  regions (`spectre.signal_cover.canonical_coverage_problem`), with deliberate
  cross-coverage so the greedy cover needs several agencies and retains
  measurable redundancy.

The network and brotherhood definitions are the ones hashed into the
provenance record; the traffic and placement scenarios are constructed by their
own modules and are fixed constants of those modules.

## Determinism

* One base seed, `_SEED` in `spectre.mission`, governs both cascades: it is
  passed to `spectre.surveillance_net.expected_cascade_coverage` and to
  `spectre.infiltration.expected_damage`, and each derives per-trial seeds as
  `seed + i`. The seed recorded in `Provenance` is therefore the seed the
  reported numbers were produced under — changing it changes them;
* fixed layout seed in the figure generator;
* deterministic tie-breaking by label in both greedy selections, so the results
  do not depend on input ordering;
* no wall-clock in persisted artifacts (``Provenance.wall_time_s == 0.0``);
* execution provenance carries a canonical SHA-256 ``input_hash`` of the
  mission inputs.

## Software environment

* Python {{PYTHON_VERSION}} on {{PLATFORM}}
* Numpy for numerical arrays, matplotlib for figure rendering, PyYAML for
  configuration, `bond_api` (FROZEN protocol) for the mission contract.
* The {{SPECTRE_NUM_DOMAIN_MODULES}} domain modules
  ({{SPECTRE_DOMAIN_MODULES}}) import only numpy and the standard library, so
  they run outside this environment unchanged.

## Mission flow

The provider implements the five FROZEN stages — ``brief``, ``recon``,
``plan``, ``execute``, ``debrief`` — declaring {{SPECTRE_NUM_OBJECTIVES}}
objectives and executing a {{SPECTRE_PLAN_STEPS}}-step plan, one step per
domain module. It also registers {{SPECTRE_NUM_GADGETS}} Q-branch gadgets for
cross-package use.
