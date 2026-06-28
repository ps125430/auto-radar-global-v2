"""Fail-fast Outcome, Evaluation, and Review Repository.

The repository validates and indexes static post-event records. It intentionally
provides no Prediction, Decision, Learning, Runtime, or scoring behavior.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class OutcomeReviewRepositoryError(RuntimeError):
    """Base error for post-event Repository failures."""


class OutcomeReviewValidationError(OutcomeReviewRepositoryError):
    """Raised when a record, schema, or cross-reference is invalid."""


@dataclass(frozen=True, slots=True)
class OutcomeRecord:
    outcome_id: str
    prediction_ref: str
    decision_ref: str
    market_open: str
    market_close: str
    window_10m: dict[str, Any]
    window_24h: dict[str, Any]
    window_t5d: dict[str, Any]
    status: str
    model_impact: str
    source_path: Path

    def to_index_record(self) -> dict[str, str]:
        return {
            "id": self.outcome_id,
            "prediction_ref": self.prediction_ref,
            "decision_ref": self.decision_ref,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class EvaluationRecord:
    evaluation_id: str
    prediction_ref: str
    outcome_ref: str
    overall_pms: float
    evaluation_status: str
    status: str
    model_impact: str
    source_path: Path

    def to_index_record(self) -> dict[str, Any]:
        return {
            "id": self.evaluation_id,
            "prediction_ref": self.prediction_ref,
            "outcome_ref": self.outcome_ref,
            "overall_pms": self.overall_pms,
            "evaluation_status": self.evaluation_status,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class ReviewRecord:
    review_id: str
    prediction_ref: str
    outcome_ref: str
    evaluation_ref: str
    status: str
    model_impact: str
    source_path: Path

    def to_index_record(self) -> dict[str, str]:
        return {
            "id": self.review_id,
            "prediction_ref": self.prediction_ref,
            "outcome_ref": self.outcome_ref,
            "evaluation_ref": self.evaluation_ref,
            "status": self.status,
        }


class OutcomeReviewRepository:
    """Unified scanner, validator, registry, and index builder."""

    def __init__(
        self,
        outcome_root: Path | str | None = None,
        evaluation_root: Path | str | None = None,
        review_root: Path | str | None = None,
        outcome_schema_path: Path | str | None = None,
        evaluation_schema_path: Path | str | None = None,
        review_schema_path: Path | str | None = None,
        *,
        auto_start: bool = True,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.outcome_root = Path(
            outcome_root or repository_root / "Knowledge" / "Outcome"
        )
        self.evaluation_root = Path(
            evaluation_root or repository_root / "Knowledge" / "OutcomeEvaluation"
        )
        self.review_root = Path(
            review_root or repository_root / "Knowledge" / "DailyReview"
        )
        self.outcome_schema_path = Path(
            outcome_schema_path
            or repository_root / "Schemas" / "Outcome" / "outcome.schema.json"
        )
        self.evaluation_schema_path = Path(
            evaluation_schema_path
            or repository_root
            / "Schemas"
            / "OutcomeEvaluation"
            / "outcome_evaluation.schema.json"
        )
        self.review_schema_path = Path(
            review_schema_path
            or repository_root
            / "Schemas"
            / "DailyDecision"
            / "review_record.schema.json"
        )
        self._outcome_schema = self._load_schema(
            self.outcome_schema_path, "Outcome", "review_only_not_production"
        )
        self._evaluation_schema = self._load_schema(
            self.evaluation_schema_path,
            "Evaluation",
            "research_only_not_production",
        )
        self._review_schema = self._load_schema(
            self.review_schema_path, "Review", "review_pipeline_only"
        )
        self._outcomes: dict[str, OutcomeRecord] = {}
        self._evaluations: dict[str, EvaluationRecord] = {}
        self._reviews: dict[str, ReviewRecord] = {}

        if auto_start:
            self.start()

    def start(self) -> None:
        """Validate all three layers before atomically replacing their indexes."""
        outcome_payloads = self._scan_and_load(
            self.outcome_root, self._outcome_schema, "Outcome"
        )
        evaluation_payloads = self._scan_and_load(
            self.evaluation_root, self._evaluation_schema, "Evaluation"
        )
        review_payloads = self._scan_and_load(
            self.review_root, self._review_schema, "Review"
        )

        outcomes = self._register_outcomes(outcome_payloads)
        evaluations = self._register_evaluations(evaluation_payloads, outcomes)
        reviews = self._register_reviews(review_payloads, outcomes, evaluations)

        self._outcomes = outcomes
        self._evaluations = evaluations
        self._reviews = reviews
        self._write_indexes()

    def list_outcomes(self) -> list[OutcomeRecord]:
        return [self._outcomes[key] for key in sorted(self._outcomes)]

    def list_evaluations(self) -> list[EvaluationRecord]:
        return [self._evaluations[key] for key in sorted(self._evaluations)]

    def list_reviews(self) -> list[ReviewRecord]:
        return [self._reviews[key] for key in sorted(self._reviews)]

    def _scan_and_load(
        self,
        root: Path,
        schema: dict[str, Any],
        entity_name: str,
    ) -> list[tuple[dict[str, Any], Path]]:
        records_root = root / "Records"
        if not records_root.is_dir():
            raise OutcomeReviewRepositoryError(
                f"{entity_name} Records directory does not exist: {records_root}"
            )

        loaded: list[tuple[dict[str, Any], Path]] = []
        for path in sorted(records_root.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                raise OutcomeReviewValidationError(
                    f"Unable to load {entity_name} JSON: {path}"
                ) from exc
            self._validate_schema(payload, schema, path)
            loaded.append((payload, path))
        return loaded

    def _register_outcomes(
        self, payloads: list[tuple[dict[str, Any], Path]]
    ) -> dict[str, OutcomeRecord]:
        registry: dict[str, OutcomeRecord] = {}
        for payload, path in payloads:
            record = OutcomeRecord(
                outcome_id=payload["outcome_id"],
                prediction_ref=payload["prediction_ref"],
                decision_ref=payload["decision_ref"],
                market_open=payload["market_open"],
                market_close=payload["market_close"],
                window_10m=payload["window_10m"],
                window_24h=payload["window_24h"],
                window_t5d=payload["window_t5d"],
                status=payload["status"],
                model_impact=payload["model_impact"],
                source_path=path,
            )
            self._reject_duplicate(
                registry, record.outcome_id, path, "Outcome"
            )
            registry[record.outcome_id] = record
        return registry

    def _register_evaluations(
        self,
        payloads: list[tuple[dict[str, Any], Path]],
        outcomes: dict[str, OutcomeRecord],
    ) -> dict[str, EvaluationRecord]:
        registry: dict[str, EvaluationRecord] = {}
        for payload, path in payloads:
            outcome = outcomes.get(payload["outcome_ref"])
            if outcome is None:
                raise OutcomeReviewValidationError(
                    f"{path}: missing outcome_ref {payload['outcome_ref']}"
                )
            if payload["prediction_ref"] != outcome.prediction_ref:
                raise OutcomeReviewValidationError(
                    f"{path}: prediction_ref does not match referenced Outcome"
                )

            record = EvaluationRecord(
                evaluation_id=payload["evaluation_id"],
                prediction_ref=payload["prediction_ref"],
                outcome_ref=payload["outcome_ref"],
                overall_pms=float(payload["overall_pms"]),
                evaluation_status=payload["evaluation_status"],
                status=payload["status"],
                model_impact=payload["model_impact"],
                source_path=path,
            )
            self._reject_duplicate(
                registry, record.evaluation_id, path, "Evaluation"
            )
            registry[record.evaluation_id] = record
        return registry

    def _register_reviews(
        self,
        payloads: list[tuple[dict[str, Any], Path]],
        outcomes: dict[str, OutcomeRecord],
        evaluations: dict[str, EvaluationRecord],
    ) -> dict[str, ReviewRecord]:
        registry: dict[str, ReviewRecord] = {}
        for payload, path in payloads:
            outcome = outcomes.get(payload["outcome_ref"])
            if outcome is None:
                raise OutcomeReviewValidationError(
                    f"{path}: missing outcome_ref {payload['outcome_ref']}"
                )
            evaluation = evaluations.get(payload["evaluation_ref"])
            if evaluation is None:
                raise OutcomeReviewValidationError(
                    f"{path}: missing evaluation_ref {payload['evaluation_ref']}"
                )
            if evaluation.outcome_ref != outcome.outcome_id:
                raise OutcomeReviewValidationError(
                    f"{path}: evaluation_ref does not belong to outcome_ref"
                )
            if (
                payload["prediction_ref"] != outcome.prediction_ref
                or payload["prediction_ref"] != evaluation.prediction_ref
            ):
                raise OutcomeReviewValidationError(
                    f"{path}: prediction_ref is inconsistent across records"
                )

            record = ReviewRecord(
                review_id=payload["review_id"],
                prediction_ref=payload["prediction_ref"],
                outcome_ref=payload["outcome_ref"],
                evaluation_ref=payload["evaluation_ref"],
                status=payload["status"],
                model_impact=payload["model_impact"],
                source_path=path,
            )
            self._reject_duplicate(registry, record.review_id, path, "Review")
            registry[record.review_id] = record
        return registry

    @staticmethod
    def _reject_duplicate(
        registry: dict[str, Any],
        entity_id: str,
        path: Path,
        entity_name: str,
    ) -> None:
        if entity_id in registry:
            first = registry[entity_id].source_path
            raise OutcomeReviewValidationError(
                f"Duplicate {entity_name} ID {entity_id}: {first} and {path}"
            )

    @staticmethod
    def _load_schema(
        path: Path, entity_name: str, expected_model_impact: str
    ) -> dict[str, Any]:
        try:
            schema = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise OutcomeReviewValidationError(
                f"Unable to load {entity_name} schema: {path}"
            ) from exc

        required_keys = {
            "$schema",
            "$id",
            "type",
            "additionalProperties",
            "required",
            "properties",
            "x-repository",
        }
        missing = required_keys - set(schema)
        if missing:
            raise OutcomeReviewValidationError(
                f"{entity_name} schema missing fields: {', '.join(sorted(missing))}"
            )
        if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            raise OutcomeReviewValidationError(
                f"{entity_name} schema must use JSON Schema 2020-12"
            )
        if schema["type"] != "object" or schema["additionalProperties"] is not False:
            raise OutcomeReviewValidationError(
                f"{entity_name} schema must define a closed object"
            )
        if schema["x-repository"].get("model_impact") != expected_model_impact:
            raise OutcomeReviewValidationError(
                f"{entity_name} schema has invalid model impact"
            )
        return schema

    def _validate_schema(
        self, payload: Any, schema: dict[str, Any], path: Path
    ) -> None:
        if not isinstance(payload, dict):
            raise OutcomeReviewValidationError(f"{path}: record must be an object")

        required = set(schema["required"])
        missing = required - set(payload)
        if missing:
            raise OutcomeReviewValidationError(
                f"{path}: missing fields: {', '.join(sorted(missing))}"
            )
        if schema["additionalProperties"] is False:
            extra = set(payload) - set(schema["properties"])
            if extra:
                raise OutcomeReviewValidationError(
                    f"{path}: unexpected fields: {', '.join(sorted(extra))}"
                )

        for field, definition in schema["properties"].items():
            if field in payload:
                self._validate_value(field, payload[field], definition, path)

    def _validate_value(
        self,
        field: str,
        value: Any,
        definition: dict[str, Any],
        path: Path,
    ) -> None:
        expected_type = definition.get("type")
        if expected_type == "number":
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise OutcomeReviewValidationError(
                    f"{path}: {field} must be a finite number"
                )
            if value < definition.get("minimum", value):
                raise OutcomeReviewValidationError(
                    f"{path}: {field} is below its minimum"
                )
            if value > definition.get("maximum", value):
                raise OutcomeReviewValidationError(
                    f"{path}: {field} is above its maximum"
                )
            return

        type_map = {"string": str, "object": dict, "array": list}
        python_type = type_map.get(expected_type)
        if python_type is None or not isinstance(value, python_type):
            raise OutcomeReviewValidationError(
                f"{path}: {field} must be {expected_type}"
            )

        if expected_type == "string":
            pattern = definition.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                raise OutcomeReviewValidationError(
                    f"{path}: {field} has an invalid format"
                )
            if "enum" in definition and value not in definition["enum"]:
                raise OutcomeReviewValidationError(
                    f"{path}: invalid {field} {value!r}"
                )
            if "const" in definition and value != definition["const"]:
                raise OutcomeReviewValidationError(
                    f"{path}: invalid {field} {value!r}"
                )

        if expected_type == "array":
            item_definition = definition.get("items", {})
            for index, item in enumerate(value):
                self._validate_value(
                    f"{field}[{index}]", item, item_definition, path
                )

    def _write_indexes(self) -> None:
        indexes = (
            (
                self.outcome_root / "index.json",
                {
                    "document_id": "AR-OUTCOME-REPOSITORY-INDEX-v1",
                    "version": "1.0",
                    "status": "repository_index",
                    "model_impact": "review_only_not_production",
                    "outcome_count": len(self._outcomes),
                    "outcomes": [
                        record.to_index_record() for record in self.list_outcomes()
                    ],
                },
            ),
            (
                self.evaluation_root / "index.json",
                {
                    "document_id": "AR-OUTCOME-EVALUATION-INDEX-v1",
                    "version": "1.0",
                    "status": "repository_index",
                    "model_impact": "research_only_not_production",
                    "evaluation_count": len(self._evaluations),
                    "evaluations": [
                        record.to_index_record()
                        for record in self.list_evaluations()
                    ],
                },
            ),
            (
                self.review_root / "index.json",
                {
                    "document_id": "AR-DAILY-REVIEW-INDEX-v1",
                    "version": "1.0",
                    "status": "repository_index",
                    "model_impact": "review_pipeline_only",
                    "review_count": len(self._reviews),
                    "reviews": [
                        record.to_index_record() for record in self.list_reviews()
                    ],
                },
            ),
        )

        temporary_paths: list[tuple[Path, Path]] = []
        try:
            for path, payload in indexes:
                temporary_path = path.with_suffix(f"{path.suffix}.tmp")
                temporary_path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                temporary_paths.append((temporary_path, path))
            for temporary_path, path in temporary_paths:
                temporary_path.replace(path)
        except OSError as exc:
            for temporary_path, _ in temporary_paths:
                temporary_path.unlink(missing_ok=True)
            raise OutcomeReviewRepositoryError(
                "Unable to write Outcome Review Repository indexes"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build Outcome, Evaluation, and Review Repository indexes."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    repository = OutcomeReviewRepository()
    print(f"Registered {len(repository.list_outcomes())} Outcome(s).")
    print(f"Registered {len(repository.list_evaluations())} Evaluation(s).")
    print(f"Registered {len(repository.list_reviews())} Review(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

