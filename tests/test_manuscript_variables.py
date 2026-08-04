"""Tests for spectre.manuscript_variables — {{TOKEN}} hydration + live refs."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from spectre.manuscript_variables import (
    generate_variables,
    load_manuscript_config,
    resolve_manuscript_tree,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_DIR = PACKAGE_ROOT / "manuscript"


class TestLoadConfig:
    def test_loads(self) -> None:
        config = load_manuscript_config()
        assert "paper" in config
        assert "keywords" in config

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_manuscript_config(tmp_path / "nope.yaml")

    def test_non_mapping_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("- just\n- a\n- list\n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_manuscript_config(bad)


class TestGenerateVariables:
    def test_returns_tokens(self) -> None:
        variables = generate_variables()
        assert variables["SPECTRE_CODENAME"] == "NINE EYES"
        assert variables["SPECTRE_TITLE"].startswith("Spectre")
        assert "SPECTRE_KEYWORDS" in variables

    def test_measured_values_present(self) -> None:
        variables = generate_variables()
        for key in (
            "SPECTRE_CENTRALIZATION_INDEX",
            "SPECTRE_FLOW_CONCENTRATION_HHI",
            "SPECTRE_CASCADE_COVERAGE",
            "SPECTRE_COMPARTMENTALIZATION",
            "SPECTRE_NETWORK_EFFICIENCY",
        ):
            assert float(variables[key]) > 0.0

    def test_counts(self) -> None:
        variables = generate_variables()
        assert int(variables["SPECTRE_NUM_NODES"]) == 9
        assert int(variables["SPECTRE_NUM_OBJECTIVES"]) == 3


class TestLiveReference:
    def test_all_manuscript_tokens_are_generated(self) -> None:
        """Every {{TOKEN}} in the prose sections must exist in generate_variables()."""
        variables = generate_variables()
        token_re = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
        missing: set[str] = set()
        for source in sorted(MANUSCRIPT_DIR.glob("[0-9][0-9]_*.md")):
            for token in token_re.findall(source.read_text(encoding="utf-8")):
                if token not in variables:
                    missing.add(f"{source.name}:{token}")
        assert not missing, f"tokens missing from generate_variables(): {sorted(missing)}"


class TestResolveTree:
    def test_resolves_sections(self, tmp_path: Path) -> None:
        variables = generate_variables()
        out_dir, resolved = resolve_manuscript_tree(
            variables,
            manuscript_dir=MANUSCRIPT_DIR,
            output_dir=tmp_path,
        )
        assert out_dir == tmp_path
        assert resolved
        # No unresolved braces in any resolved file.
        for name in resolved:
            text = (tmp_path / name).read_text(encoding="utf-8")
            assert "{{" not in text

    def test_strict_unresolved_raises(self, tmp_path: Path) -> None:
        manuscript = tmp_path / "ms"
        manuscript.mkdir()
        (manuscript / "00_sample.md").write_text("uses {{UNKNOWN_TOKEN_HERE}} in prose", encoding="utf-8")
        with pytest.raises(ValueError):
            resolve_manuscript_tree({"KNOWN": "x"}, manuscript_dir=manuscript)
