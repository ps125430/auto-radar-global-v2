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
from Scripts.Shadow.build_shadow_brief import render_shadow_brief


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
    "Data/ShadowInput/sample_real_input_v1.json",
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
            ["SHADOW-OPP-001", "SHADOW-OPP-002", "SHADOW-OPP-003"],
            [item["id"] for item in payload["opportunities"]],
        )

    def test_shadow_display_score_is_labeled_as_input_not_calculation(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertEqual([86, 82, 78], [
            item["opportunity_score"] for item in payload["opportunities"]
        ])
        self.assertTrue(
            all(
                item["score_status"] == "sample_shadow_input"
                and "不是 Runtime 計算結果"
                in item["explainability"]["why_score"]
                for item in payload["opportunities"]
            )
        )

    def test_shadow_input_populates_strategy_and_regime(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertEqual("AI 基礎建設供應鏈", payload["strategy"]["name"])
        self.assertIsNone(payload["strategy"]["confidence"])
        self.assertEqual("風險偏好中性偏多", payload["regime"]["macro"])
        self.assertNotIn("今日策略", payload["meta"]["data_gaps"])
        self.assertNotIn("總經環境", payload["meta"]["data_gaps"])

    def test_pattern_case_evidence_traceability_is_projected(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()
        first = payload["opportunities"][0]

        self.assertEqual([], first["source_cases"])
        self.assertEqual(["EV-101", "EV-103"], first["evidence_ids"])

    def test_shadow_input_populates_capital_flow_path(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertEqual(
            "已有資料", payload["capital_flow"]["status"]
        )
        self.assertEqual(
            ["美國 AI 基礎建設", "HBM", "散熱", "電力", "CPO"],
            [item["name"] for item in payload["capital_flow"]["nodes"]],
        )
        self.assertEqual(4, len(payload["capital_flow"]["edges"]))

    def test_shadow_runtime_projection_drives_daily_dashboard_fields(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()
        shadow = payload["shadow_runtime"]

        self.assertEqual("shadow_dashboard_projection", shadow["status"])
        self.assertEqual("Shadow Runtime", shadow["mode"]["label"])
        self.assertEqual("Read Only", shadow["mode"]["repository"])
        self.assertFalse(shadow["mode"]["production_authorized"])
        self.assertTrue(shadow["today"]["direction"])
        self.assertTrue(shadow["today"]["captain_mission"])
        self.assertTrue(shadow["today"]["market_story"])
        self.assertTrue(shadow["today"]["daily_brief"])
        self.assertTrue(shadow["today"]["risk_summary"])
        self.assertTrue(shadow["today"]["why_now"])
        self.assertIn("yesterday", shadow["timeline"])
        self.assertIn("today", shadow["timeline"])
        self.assertIn("tomorrow", shadow["timeline"])
        self.assertIn("nodes", shadow["explain"])

    def test_dashboard_binding_uses_single_shadow_waiting_message(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()

        self.assertEqual(
            "Waiting for today's shadow run...",
            payload["shadow_runtime"]["waiting_message"],
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

    def test_first_shadow_brief_contains_complete_data_flow(self) -> None:
        payload = DashboardDataBuilder(
            REPOSITORY_ROOT, generated_at=FIXED_TIME
        ).build()
        brief = render_shadow_brief(payload)

        for section in (
            "今日北極星",
            "今日航向",
            "Why Now",
            "今日 Top3",
            "今日禁航區",
            "今日風險",
            "Explain Chain",
        ):
            self.assertIn(section, brief)
        self.assertIn("AI 基礎建設供應鏈", brief)
        self.assertIn("EV-101", brief)
        self.assertNotIn("Placeholder", brief)
        self.assertNotIn("Not Available", brief)
        self.assertNotIn("Awaiting", brief)

    def test_shadow_input_schema_is_valid_json_schema_candidate(self) -> None:
        schema = json.loads(
            (
                REPOSITORY_ROOT
                / "Schemas/Runtime/shadow_input.schema.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema",
            schema["$schema"],
        )
        self.assertEqual(
            "shadow_input_candidate",
            schema["properties"]["status"]["const"],
        )
        self.assertFalse(schema["x-runtime"]["algorithm"])
        self.assertFalse(schema["x-runtime"]["production_authorized"])

    def test_missing_evidence_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            (root / "Sandbox/Ingestion/processed/EV-101.md").unlink()

            with self.assertRaisesRegex(
                DashboardDataError, "Evidence reference does not exist"
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
                "AI 基礎建設供應鏈", payload["strategy"]["name"]
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
            "Shadow Runtime",
            "North Star Timeline",
            "Daily Brief",
        ):
            self.assertIn(section, html)

    def test_north_star_mission_control_contract(self) -> None:
        html = (REPOSITORY_ROOT / "Dashboard/index.html").read_text(
            encoding="utf-8"
        )
        css = (REPOSITORY_ROOT / "Dashboard/styles.css").read_text(
            encoding="utf-8"
        )
        javascript = (REPOSITORY_ROOT / "Dashboard/app.js").read_text(
            encoding="utf-8"
        )

        for module in (
            "今日北極星",
            "我的船",
            "禁航區",
            "前三大機會雷達",
            "全球洋流圖",
            "資金方向",
            "敘事強弱",
            "市場環境",
            "資料健康度",
            "資金足跡",
            "籌碼擁擠",
            "主題動能",
            "傳導速度",
            "今天市場在說什麼",
            "每日學習",
            "演化狀態",
            "檢討佇列",
            "Shadow Runtime",
            "North Star Timeline",
            "Daily Brief",
        ):
            self.assertIn(module, html)

        for card_contract in (
            "card-header",
            "card-score",
            "card-trend",
            "card-meta",
            "card-why",
            "card-evidence",
        ):
            self.assertIn(card_contract, html)
            self.assertIn(card_contract, css)

        for route_node in ("美國", "台灣", "HBM", "散熱", "PCB"):
            self.assertIn(route_node, javascript)

        self.assertIn("概念航線 · 尚無已驗證資金流", javascript)
        self.assertIn("shadow_runtime", javascript)
        self.assertIn("direction-explain-button", html)
        self.assertIn("renderShadowExplainContent", javascript)
        self.assertNotIn("AI Infrastructure", html + javascript)
        self.assertNotIn("91%", html + javascript)
        self.assertNotIn("gradient", css)

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
            "Awaiting Node",
            "Placeholder",
        ):
            self.assertNotIn(phrase, visible_text)

        for literal in (
            '"Not available"',
            '"Not scored"',
            '"Awaiting validated node"',
            '"Unlinked"',
            '"Capital flow is unavailable."',
            '"Open explainability"',
            '"Placeholder"',
            '"Awaiting Node"',
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
