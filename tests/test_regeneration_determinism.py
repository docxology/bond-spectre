"""The gate for the byte-identical regeneration claim.

`README.md`, `AGENTS.md` and `manuscript/06_reproducibility.md` all state that,
within one software environment, regenerating the artifact set reproduces every
`output/` file byte-for-byte. This module is the only thing that makes that
statement a claim rather than a wish.

The test regenerates the **whole** artifact set twice, in-process for hydration
and by subprocess for the scripts, with more than a wall-clock second between
the two passes, then compares SHA-256 digests file by file. Nothing here injects
a fixed clock: an injected `now` is precisely the test that lets a wall clock
survive in the shipped pipeline, which is how `GENERATION_TIMESTAMP` rendered a
different timestamp into `output/manuscript/06_reproducibility.md` on every run
while the suite stayed green.

Positive control: re-introduce any `datetime.now()` into
`spectre.manuscript_variables.generate_variables` (or drop `sort_keys=True` from
a writer) and these tests go red.
"""

from __future__ import annotations

import ast
import hashlib
import subprocess
import sys
import time
from pathlib import Path

import pytest

from spectre.manuscript_variables import (
    ENVIRONMENT_TOKENS,
    generate_variables,
    load_manuscript_config,
    release_date,
    resolve_manuscript_tree,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"
MANUSCRIPT_DIR = PROJECT_ROOT / "manuscript"

#: Long enough that a re-introduced ISO-8601 stamp at second resolution — the
#: exact shape of the defect this file exists to prevent — differs between the
#: two passes. Without it the positive control would be flaky rather than red.
_TICK_S = 1.1

#: The generator scripts, in the documented run order.
_PIPELINE = ("debrief.py", "generate_figures.py", "z_generate_manuscript_variables.py")


def _digests(root: Path) -> dict[str, str]:
    """SHA-256 of every file under ``root``, keyed by relative path."""
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _run_pipeline() -> None:
    for script in _PIPELINE:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / script)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, f"{script} failed: {result.stderr}"


class TestArtifactSetRegeneratesByteIdentical:
    """The headline claim: two full regenerations, same bytes."""

    def test_full_pipeline_is_byte_identical_across_runs(self) -> None:
        output_dir = PROJECT_ROOT / "output"

        _run_pipeline()
        first = _digests(output_dir)
        assert first, "the pipeline produced no artifacts to compare"

        time.sleep(_TICK_S)

        _run_pipeline()
        second = _digests(output_dir)

        assert sorted(second) == sorted(first), "the two runs produced different artifact sets"
        drifted = sorted(name for name in first if first[name] != second[name])
        assert not drifted, f"artifacts differ between two identical regenerations: {drifted}"

    def test_manuscript_hydration_is_byte_identical_across_runs(self, tmp_path: Path) -> None:
        """The same property for the hydration layer alone, isolated in tmp_path.

        This is the narrow oracle: it fails on a non-deterministic *token*
        even if the scripts' writers are fine.
        """
        first_dir = tmp_path / "first"
        second_dir = tmp_path / "second"

        resolve_manuscript_tree(generate_variables(), manuscript_dir=MANUSCRIPT_DIR, output_dir=first_dir)
        time.sleep(_TICK_S)
        resolve_manuscript_tree(generate_variables(), manuscript_dir=MANUSCRIPT_DIR, output_dir=second_dir)

        assert _digests(first_dir) == _digests(second_dir)

    def test_no_token_value_changes_across_a_wall_clock_tick(self) -> None:
        """Names the drifted tokens, so a failure points at the culprit."""
        first = generate_variables()
        time.sleep(_TICK_S)
        second = generate_variables()

        drifted = sorted(token for token in first if first[token] != second[token])
        assert not drifted, f"token values changed between two runs: {drifted}"


class TestNoWallClockInHydration:
    """Structural guards, so the defect cannot come back quietly."""

    def test_generator_source_never_reads_the_clock(self) -> None:
        """Parsed, not grepped — prose about the clock must not read as a clock.

        A substring scan would fire on this module's own docstrings; it would
        also miss ``from datetime import datetime as d; d.now()``. The AST
        walk asserts two structural facts instead: the hydration module imports
        no time source, and calls nothing named like one.
        """
        source = (PROJECT_ROOT / "src" / "spectre" / "manuscript_variables.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        time_modules = {"time", "datetime", "calendar"}
        imported: set[str] = set()
        called: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    called.add(func.attr)
                elif isinstance(func, ast.Name):
                    called.add(func.id)

        assert not (imported & time_modules), f"hydration imports a time source: {sorted(imported & time_modules)}"
        clock_calls = called & {"now", "utcnow", "today", "time", "monotonic", "timestamp", "time_ns"}
        assert not clock_calls, f"hydration calls a wall clock: {sorted(clock_calls)}"

    def test_release_date_comes_from_committed_config(self) -> None:
        config = load_manuscript_config()
        variables = generate_variables()
        assert variables["SPECTRE_RELEASE_DATE"] == release_date(config)
        assert variables["SPECTRE_RELEASE_DATE"] == str(config["paper"]["date"])
        assert "SPECTRE_RELEASE_DATE" in ENVIRONMENT_TOKENS

    @pytest.mark.parametrize("bad_date", ["", "not-a-date", "2026/08/05", "2026-8-5"])
    def test_missing_or_malformed_date_fails_loudly(self, bad_date: str) -> None:
        """No silent `datetime.now()` fallback — the guard fires instead."""
        with pytest.raises(ValueError, match="paper.date"):
            release_date({"paper": {"date": bad_date}})

    def test_absent_paper_section_fails_loudly(self) -> None:
        with pytest.raises(ValueError, match="paper.date"):
            release_date({})
