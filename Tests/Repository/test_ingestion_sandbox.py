from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from Sandbox.Ingestion.import_evidence import (
    EvidenceIngestionSandbox,
    IngestionError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "Schemas" / "Evidence" / "evidence.schema.json"
SAMPLES_ROOT = REPOSITORY_ROOT / "Sandbox" / "Ingestion" / "samples"
FIXED_TIME = datetime(2026, 6, 28, 8, 30, tzinfo=timezone.utc)


def create_sandbox(root: Path) -> Path:
    sandbox_root = root / "Ingestion"
    for folder in ("imports", "processed", "failed"):
        (sandbox_root / folder).mkdir(parents=True)
    (sandbox_root / "ingestion_manifest.json").write_text(
        json.dumps(
            {
                "document_id": "AR-INGESTION-MANIFEST-v1",
                "version": "1.0",
                "status": "sandbox_manifest",
                "imports": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return sandbox_root


def raw_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "evidence_id": "EV-901",
        "source": "https://example.test/manual/ev-901",
        "source_type": "news",
        "timestamp": "2026-06-28T08:00:00+08:00",
        "title": "Manual Sandbox Input",
        "summary": "A manual test record.",
        "language": "en",
        "region": "Global",
        "symbols": ["TEST"],
        "tags": ["manual"],
        "importance": 50,
        "reliability": 60,
    }
    payload.update(overrides)
    return payload


def create_importer(sandbox_root: Path) -> EvidenceIngestionSandbox:
    return EvidenceIngestionSandbox(
        sandbox_root,
        SCHEMA_PATH,
        imported_at=FIXED_TIME,
    )


class EvidenceIngestionSandboxTests(unittest.TestCase):
    def test_json_import_generates_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            (sandbox_root / "imports/IMP-901.json").write_text(
                json.dumps(raw_payload()),
                encoding="utf-8",
            )

            manifest = create_importer(sandbox_root).ingest_all()

            self.assertEqual(1, len(manifest["imports"]))
            self.assertEqual("json", manifest["imports"][0]["format"])
            self.assertTrue((sandbox_root / "processed/EV-901.md").is_file())

    def test_yaml_import_generates_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            payload = raw_payload()
            lines = [
                f"{key}: {json.dumps(value) if isinstance(value, list) else value}"
                for key, value in payload.items()
            ]
            (sandbox_root / "imports/IMP-901.yaml").write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )

            manifest = create_importer(sandbox_root).ingest_all()

            self.assertEqual("yaml", manifest["imports"][0]["format"])
            self.assertTrue((sandbox_root / "processed/EV-901.md").is_file())

    def test_markdown_import_generates_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            payload = raw_payload()
            lines = ["---"]
            lines.extend(
                f"{key}: {json.dumps(value) if isinstance(value, list) else value}"
                for key, value in payload.items()
            )
            lines.extend(["---", "", "# Manual Input", ""])
            (sandbox_root / "imports/IMP-901.md").write_text(
                "\n".join(lines),
                encoding="utf-8",
            )

            manifest = create_importer(sandbox_root).ingest_all()

            self.assertEqual("markdown", manifest["imports"][0]["format"])
            self.assertTrue((sandbox_root / "processed/EV-901.md").is_file())

    def test_unsupported_format_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            (sandbox_root / "imports/IMP-901.txt").write_text(
                "unsupported",
                encoding="utf-8",
            )

            with self.assertRaises(IngestionError):
                create_importer(sandbox_root).ingest_all()

            self.assertTrue((sandbox_root / "failed/IMP-901.txt").is_file())

    def test_duplicate_import_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            (sandbox_root / "imports/IMP-901.json").write_text(
                json.dumps(raw_payload()),
                encoding="utf-8",
            )
            (sandbox_root / "imports/IMP-901.yaml").write_text(
                "evidence_id: EV-902\n",
                encoding="utf-8",
            )

            with self.assertRaises(IngestionError):
                create_importer(sandbox_root).ingest_all()

    def test_missing_required_input_fails_fast(self) -> None:
        for field in ("title", "timestamp", "source"):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    sandbox_root = create_sandbox(Path(temporary_directory))
                    payload = raw_payload()
                    del payload[field]
                    (sandbox_root / "imports/IMP-901.json").write_text(
                        json.dumps(payload),
                        encoding="utf-8",
                    )

                    with self.assertRaises(IngestionError):
                        create_importer(sandbox_root).ingest_all()

    def test_invalid_output_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            (sandbox_root / "imports/IMP-901.json").write_text(
                json.dumps(raw_payload(importance=101)),
                encoding="utf-8",
            )

            with self.assertRaises(IngestionError):
                create_importer(sandbox_root).ingest_all()

    def test_five_sample_records_ingest_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            for sample in SAMPLES_ROOT.iterdir():
                if sample.is_file():
                    shutil.copy2(sample, sandbox_root / "imports" / sample.name)

            importer = create_importer(sandbox_root)
            manifest = importer.ingest_all()
            result = importer.validate_existing()

            self.assertEqual(5, len(manifest["imports"]))
            self.assertEqual(5, result["imports_checked"])
            self.assertEqual(5, result["outputs_checked"])
            self.assertEqual(
                {"json", "yaml", "markdown"},
                {record["format"] for record in manifest["imports"]},
            )

    def test_manifest_records_required_audit_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            (sandbox_root / "imports/IMP-901.json").write_text(
                json.dumps(raw_payload()),
                encoding="utf-8",
            )

            manifest = create_importer(sandbox_root).ingest_all()
            record = manifest["imports"][0]

            self.assertEqual(
                {
                    "import_id",
                    "source",
                    "imported_at",
                    "format",
                    "status",
                    "output_evidence",
                },
                set(record),
            )

    def test_validate_existing_rejects_missing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root = create_sandbox(Path(temporary_directory))
            (sandbox_root / "imports/IMP-901.json").write_text(
                json.dumps(raw_payload()),
                encoding="utf-8",
            )
            importer = create_importer(sandbox_root)
            importer.ingest_all()
            (sandbox_root / "processed/EV-901.md").unlink()

            with self.assertRaises(IngestionError):
                importer.validate_existing()


if __name__ == "__main__":
    unittest.main()
