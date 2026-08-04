"""NINE EYES — debrief phase CLI.

Runs the full deterministic mission (brief -> recon -> plan -> execute ->
debrief), prints the debrief lessons, and persists a provenance-outcome
mission record to ``output/data/nine_eyes_debrief.json``.
"""

from __future__ import annotations

import json
from pathlib import Path

import _boot  # noqa: E402,F401 (adds src/ to sys.path)

from bond_api.protocol import ReconRequest, run_mission

from spectre.mission import PROVIDER


def _write_record(record: dict) -> Path:
    target = Path(__file__).resolve().parents[1] / "output" / "data" / "nine_eyes_debrief.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def main() -> None:
    debrief = run_mission(PROVIDER, ReconRequest(goal="assess the Nine Eyes programme"))
    outcome = debrief.outcome
    print(f"Debrief for {PROVIDER.film} ({outcome.provenance.input_hash[:16]}):")
    for lesson in debrief.lessons:
        print(f"  - {lesson}")

    record = {
        "mission_id": f"{PROVIDER.film}-nine-eyes",
        "success": outcome.success,
        "results": outcome.results,
        "provenance": {
            "package_version": outcome.provenance.package_version,
            "seed": outcome.provenance.seed,
            "input_hash": outcome.provenance.input_hash,
            "wall_time_s": outcome.provenance.wall_time_s,
        },
    }
    path = _write_record(record)
    print(f"Record written: {path}")


if __name__ == "__main__":
    main()
