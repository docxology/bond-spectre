"""Subprocess smoke tests for the thin NINE EYES CLI scripts.

Runs each script with the venv interpreter from the project root and asserts
exit code 0 plus the expected stdout/artifact side effects — real execution,
no mocks.
"""

from __future__ import annotations

import json
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
