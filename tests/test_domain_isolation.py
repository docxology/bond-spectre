"""Prove the pure domain core is importable WITHOUT bond-api.

The three (now six) domain modules must remain liftable into any environment;
only the ``mission.py`` adapter imports ``bond_api``. A fresh subprocess imports
each pure module and asserts ``bond_api`` was never pulled into ``sys.modules``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

_IMPORTS = (
    "spectre.surveillance_net",
    "spectre.org_intel",
    "spectre.network_geometry",
    "spectre.traffic_intel",
    "spectre.infiltration",
    "spectre.signal_cover",
)


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


def _with_pythonpath() -> dict[str, str]:
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    return env
