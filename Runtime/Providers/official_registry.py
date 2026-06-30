"""Official-first provider metadata registry with no network endpoints."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


class ProviderRegistryError(ValueError):
    """Raised when official provider metadata violates its contract."""


class DataProviderRegistry:
    """Validate and expose provider metadata without exposing URLs."""

    REQUIRED_SOURCE_IDS = {
        "TWSE",
        "TPEX",
        "MOPS",
        "US_MARKET",
        "MACRO",
        "ETF",
        "NEWS",
    }
    REQUIRED_FIELDS = {
        "source_id",
        "source_class",
        "trust_score",
        "update_frequency",
        "last_success",
        "last_failure",
        "health_status",
    }
    SOURCE_CLASSES = {"official", "third_party"}
    HEALTH_STATUSES = {"healthy", "warning", "degraded", "unavailable"}
    FORBIDDEN_KEYS = {"url", "endpoint", "api_url", "base_url"}

    def __init__(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ProviderRegistryError("Provider registry must be an object")
        providers = payload.get("providers")
        if not isinstance(providers, list):
            raise ProviderRegistryError("Provider registry requires providers")

        records: dict[str, dict[str, Any]] = {}
        for index, record in enumerate(providers):
            if not isinstance(record, dict):
                raise ProviderRegistryError(
                    f"Provider {index} must be an object"
                )
            forbidden = self.FORBIDDEN_KEYS.intersection(record)
            if forbidden:
                raise ProviderRegistryError(
                    "Provider registry cannot expose network locations: "
                    + ", ".join(sorted(forbidden))
                )
            missing = self.REQUIRED_FIELDS - record.keys()
            if missing:
                raise ProviderRegistryError(
                    f"Provider {index} missing: {', '.join(sorted(missing))}"
                )
            source_id = self._text(record["source_id"], "source_id")
            if source_id in records:
                raise ProviderRegistryError(
                    f"Duplicate source_id: {source_id}"
                )
            source_class = self._text(
                record["source_class"], f"{source_id}.source_class"
            )
            if source_class not in self.SOURCE_CLASSES:
                raise ProviderRegistryError(
                    f"Invalid source_class: {source_id}"
                )
            health_status = self._text(
                record["health_status"], f"{source_id}.health_status"
            )
            if health_status not in self.HEALTH_STATUSES:
                raise ProviderRegistryError(
                    f"Invalid health_status: {source_id}"
                )
            trust_score = record["trust_score"]
            if (
                isinstance(trust_score, bool)
                or not isinstance(trust_score, int)
                or not 0 <= trust_score <= 100
            ):
                raise ProviderRegistryError(
                    f"Invalid trust_score: {source_id}"
                )
            self._timestamp(
                record["last_success"],
                f"{source_id}.last_success",
                nullable=False,
            )
            self._timestamp(
                record["last_failure"],
                f"{source_id}.last_failure",
                nullable=True,
            )
            self._text(
                record["update_frequency"],
                f"{source_id}.update_frequency",
            )
            records[source_id] = deepcopy(record)

        missing_ids = self.REQUIRED_SOURCE_IDS - records.keys()
        extra_ids = records.keys() - self.REQUIRED_SOURCE_IDS
        if missing_ids or extra_ids:
            raise ProviderRegistryError(
                "Provider set mismatch; "
                f"missing={sorted(missing_ids)}, extra={sorted(extra_ids)}"
            )
        self._metadata = {
            key: deepcopy(value)
            for key, value in payload.items()
            if key != "providers"
        }
        self._records = records

    def get(self, source_id: str) -> dict[str, Any]:
        try:
            return deepcopy(self._records[source_id])
        except KeyError as exc:
            raise ProviderRegistryError(
                f"Unknown source_id: {source_id}"
            ) from exc

    def list(self) -> list[dict[str, Any]]:
        return [
            deepcopy(self._records[source_id])
            for source_id in sorted(self._records)
        ]

    def export(self) -> dict[str, Any]:
        return {
            **deepcopy(self._metadata),
            "providers": self.list(),
            "runtime_network_access": False,
            "repository_write_authorized": False,
        }

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ProviderRegistryError(f"{field} must not be blank")
        return " ".join(value.split())

    @staticmethod
    def _timestamp(value: Any, field: str, *, nullable: bool) -> None:
        if nullable and value is None:
            return
        if not isinstance(value, str):
            raise ProviderRegistryError(f"{field} must be an ISO date-time")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ProviderRegistryError(
                f"{field} must be an ISO date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise ProviderRegistryError(f"{field} requires timezone")
