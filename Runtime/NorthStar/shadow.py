"""North Star Shadow Integration.

This module wires approved Runtime infrastructure into an in-memory Shadow
flow. It does not create Strategy, Scoring, trading signals, or Repository
writes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .decision import DecisionRuntime
from .explain import ExplainRuntime
from .framework import RuntimeFramework
from .learning import LearningRuntime
from .patch_queue import PatchQueueEntry, RepositoryPatchQueue


class ShadowIntegrationError(RuntimeError):
    """Raised when Shadow Runtime Integration violates its contract."""


@dataclass(frozen=True, slots=True)
class ShadowRunResult:
    """In-memory result for one Daily Shadow Decision Run."""

    run_id: str
    generated_at: str
    decision: Mapping[str, Any]
    explain_chain: Mapping[str, Any]
    shadow_output: Mapping[str, Any]
    review: Mapping[str, Any] | None = None
    learning: Mapping[str, Any] | None = None
    patch_entry: PatchQueueEntry | None = None


class ShadowRuntimeOrchestrator:
    """Coordinate Decision, Explain, Learning, and Patch Queue in Shadow mode."""

    def __init__(
        self,
        repository_root: str,
        *,
        patch_queue: RepositoryPatchQueue | None = None,
    ) -> None:
        self.framework = RuntimeFramework(repository_root, enabled=True)
        self.framework.register(DecisionRuntime())
        self.framework.register(ExplainRuntime())
        self.framework.register(LearningRuntime())
        self.patch_queue = patch_queue or RepositoryPatchQueue()

    def run_daily_shadow_decision(
        self,
        *,
        decision_refs: Mapping[str, str],
        explain_refs: Mapping[str, Sequence[str] | str],
        display_candidates: Mapping[str, Any] | None = None,
    ) -> ShadowRunResult:
        """Run E-127 without converting Shadow output into a formal Decision."""

        required_decision_refs = (
            "captain_profile",
            "regime",
            "flow",
            "repository",
            "opportunity",
        )
        missing = [
            key
            for key in required_decision_refs
            if not isinstance(decision_refs.get(key), str)
            or not str(decision_refs.get(key)).strip()
        ]
        if missing:
            raise ShadowIntegrationError(
                f"Daily Shadow Decision is missing refs: {', '.join(missing)}"
            )

        decision_source_refs = tuple(
            str(decision_refs[key]) for key in required_decision_refs
        )
        decision_execution = self.framework.execute(
            "decision_runtime",
            source_refs=decision_source_refs,
            payload=dict(decision_refs),
        )
        decision = decision_execution.output

        explain_payload = self._build_explain_payload(
            decision_ref=str(decision["decision_id"]),
            explain_refs=explain_refs,
        )
        explain_source_refs = tuple(
            reference
            for value in explain_payload.values()
            for reference in self._references_from_value(value)
            if reference != decision["decision_id"]
        )
        explain_execution = self.framework.execute(
            "explain_runtime",
            source_refs=explain_source_refs,
            payload=explain_payload,
        )
        explain_chain = explain_execution.output

        shadow_output = DailyShadowDecisionRun.render(
            decision=decision,
            explain_chain=explain_chain,
            display_candidates=display_candidates or {},
        )
        return ShadowRunResult(
            run_id=shadow_output["shadow_run_id"],
            generated_at=shadow_output["generated_at"],
            decision=decision,
            explain_chain=explain_chain,
            shadow_output=shadow_output,
        )

    def run_shadow_review(
        self,
        *,
        shadow_result: ShadowRunResult,
        manual_outcome: Mapping[str, Any] | None = None,
    ) -> ShadowRunResult:
        """Create Review and Lesson Draft; no lesson becomes active."""

        review = ShadowReviewPipeline.create_review(
            shadow_output=shadow_result.shadow_output,
            manual_outcome=manual_outcome,
        )
        learning_execution = self.framework.execute(
            "learning_runtime",
            source_refs=(),
            payload={"review": review},
        )
        return ShadowRunResult(
            run_id=shadow_result.run_id,
            generated_at=shadow_result.generated_at,
            decision=shadow_result.decision,
            explain_chain=shadow_result.explain_chain,
            shadow_output=shadow_result.shadow_output,
            review=review,
            learning=learning_execution.output,
        )

    def enqueue_learning_patch(
        self,
        *,
        shadow_result: ShadowRunResult,
    ) -> ShadowRunResult:
        """Move a Learning Runtime suggestion into Pending Review only."""

        if shadow_result.learning is None:
            raise ShadowIntegrationError("Learning output is required first")
        patch_suggestion = shadow_result.learning["payload"][
            "repository_patch_suggestion"
        ]
        entry = PatchSuggestionFlow.enqueue(
            queue=self.patch_queue,
            patch_suggestion=patch_suggestion,
        )
        return ShadowRunResult(
            run_id=shadow_result.run_id,
            generated_at=shadow_result.generated_at,
            decision=shadow_result.decision,
            explain_chain=shadow_result.explain_chain,
            shadow_output=shadow_result.shadow_output,
            review=shadow_result.review,
            learning=shadow_result.learning,
            patch_entry=entry,
        )

    @staticmethod
    def _build_explain_payload(
        *,
        decision_ref: str,
        explain_refs: Mapping[str, Sequence[str] | str],
    ) -> dict[str, Any]:
        payload = {
            "decision_ref": decision_ref,
            "evidence_refs": explain_refs.get("evidence_refs", []),
            "pattern_refs": explain_refs.get("pattern_refs", []),
            "experience_refs": explain_refs.get("experience_refs", []),
            "repository_refs": explain_refs.get("repository_refs", []),
        }
        for key in (
            "evidence_refs",
            "pattern_refs",
            "experience_refs",
            "repository_refs",
        ):
            payload[key] = list(
                ShadowRuntimeOrchestrator._references_from_value(payload[key])
            )
        return payload

    @staticmethod
    def _references_from_value(value: Any) -> tuple[str, ...]:
        if isinstance(value, str) and value.strip():
            return (value,)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            refs = tuple(item for item in value if isinstance(item, str) and item)
            return refs
        return ()


class DailyShadowDecisionRun:
    """Render E-127 Shadow Output from validated Runtime and display inputs."""

    @staticmethod
    def render(
        *,
        decision: Mapping[str, Any],
        explain_chain: Mapping[str, Any],
        display_candidates: Mapping[str, Any],
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "contract_version": "1.0",
            "shadow_run_id": f"SHADOW-{decision['decision_id']}",
            "generated_at": now,
            "status": "shadow_output_only",
            "north_star_direction": display_candidates.get(
                "north_star_direction", "awaiting_shadow_input"
            ),
            "captain_mission": display_candidates.get(
                "captain_mission", "awaiting_shadow_input"
            ),
            "top3_candidate": list(display_candidates.get("top3_candidate", [])),
            "forbidden_zone": list(display_candidates.get("forbidden_zone", [])),
            "risk": list(display_candidates.get("risk", [])),
            "window": display_candidates.get("window"),
            "explain_chain": explain_chain["payload"],
            "decision_ref": decision["decision_id"],
            "formal_decision": False,
            "trading_signal": False,
            "production_authorized": False,
            "model_impact": "shadow_candidate_not_production",
        }


class ShadowReviewPipeline:
    """Create E-128 Review and Residual fields from Shadow output."""

    @staticmethod
    def create_review(
        *,
        shadow_output: Mapping[str, Any],
        manual_outcome: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        outcome = dict(manual_outcome or {})
        outcome_status = (
            "manual_outcome" if manual_outcome is not None else "outcome_placeholder"
        )
        return {
            "review_id": f"SHADOW-REVIEW-{shadow_output['shadow_run_id']}",
            "shadow_run_ref": shadow_output["shadow_run_id"],
            "outcome_status": outcome_status,
            "manual_outcome": outcome,
            "prediction_error": None,
            "behavior_error": None,
            "execution_error": None,
            "missing_information": [
                "Manual outcome is required before validation."
            ],
            "preventable": None,
            "residual": {
                "status": "not_evaluated",
                "notes": "Residual cannot be resolved before manual outcome review.",
            },
            "learning_target": "Draft only: review Shadow output after manual outcome.",
            "lesson_status": "draft_only",
            "generated_at": now,
            "status": "shadow_review_candidate",
            "production_authorized": False,
            "model_impact": "shadow_candidate_not_production",
        }


class PatchSuggestionFlow:
    """Move Learning Runtime suggestions into queue states only."""

    @staticmethod
    def enqueue(
        *,
        queue: RepositoryPatchQueue,
        patch_suggestion: Mapping[str, Any],
    ) -> PatchQueueEntry:
        if patch_suggestion.get("status") != "candidate":
            raise ShadowIntegrationError("Only candidate suggestions may be queued")
        if patch_suggestion.get("target_repository") is not None:
            raise ShadowIntegrationError(
                "Shadow patch suggestions cannot name a target repository"
            )
        return queue.enqueue(patch_suggestion)

    @staticmethod
    def status(entry: PatchQueueEntry) -> dict[str, str]:
        mapping = {
            "pending": "pending_review",
            "approved": "approved",
            "rejected": "rejected",
            "merge_authorized": "approved_not_merged",
        }
        return {
            "patch_id": entry.patch_id,
            "shadow_status": mapping[entry.status.value],
            "queue_status": entry.status.value,
        }


class NorthStarShadowDailyBrief:
    """Render E-130 Shadow Daily Brief in memory."""

    @staticmethod
    def render(
        *,
        shadow_result: ShadowRunResult,
    ) -> str:
        output = shadow_result.shadow_output
        learning = shadow_result.learning or {}
        lesson = (
            learning.get("payload", {}).get("lesson", {})
            if isinstance(learning, Mapping)
            else {}
        )
        top3 = output.get("top3_candidate") or []
        forbidden_zone = output.get("forbidden_zone") or []
        risks = output.get("risk") or []
        top3_lines = "\n".join(f"- {item}" for item in top3) or "- 尚無 Shadow 候選"
        forbidden_lines = (
            "\n".join(f"- {item}" for item in forbidden_zone)
            or "- 尚無 Shadow 禁航區"
        )
        risk_lines = "\n".join(f"- {item}" for item in risks) or "- 尚無 Shadow 風險"
        lesson_text = lesson.get("summary", "Lesson Draft 尚未建立")

        return "\n".join(
            [
                "# North Star Shadow Daily Brief",
                "",
                "Status: Shadow Runtime Only",
                "Model Impact: shadow_candidate_not_production",
                "",
                "## 今日北極星",
                str(output.get("north_star_direction")),
                "",
                "## 今日航向",
                str(output.get("captain_mission")),
                "",
                "## 今日 Top3",
                top3_lines,
                "",
                "## 今日禁航區",
                forbidden_lines,
                "",
                "## 今日原因",
                f"Explain Chain: {output['explain_chain']['chain_id']}",
                "",
                "## 今日風險",
                risk_lines,
                "",
                "## 今日學習草稿",
                str(lesson_text),
                "",
                "Production Authorized: false",
            ]
        )
