from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Scripts.Repository.outcome_review_repository import (
    OutcomeReviewRepository,
    OutcomeReviewValidationError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
OUTCOME_SCHEMA = REPOSITORY_ROOT / "Schemas" / "Outcome" / "outcome.schema.json"
EVALUATION_SCHEMA = (
    REPOSITORY_ROOT
    / "Schemas"
    / "OutcomeEvaluation"
    / "outcome_evaluation.schema.json"
)
REVIEW_SCHEMA = (
    REPOSITORY_ROOT
    / "Schemas"
    / "DailyDecision"
    / "review_record.schema.json"
)


def create_roots(root: Path) -> tuple[Path, Path, Path]:
    roots = (
        root / "Outcome",
        root / "OutcomeEvaluation",
        root / "DailyReview",
    )
    for repository_root in roots:
        (repository_root / "Records").mkdir(parents=True)
    return roots


def outcome_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "outcome_id": "OUT-001",
        "prediction_ref": "PRED-001",
        "decision_ref": "DEC-001",
        "market_open": "open",
        "market_close": "close",
        "window_10m": {},
        "window_24h": {},
        "window_t5d": {},
        "status": "reviewed",
        "model_impact": "review_only_not_production",
    }
    payload.update(overrides)
    return payload


def evaluation_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "evaluation_id": "EVAL-001",
        "prediction_ref": "PRED-001",
        "outcome_ref": "OUT-001",
        "overall_pms": 75,
        "narrative_match": 80,
        "leader_match": 70,
        "theme_match": 75,
        "flow_match": 65,
        "timing_match": 70,
        "risk_match": 80,
        "luck_penalty": 5,
        "evaluation_status": "PARTIAL_SUCCESS",
        "status": "reviewed",
        "model_impact": "research_only_not_production",
    }
    payload.update(overrides)
    return payload


def review_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "review_id": "REV-001",
        "prediction_ref": "PRED-001",
        "outcome_ref": "OUT-001",
        "evaluation_ref": "EVAL-001",
        "prediction_error": {},
        "behavior_error": {},
        "execution_error": {},
        "missing_information": [],
        "preventable": {},
        "learning_target": [],
        "status": "reviewed",
        "model_impact": "review_pipeline_only",
    }
    payload.update(overrides)
    return payload


def write_record(root: Path, name: str, payload: dict[str, object]) -> None:
    (root / "Records" / name).write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


class OutcomeReviewRepositoryTests(unittest.TestCase):
    def create_repository(
        self, roots: tuple[Path, Path, Path]
    ) -> OutcomeReviewRepository:
        outcome_root, evaluation_root, review_root = roots
        return OutcomeReviewRepository(
            outcome_root=outcome_root,
            evaluation_root=evaluation_root,
            review_root=review_root,
            outcome_schema_path=OUTCOME_SCHEMA,
            evaluation_schema_path=EVALUATION_SCHEMA,
            review_schema_path=REVIEW_SCHEMA,
        )

    def write_valid_chain(self, roots: tuple[Path, Path, Path]) -> None:
        outcome_root, evaluation_root, review_root = roots
        write_record(outcome_root, "OUT-001.json", outcome_payload())
        write_record(
            evaluation_root, "EVAL-001.json", evaluation_payload()
        )
        write_record(review_root, "REV-001.json", review_payload())

    def test_empty_repositories_generate_valid_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))

            repository = self.create_repository(roots)

            self.assertEqual([], repository.list_outcomes())
            self.assertEqual([], repository.list_evaluations())
            self.assertEqual([], repository.list_reviews())

    def test_valid_chain_is_registered_and_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))
            self.write_valid_chain(roots)

            repository = self.create_repository(roots)

            self.assertEqual(1, len(repository.list_outcomes()))
            self.assertEqual(1, len(repository.list_evaluations()))
            self.assertEqual(1, len(repository.list_reviews()))
            review_index = json.loads(
                (roots[2] / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual("EVAL-001", review_index["reviews"][0]["evaluation_ref"])

    def test_missing_prediction_ref_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))
            payload = outcome_payload()
            del payload["prediction_ref"]
            write_record(roots[0], "OUT-001.json", payload)

            with self.assertRaises(OutcomeReviewValidationError):
                self.create_repository(roots)

    def test_missing_outcome_ref_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))
            write_record(
                roots[1],
                "EVAL-001.json",
                evaluation_payload(outcome_ref="OUT-999"),
            )

            with self.assertRaises(OutcomeReviewValidationError):
                self.create_repository(roots)

    def test_missing_evaluation_ref_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))
            write_record(roots[0], "OUT-001.json", outcome_payload())
            write_record(
                roots[2],
                "REV-001.json",
                review_payload(evaluation_ref="EVAL-999"),
            )

            with self.assertRaises(OutcomeReviewValidationError):
                self.create_repository(roots)

    def test_invalid_status_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))
            write_record(
                roots[0], "OUT-001.json", outcome_payload(status="invalid")
            )

            with self.assertRaises(OutcomeReviewValidationError):
                self.create_repository(roots)

    def test_invalid_model_impact_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))
            write_record(
                roots[0],
                "OUT-001.json",
                outcome_payload(model_impact="production"),
            )

            with self.assertRaises(OutcomeReviewValidationError):
                self.create_repository(roots)

    def test_invalid_pms_range_fails_fast(self) -> None:
        for invalid_pms in (-1, 101, True, "50", float("nan")):
            with self.subTest(overall_pms=invalid_pms):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    roots = create_roots(Path(temporary_directory))
                    write_record(roots[0], "OUT-001.json", outcome_payload())
                    write_record(
                        roots[1],
                        "EVAL-001.json",
                        evaluation_payload(overall_pms=invalid_pms),
                    )

                    with self.assertRaises(OutcomeReviewValidationError):
                        self.create_repository(roots)

    def test_duplicate_id_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))
            write_record(roots[0], "OUT-001_A.json", outcome_payload())
            write_record(roots[0], "OUT-001_B.json", outcome_payload())

            with self.assertRaises(OutcomeReviewValidationError):
                self.create_repository(roots)

    def test_prediction_reference_mismatch_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            roots = create_roots(Path(temporary_directory))
            write_record(roots[0], "OUT-001.json", outcome_payload())
            write_record(
                roots[1],
                "EVAL-001.json",
                evaluation_payload(prediction_ref="PRED-002"),
            )

            with self.assertRaises(OutcomeReviewValidationError):
                self.create_repository(roots)


if __name__ == "__main__":
    unittest.main()

