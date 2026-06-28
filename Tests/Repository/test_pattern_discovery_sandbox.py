from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Sandbox.PatternDiscovery.pattern_discovery import (
    PatternDiscoveryError,
    PatternDiscoverySandbox,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DISCOVERY_SOURCE = REPOSITORY_ROOT / "Sandbox" / "PatternDiscovery"
REVIEW_SOURCE = REPOSITORY_ROOT / "Sandbox" / "Review"
EVIDENCE_SOURCE = REPOSITORY_ROOT / "Sandbox" / "Ingestion" / "processed"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def create_fixture(root: Path) -> tuple[Path, Path, Path]:
    discovery_root = root / "PatternDiscovery"
    review_root = root / "Review"
    evidence_root = root / "Evidence"
    for folder in ("candidates", "processed", "failed"):
        (discovery_root / folder).mkdir(parents=True)
    (review_root / "verified").mkdir(parents=True)
    evidence_root.mkdir()

    shutil.copy2(
        DISCOVERY_SOURCE / "pattern_candidate.schema.json",
        discovery_root / "pattern_candidate.schema.json",
    )
    write_json(
        discovery_root / "pattern_candidate_registry.json",
        {
            "generated_at": "2026-06-28T00:00:00+00:00",
            "pattern_candidate_count": 0,
            "pattern_candidates": [],
        },
    )
    shutil.copy2(
        REVIEW_SOURCE / "verified_case_registry.json",
        review_root / "verified_case_registry.json",
    )
    for case in (REVIEW_SOURCE / "verified").glob("*.json"):
        shutil.copy2(case, review_root / "verified" / case.name)
    for evidence in EVIDENCE_SOURCE.glob("*.md"):
        shutil.copy2(evidence, evidence_root / evidence.name)
    return discovery_root, review_root, evidence_root


def sandbox(
    discovery_root: Path,
    review_root: Path,
    evidence_root: Path,
) -> PatternDiscoverySandbox:
    return PatternDiscoverySandbox(
        sandbox_root=discovery_root,
        verified_root=review_root / "verified",
        verified_registry_path=review_root
        / "verified_case_registry.json",
        evidence_root=evidence_root,
        schema_path=discovery_root / "pattern_candidate.schema.json",
    )


def read_candidate(
    discovery_root: Path, pattern_id: str
) -> dict[str, object]:
    return json.loads(
        (discovery_root / f"candidates/{pattern_id}.json").read_text(
            encoding="utf-8"
        )
    )


def write_candidate(
    discovery_root: Path,
    pattern_id: str,
    candidate: dict[str, object],
    filename: str | None = None,
) -> None:
    write_json(
        discovery_root / "candidates" / (filename or f"{pattern_id}.json"),
        candidate,
    )


class PatternDiscoverySandboxTests(unittest.TestCase):
    def test_three_rule_groups_are_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))

            registry = sandbox(*roots).discover_all()

            self.assertEqual(3, registry["pattern_candidate_count"])
            self.assertEqual(
                ["VC-101", "VC-103"],
                read_candidate(roots[0], "PC-001")["source_cases"],
            )
            self.assertEqual(
                ["VC-102", "VC-104"],
                read_candidate(roots[0], "PC-002")["source_cases"],
            )
            self.assertEqual(
                ["VC-105"],
                read_candidate(roots[0], "PC-003")["source_cases"],
            )

    def test_pattern_case_evidence_traceability_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()

            result = engine.validate_existing()

            self.assertEqual("PASS", result["validation_status"])
            self.assertEqual(3, result["pattern_candidate_count"])
            self.assertEqual(5, result["verified_cases_traced"])
            self.assertEqual(5, result["evidence_records_traced"])

    def test_duplicate_pattern_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()
            candidate = read_candidate(roots[0], "PC-001")
            write_candidate(
                roots[0], "PC-001", candidate, filename="DUPLICATE.json"
            )

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Duplicate Pattern"
            ):
                engine.validate_existing()

    def test_discovery_rejects_existing_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Duplicate Pattern"
            ):
                engine.discover_all()

    def test_missing_case_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()
            candidate = read_candidate(roots[0], "PC-001")
            candidate["source_cases"] = []
            write_candidate(roots[0], "PC-001", candidate)

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Missing Case"
            ):
                engine.validate_existing()

    def test_broken_case_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()
            candidate = read_candidate(roots[0], "PC-001")
            candidate["source_cases"] = ["VC-999"]
            write_candidate(roots[0], "PC-001", candidate)

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Broken Case reference"
            ):
                engine.validate_existing()

    def test_broken_evidence_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            (roots[2] / "EV-101.md").unlink()

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Broken Evidence reference"
            ):
                sandbox(*roots).discover_all()

    def test_invalid_status_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()
            candidate = read_candidate(roots[0], "PC-001")
            candidate["status"] = "Verified"
            write_candidate(roots[0], "PC-001", candidate)

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Invalid Status"
            ):
                engine.validate_existing()

    def test_invalid_similarity_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()
            candidate = read_candidate(roots[0], "PC-001")
            candidate["similarity_score"] = 1.1
            write_candidate(roots[0], "PC-001", candidate)

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Invalid Similarity"
            ):
                engine.validate_existing()

    def test_missing_fields_fail_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()
            candidate = read_candidate(roots[0], "PC-001")
            del candidate["feature_summary"]
            write_candidate(roots[0], "PC-001", candidate)

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Missing Fields"
            ):
                engine.validate_existing()

    def test_registry_mismatch_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()
            registry_path = (
                roots[0] / "pattern_candidate_registry.json"
            )
            registry = json.loads(
                registry_path.read_text(encoding="utf-8")
            )
            registry["pattern_candidate_count"] = 2
            write_json(registry_path, registry)

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Registry mismatch"
            ):
                engine.validate_existing()

    def test_changed_rule_mapping_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_fixture(Path(temporary_directory))
            engine = sandbox(*roots)
            engine.discover_all()
            candidate = read_candidate(roots[0], "PC-001")
            candidate["pattern_tags"] = ["changed"]
            write_candidate(roots[0], "PC-001", candidate)

            with self.assertRaisesRegex(
                PatternDiscoveryError, "Broken Pattern rule mapping"
            ):
                engine.validate_existing()

    def test_schema_preserves_rule_only_boundary(self) -> None:
        schema = json.loads(
            (
                DISCOVERY_SOURCE / "pattern_candidate.schema.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            "rule_based_only", schema["x-sandbox"]["discovery_mode"]
        )
        self.assertEqual(
            "binary_rule_match_not_model_confidence",
            schema["x-sandbox"]["similarity_semantics"],
        )
        self.assertEqual(
            "repository_only",
            schema["properties"]["model_impact"]["const"],
        )


if __name__ == "__main__":
    unittest.main()
