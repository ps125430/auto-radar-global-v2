"""Run the bounded E-146 through E-150 Shadow Daily Intelligence Loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from Runtime.NorthStar import DailyIntelligenceLoop
from Scripts.Dashboard.build_dashboard_data import DashboardDataBuilder


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-06-30")
    parser.add_argument(
        "--outcome",
        default="Data/ShadowInput/manual_outcome_2026-06-30.json",
    )
    args = parser.parse_args()

    outcome_path = (REPOSITORY_ROOT / args.outcome).resolve()
    if not outcome_path.is_relative_to(REPOSITORY_ROOT):
        raise ValueError("Outcome input must remain inside Repository")
    manual_outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
    dashboard_payload = DashboardDataBuilder(REPOSITORY_ROOT).build()
    loop = DailyIntelligenceLoop(REPOSITORY_ROOT / "Runtime/NorthStar")
    result = loop.run(
        dashboard_payload=dashboard_payload,
        manual_outcome=manual_outcome,
        record_date=args.date,
    )

    for name, path in result["paths"].items():
        print(f"{name}: {path.relative_to(REPOSITORY_ROOT)}")
    print("Repository read only: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
