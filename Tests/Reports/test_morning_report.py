from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from Scripts.Reports.morning_report import MorningReportGenerator
from Scripts.Reports.report_validator import (
    MorningReportValidator,
    ReportValidationError,
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
        root / "Runtime/Repository/index/case_index.json",
        {"case_count": 1, "cases": [{"id": "CASE-001"}]},
    )
    write_json(
        root / "Knowledge/Pattern/index.json",
        {"pattern_count": 0, "patterns": []},
    )
    write_json(
        root / "Knowledge/Experience/index.json",
        {"experience_count": 0, "experiences": []},
    )
    write_json(
        root / "Knowledge/Playbook/index.json",
        {"playbook_count": 0, "playbooks": []},
    )
    write_json(
        root / "Runtime/Repository/index/validation_report.json",
        {
            "validation_status": "PASS",
            "total_errors": 0,
            "total_warnings": 1,
        },
    )
    write_json(
        root / "Knowledge/Outcome/index.json",
        {"outcome_count": 0, "outcomes": []},
    )
    write_json(
        root / "Knowledge/OutcomeEvaluation/index.json",
        {"evaluation_count": 0, "evaluations": []},
    )
    write_json(
        root / "Knowledge/DailyReview/index.json",
        {"review_count": 0, "reviews": []},
    )


def generator(root: Path, output: Path) -> MorningReportGenerator:
    return MorningReportGenerator(
        root,
        output,
        generated_at=datetime(2026, 6, 28, 7, 0, tzinfo=timezone.utc),
        repository_version="main",
    )


class MorningReportTests(unittest.TestCase):
    def test_morning_report_is_generated_and_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            report_path = root / "Reports/Morning/latest.md"

            report = generator(root, report_path).generate()
            result = MorningReportValidator(root, report_path).validate()

            self.assertTrue(report_path.is_file())
            self.assertIn("# Auto Radar Morning Report", report)
            self.assertIn("- Repository Version: main", report)
            self.assertIn("- Case Count: 1", report)
            self.assertEqual("PASS", result["validation_status"])

    def test_latest_prediction_and_references_are_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            older = {
                "id": "PRED-OLD",
                "prediction_date": "2026-06-27",
                "generated_at": "2026-06-27T07:00:00Z",
                "status": "Generated",
                "market": "global",
                "pattern_refs": [],
                "experience_refs": [],
                "playbook_refs": [],
            }
            latest = {
                "id": "PRED-LATEST",
                "prediction_date": "2026-06-28",
                "generated_at": "2026-06-28T07:00:00Z",
                "status": "Generated",
                "market": "global",
                "pattern_refs": ["PAT-001"],
                "experience_refs": ["EXP-001"],
                "playbook_refs": ["PB-001"],
            }
            write_json(
                root / "Runtime/Repository/index/prediction_registry.json",
                {"prediction_count": 2, "predictions": [older, latest]},
            )
            write_json(
                root / "Knowledge/Pattern/index.json",
                {"pattern_count": 1, "patterns": [{"id": "PAT-001"}]},
            )
            write_json(
                root / "Knowledge/Experience/index.json",
                {"experience_count": 1, "experiences": [{"id": "EXP-001"}]},
            )
            write_json(
                root / "Knowledge/Playbook/index.json",
                {"playbook_count": 1, "playbooks": [{"id": "PB-001"}]},
            )
            write_json(
                root / "Knowledge/Pattern/Candidate/PAT-001.json",
                {"pattern_id": "PAT-001", "source_cases": ["CASE-001"]},
            )
            write_json(
                root / "Knowledge/Experience/Candidate/EXP-001.json",
                {"experience_id": "EXP-001", "source_cases": ["CASE-001"]},
            )
            report_path = root / "Reports/Morning/latest.md"

            report = generator(root, report_path).generate()
            result = MorningReportValidator(root, report_path).validate()

            self.assertIn("- Prediction ID: PRED-LATEST", report)
            self.assertNotIn("PRED-OLD", report)
            self.assertIn("- Referenced Cases: CASE-001", report)
            self.assertIn("- Referenced Patterns: PAT-001", report)
            self.assertIn("- Referenced Experiences: EXP-001", report)
            self.assertIn("- Referenced Playbooks: PB-001", report)
            self.assertEqual(5, result["references_checked"])

    def test_pending_review_counts_are_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            write_json(
                root / "Knowledge/Outcome/index.json",
                {
                    "outcome_count": 2,
                    "outcomes": [
                        {"id": "OUT-001", "status": "open"},
                        {"id": "OUT-002", "status": "reviewed"},
                    ],
                },
            )
            write_json(
                root / "Knowledge/OutcomeEvaluation/index.json",
                {
                    "evaluation_count": 1,
                    "evaluations": [{"id": "EVAL-001", "status": "draft"}],
                },
            )
            write_json(
                root / "Knowledge/DailyReview/index.json",
                {
                    "review_count": 1,
                    "reviews": [{"id": "REV-001", "status": "archived"}],
                },
            )

            report = generator(root, root / "report.md").generate()

            self.assertIn("- Outcome Pending: 1", report)
            self.assertIn("- Evaluation Pending: 1", report)
            self.assertIn("- Review Pending: 0", report)

    def test_validator_rejects_missing_section(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            report_path = root / "report.md"
            report = generator(root, report_path).generate()
            report_path.write_text(
                report.replace("## Pending Review", "Pending Review"),
                encoding="utf-8",
            )

            with self.assertRaises(ReportValidationError):
                MorningReportValidator(root, report_path).validate()

    def test_validator_rejects_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            report_path = root / "report.md"
            report = generator(root, report_path).generate()
            report_path.write_text(
                report.replace(
                    "- Referenced Patterns: None",
                    "- Referenced Patterns: PAT-999",
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ReportValidationError):
                MorningReportValidator(root, report_path).validate()

    def test_validator_rejects_prohibited_term(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)
            report_path = root / "report.md"
            report = generator(root, report_path).generate()
            report_path.write_text(
                report + "\n- Extra Note: BUY\n",
                encoding="utf-8",
            )

            with self.assertRaises(ReportValidationError):
                MorningReportValidator(root, report_path).validate()

    def test_validator_rejects_missing_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            create_repository(root)

            with self.assertRaises(ReportValidationError):
                MorningReportValidator(root, root / "missing.md").validate()


if __name__ == "__main__":
    unittest.main()

