"""Fail-fast quality validation before Market Snapshot creation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from .models import ProviderRecord


class DataQualityError(RuntimeError):
    """Raised when provider data is missing, duplicate, invalid, or stale."""


class DataQualityEngine:
    """Validate raw Provider records without calculating market scores."""

    REQUIRED_FIELDS = (
        "record_id",
        "provider",
        "market",
        "timestamp",
        "category",
        "value",
        "unit",
        "source",
        "importance",
        "reliability",
        "reference",
    )
    ALLOWED_PROVIDERS = {"taiwan", "us", "macro", "news", "etf", "mock"}
    ALLOWED_MARKETS = {"GLOBAL", "US", "TAIWAN", "CRYPTO", "MACRO"}

    @classmethod
    def validate(
        cls,
        raw_records: Sequence[Mapping[str, Any]],
        *,
        as_of: str,
    ) -> tuple[ProviderRecord, ...]:
        if not isinstance(raw_records, Sequence) or isinstance(
            raw_records, (str, bytes)
        ):
            raise DataQualityError("Provider records must be a sequence")
        as_of_time = cls._date_time(as_of, "as_of")
        seen_ids: set[str] = set()
        seen_semantic_keys: set[tuple[Any, ...]] = set()
        records: list[ProviderRecord] = []

        for index, raw in enumerate(raw_records):
            if not isinstance(raw, Mapping):
                raise DataQualityError(f"Record {index} must be an object")
            missing = [
                field
                for field in cls.REQUIRED_FIELDS
                if field not in raw or raw[field] in (None, "")
            ]
            if missing:
                raise DataQualityError(
                    f"Record {index} missing fields: {', '.join(missing)}"
                )

            record_id = cls._text(raw["record_id"], f"record[{index}].record_id")
            if record_id in seen_ids:
                raise DataQualityError(f"Duplicate record_id: {record_id}")
            seen_ids.add(record_id)

            provider = cls._text(raw["provider"], f"{record_id}.provider")
            if provider not in cls.ALLOWED_PROVIDERS:
                raise DataQualityError(f"Invalid provider: {provider}")
            market = cls._text(raw["market"], f"{record_id}.market")
            if market not in cls.ALLOWED_MARKETS:
                raise DataQualityError(f"Invalid market: {market}")
            timestamp = cls._text(raw["timestamp"], f"{record_id}.timestamp")
            timestamp_value = cls._date_time(timestamp, f"{record_id}.timestamp")
            if timestamp_value > as_of_time:
                raise DataQualityError(f"Future timestamp: {record_id}")

            category = cls._text(raw["category"], f"{record_id}.category")
            symbol = raw.get("symbol")
            if symbol is not None:
                symbol = cls._text(symbol, f"{record_id}.symbol")
            value = raw["value"]
            if isinstance(value, bool) or not isinstance(value, (str, int, float)):
                raise DataQualityError(f"Invalid value: {record_id}")
            if isinstance(value, str):
                value = cls._text(value, f"{record_id}.value")
            else:
                value = float(value)

            importance = cls._percentage(
                raw["importance"], f"{record_id}.importance"
            )
            reliability = cls._percentage(
                raw["reliability"], f"{record_id}.reliability"
            )
            expected_min, expected_max = cls._bounds(raw, record_id)
            if isinstance(value, float) and expected_min is not None:
                if value < expected_min or value > expected_max:
                    raise DataQualityError(
                        f"Outlier value outside declared range: {record_id}"
                    )

            semantic_key = (
                provider,
                market,
                category,
                symbol,
                timestamp,
            )
            if semantic_key in seen_semantic_keys:
                raise DataQualityError(
                    f"Duplicate semantic record: {record_id}"
                )
            seen_semantic_keys.add(semantic_key)
            records.append(
                ProviderRecord(
                    record_id=record_id,
                    provider=provider,
                    market=market,
                    timestamp=timestamp,
                    category=category,
                    symbol=symbol,
                    value=value,
                    unit=cls._text(raw["unit"], f"{record_id}.unit"),
                    source=cls._text(raw["source"], f"{record_id}.source"),
                    importance=importance,
                    reliability=reliability,
                    reference=cls._text(
                        raw["reference"], f"{record_id}.reference"
                    ),
                    expected_min=expected_min,
                    expected_max=expected_max,
                )
            )
        return tuple(sorted(records, key=lambda item: item.record_id))

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise DataQualityError(f"{field} must not be blank")
        return " ".join(value.split())

    @staticmethod
    def _date_time(value: Any, field: str) -> datetime:
        if not isinstance(value, str):
            raise DataQualityError(f"{field} must be an ISO date-time")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise DataQualityError(
                f"Invalid timestamp format: {field}"
            ) from exc
        if parsed.tzinfo is None:
            raise DataQualityError(f"Timestamp requires timezone: {field}")
        return parsed

    @staticmethod
    def _percentage(value: Any, field: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
            raise DataQualityError(f"{field} must be an integer from 0 to 100")
        return value

    @staticmethod
    def _bounds(
        raw: Mapping[str, Any],
        record_id: str,
    ) -> tuple[float | None, float | None]:
        has_min = "expected_min" in raw
        has_max = "expected_max" in raw
        if has_min != has_max:
            raise DataQualityError(
                f"Both expected bounds are required: {record_id}"
            )
        if not has_min:
            return None, None
        minimum = raw["expected_min"]
        maximum = raw["expected_max"]
        if (
            isinstance(minimum, bool)
            or isinstance(maximum, bool)
            or not isinstance(minimum, (int, float))
            or not isinstance(maximum, (int, float))
            or minimum > maximum
        ):
            raise DataQualityError(f"Invalid expected range: {record_id}")
        return float(minimum), float(maximum)
