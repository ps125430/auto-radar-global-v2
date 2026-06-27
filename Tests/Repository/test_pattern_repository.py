from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Scripts.Repository.pattern_repository import (
    PatternRepository,
    PatternValidationError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "Schemas" / "Pattern" / "pattern.schema.json"
CASE_INDEX_PATH = (
    REPOSITORY_ROOT / "Runtime" / "Repository" / "index" / "case_index.json"
)
LIFECYCLE_FOLDERS = (
    "Draft",
    "Candidate",
    "Verified",
    "Deprecated",
    "Archived",
)


def create_pattern_root(root: Path) -> Path:
    pattern_root = root / "Pattern"
    for folder in LIFECYCLE_FOLDERS:
        (pattern_root / folder).mkdir(parents=True)
    return pattern_root


def pattern_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pattern_id": "PAT-001",
        "version": "1.0",
        "status": "Draft",
        "title": "Repository Validation Pattern",
        "description": "A repository-only test Pattern.",
        "source_cases": ["CASE-001"],
        "feature_vector": {"test_feature": 1},
        "created_at": "2026-06-27T00:00:00+08:00",
        "updated_at": "2026-06-27T00:00:00+08:00",
    }
    payload.update(overrides)
    return payload


def write_pattern(pattern_root: Path, name: str, payload: dict[str, object]) -> Path:
    path = pattern_root / str(payload["status"]) / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class PatternRepositoryTests(unittest.TestCase):
    def test_empty_repository_builds_valid_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pattern_root = create_pattern_root(root)
            index_path = pattern_root / "index.json"

            repository = PatternRepository(
                pattern_root=pattern_root,
                schema_path=SCHEMA_PATH,
                case_index_path=CASE_INDEX_PATH,
                index_path=index_path,
            )

            self.assertEqual([], repository.list_patterns())
            index = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(0, index["pattern_count"])
            self.assertEqual([], index["patterns"])

    def test_valid_pattern_is_registered_and_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pattern_root = create_pattern_root(root)
            write_pattern(pattern_root, "PAT-001.json", pattern_payload())

            repository = PatternRepository(
                pattern_root=pattern_root,
                schema_path=SCHEMA_PATH,
                case_index_path=CASE_INDEX_PATH,
                index_path=pattern_root / "index.json",
            )

            pattern = repository.get_pattern("PAT-001")
            self.assertEqual(("CASE-001",), pattern.source_cases)
            index = json.loads(
                (pattern_root / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {"id", "status", "version", "created_at"},
                set(index["patterns"][0]),
            )

    def test_missing_source_case_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pattern_root = create_pattern_root(root)
            write_pattern(
                pattern_root,
                "PAT-001.json",
                pattern_payload(source_cases=["CASE-999"]),
            )

            with self.assertRaises(PatternValidationError):
                PatternRepository(
                    pattern_root=pattern_root,
                    schema_path=SCHEMA_PATH,
                    case_index_path=CASE_INDEX_PATH,
                    index_path=pattern_root / "index.json",
                )

    def test_missing_required_field_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pattern_root = create_pattern_root(root)
            payload = pattern_payload()
            del payload["description"]
            write_pattern(pattern_root, "PAT-001.json", payload)

            with self.assertRaises(PatternValidationError):
                PatternRepository(
                    pattern_root=pattern_root,
                    schema_path=SCHEMA_PATH,
                    case_index_path=CASE_INDEX_PATH,
                    index_path=pattern_root / "index.json",
                )

    def test_invalid_status_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pattern_root = create_pattern_root(root)
            payload = pattern_payload(status="Invalid")
            invalid_path = pattern_root / "Draft" / "PAT-001.json"
            invalid_path.write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(PatternValidationError):
                PatternRepository(
                    pattern_root=pattern_root,
                    schema_path=SCHEMA_PATH,
                    case_index_path=CASE_INDEX_PATH,
                    index_path=pattern_root / "index.json",
                )

    def test_duplicate_pattern_id_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            pattern_root = create_pattern_root(root)
            write_pattern(pattern_root, "PAT-001_FIRST.json", pattern_payload())
            write_pattern(pattern_root, "PAT-001_SECOND.json", pattern_payload())

            with self.assertRaises(PatternValidationError):
                PatternRepository(
                    pattern_root=pattern_root,
                    schema_path=SCHEMA_PATH,
                    case_index_path=CASE_INDEX_PATH,
                    index_path=pattern_root / "index.json",
                )


if __name__ == "__main__":
    unittest.main()
