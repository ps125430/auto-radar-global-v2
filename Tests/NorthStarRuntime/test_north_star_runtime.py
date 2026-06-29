from __future__ import annotations

import json
import tempfile
import unittest
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

from Runtime.NorthStar import (
    DecisionRuntime,
    DecisionRuntimeError,
    ExplainRuntime,
    LearningRuntime,
    MergeAuthorization,
    NorthStarDecisionValidator,
    PatchQueueError,
    PatchStatus,
    RepositoryPatchQueue,
    RuntimeContext,
    RuntimeDispatcher,
    RuntimeFramework,
    RuntimeFrameworkError,
    RuntimeLoader,
    RuntimeLoaderError,
    RuntimeSession,
    SessionStatus,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DECISION_SCHEMA = (
    REPOSITORY_ROOT / "Schemas" / "Runtime" / "north_star_decision.schema.json"
)


def write_json(root: Path, reference: str, payload: Mapping[str, object]) -> None:
    path = root / reference
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_runtime_repository(root: Path) -> tuple[str, ...]:
    references = (
        "Knowledge/runtime/regime.json",
        "Knowledge/runtime/flow.json",
        "Runtime/Repository/index/repository_snapshot.json",
        "Knowledge/runtime/opportunity.json",
        "Knowledge/runtime/evidence.json",
        "Knowledge/runtime/pattern.json",
        "Knowledge/runtime/experience.json",
        "Knowledge/runtime/review.json",
    )
    for reference in references:
        write_json(
            root,
            reference,
            {
                "reference": reference,
                "status": "validated",
                "model_impact": "shadow_candidate_not_production",
            },
        )
    return references


class InvalidHandler:
    engine_id = "invalid_handler"

    def run(self, context: RuntimeContext) -> list[str]:
        return ["not", "a", "mapping"]


class EchoHandler:
    engine_id = "echo_handler"

    def run(self, context: RuntimeContext) -> Mapping[str, object]:
        return {
            "request_id": context.request_id,
            "runtime_mode": context.runtime_mode,
            "source_refs": list(context.source_refs),
        }


class NorthStarRuntimeTests(unittest.TestCase):
    def test_loader_reads_only_allowed_immutable_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_json(
                root,
                "Knowledge/runtime/input.json",
                {"nested": {"value": 1}},
            )
            loader = RuntimeLoader(root)
            snapshot = loader.load_json("Knowledge/runtime/input.json")

            self.assertEqual(1, snapshot.payload["nested"]["value"])
            with self.assertRaises(TypeError):
                snapshot.payload["nested"]["value"] = 2
            self.assertEqual(64, len(snapshot.sha256))

    def test_loader_rejects_traversal_and_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_json(root, "Sandbox/input.json", {"status": "candidate"})
            loader = RuntimeLoader(root)

            with self.assertRaises(RuntimeLoaderError):
                loader.load_json("../outside.json")
            with self.assertRaises(RuntimeLoaderError):
                loader.load_json("Sandbox/input.json")

    def test_framework_is_disabled_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            framework = RuntimeFramework(temporary_directory)
            framework.register(EchoHandler())

            with self.assertRaises(RuntimeFrameworkError):
                framework.execute(
                    "echo_handler",
                    source_refs=(),
                )

    def test_framework_dispatches_one_shadow_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            write_json(root, "Knowledge/runtime/input.json", {"value": 1})
            framework = RuntimeFramework(root, enabled=True)
            framework.register(EchoHandler())

            execution = framework.execute(
                "echo_handler",
                source_refs=("Knowledge/runtime/input.json",),
                payload={"purpose": "infrastructure_test"},
            )

            self.assertEqual(SessionStatus.COMPLETED, execution.session.status)
            self.assertEqual(
                "shadow_candidate", execution.output["runtime_mode"]
            )
            self.assertEqual(
                ["Knowledge/runtime/input.json"],
                execution.output["source_refs"],
            )
            with self.assertRaises(TypeError):
                execution.context.payload["purpose"] = "changed"

    def test_dispatch_failure_is_recorded_and_fails_fast(self) -> None:
        dispatcher = RuntimeDispatcher()
        dispatcher.register(InvalidHandler())
        context = RuntimeContext(
            request_id="REQ-1",
            session_id="SES-1",
            as_of=datetime.now(timezone.utc),
            runtime_mode="shadow_candidate",
            snapshots={},
            payload={},
        )
        session = RuntimeSession("SES-1", "REQ-1")

        with self.assertRaises(Exception):
            dispatcher.dispatch("invalid_handler", context, session)
        self.assertEqual(SessionStatus.FAILED, session.status)
        self.assertIsNotNone(session.error)

    def test_session_can_rollback_without_repository_side_effect(self) -> None:
        session = RuntimeSession("SES-2", "REQ-2")
        session.start("echo")
        session.complete({"status": "candidate"})
        session.rollback("validation failed")

        self.assertEqual(SessionStatus.ROLLED_BACK, session.status)
        self.assertEqual("rolled_back", session.events[-1].event)

    def test_decision_runtime_packages_inputs_without_decision_logic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            references = create_runtime_repository(root)
            regime, flow, repository, opportunity = references[:4]
            framework = RuntimeFramework(root, enabled=True)
            framework.register(DecisionRuntime())

            execution = framework.execute(
                "decision_runtime",
                source_refs=(regime, flow, repository, opportunity),
                payload={
                    "regime": regime,
                    "flow": flow,
                    "repository": repository,
                    "opportunity": opportunity,
                },
            )
            decision = execution.output

            self.assertEqual("insufficient_data", decision["decision_state"])
            self.assertIsNone(decision["direction_candidate"])
            self.assertIsNone(decision["recommendation_candidate"]["type"])
            self.assertIsNone(decision["recommendation_candidate"]["text"])
            self.assertFalse(
                decision["recommendation_candidate"]["production_authorized"]
            )
            self.assertIsNone(decision["confidence"]["value"])
            self.assertFalse(decision["confidence"]["production_authorized"])
            self.assertTrue(NorthStarDecisionValidator.validate(decision))

    def test_decision_validator_rejects_production_and_trading_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            references = create_runtime_repository(root)
            framework = RuntimeFramework(root, enabled=True)
            framework.register(DecisionRuntime())
            decision = framework.execute(
                "decision_runtime",
                source_refs=references[:4],
                payload={
                    "regime": references[0],
                    "flow": references[1],
                    "repository": references[2],
                    "opportunity": references[3],
                },
            ).output

            decision["recommendation_candidate"]["production_authorized"] = True
            with self.assertRaises(DecisionRuntimeError):
                NorthStarDecisionValidator.validate(decision)

            decision["recommendation_candidate"]["production_authorized"] = False
            decision["trade"] = {"symbol": "TEST"}
            with self.assertRaises(DecisionRuntimeError):
                NorthStarDecisionValidator.validate(decision)

    def test_explain_runtime_preserves_layer_order_and_missing_refs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            references = create_runtime_repository(root)
            evidence, pattern, experience, repository = (
                references[4],
                references[5],
                references[6],
                references[2],
            )
            framework = RuntimeFramework(root, enabled=True)
            framework.register(ExplainRuntime())

            output = framework.execute(
                "explain_runtime",
                source_refs=(evidence, pattern, experience, repository),
                payload={
                    "decision_ref": "NSD-001",
                    "evidence_refs": [evidence],
                    "pattern_refs": [pattern],
                    "experience_refs": [experience],
                    "repository_refs": [repository, "Knowledge/missing.json"],
                },
            ).output
            chain = output["payload"]

            self.assertEqual(
                ["decision", "evidence", "pattern", "experience", "repository"],
                chain["layer_order"],
            )
            self.assertEqual(
                ["Knowledge/missing.json"], chain["missing_refs"]
            )
            self.assertEqual(5, len(chain["edges"]))

    def test_learning_runtime_only_generates_suggestions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            references = create_runtime_repository(root)
            review_ref = references[7]
            before = sorted(path.relative_to(root) for path in root.rglob("*"))
            framework = RuntimeFramework(root, enabled=True)
            framework.register(LearningRuntime())

            output = framework.execute(
                "learning_runtime",
                source_refs=(review_ref,),
                payload={
                    "review": {
                        "review_id": "REVIEW-001",
                        "prediction_error": "timing mismatch",
                        "missing_information": ["outcome window"],
                        "learning_target": "Validate timing with more cases.",
                    }
                },
            ).output
            after = sorted(path.relative_to(root) for path in root.rglob("*"))
            patch = output["payload"]["repository_patch_suggestion"]

            self.assertEqual(before, after)
            self.assertEqual("candidate", patch["status"])
            self.assertIsNone(patch["target_repository"])
            self.assertTrue(patch["validation_required"])
            self.assertFalse(patch["production_authorized"])

    def test_patch_queue_requires_repository_manager_review(self) -> None:
        queue = RepositoryPatchQueue()
        suggestion = {
            "suggestion_id": "PATCH-001",
            "suggestion_type": "lesson",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_refs": ["REVIEW-001"],
            "description": "Candidate only",
            "uncertainty": [],
            "validation_required": True,
            "target_repository": None,
            "status": "candidate",
            "production_authorized": False,
        }
        entry = queue.enqueue(suggestion)

        self.assertEqual(PatchStatus.PENDING, entry.status)
        with self.assertRaises(PatchQueueError):
            queue.authorize_merge(
                "PATCH-001", repository_manager="Repository Manager"
            )

        reviewed = queue.review(
            "PATCH-001",
            repository_manager="Repository Manager",
            approved=True,
            target_repository="Knowledge/Lessons/",
            notes="Validated for separate Repository task.",
        )
        authorization = queue.authorize_merge(
            "PATCH-001", repository_manager="Repository Manager"
        )

        self.assertEqual(PatchStatus.APPROVED, reviewed.status)
        self.assertIsInstance(authorization, MergeAuthorization)
        self.assertFalse(authorization.production_authorized)
        self.assertFalse(hasattr(queue, "merge"))

    def test_rejected_patch_cannot_receive_merge_authorization(self) -> None:
        queue = RepositoryPatchQueue()
        queue.enqueue(
            {
                "suggestion_id": "PATCH-002",
                "suggestion_type": "lesson",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_refs": ["REVIEW-002"],
                "description": "Rejected candidate",
                "uncertainty": ["missing evidence"],
                "validation_required": True,
                "target_repository": None,
                "status": "candidate",
                "production_authorized": False,
            }
        )
        queue.review(
            "PATCH-002",
            repository_manager="Repository Manager",
            approved=False,
            notes="Evidence is insufficient.",
        )

        with self.assertRaises(PatchQueueError):
            queue.authorize_merge(
                "PATCH-002", repository_manager="Repository Manager"
            )

    def test_decision_schema_is_valid_and_infrastructure_only(self) -> None:
        schema = json.loads(DECISION_SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema",
            schema["$schema"],
        )
        self.assertFalse(schema["x-runtime"]["decision_logic"])
        self.assertFalse(schema["x-runtime"]["strategy_logic"])
        self.assertFalse(schema["x-runtime"]["repository_write"])
        self.assertFalse(schema["x-runtime"]["production_authorized"])


if __name__ == "__main__":
    unittest.main()
