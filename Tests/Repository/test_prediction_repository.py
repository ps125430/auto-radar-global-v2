from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Scripts.Repository.prediction_repository import (
    PredictionRepository,
    PredictionValidationError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "Schemas" / "Prediction" / "prediction.schema.json"
TEMPLATE_PATH = REPOSITORY_ROOT / "Knowledge" / "Prediction" / "TEMPLATE.md"


def create_prediction_root(root: Path) -> Path:
    prediction_root = root / "Prediction"
    (prediction_root / "daily").mkdir(parents=True)
    (prediction_root / "archive").mkdir()
    shutil.copyfile(TEMPLATE_PATH, prediction_root / "TEMPLATE.md")
    return prediction_root


def create_index(root: Path, name: str, key: str, entity_id: str) -> Path:
    path = root / f"{name}.json"
    path.write_text(
        json.dumps({key: [{"id": entity_id}]}, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def snapshot_content(**overrides: object) -> str:
    values: dict[str, object] = {
        "prediction_id": "PRED-2026-06-28",
        "prediction_date": "2026-06-28",
        "generated_at": "2026-06-28T08:00:00+08:00",
        "state": "repository_test",
        "market": "global",
        "playbook_refs": ["PB-001"],
        "experience_refs": ["EXP-001"],
        "pattern_refs": ["PAT-001"],
        "confidence_ref": None,
        "decision_status": "not_evaluated",
        "model_impact": "snapshot_only_not_production_scoring",
        "status": "Generated",
    }
    values.update(overrides)

    lines = ["---"]
    for key, value in values.items():
        if value is None:
            rendered = "null"
        elif isinstance(value, list):
            rendered = json.dumps(value)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    lines.extend(
        [
            "---",
            "",
            "# Prediction Snapshot",
            "",
            "## Prediction Summary",
            "",
            "## Evidence Summary",
            "",
            "## Referenced Entities",
            "",
            "## Validation",
            "",
            "## Notes",
            "",
        ]
    )
    return "\n".join(lines)


def write_snapshot(
    prediction_root: Path,
    name: str,
    content: str,
    folder: str = "daily",
) -> Path:
    path = prediction_root / folder / name
    path.write_text(content, encoding="utf-8")
    return path


class PredictionRepositoryTests(unittest.TestCase):
    def create_repository(
        self, root: Path, prediction_root: Path
    ) -> PredictionRepository:
        return PredictionRepository(
            prediction_root=prediction_root,
            schema_path=SCHEMA_PATH,
            registry_path=root / "prediction_registry.json",
            playbook_index_path=create_index(
                root, "playbooks", "playbooks", "PB-001"
            ),
            experience_index_path=create_index(
                root, "experiences", "experiences", "EXP-001"
            ),
            pattern_index_path=create_index(
                root, "patterns", "patterns", "PAT-001"
            ),
        )

    def test_empty_repository_generates_registry_and_validates_template(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)

            repository = self.create_repository(root, prediction_root)

            self.assertEqual([], repository.list_predictions())
            registry = json.loads(
                (root / "prediction_registry.json").read_text(encoding="utf-8")
            )
            self.assertEqual(0, registry["prediction_count"])

    def test_valid_snapshot_is_registered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            write_snapshot(
                prediction_root,
                "PRED-2026-06-28.md",
                snapshot_content(),
            )

            repository = self.create_repository(root, prediction_root)

            snapshot = repository.get_prediction("PRED-2026-06-28")
            self.assertEqual("Generated", snapshot.status)
            self.assertEqual(("PB-001",), snapshot.playbook_refs)

    def test_missing_entity_reference_fails_fast(self) -> None:
        reference_cases = (
            ("playbook_refs", ["PB-999"]),
            ("experience_refs", ["EXP-999"]),
            ("pattern_refs", ["PAT-999"]),
        )
        for field, value in reference_cases:
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory)
                    prediction_root = create_prediction_root(root)
                    write_snapshot(
                        prediction_root,
                        "PRED-2026-06-28.md",
                        snapshot_content(**{field: value}),
                    )

                    with self.assertRaises(PredictionValidationError):
                        self.create_repository(root, prediction_root)

    def test_duplicate_prediction_id_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            write_snapshot(
                prediction_root,
                "first.md",
                snapshot_content(),
            )
            write_snapshot(
                prediction_root,
                "second.md",
                snapshot_content(prediction_date="2026-06-29"),
            )

            with self.assertRaises(PredictionValidationError):
                self.create_repository(root, prediction_root)

    def test_duplicate_prediction_date_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            write_snapshot(
                prediction_root,
                "first.md",
                snapshot_content(),
            )
            write_snapshot(
                prediction_root,
                "second.md",
                snapshot_content(prediction_id="PRED-SECOND"),
            )

            with self.assertRaises(PredictionValidationError):
                self.create_repository(root, prediction_root)

    def test_invalid_status_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            write_snapshot(
                prediction_root,
                "invalid.md",
                snapshot_content(status="Invalid"),
            )

            with self.assertRaises(PredictionValidationError):
                self.create_repository(root, prediction_root)

    def test_missing_required_field_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            content = snapshot_content().replace("market: global\n", "")
            write_snapshot(
                prediction_root,
                "missing_market.md",
                content,
            )

            with self.assertRaises(PredictionValidationError):
                self.create_repository(root, prediction_root)

    def test_archived_snapshot_in_daily_folder_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            write_snapshot(
                prediction_root,
                "archived.md",
                snapshot_content(status="Archived"),
            )

            with self.assertRaises(PredictionValidationError):
                self.create_repository(root, prediction_root)

    def test_invalid_confidence_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            write_snapshot(
                prediction_root,
                "invalid_confidence.md",
                snapshot_content(confidence_ref="INVALID"),
            )

            with self.assertRaises(PredictionValidationError):
                self.create_repository(root, prediction_root)

    def test_trading_command_decision_status_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            write_snapshot(
                prediction_root,
                "invalid_decision.md",
                snapshot_content(decision_status="BUY"),
            )

            with self.assertRaises(PredictionValidationError):
                self.create_repository(root, prediction_root)

    def test_missing_template_heading_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            prediction_root = create_prediction_root(root)
            template_path = prediction_root / "TEMPLATE.md"
            template_path.write_text(
                template_path.read_text(encoding="utf-8").replace(
                    "## Validation", "Validation"
                ),
                encoding="utf-8",
            )

            with self.assertRaises(PredictionValidationError):
                self.create_repository(root, prediction_root)


if __name__ == "__main__":
    unittest.main()
