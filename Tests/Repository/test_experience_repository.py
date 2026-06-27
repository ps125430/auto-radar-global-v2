from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Scripts.Repository.experience_repository import (
    ExperienceRepository,
    ExperienceValidationError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "Schemas" / "Experience" / "experience.schema.json"
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


def create_experience_root(root: Path) -> Path:
    experience_root = root / "Experience"
    for folder in LIFECYCLE_FOLDERS:
        (experience_root / folder).mkdir(parents=True)
    return experience_root


def create_pattern_index(root: Path) -> Path:
    path = root / "pattern_index.json"
    path.write_text(
        json.dumps({"patterns": [{"id": "PAT-001"}]}, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def experience_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "experience_id": "EXP-001",
        "version": "1.0",
        "status": "Draft",
        "title": "Repository Validation Experience",
        "description": "A repository-only test Experience.",
        "source_patterns": ["PAT-001"],
        "source_cases": ["CASE-001"],
        "health": 50,
        "health_state": "unreviewed",
        "created_at": "2026-06-27T00:00:00+08:00",
        "updated_at": "2026-06-27T00:00:00+08:00",
    }
    payload.update(overrides)
    return payload


def write_experience(
    experience_root: Path, name: str, payload: dict[str, object]
) -> Path:
    path = experience_root / str(payload["status"]) / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class ExperienceRepositoryTests(unittest.TestCase):
    def create_repository(
        self,
        root: Path,
        experience_root: Path,
        *,
        auto_start: bool = True,
    ) -> ExperienceRepository:
        return ExperienceRepository(
            experience_root=experience_root,
            schema_path=SCHEMA_PATH,
            pattern_index_path=create_pattern_index(root),
            case_index_path=CASE_INDEX_PATH,
            index_path=experience_root / "index.json",
            auto_start=auto_start,
        )

    def test_empty_repository_builds_valid_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            experience_root = create_experience_root(root)

            repository = self.create_repository(root, experience_root)

            self.assertEqual([], repository.list_experiences())
            index = json.loads(
                (experience_root / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(0, index["experience_count"])
            self.assertEqual([], index["experiences"])

    def test_valid_experience_is_registered_and_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            experience_root = create_experience_root(root)
            write_experience(
                experience_root,
                "EXP-001.json",
                experience_payload(),
            )

            repository = self.create_repository(root, experience_root)

            experience = repository.get_experience("EXP-001")
            self.assertEqual(("PAT-001",), experience.source_patterns)
            self.assertEqual(("CASE-001",), experience.source_cases)
            index = json.loads(
                (experience_root / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {"id", "version", "status", "health_state", "created_at"},
                set(index["experiences"][0]),
            )

    def test_duplicate_experience_id_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            experience_root = create_experience_root(root)
            write_experience(
                experience_root,
                "EXP-001_FIRST.json",
                experience_payload(),
            )
            write_experience(
                experience_root,
                "EXP-001_SECOND.json",
                experience_payload(),
            )

            with self.assertRaises(ExperienceValidationError):
                self.create_repository(root, experience_root)

    def test_missing_pattern_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            experience_root = create_experience_root(root)
            write_experience(
                experience_root,
                "EXP-001.json",
                experience_payload(source_patterns=["PAT-999"]),
            )

            with self.assertRaises(ExperienceValidationError):
                self.create_repository(root, experience_root)

    def test_missing_case_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            experience_root = create_experience_root(root)
            write_experience(
                experience_root,
                "EXP-001.json",
                experience_payload(source_cases=["CASE-999"]),
            )

            with self.assertRaises(ExperienceValidationError):
                self.create_repository(root, experience_root)

    def test_invalid_status_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            experience_root = create_experience_root(root)
            payload = experience_payload(status="Invalid")
            invalid_path = experience_root / "Draft" / "EXP-001.json"
            invalid_path.write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(ExperienceValidationError):
                self.create_repository(root, experience_root)

    def test_invalid_health_fails_fast(self) -> None:
        for invalid_health in (-1, 101, True, "50", float("nan"), float("inf")):
            with self.subTest(health=invalid_health):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory)
                    experience_root = create_experience_root(root)
                    write_experience(
                        experience_root,
                        "EXP-001.json",
                        experience_payload(health=invalid_health),
                    )

                    with self.assertRaises(ExperienceValidationError):
                        self.create_repository(root, experience_root)

    def test_missing_required_field_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            experience_root = create_experience_root(root)
            payload = experience_payload()
            del payload["description"]
            write_experience(experience_root, "EXP-001.json", payload)

            with self.assertRaises(ExperienceValidationError):
                self.create_repository(root, experience_root)


if __name__ == "__main__":
    unittest.main()
