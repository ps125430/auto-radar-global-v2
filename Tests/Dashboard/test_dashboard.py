from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from Scripts.Dashboard.build_dashboard_data import (
    DashboardDataBuilder,
    DashboardDataError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXED_TIME = datetime(2026, 6, 29, 0, 0, tzinfo=timezone.utc)
SOURCE_PATHS = (
    "Runtime/Repository/index/validation_report.json",
    "Knowledge/Daily/2026/2026-06/2026-06-26/prediction.json",
    "Knowledge/MarketMind/2026/2026-06/2026-06-26/market_mind.json",
    "Sandbox/PatternDiscovery/pattern_candidate_registry.json",
    "Sandbox/PatternDiscovery/candidates/PC-001.json",
    "Sandbox/PatternDiscovery/candidates/PC-002.json",
    "Sandbox/PatternDiscovery/candidates/PC-003.json",
    "Sandbox/Review/verified_case_registry.json",
    "Sandbox/Review/verified/VC-101.json",
    "Sandbox/Review/verified/VC-102.json",
    "Sandbox/Review/verified/VC-103.json",
    "Sandbox/Review/verified/VC-104.json",
    "Sandbox/Review/verified/VC-105.json",
    "Sandbox/Ingestion/processed/EV-101.md",
    "Sandbox/Ingestion/processed/EV-102.md",
    "Sandbox/Ingestion/processed/EV-103.md",
    "Sandbox/Ingestion/processed/EV-104.md",
    "Sandbox/Ingestion/processed/EV-105.md",
    "Data/KnowledgeGraph/NODES.json",
    "Data/KnowledgeGraph/EDGES.json",
)


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.values.append(value)

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        for name, value in attrs:
            if name in {"aria-label", "title"} and value:
                self.values.append(value)


def create_repository(root: Path) -> None:
    for relative in SOURCE_PATHS:
        source = REPOSITORY_ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


class DashboardDataTests(unittest.TestCase):
    def test_projection_reads_repository_counts(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertEqual("通過", payload["meta"]["repository_status"])
        self.assertEqual(3, payload["repository"]["pattern_candidates"])
        self.assertEqual(5, payload["repository"]["verified_cases"])
        self.assertEqual(5, payload["repository"]["evidence_records"])

    def test_top_three_uses_pattern_candidates_in_stable_order(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertEqual(
            ["PC-001", "PC-002", "PC-003"],
            [item["id"] for item in payload["opportunities"]],
        )

    def test_similarity_is_not_reused_as_opportunity_score(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertTrue(
            all(
                item["opportunity_score"] is None
                for item in payload["opportunities"]
            )
        )
        self.assertTrue(
            all(
                "不會以相似度替代"
                in item["explainability"]["why_score"]
                for item in payload["opportunities"]
            )
        )

    def test_missing_strategy_and_regime_are_explicit(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertIsNone(payload["strategy"]["name"])
        self.assertIsNone(payload["strategy"]["confidence"])
        self.assertIsNone(payload["regime"]["macro"])
        self.assertIn("今日策略", payload["meta"]["data_gaps"])
        self.assertIn("總經環境", payload["meta"]["data_gaps"])

    def test_pattern_case_evidence_traceability_is_projected(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()
        first = payload["opportunities"][0]

        self.assertEqual(["VC-101", "VC-103"], first["source_cases"])
        self.assertEqual(["EV-101", "EV-103"], first["evidence_ids"])

    def test_empty_graph_has_honest_capital_flow_state(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertEqual(
            "尚無資料", payload["capital_flow"]["status"]
        )
        self.assertEqual([], payload["capital_flow"]["nodes"])
        self.assertIn(
            "目前尚無已驗證資金流資料",
            payload["capital_flow"]["message"],
        )

    def test_write_creates_local_file_safe_javascript(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "dashboard-data.js"
            payload = DashboardDataBuilder(
                REPOSITORY_ROOT,
                output,
                generated_at=FIXED_TIME,
            ).write()
            content = output.read_text(encoding="utf-8")

            self.assertTrue(
                content.startswith("window.AUTO_RADAR_DASHBOARD_DATA = ")
            )
            self.assertIn(payload["opportunities"][0]["id"], content)
            self.assertTrue(content.endswith(";\n"))

    def test_missing_evidence_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            (root / "Sandbox/Ingestion/processed/EV-101.md").unlink()

            with self.assertRaisesRegex(
                DashboardDataError, "Evidence reference is missing"
            ):
                DashboardDataBuilder(root, generated_at=FIXED_TIME).build()

    def test_latest_daily_records_are_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            latest_prediction = (
                root
                / "Knowledge/Daily/2026/2026-06/2026-06-29/prediction.json"
            )
            latest_prediction.parent.mkdir(parents=True)
            latest_prediction.write_text(
                json.dumps(
                    {
                        "status": "draft",
                        "prediction_probability": None,
                        "expected_scenario": "最新核准文字",
                        "prediction_window": "",
                        "expected_risk": [],
                        "notes": "",
                    }
                ),
                encoding="utf-8",
            )

            payload = DashboardDataBuilder(
                root, generated_at=FIXED_TIME
            ).build()

            self.assertEqual(
                "最新核准文字", payload["strategy"]["name"]
            )

    def test_static_dashboard_contains_required_modules(self) -> None:
        html = (REPOSITORY_ROOT / "Dashboard/index.html").read_text(
            encoding="utf-8"
        )

        for section in (
            "今日核心策略",
            "市場狀態",
            "今日前三大機會",
            "資金流地圖",
            "每日戰術面板",
            "決策解釋",
        ):
            self.assertIn(section, html)

    def test_visible_interface_contains_no_prohibited_english(self) -> None:
        html = (REPOSITORY_ROOT / "Dashboard/index.html").read_text(
            encoding="utf-8"
        )
        javascript = (REPOSITORY_ROOT / "Dashboard/app.js").read_text(
            encoding="utf-8"
        )
        parser = VisibleTextParser()
        parser.feed(html)
        visible_text = " ".join(parser.values)

        for phrase in (
            "Daily Command",
            "Overview",
            "Opportunities",
            "Capital Flow",
            "Repository Health",
            "Market Regime",
            "Opportunity Ranking",
            "Strategy Posture",
            "Confidence",
            "Window",
            "Not available",
        ):
            self.assertNotIn(phrase, visible_text)

        for literal in (
            '"Not available"',
            '"Not scored"',
            '"Awaiting validated node"',
            '"Unlinked"',
            '"Capital flow is unavailable."',
            '"Open explainability"',
        ):
            self.assertNotIn(literal, javascript)

    def test_frontend_contains_responsive_and_explainability_contracts(
        self,
    ) -> None:
        css = (REPOSITORY_ROOT / "Dashboard/styles.css").read_text(
            encoding="utf-8"
        )
        javascript = (REPOSITORY_ROOT / "Dashboard/app.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("@media (max-width: 820px)", css)
        self.assertIn("openDrawer", javascript)
        self.assertIn("data-flow-mode", javascript)
        self.assertIn("opportunity_score", javascript)


if __name__ == "__main__":
    unittest.main()
