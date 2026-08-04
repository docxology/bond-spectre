"""NINE EYES — execute phase CLI.

Runs the mission plan against the pure domain core and prints the measured
results (surveillance centralization, org compartmentalization, critical
nodes) plus the execution provenance.
"""

from __future__ import annotations

import json

import _boot  # noqa: E402,F401 (adds src/ to sys.path)

from spectre.mission import PROVIDER


def main() -> None:
    outcome = PROVIDER.execute(PROVIDER.plan(PROVIDER.brief()))
    print(f"Success: {outcome.success}")
    for key, value in outcome.results.items():
        print(f"  {key}: {value}")
    print("Provenance:")
    print(
        f"  package={outcome.provenance.package_version} seed={outcome.provenance.seed} "
        f"input_hash={outcome.provenance.input_hash[:16]}"
    )
    print("json=" + json.dumps(outcome.results, sort_keys=True))


if __name__ == "__main__":
    main()
