"""NINE EYES — manuscript variable hydration script (runs LAST).

Computes every ``{{TOKEN}}`` for the manuscript from ``manuscript/config.yaml``
plus the deterministic NINE EYES mission metrics, writes
``output/data/manuscript_variables.json``, and resolves the token-substituted
manuscript tree to ``output/manuscript/``.

Strict by default: ``--allow-draft`` relaxes the measured-metrics gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import _boot  # noqa: E402,F401 (adds src/ to sys.path)

from spectre.manuscript_variables import generate_variables, resolve_manuscript_tree


def main() -> None:
    parser = argparse.ArgumentParser(description="Hydrate Spectre manuscript tokens")
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="skip the measured-metrics gate (draft mode)",
    )
    args = parser.parse_args()

    variables = generate_variables(require_outputs=not args.allow_draft)
    root = Path(__file__).resolve().parents[1]
    out_json = root / "output" / "data" / "manuscript_variables.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(variables, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    out_dir, resolved = resolve_manuscript_tree(variables)
    print(f"Wrote {len(variables)} variables -> {out_json}")
    print(f"Resolved {len(resolved)} manuscript sections -> {out_dir}")
    for name in resolved:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
