"""Reconciliation gate for ``data/claim_ledger.yaml``.

The README and ``manuscript/06_reproducibility.md`` both say the ledger
carries the current value of *every* measured claim. Before this file that was
prose: the ledger held 11 rows against ~30 measured tokens and nothing checked
either the coverage or the values. These tests make the sentence enforceable —
a measured token with no row, a row for a token that is no longer measured, or
a recorded value that no longer matches the code all fail here.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spectre.manuscript_variables import (
    ENVIRONMENT_TOKENS,
    generate_variables,
    load_claim_ledger,
    measured_tokens,
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = PACKAGE_ROOT / "data" / "claim_ledger.yaml"


class TestLedgerCoverage:
    def test_every_measured_token_has_a_row(self) -> None:
        measured = set(measured_tokens(generate_variables()))
        rows = set(load_claim_ledger())
        assert measured - rows == set(), "measured tokens missing from the claim ledger"

    def test_no_row_claims_an_unmeasured_token(self) -> None:
        measured = set(measured_tokens(generate_variables()))
        rows = set(load_claim_ledger())
        assert rows - measured == set(), "claim ledger rows for tokens no longer measured"

    def test_environment_tokens_are_excluded_and_non_empty(self) -> None:
        variables = generate_variables()
        assert ENVIRONMENT_TOKENS <= set(variables)
        assert set(load_claim_ledger()).isdisjoint(ENVIRONMENT_TOKENS)
        # A vacuous partition (everything environmental) would make the two
        # tests above trivially true.
        assert len(measured_tokens(variables)) > len(ENVIRONMENT_TOKENS)


class TestLedgerValues:
    def test_recorded_values_match_the_measured_values(self) -> None:
        variables = generate_variables()
        rows = load_claim_ledger()
        drift = {
            token: (row["value"], variables[token])
            for token, row in rows.items()
            if str(row["value"]) != variables[token]
        }
        assert drift == {}, f"claim ledger drift (recorded, measured): {drift}"

    def test_rows_carry_provenance_fields(self) -> None:
        for token, row in load_claim_ledger().items():
            for field in ("claim_id", "kind", "source", "source_tier", "freshness"):
                assert row.get(field), f"{token} row is missing {field}"


class TestLedgerLoaderRejectsBadFiles:
    """The loader's guards are reachable and fire — no unfalsifiable branches."""

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_claim_ledger(tmp_path / "absent.yaml")

    def test_non_mapping_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "ledger.yaml"
        path.write_text("- not\n- a mapping\n", encoding="utf-8")
        with pytest.raises(ValueError, match="claims"):
            load_claim_ledger(path)

    def test_row_without_token_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "ledger.yaml"
        path.write_text('claims:\n  - claim_id: x\n    value: "1"\n', encoding="utf-8")
        with pytest.raises(ValueError, match="without a 'token'"):
            load_claim_ledger(path)

    def test_duplicate_token_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "ledger.yaml"
        path.write_text(
            'claims:\n  - {claim_id: a, token: T, value: "1"}\n  - {claim_id: b, token: T, value: "2"}\n',
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="two rows for token"):
            load_claim_ledger(path)


class TestLedgerGateCanFail:
    """Positive control: perturbing a recorded value must be detected.

    Written against a real copy of the shipped ledger on disk, so it proves the
    comparison itself is live rather than that a hand-built fixture mismatches.
    """

    def test_a_perturbed_value_is_detected(self, tmp_path: Path) -> None:
        data = yaml.safe_load(LEDGER_PATH.read_text(encoding="utf-8"))
        target = next(row for row in data["claims"] if row["token"] == "SPECTRE_FLOW_CONCENTRATION_HHI")
        target["value"] = "0.1250"  # the value the degenerate metric produced
        broken = tmp_path / "claim_ledger.yaml"
        broken.write_text(yaml.safe_dump(data), encoding="utf-8")

        variables = generate_variables()
        rows = load_claim_ledger(broken)
        drift = {
            token: (row["value"], variables[token])
            for token, row in rows.items()
            if str(row["value"]) != variables[token]
        }
        assert "SPECTRE_FLOW_CONCENTRATION_HHI" in drift

    def test_a_dropped_row_is_detected(self, tmp_path: Path) -> None:
        data = yaml.safe_load(LEDGER_PATH.read_text(encoding="utf-8"))
        data["claims"] = [row for row in data["claims"] if row["token"] != "SPECTRE_CASCADE_COVERAGE"]
        broken = tmp_path / "claim_ledger.yaml"
        broken.write_text(yaml.safe_dump(data), encoding="utf-8")

        measured = set(measured_tokens(generate_variables()))
        assert measured - set(load_claim_ledger(broken)) == {"SPECTRE_CASCADE_COVERAGE"}
