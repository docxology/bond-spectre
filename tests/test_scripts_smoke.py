"""Subprocess smoke tests for the thin NINE EYES CLI scripts.

Runs each script with the venv interpreter from the project root and asserts
exit code 0 plus the expected stdout/artifact side effects — real execution,
no mocks.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"


def _run(script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestMissionPhaseScripts:
    def test_brief(self) -> None:
        result = _run("brief.py")
        assert result.returncode == 0, result.stderr
        assert "NINE EYES" in result.stdout
        assert "spectre" in result.stdout

    def test_recon(self) -> None:
        result = _run("recon.py")
        assert result.returncode == 0, result.stderr
        assert "Recon" in result.stdout

    def test_plan(self) -> None:
        result = _run("plan.py")
        assert result.returncode == 0, result.stderr
        assert "Steps" in result.stdout or "Plan" in result.stdout

    def test_execute(self) -> None:
        result = _run("execute.py")
        assert result.returncode == 0, result.stderr
        assert "centralization_index" in result.stdout

    def test_debrief_writes_record(self) -> None:
        result = _run("debrief.py")
        assert result.returncode == 0, result.stderr
        record = PROJECT_ROOT / "output" / "data" / "nine_eyes_debrief.json"
        assert record.exists()
        data = json.loads(record.read_text(encoding="utf-8"))
        assert data["success"] is True
        assert data["provenance"]["input_hash"]


class TestManuscriptScript:
    def test_generate_variables(self) -> None:
        result = _run("z_generate_manuscript_variables.py", "--allow-draft")
        assert result.returncode == 0, result.stderr
        variables_path = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
        assert variables_path.exists()
        data = json.loads(variables_path.read_text(encoding="utf-8"))
        assert data["SPECTRE_CODENAME"] == "NINE EYES"
        # The resolved manuscript tree should have no leftover braces.
        resolved = PROJECT_ROOT / "output" / "manuscript"
        assert list(resolved.glob("*.md"))


class TestFigureScript:
    def test_generate_figures(self) -> None:
        result = _run("generate_figures.py")
        assert result.returncode == 0, result.stderr
        figure = PROJECT_ROOT / "output" / "figures" / "network_flow_centralization.png"
        assert figure.exists()
        assert figure.stat().st_size > 0


class TestFigureDeployment:
    """C1: every image embed in the resolved manuscript must resolve to a file."""

    def test_every_embedded_figure_resolves_from_resolved_manuscript(self) -> None:
        result = _run("z_generate_manuscript_variables.py", "--allow-draft")
        assert result.returncode == 0, result.stderr
        result = _run("generate_figures.py")
        assert result.returncode == 0, result.stderr

        manuscript_dir = PROJECT_ROOT / "output" / "manuscript"
        refs: list[tuple[str, str]] = []
        for md in manuscript_dir.glob("*.md"):
            for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", md.read_text(encoding="utf-8")):
                refs.append((md.name, match.group(1)))
        assert refs, "no image references found in the resolved manuscript"
        for fname, ref in refs:
            target = (manuscript_dir / ref).resolve()
            assert target.exists(), f"{fname}: embedded figure {ref!r} does not resolve"


class TestRecordCanonicality:
    """V1 half: the persisted record must be canonical key-sorted JSON.

    Dropping ``sort_keys=True`` from a writer would not change two identical
    runs (insertion order is stable), so the run-to-run determinism test cannot
    catch it; this asserts the bytes equal the key-sorted re-serialization, so
    the flag is load-bearing.
    """

    def test_persisted_record_is_key_sorted(self) -> None:
        result = _run("debrief.py")
        assert result.returncode == 0, result.stderr
        path = PROJECT_ROOT / "output" / "data" / "nine_eyes_debrief.json"
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        assert raw == json.dumps(data, indent=2, sort_keys=True) + "\n", (
            "persisted debrief record is not key-sorted canonical JSON"
        )
