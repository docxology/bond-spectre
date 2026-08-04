# Experimental Setup

## Dataset

The analysis runs over a fixed canonical dataset declared in
`src/spectre/mission.py`:

* **NINE EYES surveillance network** — {{SPECTRE_NUM_NODES}} agencies
  (``UK, US, CA, AU, NZ, DE, FR, ES, SE``) with {{SPECTRE_NUM_EDGES}} directed
  data-sharing links, the United States at the hub;
* **SPECTRE brotherhood** — {{SPECTRE_NUM_OPERATIVES}} operatives across
  {{SPECTRE_NUM_CELLS}} cells, an apex leader, and one executive layer.

## Determinism

* Fixed RNG seed for the influence-cascade activation draws (inside
  `spectre.surveillance_net.cascade_coverage`);
* fixed layout seed in the figure generator;
* no wall-clock in persisted artifacts (``Provenance.wall_time_s == 0.0``);
* execution provenance carries a canonical SHA-256 ``input_hash`` of the
  mission inputs.

## Software environment

* Python {{PYTHON_VERSION}} on {{PLATFORM}}
* Numpy for numerical arrays, matplotlib for figure rendering, PyYAML for
  configuration, `bond_api` (FROZEN protocol) for the mission contract.

## Mission flow

The provider implements the five FROZEN stages — ``brief``, ``recon``,
``plan``, ``execute``, ``debrief`` — with {{SPECTRE_NUM_OBJECTIVES}} objectives.
