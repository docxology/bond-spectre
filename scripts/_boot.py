"""Shared sys.path bootstrap for Spectre CLI scripts.

Thin scripts are invoked from the project root as ``uv run python
scripts/<phase>.py``; Python puts only ``scripts/`` on ``sys.path``, so this
module inserts ``src/`` (where the ``spectre`` package lives) before any
``spectre`` import. Import it for its side effect only.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
