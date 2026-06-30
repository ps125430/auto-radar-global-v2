from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from Runtime.NorthStar import (
    DailyIntelligenceError,
    DailyIntelligenceLoop,
    OutcomeCollector,
    ShadowRecordWriter,
)
from Scripts.Dashboard.build_dashboard_data import DashboardDataBuilder


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXED_TIME = datetime(2026, 6, 30, 8, 20, tzinfo=timezone.utc)
OUTCOME_PATH = (
    REPOSITORY_ROOT
    / "Data/ShadowInput/manual_outcome_2026-06-30.json"
)


def repository_fingerprint(root: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        records.append(
            (
                path.relative_to(root).as_posix(),
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )
    return records


class DailyIntelligenceLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dashboard = DashboardDataBuilder(
            REPOSITORY_ROOT,
            generated_at=FIXED_TIME,
        ).build()
        self.manual_outcome = json.loads(
            OUTCOME_PATH.read_text(encoding="utf-8")
        )

    def test_daily_loop_saves_all_five_review_records(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            runtime_root = Path(temporary_directory) / "Runtime/NorthStar"
            result = DailyIntelligenceLoop(runtime_root).run(
                dashboard_payload=self.dashboard,
                manual_outcome=self.manual_outcome,
                record_date="2026-06-30",
                generated_at=FIXED_TIME,
            )

            self.assertEqual(
                {
                    "snapshot",
                    "outcome",
                    "residual",
                    "root_cause",
                    "reflection",
                },
                set(result["paths"]),
            )
            self.assertTrue(all(path.is_file() for path in result["paths"].values()))
            self.assertTrue(result["repository_read_only"])
            self.assertFalse(result["production_authorized"])
            self.assertFalse(result["automatic_merge"])

    def test_snapshot_preserves_today_brain_without_confidence_calculation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = DailyIntelligenceLoop(temporary_directory).run(
                dashboard_payload=self.dashboard,
                manual_outcome=self.manual_outcome,
                record_date="2026-06-30",
                generated_at=FIXED_TIME,
            )
            snapshot = result["records"]["snapshot"]

            self.assertEqual("AI 基礎建設供應鏈", snapshot["north_star"])
            self.assertEqual(["HBM", "散熱", "電力"], [
                item["symbol"] for item in snapshot["top3"]
            ])
            self.assertEqual([5, 4, 4], [
                item["expectation_stars"] for item in snapshot["top3"]
            ])
            self.assertIsNone(snapshot["confidence"]["value"])
            self.assertFalse(snapshot["confidence"]["calculated_by_loop"])
            self.assertTrue(snapshot["explain_chain"]["nodes"])

    def test_residual_and_accuracy_are_review_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = DailyIntelligenceLoop(temporary_directory).run(
                dashboard_payload=self.dashboard,
                manual_outcome=self.manual_outcome,
                record_date="2026-06-30",
                generated_at=FIXED_TIME,
            )
            residual = result["records"]["residual"]

            self.assertEqual([-2, 1, -2], [
                item["residual"] for item in residual["items"]
            ])
            self.assertEqual(58.33, residual["accuracy_percent"])
            self.assertEqual("none", residual["scoring_impact"])
            self.assertFalse(residual["production_authorized"])

    def test_root_cause_uses_manual_diagnostics_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = DailyIntelligenceLoop(temporary_directory).run(
                dashboard_payload=self.dashboard,
                manual_outcome=self.manual_outcome,
                record_date="2026-06-30",
                generated_at=FIXED_TIME,
            )
            root_cause = result["records"]["root_cause"]

            self.assertEqual(
                "manual_diagnostic_input",
                root_cause["attribution_mode"],
            )
            self.assertEqual("timing", root_cause["primary_driver"]["engine"])
            self.assertEqual(18.0, root_cause["primary_driver"]["impact"])
            self.assertFalse(root_cause["automatic_causality_claim"])

    def test_reflection_is_suggestion_only_and_repository_stays_read_only(
        self,
    ) -> None:
        before = repository_fingerprint(REPOSITORY_ROOT / "Knowledge")
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = DailyIntelligenceLoop(temporary_directory).run(
                dashboard_payload=self.dashboard,
                manual_outcome=self.manual_outcome,
                record_date="2026-06-30",
                generated_at=FIXED_TIME,
            )
        after = repository_fingerprint(REPOSITORY_ROOT / "Knowledge")
        reflection = result["records"]["reflection"]

        self.assertEqual(before, after)
        self.assertEqual("suggest_only", reflection["learning_action"])
        self.assertEqual(
            "draft_suggestion_only",
            reflection["hypothesis_suggestion"]["status"],
        )
        self.assertFalse(reflection["automatic_merge"])
        self.assertFalse(reflection["repository_write_authorized"])

    def test_fail_fast_rejects_invalid_outcome_and_write_authority(self) -> None:
        invalid_outcome = json.loads(json.dumps(self.manual_outcome))
        invalid_outcome["items"][0]["actual_stars"] = 6
        with self.assertRaisesRegex(
            DailyIntelligenceError, "integer from 1 to 5"
        ):
            OutcomeCollector.collect_manual(invalid_outcome)

        with tempfile.TemporaryDirectory() as temporary_directory:
            writer = ShadowRecordWriter(temporary_directory)
            with self.assertRaisesRegex(
                DailyIntelligenceError, "Repository write authorization"
            ):
                writer.save(
                    {
                        "record_type": "daily_reflection",
                        "record_date": "2026-06-30",
                        "production_authorized": False,
                        "repository_write_authorized": True,
                    }
                )

    def test_daily_loop_schema_is_non_production(self) -> None:
        schema = json.loads(
            (
                REPOSITORY_ROOT
                / "Schemas/Runtime/daily_intelligence_loop.schema.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema",
            schema["$schema"],
        )
        self.assertFalse(schema["x-runtime"]["scoring_change"])
        self.assertFalse(schema["x-runtime"]["repository_auto_write"])
        self.assertFalse(schema["x-runtime"]["automatic_merge"])
        self.assertFalse(schema["x-runtime"]["production_authorized"])


if __name__ == "__main__":
    unittest.main()
