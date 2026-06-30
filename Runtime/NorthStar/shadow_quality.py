"""Shadow input validation and output quality gates.

The module validates authored Shadow data. It does not calculate scores,
create Strategy, authorize Production, or write to the Repository.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any


class ShadowInputValidationError(RuntimeError):
    """Raised when a Shadow input pack violates its data contract."""


class ShadowOutputQualityError(RuntimeError):
    """Raised when a Shadow output is incomplete for Dashboard projection."""


class ShadowInputValidator:
    """Fail-fast validator for the E-136 Shadow input contract."""

    REQUIRED_SECTIONS = (
        "north_star_input",
        "timeline_input",
        "market_regime_input",
        "capital_flow_input",
        "opportunity_input",
        "risk_input",
        "evidence_reference_input",
    )
    VELOCITIES = {"slow", "moderate", "fast"}
    TIDES = {"rising", "stable", "receding"}

    @classmethod
    def validate(
        cls,
        payload: Mapping[str, Any],
        *,
        repository_root: Path | str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ShadowInputValidationError("Shadow input must be an object")
        for field in (
            "document_id",
            "version",
            "status",
            "model_impact",
            "as_of",
            *cls.REQUIRED_SECTIONS,
        ):
            if field not in payload:
                raise ShadowInputValidationError(
                    f"Shadow input is missing field: {field}"
                )

        cls._require_text(payload["document_id"], "document_id")
        if payload["version"] != "1.0":
            raise ShadowInputValidationError("version must be 1.0")
        if payload["status"] != "shadow_input_candidate":
            raise ShadowInputValidationError(
                "status must be shadow_input_candidate"
            )
        if payload["model_impact"] != "shadow_only_not_production":
            raise ShadowInputValidationError(
                "model_impact must remain shadow_only_not_production"
            )
        cls._require_datetime(payload["as_of"], "as_of")

        north_star = cls._object(payload["north_star_input"], "north_star_input")
        for field in ("direction", "captain_mission", "why_now"):
            cls._require_text(north_star.get(field), f"north_star_input.{field}")
        cls._require_window(
            north_star.get("window_days"),
            "north_star_input.window_days",
        )

        timeline = cls._object(payload["timeline_input"], "timeline_input")
        for field in ("yesterday", "today", "tomorrow_projection"):
            cls._require_text(timeline.get(field), f"timeline_input.{field}")

        regime = cls._object(
            payload["market_regime_input"], "market_regime_input"
        )
        for field in ("macro", "sector", "micro"):
            cls._require_text(regime.get(field), f"market_regime_input.{field}")

        flow = cls._object(payload["capital_flow_input"], "capital_flow_input")
        for field in ("source", "destination"):
            cls._require_text(flow.get(field), f"capital_flow_input.{field}")
        path = cls._text_list(
            flow.get("path"), "capital_flow_input.path", minimum=2
        )
        if len(path) != len(set(path)):
            raise ShadowInputValidationError(
                "capital_flow_input.path must not contain duplicates"
            )
        if flow.get("velocity") not in cls.VELOCITIES:
            raise ShadowInputValidationError(
                "capital_flow_input.velocity is invalid"
            )
        if flow.get("tide") not in cls.TIDES:
            raise ShadowInputValidationError("capital_flow_input.tide is invalid")

        opportunities = payload["opportunity_input"]
        if not isinstance(opportunities, list) or not 3 <= len(opportunities) <= 5:
            raise ShadowInputValidationError(
                "opportunity_input must contain 3 to 5 items"
            )
        opportunity_ids: set[str] = set()
        opportunity_evidence: set[str] = set()
        for index, raw in enumerate(opportunities):
            item = cls._object(raw, f"opportunity_input[{index}]")
            item_id = cls._require_text(
                item.get("id"), f"opportunity_input[{index}].id"
            )
            if item_id in opportunity_ids:
                raise ShadowInputValidationError(
                    f"Duplicate opportunity id: {item_id}"
                )
            opportunity_ids.add(item_id)
            cls._require_text(
                item.get("theme"), f"opportunity_input[{index}].theme"
            )
            cls._require_score(
                item.get("display_score"),
                f"opportunity_input[{index}].display_score",
            )
            cls._require_stars(
                item.get("expectation_stars"),
                f"opportunity_input[{index}].expectation_stars",
            )
            cls._require_window(
                item.get("window_days"),
                f"opportunity_input[{index}].window_days",
            )
            cls._require_text(
                item.get("why_now"), f"opportunity_input[{index}].why_now"
            )
            cls._require_text(
                item.get("risk"), f"opportunity_input[{index}].risk"
            )
            refs = cls._text_list(
                item.get("evidence_refs"),
                f"opportunity_input[{index}].evidence_refs",
                minimum=1,
            )
            opportunity_evidence.update(refs)

        risk = cls._object(payload["risk_input"], "risk_input")
        cls._require_text(risk.get("summary"), "risk_input.summary")
        cls._text_list(risk.get("items"), "risk_input.items", minimum=1)
        cls._text_list(
            risk.get("forbidden_zones"),
            "risk_input.forbidden_zones",
            minimum=1,
        )

        evidence_items = payload["evidence_reference_input"]
        if not isinstance(evidence_items, list) or not evidence_items:
            raise ShadowInputValidationError(
                "evidence_reference_input must not be empty"
            )
        evidence_refs: dict[str, str] = {}
        for index, raw in enumerate(evidence_items):
            item = cls._object(raw, f"evidence_reference_input[{index}]")
            evidence_id = cls._require_text(
                item.get("evidence_id"),
                f"evidence_reference_input[{index}].evidence_id",
            )
            repository_ref = cls._require_text(
                item.get("repository_ref"),
                f"evidence_reference_input[{index}].repository_ref",
            )
            if evidence_id in evidence_refs:
                raise ShadowInputValidationError(
                    f"Duplicate evidence reference: {evidence_id}"
                )
            evidence_refs[evidence_id] = repository_ref

        missing_evidence = sorted(opportunity_evidence - evidence_refs.keys())
        if missing_evidence:
            raise ShadowInputValidationError(
                "Opportunity is missing Evidence reference: "
                + ", ".join(missing_evidence)
            )

        if repository_root is not None:
            root = Path(repository_root).resolve()
            for evidence_id, reference in evidence_refs.items():
                source = (root / reference).resolve()
                if not source.is_relative_to(root) or not source.is_file():
                    raise ShadowInputValidationError(
                        f"Evidence reference does not exist: {evidence_id}"
                    )

        return dict(payload)

    @staticmethod
    def _object(value: Any, field: str) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise ShadowInputValidationError(f"{field} must be an object")
        return value

    @staticmethod
    def _require_text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ShadowInputValidationError(f"{field} must not be blank")
        return value.strip()

    @staticmethod
    def _require_datetime(value: Any, field: str) -> None:
        if not isinstance(value, str):
            raise ShadowInputValidationError(f"{field} must be a date-time")
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ShadowInputValidationError(
                f"{field} must be a valid date-time"
            ) from exc

    @staticmethod
    def _require_score(value: Any, field: str) -> None:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0 <= value <= 100
        ):
            raise ShadowInputValidationError(
                f"{field} must be a number from 0 to 100"
            )

    @staticmethod
    def _require_window(value: Any, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 30:
            raise ShadowInputValidationError(
                f"{field} must be an integer from 1 to 30"
            )

    @staticmethod
    def _require_stars(value: Any, field: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            raise ShadowInputValidationError(
                f"{field} must be an integer from 1 to 5"
            )

    @classmethod
    def _text_list(
        cls,
        value: Any,
        field: str,
        *,
        minimum: int,
    ) -> list[str]:
        if (
            not isinstance(value, Sequence)
            or isinstance(value, (str, bytes))
            or len(value) < minimum
        ):
            raise ShadowInputValidationError(
                f"{field} must contain at least {minimum} item(s)"
            )
        return [
            cls._require_text(item, f"{field}[{index}]")
            for index, item in enumerate(value)
        ]


class ShadowOutputQualityGate:
    """Block incomplete Shadow output before Dashboard projection."""

    @classmethod
    def validate(
        cls,
        *,
        shadow_output: Mapping[str, Any],
        explain_chain: Mapping[str, Any],
    ) -> None:
        if not isinstance(shadow_output, Mapping):
            raise ShadowOutputQualityError("Shadow output must be an object")
        for field in ("north_star_direction", "captain_mission", "window"):
            cls._require_text(shadow_output.get(field), field)
        for field in ("top3_candidate", "forbidden_zone", "risk"):
            values = shadow_output.get(field)
            if (
                not isinstance(values, list)
                or not values
                or not all(isinstance(item, str) and item.strip() for item in values)
            ):
                raise ShadowOutputQualityError(
                    f"Shadow output requires non-empty {field}"
                )
        if len(shadow_output["top3_candidate"]) != 3:
            raise ShadowOutputQualityError(
                "Shadow output must contain exactly three Top3 candidates"
            )
        cls._require_text(shadow_output.get("why_now"), "why_now")
        timeline = shadow_output.get("timeline")
        if not isinstance(timeline, Mapping):
            raise ShadowOutputQualityError("Shadow output requires timeline")
        for field in ("yesterday", "today", "tomorrow"):
            cls._require_text(timeline.get(field), f"timeline.{field}")
        if shadow_output.get("production_authorized") is not False:
            raise ShadowOutputQualityError(
                "Shadow output cannot authorize Production"
            )
        if shadow_output.get("trading_signal") is not False:
            raise ShadowOutputQualityError(
                "Shadow output cannot contain a trading signal"
            )

        if not isinstance(explain_chain, Mapping):
            raise ShadowOutputQualityError("Explain Chain must be an object")
        cls._require_text(explain_chain.get("chain_id"), "explain_chain.chain_id")
        nodes = explain_chain.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            raise ShadowOutputQualityError("Explain Chain requires nodes")
        layers = {
            item.get("layer")
            for item in nodes
            if isinstance(item, Mapping)
        }
        required_layers = {"decision", "evidence", "repository"}
        missing_layers = sorted(required_layers - layers)
        if missing_layers:
            raise ShadowOutputQualityError(
                "Explain Chain is missing layers: " + ", ".join(missing_layers)
            )

    @staticmethod
    def _require_text(value: Any, field: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ShadowOutputQualityError(f"Shadow output requires {field}")
