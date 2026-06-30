"""Build the first readable Shadow Brief from validated Dashboard data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from Scripts.Dashboard.build_dashboard_data import DashboardDataBuilder


def render_shadow_brief(payload: dict[str, Any]) -> str:
    """Render a presentation-only brief from a gated Shadow projection."""
    shadow = payload["shadow_runtime"]
    today = shadow["today"]
    mode = shadow["mode"]
    opportunities = payload["opportunities"]
    top3_lines = "\n".join(
        (
            f"{index}. {item['name']} | 顯示分數 {item['opportunity_score']} | "
            f"觀察窗 {item['window']} | {item['why_now']}"
        )
        for index, item in enumerate(opportunities, start=1)
    )
    risk_lines = "\n".join(
        f"- {item}" for item in today["risk_summary"]
    )
    forbidden_lines = "\n".join(
        f"- {item}" for item in today["forbidden_zone"]
    )
    evidence = sorted(
        {
            evidence_id
            for item in opportunities
            for evidence_id in item["evidence_ids"]
        }
    )
    return "\n".join(
        [
            "# North Star First Real Shadow Brief",
            "",
            "Status: Shadow Runtime Only",
            "Model Impact: shadow_only_not_production",
            "Data Note: 半真實測試輸入，用於驗證資料流，不代表正式市場判斷。",
            "",
            "## 執行狀態",
            "",
            f"- 模式：{mode['label']}",
            f"- 狀態：{mode['status']}",
            f"- Schema：{mode['schema']}",
            f"- 知識庫：{mode['repository']}",
            "",
            "## 今日北極星",
            "",
            today["direction"],
            "",
            "## 今日航向",
            "",
            today["captain_mission"],
            "",
            "## Why Now",
            "",
            today["why_now"],
            "",
            "## 今日 Top3",
            "",
            top3_lines,
            "",
            "## 今日禁航區",
            "",
            forbidden_lines,
            "",
            "## 今日風險",
            "",
            risk_lines,
            "",
            "## Explain Chain",
            "",
            f"- Chain ID：{shadow['explain']['chain_id']}",
            f"- Evidence：{', '.join(evidence)}",
            "- Repository：Dashboard/dashboard-data.js",
            "",
            "## Boundary",
            "",
            "- No Production Runtime",
            "- No Trading Signal",
            "- No Scoring Change",
            "- No Strategy Change",
            "- No Repository Auto-write",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="Reports/Shadow/latest.md",
        help="Repository-relative output path.",
    )
    args = parser.parse_args()

    payload = DashboardDataBuilder(REPOSITORY_ROOT).build()
    output = (REPOSITORY_ROOT / args.output).resolve()
    if not output.is_relative_to(REPOSITORY_ROOT):
        raise ValueError("Shadow Brief output must remain inside Repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_shadow_brief(payload), encoding="utf-8")
    print(f"Shadow Brief built: {output.relative_to(REPOSITORY_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
