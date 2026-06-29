"""Review-to-suggestion Learning Runtime with no Repository write access."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .context import RuntimeContext


class LearningRuntimeError(RuntimeError):
    """Raised when Review input cannot produce a bounded suggestion."""


@dataclass(frozen=True, slots=True)
class LessonSuggestion:
    lesson_id: str
    generated_at: str
    review_ref: str
    summary: str
    copied_review_fields: Mapping[str, Any]
    status: str = "candidate"
    production_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "generated_at": self.generated_at,
            "review_ref": self.review_ref,
            "summary": self.summary,
            "copied_review_fields": dict(self.copied_review_fields),
            "status": self.status,
            "production_authorized": self.production_authorized,
        }


@dataclass(frozen=True, slots=True)
class RepositoryPatchSuggestion:
    suggestion_id: str
    suggestion_type: str
    generated_at: str
    source_refs: tuple[str, ...]
    description: str
    uncertainty: tuple[str, ...]
    validation_required: bool
    target_repository: None
    status: str
    production_authorized: bool
    proposed_payload: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "suggestion_id": self.suggestion_id,
            "suggestion_type": self.suggestion_type,
            "generated_at": self.generated_at,
            "source_refs": list(self.source_refs),
            "description": self.description,
            "uncertainty": list(self.uncertainty),
            "validation_required": self.validation_required,
            "target_repository": self.target_repository,
            "status": self.status,
            "production_authorized": self.production_authorized,
            "proposed_payload": dict(self.proposed_payload),
        }


class LearningRuntime:
    """Copy an approved Review target into Lesson and Patch suggestions."""

    engine_id = "learning_runtime"
    COPIED_FIELDS = (
        "prediction_error",
        "behavior_error",
        "execution_error",
        "missing_information",
        "preventable",
        "learning_target",
    )

    def run(self, context: RuntimeContext) -> Mapping[str, Any]:
        payload = context.mutable_payload()
        review = payload.get("review")
        if not isinstance(review, Mapping):
            raise LearningRuntimeError("Learning Runtime requires a Review object")

        review_id = review.get("review_id")
        learning_target = review.get("learning_target")
        if not isinstance(review_id, str) or not review_id.strip():
            raise LearningRuntimeError("Review is missing review_id")
        if not isinstance(learning_target, str) or not learning_target.strip():
            raise LearningRuntimeError("Review is missing learning_target")

        now = datetime.now(timezone.utc).isoformat()
        copied = {
            field: review.get(field)
            for field in self.COPIED_FIELDS
            if field in review
        }
        lesson = LessonSuggestion(
            lesson_id=f"LESSON-{uuid4()}",
            generated_at=now,
            review_ref=review_id,
            summary=learning_target,
            copied_review_fields=copied,
        )

        uncertainty_raw = review.get("missing_information")
        if isinstance(uncertainty_raw, list):
            uncertainty = tuple(
                item for item in uncertainty_raw if isinstance(item, str)
            )
        elif isinstance(uncertainty_raw, str) and uncertainty_raw.strip():
            uncertainty = (uncertainty_raw,)
        else:
            uncertainty = ()

        patch = RepositoryPatchSuggestion(
            suggestion_id=f"PATCH-{uuid4()}",
            suggestion_type="lesson",
            generated_at=now,
            source_refs=(review_id,),
            description=learning_target,
            uncertainty=uncertainty,
            validation_required=True,
            target_repository=None,
            status="candidate",
            production_authorized=False,
            proposed_payload=lesson.to_dict(),
        )

        return {
            "contract_version": "1.0",
            "request_id": context.request_id,
            "engine_id": self.engine_id,
            "generated_at": now,
            "output_state": "candidate",
            "payload": {
                "lesson": lesson.to_dict(),
                "repository_patch_suggestion": patch.to_dict(),
            },
            "source_refs": list(context.source_refs),
            "warnings": [],
            "errors": [],
            "model_impact": "shadow_candidate_not_production",
        }
