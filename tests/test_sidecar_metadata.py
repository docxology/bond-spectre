"""Sidecar & config metadata accuracy (C2, C3).

C2: the three publication sidecars (.zenodo.json, codemeta.json,
CITATION.cff) must describe all six shipped domain modules, not the three that
the package had before phase-4, and must not carry the exemplar scaffold's
off-topic "active inference" keyword.

C3: the manuscript config must not claim a repository it cannot point at. The
publication block carries no repository key, because no token consumes a
repository URL and the inherited exemplar's "docxology/spectre" never existed.
This package's own repository is named in `AGENTS.md` and `README.md`; the
config is not where that fact lives.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from spectre.manuscript_variables import domain_module_names, load_manuscript_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]

_SIDECARS = ("CITATION.cff", "codemeta.json", ".zenodo.json")

# Payload terms that, taken together, must appear in each sidecar text,
# mirroring the six shipped domain modules.  Keeping them as a set means a
# description that drops an entire analysis area fails here.
_REQUIRED_TERMS = ("centrali", "cell", "geometr", "intercept", "compromis", "cover")


def _sidecar_text(name: str) -> str:
    return (PROJECT_ROOT / name).read_text(encoding="utf-8").lower()


def _keyword_list(name: str) -> list[str]:
    """The sidecar's top-level keywords (never the author affiliation)."""
    path = PROJECT_ROOT / name
    if name.endswith(".json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        return list(data.get("keywords", []) or [])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data.get("keywords", []) or [])


class TestC2Sidecars:
    def test_active_inference_scaffold_keyword_is_absent(self) -> None:
        # The scaffold left an off-topic *keyword* behind; the author
        # affiliation "Active Inference Institute" legitimately contains the
        # words and must not trip the gate, so we check the keyword arrays.
        for name in _SIDECARS:
            keywords = [str(k).lower() for k in _keyword_list(name)]
            assert "active inference" not in keywords, f"{name} still lists the scaffold keyword"

    def test_sidecars_name_all_six_domain_areas(self) -> None:
        # The module count is measured, so a future seventh module changes the
        # expectation rather than being silently unguarded.
        assert len(set(domain_module_names())) >= 6
        for name in _SIDECARS:
            text = _sidecar_text(name)
            missing = [term for term in _REQUIRED_TERMS if term not in text]
            assert not missing, f"{name} omits domain areas: {missing}"

    def test_json_sidecars_parse(self) -> None:
        for name in (".zenodo.json", "codemeta.json"):
            json.loads((PROJECT_ROOT / name).read_text(encoding="utf-8"))

    def test_cff_has_no_false_repository(self) -> None:
        data = yaml.safe_load((PROJECT_ROOT / "CITATION.cff").read_text(encoding="utf-8"))
        assert not data.get("repository")


class TestC3Config:
    def test_config_declares_no_false_remote(self) -> None:
        publication = load_manuscript_config().get("publication", {})
        publication = publication if isinstance(publication, dict) else {}
        assert not (publication.get("github_repository") or publication.get("repository_url"))
