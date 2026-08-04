"""Pytest configuration for the Spectre / NINE EYES tests."""

from __future__ import annotations

import os
import sys

# Force headless backend for matplotlib in tests.
os.environ.setdefault("MPLBACKEND", "Agg")

# Add src/ to the path so the documented per-project pytest command works from
# a clean environment (the pyproject pythonpath handles it too; this makes it
# explicit and robust).
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
for _path in (SRC,):
    if _path not in sys.path:
        sys.path.insert(0, _path)
