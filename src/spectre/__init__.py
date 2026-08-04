"""Spectre — mission codename NINE EYES.

A BOND film package modelling the global surveillance-network analysis of the
Nine Eyes programme (data flows, centralization), the SPECTRE brotherhood's
criminal-org intelligence model (hierarchy, cells), and network geometry
(connectivity, critical nodes).

The three pure domain modules (:mod:`spectre.surveillance_net`,
:mod:`spectre.org_intel`, :mod:`spectre.network_geometry`) are infrastructure-
**and** bond-api-free: they import only ``numpy`` and the standard library, so
they can be lifted and run in any environment. The ``bond-api`` contract lives
exclusively in :mod:`spectre.mission` (the thin ``MissionProvider`` adapter),
which is intentionally NOT re-exported here so importing ``spectre`` never
requires ``bond-api``.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
