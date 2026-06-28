from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Scripts.Repository.evidence_repository import (
    EvidenceRepository,
    EvidenceValidationError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "Schemas" / "Evidence" / "evidence.schema.json"
TEMPLATE_PATH = REPOSITORY_ROOT / "Knowledge" / "Evidence" / "TEMPLATE.md"
LIFECYCLE_FOLDERS = ("incoming", "verified", "rejected", "archive")


def create_evidence_root(root: Path) -> Path:
    evidence_root = root / "Evidence"
    for folder in LIFECYCLE_FOLDERS:
        (evidence_root / folder).mkdir(parents=True)
    shutil.copyfile(TEMPLATE_PATH, evidence_root / "TEMPLATE.md")
    return evidence_root


def evidence_content(**overrides: object) -> str:
    values: dict[str, object] = {
        "evidence_id": "EV-001",
        "source": "https://example.test/source",
        "source_type": "company_filing",
        "published_at": "2026-06-28T08:00:00+08:00",
        "collected_at": "2026-06-28T08:05:00+08:00",
        "title": "Repository Evidence",
        "summary": "A manually recorded Evidence summary.",
        "language": "en",
        "region": "US",
        "symbols": ["TEST"],
        "tags": ["filing"],
        "importance": 70,
        "reliability": 90,
        "status": "Incoming",
        "model_impact": "evidence_only_not_production",
    }
    values.update(overrides)
    lines = ["---"]
    for key, value in values.items():
        rendered = json.dumps(value) if isinstance(value, list) else str(value)
        lines.append(f"{key}: {rendered}")
    lines.extend(
        [
            "---",
            "",
            "# Evidence Record",
            "",
            "## Original Source",
            "",
            "## Summary",
            "",
            "## Tags",
            "",
            "## Symbols",
            "",
            "## Evidence Notes",
            "",
            "## Validation",
            "",
        ]
    )
    return "\n".join(lines)


def write_evidence(
    evidence_root: Path,
    name: str,
    content: str,
    folder: str = "incoming",
) -> Path:
    path = evidence_root / folder / name
    path.write_text(content, encoding="utf-8")
    return path


class EvidenceRepositoryTests(unittest.TestCase):
    def create_repository(
        self,
        root: Path,
        evidence_root: Path,
        *,
        schema_path: Path = SCHEMA_PATH,
    ) -> EvidenceRepository:
        return EvidenceRepository(
            evidence_root=evidence_root,
            schema_path=schema_path,
            registry_path=root / "evidence_registry.json",
        )

    def test_empty_repository_generates_registry_and_validates_template(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)

            repository = self.create_repository(root, evidence_root)

            self.assertEqual([], repository.list_evidence())
            registry = json.loads(
                (root / "evidence_registry.json").read_text(encoding="utf-8")
            )
            self.assertEqual(0, registry["evidence_count"])

    def test_valid_incoming_evidence_is_registered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)
            write_evidence(evidence_root, "EV-001.md", evidence_content())

            repository = self.create_repository(root, evidence_root)

            record = repository.get_evidence("EV-001")
            self.assertEqual("Incoming", record.status)
            self.assertEqual(70, record.importance)

    def test_valid_archived_evidence_is_registered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)
            write_evidence(
                evidence_root,
                "EV-001.md",
                evidence_content(status="Archived"),
                folder="archive",
            )

            repository = self.create_repository(root, evidence_root)

            self.assertEqual("Archived", repository.get_evidence("EV-001").status)

    def test_duplicate_id_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)
            write_evidence(evidence_root, "first.md", evidence_content())
            write_evidence(evidence_root, "second.md", evidence_content())

            with self.assertRaises(EvidenceValidationError):
                self.create_repository(root, evidence_root)

    def test_missing_source_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)
            content = evidence_content().replace(
                "source: https://example.test/source\n", ""
            )
            write_evidence(evidence_root, "EV-001.md", content)

            with self.assertRaises(EvidenceValidationError):
                self.create_repository(root, evidence_root)

    def test_missing_timestamp_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)
            content = evidence_content().replace(
                "published_at: 2026-06-28T08:00:00+08:00\n", ""
            )
            write_evidence(evidence_root, "EV-001.md", content)

            with self.assertRaises(EvidenceValidationError):
                self.create_repository(root, evidence_root)

    def test_invalid_lifecycle_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)
            write_evidence(
                evidence_root,
                "EV-001.md",
                evidence_content(status="Verified"),
                folder="incoming",
            )

            with self.assertRaises(EvidenceValidationError):
                self.create_repository(root, evidence_root)

    def test_invalid_importance_fails_fast(self) -> None:
        for importance in (-1, 101, 50.5, "high", True):
            with self.subTest(importance=importance):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory)
                    evidence_root = create_evidence_root(root)
                    write_evidence(
                        evidence_root,
                        "EV-001.md",
                        evidence_content(importance=importance),
                    )

                    with self.assertRaises(EvidenceValidationError):
                        self.create_repository(root, evidence_root)

    def test_missing_schema_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)

            with self.assertRaises(EvidenceValidationError):
                self.create_repository(
                    root,
                    evidence_root,
                    schema_path=root / "missing.schema.json",
                )

    def test_invalid_template_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            evidence_root = create_evidence_root(root)
            template = evidence_root / "TEMPLATE.md"
            template.write_text(
                template.read_text(encoding="utf-8").replace(
                    "## Validation", "Validation"
                ),
                encoding="utf-8",
            )

            with self.assertRaises(EvidenceValidationError):
                self.create_repository(root, evidence_root)


if __name__ == "__main__":
    unittest.main()

