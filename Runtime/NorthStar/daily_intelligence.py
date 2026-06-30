"""Daily Intelligence Loop for Shadow review records.

The loop stores Shadow snapshots and review artifacts under Runtime/NorthStar.
It never changes Strategy, production scoring, Knowledge, Data, or Repository
indexes.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DailyIntelligenceError(RuntimeError):
    """Raised when a Daily Intelligence record violates its contract."""


class ShadowRecordWriter:
    """Write only approved Shadow review records to Runtime/NorthStar."""

    OUTPUT_DIRECTORIES = {
        "decision_snapshot": "Snapshots",
        "outcome": "Outcomes",
        "decision_residual": "Residuals",
        "root_cause_analysis": "RootCauses",
        "daily_reflection": "Reflections",
    }
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def __init__(self, runtime_root: Path | str) -> None:
        self.runtime_root = Path(runtime_root).resolve()

    def save(self, record: Mapping[str, Any]) -> Path:
        record_type = record.get("record_type")
        if record_type not in self.OUTPUT_DIRECTORIES:
            raise DailyIntelligenceError(
                f"Unsupported Daily Intelligence record: {record_type}"
            )
        record_date = record.get("record_date")
        if not isinstance(record_date, str) or not self.DATE_PATTERN.fullmatch(
            record_date
        ):
            raise DailyIntelligenceError("record_date must use YYYY-MM-DD")
        _validate_date(record_date, "record_date")
        if record.get("production_authorized") is not False:
            raise DailyIntelligenceError("Production authorization is forbidden")
        if record.get("repository_write_authorized") is not False:
            raise DailyIntelligenceError(
                "Repository write authorization is forbidden"
            )

        directory = (
            self.runtime_root / self.OUTPUT_DIRECTORIES[record_type]
        ).resolve()
        if not directory.is_relative_to(self.runtime_root):
            raise DailyIntelligenceError("Output escaped Runtime/NorthStar")
        directory.mkdir(parents=True, exist_ok=True)
        destination = (directory / f"{record_date}.json").resolve()
        if not destination.is_relative_to(directory):
            raise DailyIntelligenceError("Output escaped its approved directory")
        destination.write_text(
            json.dumps(dict(record), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return destination


class DecisionSnapshot:
    """Freeze the completed Shadow Run as today's review memory."""

    @classmethod
    def create(
        cls,
        dashboard_payload: Mapping[str, Any],
        *,
        record_date: str,
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        _validate_date(record_date, "record_date")
        shadow = _mapping(dashboard_payload.get("shadow_runtime"), "shadow_runtime")
        today = _mapping(shadow.get("today"), "shadow_runtime.today")
        explain = _mapping(shadow.get("explain"), "shadow_runtime.explain")
        strategy = _mapping(dashboard_payload.get("strategy"), "strategy")
        opportunities = _object_list(
            dashboard_payload.get("opportunities"), "opportunities", minimum=3
        )

        top3: list[dict[str, Any]] = []
        for index, item in enumerate(opportunities[:3]):
            symbol = _text(item.get("name"), f"opportunities[{index}].name")
            expectation_stars = _stars(
                item.get("expectation_stars"),
                f"opportunities[{index}].expectation_stars",
            )
            top3.append(
                {
                    "rank": index + 1,
                    "symbol": symbol,
                    "expectation_stars": expectation_stars,
                    "window": _text(
                        item.get("window"), f"opportunities[{index}].window"
                    ),
                    "why_now": _text(
                        item.get("why_now"), f"opportunities[{index}].why_now"
                    ),
                    "evidence_refs": _text_list(
                        item.get("evidence_ids"),
                        f"opportunities[{index}].evidence_ids",
                        minimum=1,
                    ),
                }
            )

        confidence = strategy.get("confidence")
        if isinstance(confidence, bool) or not isinstance(
            confidence, (int, float)
        ):
            confidence = None
        elif not 0 <= confidence <= 100:
            raise DailyIntelligenceError("confidence must be from 0 to 100")

        now = generated_at or datetime.now(timezone.utc)
        return {
            **_common_record("decision_snapshot", record_date, now),
            "snapshot_id": f"NORTHSTAR-SNAPSHOT-{record_date.replace('-', '')}",
            "north_star": _text(today.get("direction"), "today.direction"),
            "captain": _text(
                today.get("captain_mission"), "today.captain_mission"
            ),
            "confidence": {
                "value": confidence,
                "status": "available" if confidence is not None else "unavailable",
                "calculated_by_loop": False,
            },
            "top3": top3,
            "risk": _text_list(
                today.get("risk_summary"), "today.risk_summary", minimum=1
            ),
            "story": _text(today.get("market_story"), "today.market_story"),
            "explain_chain": {
                "chain_id": _text(explain.get("chain_id"), "explain.chain_id"),
                "decision": _text(explain.get("decision"), "explain.decision"),
                "nodes": _object_list(
                    explain.get("nodes"), "explain.nodes", minimum=1
                ),
                "edges": _object_list(
                    explain.get("edges"), "explain.edges", minimum=0
                ),
            },
        }


class OutcomeCollector:
    """Validate a manually entered closing Outcome."""

    ENGINES = {"capital_flow", "evidence", "timing", "regime"}

    @classmethod
    def collect_manual(
        cls,
        payload: Mapping[str, Any],
        *,
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        outcome_date = _text(payload.get("outcome_date"), "outcome_date")
        _validate_date(outcome_date, "outcome_date")
        if payload.get("source") != "manual":
            raise DailyIntelligenceError("Outcome source must be manual")
        if payload.get("status") != "manual_shadow_outcome":
            raise DailyIntelligenceError(
                "Outcome status must be manual_shadow_outcome"
            )
        if payload.get("model_impact") != "review_only_not_production":
            raise DailyIntelligenceError(
                "Outcome model_impact must remain review_only_not_production"
            )

        items = _object_list(payload.get("items"), "items", minimum=1)
        normalized_items: list[dict[str, Any]] = []
        symbols: set[str] = set()
        for index, item in enumerate(items):
            symbol = _text(item.get("symbol"), f"items[{index}].symbol")
            if symbol in symbols:
                raise DailyIntelligenceError(f"Duplicate Outcome symbol: {symbol}")
            symbols.add(symbol)
            return_percent = item.get("return_percent")
            if isinstance(return_percent, bool) or not isinstance(
                return_percent, (int, float)
            ):
                raise DailyIntelligenceError(
                    f"items[{index}].return_percent must be numeric"
                )
            normalized_items.append(
                {
                    "symbol": symbol,
                    "return_percent": float(return_percent),
                    "actual_stars": _stars(
                        item.get("actual_stars"),
                        f"items[{index}].actual_stars",
                    ),
                    "notes": _text(
                        item.get("notes"), f"items[{index}].notes"
                    ),
                }
            )

        diagnostics = _object_list(
            payload.get("engine_diagnostics"),
            "engine_diagnostics",
            minimum=1,
        )
        normalized_diagnostics: list[dict[str, Any]] = []
        seen_engines: set[str] = set()
        for index, item in enumerate(diagnostics):
            engine = _text(
                item.get("engine"), f"engine_diagnostics[{index}].engine"
            )
            if engine not in cls.ENGINES:
                raise DailyIntelligenceError(
                    f"Invalid diagnostic engine: {engine}"
                )
            if engine in seen_engines:
                raise DailyIntelligenceError(
                    f"Duplicate diagnostic engine: {engine}"
                )
            seen_engines.add(engine)
            impact = item.get("impact")
            if (
                isinstance(impact, bool)
                or not isinstance(impact, (int, float))
                or not -100 <= impact <= 100
            ):
                raise DailyIntelligenceError(
                    f"engine_diagnostics[{index}].impact "
                    "must be from -100 to 100"
                )
            normalized_diagnostics.append(
                {
                    "engine": engine,
                    "impact": float(impact),
                    "notes": _text(
                        item.get("notes"),
                        f"engine_diagnostics[{index}].notes",
                    ),
                }
            )

        reflection_context = _mapping(
            payload.get("reflection_context"), "reflection_context"
        )
        normalized_context = {
            field: _text(
                reflection_context.get(field), f"reflection_context.{field}"
            )
            for field in (
                "stale_knowledge",
                "correction_candidate",
                "hypothesis_candidate",
            )
        }
        now = generated_at or datetime.now(timezone.utc)
        return {
            **_common_record("outcome", outcome_date, now),
            "outcome_id": _text(payload.get("outcome_id"), "outcome_id"),
            "source": "manual",
            "items": normalized_items,
            "engine_diagnostics": normalized_diagnostics,
            "reflection_context": normalized_context,
            "api_integration": False,
        }


class DecisionResidualEngine:
    """Compare authored expectation stars with manual reality stars."""

    @classmethod
    def calculate(
        cls,
        snapshot: Mapping[str, Any],
        outcome: Mapping[str, Any],
        *,
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        if snapshot.get("record_type") != "decision_snapshot":
            raise DailyIntelligenceError("Decision Snapshot is required")
        if outcome.get("record_type") != "outcome":
            raise DailyIntelligenceError("Outcome is required")
        if snapshot.get("record_date") != outcome.get("record_date"):
            raise DailyIntelligenceError("Snapshot and Outcome dates must match")

        outcome_by_symbol = {
            item["symbol"]: item
            for item in _object_list(
                outcome.get("items"), "outcome.items", minimum=1
            )
        }
        residual_items: list[dict[str, Any]] = []
        for item in _object_list(
            snapshot.get("top3"), "snapshot.top3", minimum=3
        ):
            symbol = item["symbol"]
            actual = outcome_by_symbol.get(symbol)
            if actual is None:
                raise DailyIntelligenceError(
                    f"Outcome is missing Snapshot symbol: {symbol}"
                )
            predicted = _stars(
                item.get("expectation_stars"), f"{symbol}.prediction"
            )
            actual_stars = _stars(
                actual.get("actual_stars"), f"{symbol}.reality"
            )
            residual = actual_stars - predicted
            accuracy = round(
                max(0.0, 1.0 - abs(residual) / 4.0) * 100.0,
                2,
            )
            residual_items.append(
                {
                    "symbol": symbol,
                    "prediction_stars": predicted,
                    "reality_stars": actual_stars,
                    "residual": residual,
                    "accuracy_percent": accuracy,
                    "return_percent": actual["return_percent"],
                }
            )

        overall_accuracy = round(
            sum(item["accuracy_percent"] for item in residual_items)
            / len(residual_items),
            2,
        )
        now = generated_at or datetime.now(timezone.utc)
        record_date = snapshot["record_date"]
        return {
            **_common_record("decision_residual", record_date, now),
            "residual_id": f"NORTHSTAR-RESIDUAL-{record_date.replace('-', '')}",
            "prediction_ref": snapshot["snapshot_id"],
            "outcome_ref": outcome["outcome_id"],
            "items": residual_items,
            "accuracy_percent": overall_accuracy,
            "accuracy_method": (
                "Review-only 1-to-5 star distance; "
                "100 * max(0, 1 - abs(residual) / 4)"
            ),
            "scoring_impact": "none",
        }


class RootCauseAnalyzer:
    """Package manual Engine diagnostics and identify the largest impact."""

    @classmethod
    def analyze(
        cls,
        residual: Mapping[str, Any],
        outcome: Mapping[str, Any],
        *,
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        if residual.get("record_type") != "decision_residual":
            raise DailyIntelligenceError("Decision Residual is required")
        diagnostics = _object_list(
            outcome.get("engine_diagnostics"),
            "outcome.engine_diagnostics",
            minimum=1,
        )
        ordered = sorted(
            (dict(item) for item in diagnostics),
            key=lambda item: (-abs(item["impact"]), item["engine"]),
        )
        residual_items = _object_list(
            residual.get("items"), "residual.items", minimum=1
        )
        largest_error = sorted(
            (dict(item) for item in residual_items),
            key=lambda item: (-abs(item["residual"]), item["symbol"]),
        )[0]
        primary = ordered[0]
        now = generated_at or datetime.now(timezone.utc)
        record_date = residual["record_date"]
        return {
            **_common_record("root_cause_analysis", record_date, now),
            "analysis_id": (
                f"NORTHSTAR-ROOT-CAUSE-{record_date.replace('-', '')}"
            ),
            "residual_ref": residual["residual_id"],
            "attribution_mode": "manual_diagnostic_input",
            "primary_driver": {
                "engine": primary["engine"],
                "impact": primary["impact"],
                "notes": primary["notes"],
            },
            "largest_residual": largest_error,
            "engine_attribution": ordered,
            "automatic_causality_claim": False,
            "scoring_impact": "none",
        }


class DailyReflection:
    """Generate a draft reflection from review records only."""

    @classmethod
    def generate(
        cls,
        residual: Mapping[str, Any],
        root_cause: Mapping[str, Any],
        outcome: Mapping[str, Any],
        *,
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        residual_items = _object_list(
            residual.get("items"), "residual.items", minimum=1
        )
        biggest_error = sorted(
            (dict(item) for item in residual_items),
            key=lambda item: (-abs(item["residual"]), item["symbol"]),
        )[0]
        biggest_surprise = sorted(
            (dict(item) for item in residual_items),
            key=lambda item: (-item["residual"], item["symbol"]),
        )[0]
        context = _mapping(
            outcome.get("reflection_context"), "outcome.reflection_context"
        )
        primary = _mapping(
            root_cause.get("primary_driver"), "root_cause.primary_driver"
        )
        now = generated_at or datetime.now(timezone.utc)
        record_date = residual["record_date"]
        return {
            **_common_record("daily_reflection", record_date, now),
            "reflection_id": (
                f"NORTHSTAR-REFLECTION-{record_date.replace('-', '')}"
            ),
            "residual_ref": residual["residual_id"],
            "root_cause_ref": root_cause["analysis_id"],
            "biggest_error": {
                "symbol": biggest_error["symbol"],
                "residual": biggest_error["residual"],
                "answer": (
                    f"{biggest_error['symbol']} 的預期與實際相差 "
                    f"{biggest_error['residual']} 星。"
                ),
            },
            "biggest_surprise": {
                "symbol": biggest_surprise["symbol"],
                "residual": biggest_surprise["residual"],
                "answer": (
                    f"{biggest_surprise['symbol']} 的實際結果相對預期為 "
                    f"{biggest_surprise['residual']} 星。"
                ),
            },
            "stale_knowledge": _text(
                context.get("stale_knowledge"),
                "reflection_context.stale_knowledge",
            ),
            "correction_suggestion": {
                "engine": primary["engine"],
                "text": _text(
                    context.get("correction_candidate"),
                    "reflection_context.correction_candidate",
                ),
            },
            "hypothesis_suggestion": {
                "status": "draft_suggestion_only",
                "text": _text(
                    context.get("hypothesis_candidate"),
                    "reflection_context.hypothesis_candidate",
                ),
            },
            "learning_action": "suggest_only",
            "automatic_merge": False,
        }


class DailyIntelligenceLoop:
    """Run E-146 through E-150 and save bounded Shadow review artifacts."""

    def __init__(self, runtime_root: Path | str) -> None:
        self.writer = ShadowRecordWriter(runtime_root)

    def run(
        self,
        *,
        dashboard_payload: Mapping[str, Any],
        manual_outcome: Mapping[str, Any],
        record_date: str,
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        snapshot = DecisionSnapshot.create(
            dashboard_payload,
            record_date=record_date,
            generated_at=generated_at,
        )
        outcome = OutcomeCollector.collect_manual(
            manual_outcome,
            generated_at=generated_at,
        )
        residual = DecisionResidualEngine.calculate(
            snapshot,
            outcome,
            generated_at=generated_at,
        )
        root_cause = RootCauseAnalyzer.analyze(
            residual,
            outcome,
            generated_at=generated_at,
        )
        reflection = DailyReflection.generate(
            residual,
            root_cause,
            outcome,
            generated_at=generated_at,
        )
        records = {
            "snapshot": snapshot,
            "outcome": outcome,
            "residual": residual,
            "root_cause": root_cause,
            "reflection": reflection,
        }
        paths = {
            name: self.writer.save(record)
            for name, record in records.items()
        }
        return {
            "records": records,
            "paths": paths,
            "repository_read_only": True,
            "production_authorized": False,
            "automatic_merge": False,
        }


def _common_record(
    record_type: str,
    record_date: str,
    generated_at: datetime,
) -> dict[str, Any]:
    return {
        "record_type": record_type,
        "record_date": record_date,
        "generated_at": generated_at.isoformat(),
        "status": "shadow_review_record",
        "model_impact": "review_only_not_production",
        "production_authorized": False,
        "repository_write_authorized": False,
    }


def _validate_date(value: str, field: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError) as exc:
        raise DailyIntelligenceError(
            f"{field} must use a valid YYYY-MM-DD"
        ) from exc


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DailyIntelligenceError(f"{field} must be an object")
    return value


def _object_list(
    value: Any,
    field: str,
    *,
    minimum: int,
) -> list[Mapping[str, Any]]:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
        or len(value) < minimum
        or not all(isinstance(item, Mapping) for item in value)
    ):
        raise DailyIntelligenceError(
            f"{field} must contain at least {minimum} object(s)"
        )
    return list(value)


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DailyIntelligenceError(f"{field} must not be blank")
    return " ".join(value.split())


def _text_list(value: Any, field: str, *, minimum: int) -> list[str]:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
        or len(value) < minimum
    ):
        raise DailyIntelligenceError(
            f"{field} must contain at least {minimum} item(s)"
        )
    return [
        _text(item, f"{field}[{index}]")
        for index, item in enumerate(value)
    ]


def _stars(value: Any, field: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 1 <= value <= 5
    ):
        raise DailyIntelligenceError(
            f"{field} must be an integer from 1 to 5"
        )
    return value
