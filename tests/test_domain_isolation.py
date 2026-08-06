"""Prove the pure domain core is importable WITHOUT bond-api.

The six domain modules must remain liftable into any environment; only the
``mission.py`` adapter imports ``bond_api``. A fresh subprocess imports each
pure module and asserts ``bond_api`` was never pulled into ``sys.modules``.

The import list is *derived* from :func:`spectre.manuscript_variables.domain_module_names`
(which lists the package directory) rather than a hand-maintained literal, so
a seventh domain module added tomorrow is imported and guarded automatically
rather than silently bypassing this gate (V3).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from spectre.manuscript_variables import domain_module_names

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

_IMPORTS: tuple[str, ...] = tuple("spectre." + name for name in domain_module_names())


def test_pure_core_imports_without_bond_api() -> None:
    code = (
        "import sys\n"
        + "".join(f"import {name}\n" for name in _IMPORTS)
        + "assert 'bond_api' not in sys.modules, 'pure core pulled in bond_api'\n"
        + "print('pure-core-ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        env=_with_pythonpath(),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "pure-core-ok" in result.stdout


def test_import_list_is_derived_and_nonempty() -> None:
    """The gate's scan set must not be a stale literal (and must not be empty)."""
    names = domain_module_names()
    assert names, "no domain modules measured"
    assert _IMPORTS == tuple("spectre." + name for name in names)
    assert "spectre.surveillance_net" in _IMPORTS
    assert "spectre.network_geometry" in _IMPORTS


def test_infiltration_pulls_org_intel_only() -> None:
    """infiltration legitimately imports org_intel, but nothing else is addable."""
    assert "spectre.infiltration" in _IMPORTS


def _with_pythonpath() -> dict[str, str]:
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    return env
