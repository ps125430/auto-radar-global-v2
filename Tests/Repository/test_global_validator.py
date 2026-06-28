from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Runtime.Repository import validate_all
from Runtime.Repository.global_validator import (
    GlobalRepositoryValidator,
    GlobalValidationError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class GlobalRepositoryValidatorTests(unittest.TestCase):
    def test_package_entry_runs_global_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            report = validate_all(
                REPOSITORY_ROOT,
                Path(temporary_directory) / "validation_report.json",
            )

            self.assertEqual("PASS", report["validation_status"])

    def test_global_validation_passes_and_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            report_path = Path(temporary_directory) / "validation_report.json"
            validator = GlobalRepositoryValidator(
                REPOSITORY_ROOT, report_path
            )

            report = validator.validate_all()

            self.assertEqual("PASS", report["validation_status"])
            self.assertEqual(10, len(report["checked_modules"]))
            self.assertEqual(1, report["total_entities"])
            self.assertEqual(0, report["total_errors"])
            self.assertEqual(1, report["total_warnings"])
            persisted = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("PASS", persisted["validation_status"])

    def test_missing_schema_fails_fast_and_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            report_path = root / "validation_report.json"
            validator = GlobalRepositoryValidator(
                REPOSITORY_ROOT, report_path
            )
            validator.schema_paths["Case"] = root / "missing.schema.json"

            with self.assertRaises(GlobalValidationError):
                validator.validate_all()

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("FAIL", report["validation_status"])
            self.assertEqual(1, report["total_errors"])

    def test_missing_index_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            validator = GlobalRepositoryValidator(
                REPOSITORY_ROOT, root / "report.json"
            )
            validator.index_specs["Pattern"]["path"] = root / "missing_index.json"

            with self.assertRaises(GlobalValidationError):
                validator.validate_all()

    def test_duplicate_registry_id_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            duplicate_index = root / "pattern_index.json"
            duplicate_index.write_text(
                json.dumps(
                    {
                        "pattern_count": 2,
                        "patterns": [
                            {"id": "PAT-001"},
                            {"id": "PAT-001"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            validator = GlobalRepositoryValidator(
                REPOSITORY_ROOT, root / "report.json"
            )
            validator.index_specs["Pattern"]["path"] = duplicate_index

            with self.assertRaises(GlobalValidationError):
                validator.validate_all()

    def test_registry_item_with_missing_file_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            stale_index = root / "pattern_index.json"
            stale_index.write_text(
                json.dumps(
                    {
                        "pattern_count": 1,
                        "patterns": [{"id": "PAT-999"}],
                    }
                ),
                encoding="utf-8",
            )
            validator = GlobalRepositoryValidator(
                REPOSITORY_ROOT, root / "report.json"
            )
            validator.index_specs["Pattern"]["path"] = stale_index

            with self.assertRaises(GlobalValidationError):
                validator.validate_all()

    def test_missing_prediction_consumer_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            indexes = {
                "Prediction": ("predictions", []),
                "Outcome": (
                    "outcomes",
                    [{"id": "OUT-001", "prediction_ref": "PRED-999"}],
                ),
                "OutcomeEvaluation": ("evaluations", []),
                "DailyReview": ("reviews", []),
            }
            validator = GlobalRepositoryValidator(
                REPOSITORY_ROOT, root / "report.json"
            )
            for module, (records_key, records) in indexes.items():
                path = root / f"{module}.json"
                path.write_text(
                    json.dumps({records_key: records}),
                    encoding="utf-8",
                )
                validator.index_specs[module]["path"] = path

            with self.assertRaises(GlobalValidationError):
                validator._validate_prediction_consumers()


if __name__ == "__main__":
    unittest.main()
