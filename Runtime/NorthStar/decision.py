"""Decision Pipeline infrastructure without Decision Logic."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from .context import RuntimeContext


class DecisionRuntimeError(RuntimeError):
    """Raised when Decision Runtime input or output violates its contract."""


class NorthStarDecisionValidator:
    REQUIRED_FIELDS = {
        "schema_version",
        "decision_id",
        "generated_at",
        "as_of",
        "runtime_mode",
        "decision_state",
        "direction_candidate",
        "recommendation_candidate",
        "window",
        "reasons",
        "confidence",
        "risk_factors",
        "invalidators",
        "input_refs",
        "validation",
        "model_impact",
    }
    DECISION_STATES = {
        "insufficient_data",
        "candidate",
        "validated",
        "rejected",
        "archived",
    }
    FORBIDDEN_KEYS = {
        "order",
        "trade",
        "position_size",
        "capital_allocation",
        "buy",
        "sell",
        "score_weight",
    }

    @classmethod
    def validate(cls, decision: Mapping[str, Any]) -> bool:
        missing = sorted(cls.REQUIRED_FIELDS - set(decision))
        if missing:
            raise DecisionRuntimeError(
                f"NorthStarDecision is missing fields: {', '.join(missing)}"
            )
        if decision["runtime_mode"] != "shadow_candidate":
            raise DecisionRuntimeError(
                "NorthStarDecision runtime_mode must be shadow_candidate"
            )
        if decision["decision_state"] not in cls.DECISION_STATES:
            raise DecisionRuntimeError("NorthStarDecision state is invalid")
        if decision["model_impact"] != "shadow_candidate_not_production":
            raise DecisionRuntimeError(
                "NorthStarDecision must remain non-production"
            )

        recommendation = decision["recommendation_candidate"]
        if not isinstance(recommendation, Mapping):
            raise DecisionRuntimeError("recommendation_candidate must be an object")
        if recommendation.get("production_authorized") is not False:
            raise DecisionRuntimeError(
                "NorthStarDecision cannot authorize Production"
            )

        confidence = decision["confidence"]
        if not isinstance(confidence, Mapping):
            raise DecisionRuntimeError("confidence must be an object")
        value = confidence.get("value")
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0 <= value <= 100
        ):
            raise DecisionRuntimeError("confidence value must be null or 0-100")
        if confidence.get("methodology_ref") is None and value is not None:
            raise DecisionRuntimeError(
                "confidence value requires methodology_ref"
            )
        if confidence.get("production_authorized") is not False:
            raise DecisionRuntimeError("confidence cannot authorize Production")

        cls._reject_forbidden_keys(decision)
        return True

    @classmethod
    def _reject_forbidden_keys(cls, value: Any) -> None:
        if isinstance(value, Mapping):
            found = cls.FORBIDDEN_KEYS.intersection(value)
            if found:
                raise DecisionRuntimeError(
                    f"Decision output contains forbidden fields: {sorted(found)}"
                )
            for item in value.values():
                cls._reject_forbidden_keys(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                cls._reject_forbidden_keys(item)


class DecisionRuntime:
    """Package validated inputs into a Decision Schema without deciding."""

    engine_id = "decision_runtime"
    INPUT_FIELDS = {
        "regime": "market_regime_ref",
        "flow": "capital_flow_ref",
        "repository": "repository_snapshot_ref",
        "opportunity": "opportunity_ref",
    }

    def run(self, context: RuntimeContext) -> Mapping[str, Any]:
        payload = context.mutable_payload()
        input_refs: dict[str, str | None] = {
            "market_regime_ref": None,
            "capital_flow_ref": None,
            "repository_snapshot_ref": None,
            "opportunity_ref": None,
            "strategy_candidate_ref": None,
            "validation_report_ref": None,
        }

        for input_name, output_name in self.INPUT_FIELDS.items():
            reference = payload.get(input_name)
            if not isinstance(reference, str) or not reference.strip():
                raise DecisionRuntimeError(
                    f"Decision Runtime input is missing {input_name}"
                )
            context.snapshot(reference)
            input_refs[output_name] = reference

        now = datetime.now(timezone.utc)
        decision = {
            "schema_version": "1.0",
            "decision_id": f"NSD-{context.request_id.removeprefix('REQ-')}",
            "generated_at": now.isoformat(),
            "as_of": context.as_of.isoformat(),
            "runtime_mode": "shadow_candidate",
            "decision_state": "insufficient_data",
            "direction_candidate": None,
            "recommendation_candidate": {
                "type": None,
                "text": None,
                "owner": "綠茶",
                "production_authorized": False,
            },
            "window": {
                "start_at": None,
                "end_at": None,
                "label": None,
            },
            "reasons": [
                {
                    "reason_id": "REASON-INFRASTRUCTURE-ONLY",
                    "claim": (
                        "Runtime infrastructure intentionally produced no market "
                        "decision because Decision Logic is not implemented."
                    ),
                    "source_layer": "validation",
                    "source_refs": list(context.source_refs),
                    "evidence_refs": [],
                    "counter_evidence_refs": [],
                    "limitations": [
                        "No Decision Algorithm.",
                        "No Strategy Logic.",
                        "No Confidence Formula.",
                    ],
                    "status": "validated",
                }
            ],
            "confidence": {
                "value": None,
                "status": "unavailable",
                "scale": "0_100",
                "methodology_ref": None,
                "coverage": None,
                "freshness": None,
                "consistency": None,
                "uncertainty": [
                    "Confidence methodology is not implemented."
                ],
                "production_authorized": False,
            },
            "risk_factors": [],
            "invalidators": [],
            "input_refs": input_refs,
            "validation": {
                "status": "validated",
                "errors": [],
                "warnings": [
                    "Decision Logic is intentionally not implemented."
                ],
                "validated_at": now.isoformat(),
                "validator_version": "north-star-decision-validator/1.0",
            },
            "model_impact": "shadow_candidate_not_production",
        }
        NorthStarDecisionValidator.validate(decision)
        return decision
