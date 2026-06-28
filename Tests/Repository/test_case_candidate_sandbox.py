from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Sandbox.CaseCandidate.case_candidate import (
    CaseCandidateError,
    CaseCandidateSandbox,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    REPOSITORY_ROOT
    / "Sandbox"
    / "CaseCandidate"
    / "case_candidate.schema.json"
)
SAMPLE_EVIDENCE_ROOT = (
    REPOSITORY_ROOT / "Sandbox" / "Ingestion" / "processed"
)


def create_fixture(root: Path) -> tuple[Path, Path]:
    sandbox_root = root / "CaseCandidate"
    evidence_root = root / "Evidence"
    for folder in ("candidates", "processed", "failed"):
        (sandbox_root / folder).mkdir(parents=True)
    evidence_root.mkdir()
    shutil.copy2(SCHEMA_PATH, sandbox_root / "case_candidate.schema.json")
    (sandbox_root / "candidate_registry.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-06-28T00:00:00+00:00",
                "candidate_count": 0,
                "candidates": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return sandbox_root, evidence_root


def write_evidence(
    evidence_root: Path,
    *,
    evidence_id: str = "EV-901",
    include_id: bool = True,
) -> Path:
    metadata: dict[str, object] = {
        "evidence_id": evidence_id,
        "source": "https://example.test/evidence/901",
        "source_type": "news",
        "published_at": "2026-06-28T08:00:00+08:00",
        "collected_at": "2026-06-28T01:00:00+00:00",
        "title": "Rule Mapping Test Evidence",
        "summary": "A deterministic test record.",
        "language": "en",
        "region": "Global",
        "symbols": ["TEST"],
        "tags": ["manual", "sample"],
        "importance": 50,
        "reliability": 60,
        "status": "Incoming",
        "model_impact": "evidence_only_not_production",
    }
    if not include_id:
        del metadata["evidence_id"]
    lines = ["---"]
    for key, value in metadata.items():
        rendered = (
            json.dumps(value)
            if isinstance(value, list)
            else str(value)
        )
        lines.append(f"{key}: {rendered}")
    lines.extend(["---", "", "# Evidence", ""])
    path = evidence_root / f"{evidence_id}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def create_engine(
    sandbox_root: Path, evidence_root: Path
) -> CaseCandidateSandbox:
    return CaseCandidateSandbox(
        sandbox_root=sandbox_root,
        evidence_root=evidence_root,
        schema_path=sandbox_root / "case_candidate.schema.json",
    )


def read_candidate(sandbox_root: Path, candidate_id: str) -> dict[str, object]:
    return json.loads(
        (sandbox_root / f"candidates/{candidate_id}.json").read_text(
            encoding="utf-8"
        )
    )


def write_candidate(
    sandbox_root: Path, candidate_id: str, candidate: dict[str, object]
) -> None:
    (sandbox_root / f"candidates/{candidate_id}.json").write_text(
        json.dumps(candidate, indent=2) + "\n",
        encoding="utf-8",
    )


class CaseCandidateSandboxTests(unittest.TestCase):
    def test_rule_mapping_generates_review_required_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root)

            registry = create_engine(
                sandbox_root, evidence_root
            ).generate_all()
            candidate = read_candidate(sandbox_root, "CC-901")

            self.assertEqual(1, registry["candidate_count"])
            self.assertEqual("EV-901", candidate["evidence_id"])
            self.assertEqual(
                "Rule Mapping Test Evidence", candidate["title"]
            )
            self.assertEqual(["TEST"], candidate["symbols"])
            self.assertEqual(["manual", "sample"], candidate["tags"])
            self.assertIsNone(candidate["confidence"])
            self.assertIsNone(candidate["grade"])
            self.assertTrue(candidate["review_required"])
            self.assertEqual("repository_only", candidate["model_impact"])

    def test_five_evidence_records_generate_traceable_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            for sample in SAMPLE_EVIDENCE_ROOT.glob("*.md"):
                shutil.copy2(sample, evidence_root / sample.name)

            engine = create_engine(sandbox_root, evidence_root)
            registry = engine.generate_all()
            result = engine.validate_existing()

            self.assertEqual(5, registry["candidate_count"])
            self.assertEqual(5, result["candidate_count"])
            self.assertEqual(5, result["evidence_references_checked"])
            self.assertEqual(
                {f"EV-{number}" for number in range(101, 106)},
                {
                    record["evidence_id"]
                    for record in registry["candidates"]
                },
            )

    def test_duplicate_candidate_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root)
            engine = create_engine(sandbox_root, evidence_root)
            engine.generate_all()

            with self.assertRaisesRegex(
                CaseCandidateError, "Duplicate candidate"
            ):
                engine.generate_all()

    def test_missing_evidence_identifier_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root, include_id=False)

            with self.assertRaisesRegex(
                CaseCandidateError, "Missing evidence_id"
            ):
                create_engine(sandbox_root, evidence_root).generate_all()

    def test_broken_evidence_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root)
            engine = create_engine(sandbox_root, evidence_root)
            engine.generate_all()
            candidate = read_candidate(sandbox_root, "CC-901")
            candidate["evidence_id"] = "EV-999"
            write_candidate(sandbox_root, "CC-901", candidate)

            with self.assertRaisesRegex(
                CaseCandidateError, "Broken Evidence reference"
            ):
                engine.validate_existing()

    def test_missing_required_candidate_field_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root)
            engine = create_engine(sandbox_root, evidence_root)
            engine.generate_all()
            candidate = read_candidate(sandbox_root, "CC-901")
            del candidate["title"]
            write_candidate(sandbox_root, "CC-901", candidate)

            with self.assertRaisesRegex(
                CaseCandidateError, "Missing required fields"
            ):
                engine.validate_existing()

    def test_invalid_lifecycle_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root)
            engine = create_engine(sandbox_root, evidence_root)
            engine.generate_all()
            candidate = read_candidate(sandbox_root, "CC-901")
            candidate["status"] = "Verified"
            write_candidate(sandbox_root, "CC-901", candidate)

            with self.assertRaisesRegex(
                CaseCandidateError, "Invalid lifecycle"
            ):
                engine.validate_existing()

    def test_duplicate_registry_candidate_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root)
            engine = create_engine(sandbox_root, evidence_root)
            engine.generate_all()
            registry = json.loads(
                (sandbox_root / "candidate_registry.json").read_text(
                    encoding="utf-8"
                )
            )
            registry["candidates"].append(registry["candidates"][0])
            registry["candidate_count"] = 2
            (sandbox_root / "candidate_registry.json").write_text(
                json.dumps(registry, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                CaseCandidateError, "Duplicate candidate in Registry"
            ):
                engine.validate_existing()

    def test_registry_missing_candidate_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root)
            engine = create_engine(sandbox_root, evidence_root)
            engine.generate_all()
            registry = json.loads(
                (sandbox_root / "candidate_registry.json").read_text(
                    encoding="utf-8"
                )
            )
            registry["candidates"] = []
            registry["candidate_count"] = 0
            (sandbox_root / "candidate_registry.json").write_text(
                json.dumps(registry, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                CaseCandidateError, "Registry is incomplete"
            ):
                engine.validate_existing()

    def test_changed_rule_mapped_field_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sandbox_root, evidence_root = create_fixture(
                Path(temporary_directory)
            )
            write_evidence(evidence_root)
            engine = create_engine(sandbox_root, evidence_root)
            engine.generate_all()
            candidate = read_candidate(sandbox_root, "CC-901")
            candidate["tags"] = ["inferred"]
            write_candidate(sandbox_root, "CC-901", candidate)

            with self.assertRaisesRegex(
                CaseCandidateError, "Broken rule mapping"
            ):
                engine.validate_existing()

    def test_schema_preserves_sandbox_boundary(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            "repository_only",
            schema["properties"]["model_impact"]["const"],
        )
        self.assertEqual(
            ["Pattern", "Experience", "Prediction", "Decision", "Strategy"],
            schema["x-sandbox"]["forbidden_outputs"],
        )


if __name__ == "__main__":
    unittest.main()
