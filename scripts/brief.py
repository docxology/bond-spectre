"""NINE EYES — brief phase CLI.

Prints the mission brief (identity, objectives, assets, constraints) from the
deterministic SPECTRE mission provider.
"""

from __future__ import annotations

import _boot  # noqa: E402,F401 (adds src/ to sys.path)

from spectre.mission import PROVIDER


def main() -> None:
    brief = PROVIDER.brief()
    print(f"Film:      {brief.film}")
    print(f"Codename:  {brief.codename}")
    print("Objectives:")
    for objective in brief.objectives:
        print(f"  - {objective}")
    print("Assets:")
    for asset in brief.assets:
        print(f"  - {asset.kind}:{asset.name}")
    print("Constraints:")
    for constraint in brief.constraints:
        print(f"  - {constraint.kind}: {constraint.detail}")


if __name__ == "__main__":
    main()
