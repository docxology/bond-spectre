"""NINE EYES — recon phase CLI.

Surveys the canonical Nine Eyes network and SPECTRE brotherhood, logging the
findings returned by the mission provider's ``recon`` step.
"""

from __future__ import annotations

import _boot  # noqa: E402,F401 (adds src/ to sys.path)

from bond_api.protocol import ReconRequest

from spectre.mission import PROVIDER


def main() -> None:
    report = PROVIDER.recon(ReconRequest(goal="survey the Nine Eyes programme and SPECTRE"))
    print(f"Recon for {PROVIDER.film} ({PROVIDER.brief().codename}):")
    for finding in report.findings:
        print(f"  - {finding.label}: {finding.detail}")


if __name__ == "__main__":
    main()
