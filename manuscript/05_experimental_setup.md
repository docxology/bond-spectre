# Experimental Setup

## Dataset

The analysis runs over a fixed canonical dataset declared in
`src/spectre/mission.py`:

* **NINE EYES surveillance network** — {{SPECTRE_NUM_NODES}} agencies
  (``UK, US, CA, AU, NZ, DE, FR, ES, SE``) with {{SPECTRE_NUM_EDGES}} directed
  data-sharing links, the United States at the hub;
* **SPECTRE brotherhood** — {{SPECTRE_NUM_OPERATIVES}} operatives across
  {{SPECTRE_NUM_CELLS}} cells, an apex leader, and one executive layer;
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

* Fixed RNG seed for the influence-cascade activation draws (inside
  `spectre.surveillance_net.cascade_coverage`);
* explicit base seed for the compromise cascade, with per-trial seeds derived
  as `seed + i` (inside `spectre.infiltration.expected_damage`);
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
