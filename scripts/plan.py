"""NINE EYES — plan phase CLI.

Plans the deterministic analysis steps for the mission brief.
"""

from __future__ import annotations

import _boot  # noqa: E402,F401 (adds src/ to sys.path)

from spectre.mission import PROVIDER


def main() -> None:
    plan = PROVIDER.plan(PROVIDER.brief())
    print(f"Plan for {PROVIDER.brief().codename} ({len(plan.steps)} steps):")
    for step in plan.steps:
        print(f"  - {step.name} -> {step.action} {step.params}")


if __name__ == "__main__":
    main()
