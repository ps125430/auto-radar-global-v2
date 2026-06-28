from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Sandbox.Review.review_pipeline import (
    ReviewPipelineError,
    SandboxReviewPipeline,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REVIEW_SOURCE = REPOSITORY_ROOT / "Sandbox" / "Review"
CANDIDATE_SOURCE = REPOSITORY_ROOT / "Sandbox" / "CaseCandidate"


def create_fixture(root: Path) -> tuple[Path, Path]:
    review_root = root / "Review"
    candidate_root = root / "CaseCandidate"
    for folder in ("pending", "approved", "rejected", "verified"):
        (review_root / folder).mkdir(parents=True)
    (candidate_root / "candidates").mkdir(parents=True)
    shutil.copy2(
        REVIEW_SOURCE / "review.schema.json",
        review_root / "review.schema.json",
    )
    for candidate in (CANDIDATE_SOURCE / "candidates").glob("*.json"):
        shutil.copy2(
            candidate, candidate_root / "candidates" / candidate.name
        )
    shutil.copy2(
        CANDIDATE_SOURCE / "candidate_registry.json",
        candidate_root / "candidate_registry.json",
    )
    write_json(
        review_root / "verified_case_registry.json",
        {
            "generated_at": "2026-06-28T00:00:00+00:00",
            "review_count": 0,
            "reviews": [],
            "verified_case_count": 0,
            "verified_cases": [],
        },
    )
    return review_root, candidate_root


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def review_payload(
    *,
    review_id: str = "REV-101",
    candidate_id: str = "CC-101",
    status: str = "Approved",
    **overrides: object,
) -> dict[str, object]:
    decisions = {
        "Pending": "Pending",
        "Approved": "Approve",
        "Rejected": "Reject",
        "Verified": "Approve",
    }
    payload: dict[str, object] = {
        "review_id": review_id,
        "candidate_id": candidate_id,
        "review_status": status,
        "reviewed_at": "2026-06-28T16:00:00+00:00",
        "reviewer": "Test Reviewer",
        "decision": decisions.get(status, "Approve"),
        "notes": "Human review test record.",
        "verified_case_id": (
            f"VC-{candidate_id.removeprefix('CC-')}"
            if status in {"Approved", "Verified"}
            else None
        ),
        "model_impact": "repository_only",
    }
    payload.update(overrides)
    return payload


def write_review(
    review_root: Path,
    payload: dict[str, object],
    folder: str | None = None,
    filename: str | None = None,
) -> Path:
    status_folder = folder or {
        "Pending": "pending",
        "Approved": "approved",
        "Rejected": "rejected",
        "Verified": "approved",
    }.get(str(payload.get("review_status")), "approved")
    path = review_root / status_folder / (
        filename or f"{payload['review_id']}.json"
    )
    write_json(path, payload)
    return path


def pipeline(
    review_root: Path, candidate_root: Path
) -> SandboxReviewPipeline:
    return SandboxReviewPipeline(
        review_root=review_root,
        candidate_root=candidate_root / "candidates",
        candidate_registry_path=candidate_root / "candidate_registry.json",
        schema_path=review_root / "review.schema.json",
    )


class SandboxReviewPipelineTests(unittest.TestCase):
    def test_approved_review_materializes_verified_case(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(review_root, review_payload())

            registry = pipeline(review_root, candidate_root).verify_all()
            verified_case = json.loads(
                (review_root / "verified/VC-101.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(1, registry["review_count"])
            self.assertEqual(1, registry["verified_case_count"])
            self.assertEqual("CC-101", verified_case["candidate_id"])
            self.assertEqual("EV-101", verified_case["evidence_id"])
            self.assertEqual("REV-101", verified_case["review_id"])
            self.assertEqual("Verified", verified_case["status"])

    def test_five_reviews_create_five_traceable_verified_cases(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            for source in (REVIEW_SOURCE / "approved").glob("*.json"):
                shutil.copy2(source, review_root / "approved" / source.name)

            engine = pipeline(review_root, candidate_root)
            registry = engine.verify_all()
            result = engine.validate_existing()

            self.assertEqual(5, registry["review_count"])
            self.assertEqual(5, registry["verified_case_count"])
            self.assertEqual(5, result["verified_case_count"])
            self.assertEqual(
                {f"CC-{number}" for number in range(101, 106)},
                {
                    record["candidate_id"]
                    for record in registry["verified_cases"]
                },
            )

    def test_pending_review_does_not_create_verified_case(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(
                review_root, review_payload(status="Pending")
            )

            registry = pipeline(review_root, candidate_root).verify_all()

            self.assertEqual(1, registry["review_count"])
            self.assertEqual(0, registry["verified_case_count"])

    def test_rejected_review_does_not_create_verified_case(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(
                review_root, review_payload(status="Rejected")
            )

            result = pipeline(review_root, candidate_root).verify_all()

            self.assertEqual(0, result["verified_case_count"])

    def test_missing_candidate_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            (candidate_root / "candidates/CC-101.json").unlink()
            write_review(review_root, review_payload())

            with self.assertRaisesRegex(
                ReviewPipelineError, "Missing Candidate"
            ):
                pipeline(review_root, candidate_root).verify_all()

    def test_broken_candidate_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(
                review_root,
                review_payload(
                    candidate_id="CC-999",
                    verified_case_id="VC-999",
                ),
            )

            with self.assertRaisesRegex(
                ReviewPipelineError, "Broken Candidate reference"
            ):
                pipeline(review_root, candidate_root).verify_all()

    def test_duplicate_review_id_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(review_root, review_payload())
            write_review(
                review_root,
                review_payload(
                    candidate_id="CC-102",
                    status="Pending",
                    verified_case_id=None,
                ),
                filename="DUPLICATE.json",
            )

            with self.assertRaisesRegex(
                ReviewPipelineError, "Duplicate Review"
            ):
                pipeline(review_root, candidate_root).verify_all()

    def test_duplicate_review_for_candidate_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(review_root, review_payload())
            write_review(
                review_root,
                review_payload(
                    review_id="REV-102",
                    verified_case_id="VC-102",
                ),
            )

            with self.assertRaisesRegex(
                ReviewPipelineError, "Duplicate Review for Candidate"
            ):
                pipeline(review_root, candidate_root).verify_all()

    def test_invalid_status_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(
                review_root,
                review_payload(status="Unknown"),
                folder="approved",
            )

            with self.assertRaisesRegex(
                ReviewPipelineError, "Invalid Status"
            ):
                pipeline(review_root, candidate_root).verify_all()

    def test_missing_required_field_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            payload = review_payload()
            del payload["reviewer"]
            write_review(review_root, payload)

            with self.assertRaisesRegex(
                ReviewPipelineError, "Missing Required Fields"
            ):
                pipeline(review_root, candidate_root).verify_all()

    def test_invalid_status_decision_pairing_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(
                review_root,
                review_payload(decision="Reject"),
            )

            with self.assertRaisesRegex(
                ReviewPipelineError, "Invalid Status decision pairing"
            ):
                pipeline(review_root, candidate_root).verify_all()

    def test_broken_verified_case_mapping_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            review_root, candidate_root = create_fixture(
                Path(temporary_directory)
            )
            write_review(review_root, review_payload())
            engine = pipeline(review_root, candidate_root)
            engine.verify_all()
            path = review_root / "verified/VC-101.json"
            verified_case = json.loads(path.read_text(encoding="utf-8"))
            verified_case["title"] = "Changed after Review"
            write_json(path, verified_case)

            with self.assertRaisesRegex(
                ReviewPipelineError, "Broken Verified Case"
            ):
                engine.validate_existing()

    def test_review_schema_preserves_human_only_boundary(self) -> None:
        schema = json.loads(
            (REVIEW_SOURCE / "review.schema.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual("human_only", schema["x-sandbox"]["review_mode"])
        self.assertFalse(schema["x-sandbox"]["formal_case_promotion"])
        self.assertEqual(
            "repository_only",
            schema["properties"]["model_impact"]["const"],
        )


if __name__ == "__main__":
    unittest.main()
