from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Runtime.Repository.case_repository import CaseRepository, CaseValidationError


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "Schemas" / "CaseLibrary" / "case_quality.schema.json"


class CaseRepositoryTests(unittest.TestCase):
    def test_repository_scans_registers_and_builds_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            index_path = Path(temporary_directory) / "case_index.json"
            repository = CaseRepository(index_path=index_path)

            self.assertEqual(["CASE-001"], [case.id for case in repository.list_cases()])
            self.assertEqual("Micron Earnings", repository.get_case("CASE-001").title)
            self.assertEqual(
                ["CASE-001"], [case.id for case in repository.find_case("HBM")]
            )

            payload = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(1, payload["case_count"])
            self.assertEqual(
                {
                    "id",
                    "title",
                    "grade",
                    "status",
                    "theme",
                    "tags",
                },
                set(payload["cases"][0]),
            )

    def test_startup_fails_when_front_matter_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            case_root = root / "cases"
            case_root.mkdir()
            (case_root / "CASE-999_INVALID.md").write_text(
                "# Missing front matter\n", encoding="utf-8"
            )

            with self.assertRaises(CaseValidationError):
                CaseRepository(
                    case_root=case_root,
                    schema_path=SCHEMA_PATH,
                    index_path=root / "case_index.json",
                )

    def test_startup_fails_on_duplicate_case_id(self) -> None:
        case_document = """---
case_id: CASE-777
title: Duplicate
case_category: Reference
status: draft
model_impact: research_only_not_production
quality_standard_version: "1.1"
novelty: low
evidence_quality: low
prediction_confidence: low
grade: Reference Only
theme: Test Theme
tags: ["test"]
---

# Duplicate
"""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            case_root = root / "cases"
            case_root.mkdir()
            (case_root / "CASE-777_FIRST.md").write_text(
                case_document, encoding="utf-8"
            )
            (case_root / "CASE-777_SECOND.md").write_text(
                case_document, encoding="utf-8"
            )

            with self.assertRaises(CaseValidationError):
                CaseRepository(
                    case_root=case_root,
                    schema_path=SCHEMA_PATH,
                    index_path=root / "case_index.json",
                )

    def test_block_style_yaml_tags_are_parsed(self) -> None:
        case_document = """---
case_id: CASE-778
title: Block List
case_category: Reference
status: draft
model_impact: research_only_not_production
quality_standard_version: "1.1"
novelty: null
evidence_quality: low
prediction_confidence: null
grade: null
theme: Test Theme
tags:
  - first
  - second
---

# Block List
"""
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            case_root = root / "cases"
            case_root.mkdir()
            (case_root / "CASE-778_BLOCK_LIST.md").write_text(
                case_document, encoding="utf-8"
            )

            repository = CaseRepository(
                case_root=case_root,
                schema_path=SCHEMA_PATH,
                index_path=root / "case_index.json",
            )

            self.assertEqual(
                ("first", "second"),
                repository.get_case("CASE-778").metadata.tags,
            )


if __name__ == "__main__":
    unittest.main()
