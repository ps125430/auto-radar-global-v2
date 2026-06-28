from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from Runtime.Reports.daily_report import DailyReportGenerator, ReportGenerationError


REQUIRED_HEADINGS = (
    "## Report Date",
    "## Prediction ID",
    "## Prediction Status",
    "## Referenced Playbooks",
    "## Referenced Experiences",
    "## Referenced Patterns",
    "## Referenced Cases",
    "## Validation Status",
    "## Missing References",
    "## Notes",
)
PROHIBITED_REPORT_TERMS = (
    "BUY",
    "SELL",
    "WATCH",
    "WAIT",
    "Signal",
    "Strategy",
    "Confidence Calculation",
)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def create_repository(root: Path) -> None:
    write_json(
        root / "Runtime/Repository/index/prediction_registry.json",
        {"prediction_count": 0, "predictions": []},
    )
    write_json(
        root / "Runtime/Repository/index/validation_report.json",
        {"validation_status": "PASS"},
    )
    write_json(
        root / "Knowledge/Playbook/index.json",
        {"playbooks": []},
    )
    write_json(
        root / "Knowledge/Experience/index.json",
        {"experiences": []},
    )
    write_json(
        root / "Knowledge/Pattern/index.json",
        {"patterns": []},
    )
    write_json(
        root / "Runtime/Repository/index/case_index.json",
        {"cases": []},
    )
    (root / "Knowledge/Prediction/daily").mkdir(parents=True)


def prediction_record(
    prediction_id: str,
    prediction_date: str,
    *,
    generated_at: str,
    playbook_refs: list[str] | None = None,
    experience_refs: list[str] | None = None,
    pattern_refs: list[str] | None = None,
    source_file: str = "daily/prediction.md",
) -> dict[str, object]:
    return {
        "id": prediction_id,
        "prediction_date": prediction_date,
        "generated_at": generated_at,
        "state": "test",
        "market": "global",
        "status": "Generated",
        "playbook_refs": playbook_refs or [],
        "experience_refs": experience_refs or [],
        "pattern_refs": pattern_refs or [],
        "source_file": source_file,
    }


class DailyReportGeneratorTests(unittest.TestCase):
    def test_empty_prediction_repository_generates_readable_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            output = root / "Reports/Daily/latest_report.md"

            report = DailyReportGenerator(
                root,
                output,
                report_date=date(2026, 6, 28),
            ).generate()

            self.assertTrue(output.is_file())
            self.assertIn("No Snapshot", report)
            self.assertIn("2026-06-28", report)
            for heading in REQUIRED_HEADINGS:
                self.assertIn(heading, report)
            for term in PROHIBITED_REPORT_TERMS:
                self.assertNotIn(term, report)

    def test_latest_prediction_is_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            older = prediction_record(
                "PRED-OLDER",
                "2026-06-27",
                generated_at="2026-06-27T08:00:00+08:00",
                source_file="daily/older.md",
            )
            latest = prediction_record(
                "PRED-LATEST",
                "2026-06-28",
                generated_at="2026-06-28T08:00:00+08:00",
                source_file="daily/latest.md",
            )
            write_json(
                root / "Runtime/Repository/index/prediction_registry.json",
                {"prediction_count": 2, "predictions": [older, latest]},
            )
            (root / "Knowledge/Prediction/daily/older.md").write_text(
                "## Notes\nOlder\n", encoding="utf-8"
            )
            (root / "Knowledge/Prediction/daily/latest.md").write_text(
                "## Notes\nLatest repository note\n", encoding="utf-8"
            )

            report = DailyReportGenerator(
                root, root / "report.md"
            ).generate()

            self.assertIn("PRED-LATEST", report)
            self.assertNotIn("PRED-OLDER", report)
            self.assertIn("Latest repository note", report)

    def test_invalid_prediction_registry_count_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            write_json(
                root / "Runtime/Repository/index/prediction_registry.json",
                {"prediction_count": 1, "predictions": []},
            )

            with self.assertRaises(ReportGenerationError):
                DailyReportGenerator(root, root / "report.md").generate()

    def test_referenced_entities_and_cases_are_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            prediction = prediction_record(
                "PRED-001",
                "2026-06-28",
                generated_at="2026-06-28T08:00:00+08:00",
                playbook_refs=["PB-001"],
                experience_refs=["EXP-001"],
                pattern_refs=["PAT-001"],
            )
            write_json(
                root / "Runtime/Repository/index/prediction_registry.json",
                {"prediction_count": 1, "predictions": [prediction]},
            )
            write_json(
                root / "Knowledge/Playbook/index.json",
                {"playbooks": [{"id": "PB-001"}]},
            )
            write_json(
                root / "Knowledge/Experience/index.json",
                {"experiences": [{"id": "EXP-001"}]},
            )
            write_json(
                root / "Knowledge/Pattern/index.json",
                {"patterns": [{"id": "PAT-001"}]},
            )
            write_json(
                root / "Runtime/Repository/index/case_index.json",
                {"cases": [{"id": "CASE-001", "title": "Micron Earnings"}]},
            )
            write_json(
                root / "Knowledge/Experience/Candidate/EXP-001.json",
                {"experience_id": "EXP-001", "source_cases": ["CASE-001"]},
            )
            write_json(
                root / "Knowledge/Pattern/Candidate/PAT-001.json",
                {"pattern_id": "PAT-001", "source_cases": ["CASE-001"]},
            )
            (root / "Knowledge/Prediction/daily/prediction.md").write_text(
                "## Notes\nRepository note\n", encoding="utf-8"
            )

            report = DailyReportGenerator(
                root, root / "report.md"
            ).generate()

            self.assertIn("PB-001", report)
            self.assertIn("EXP-001", report)
            self.assertIn("PAT-001", report)
            self.assertIn("CASE-001 - Micron Earnings", report)
            self.assertIn("## Missing References\n\n- None", report)

    def test_missing_references_are_reported_without_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            prediction = prediction_record(
                "PRED-001",
                "2026-06-28",
                generated_at="2026-06-28T08:00:00+08:00",
                playbook_refs=["PB-999"],
                experience_refs=["EXP-999"],
                pattern_refs=["PAT-999"],
                source_file="daily/missing.md",
            )
            write_json(
                root / "Runtime/Repository/index/prediction_registry.json",
                {"prediction_count": 1, "predictions": [prediction]},
            )

            report = DailyReportGenerator(
                root, root / "report.md"
            ).generate()

            self.assertIn("Playbook: PB-999", report)
            self.assertIn("Experience: EXP-999", report)
            self.assertIn("Pattern: PAT-999", report)
            self.assertIn("Prediction source file: daily/missing.md", report)
            for term in PROHIBITED_REPORT_TERMS:
                self.assertNotIn(term, report)


if __name__ == "__main__":
    unittest.main()
