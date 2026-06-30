"""Normalize official and third-party records into one Evidence contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .official_registry import DataProviderRegistry


class EvidenceNormalizationError(ValueError):
    """Raised when source evidence cannot be normalized safely."""


class EvidenceNormalizer:
    """Convert heterogeneous source records to the Repository Evidence shape."""

    REQUIRED_FIELDS = {
        "id",
        "source",
        "timestamp",
        "importance",
        "reliability",
        "region",
        "theme",
        "reference",
    }

    @classmethod
    def normalize(
        cls,
        records: list[dict[str, Any]],
        registry: DataProviderRegistry,
    ) -> list[dict[str, Any]]:
        if not isinstance(records, list):
            raise EvidenceNormalizationError("Evidence records must be a list")
        normalized: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise EvidenceNormalizationError(
                    f"Evidence {index} must be an object"
                )
            missing = cls.REQUIRED_FIELDS - record.keys()
            if missing:
                raise EvidenceNormalizationError(
                    f"Evidence {index} missing: {', '.join(sorted(missing))}"
                )
            evidence_id = cls._text(record["id"], f"evidence[{index}].id")
            if evidence_id in seen_ids:
                raise EvidenceNormalizationError(
                    f"Duplicate evidence id: {evidence_id}"
                )
            seen_ids.add(evidence_id)
            source = cls._text(record["source"], f"{evidence_id}.source")
            source_metadata = registry.get(source)
            timestamp = cls._timestamp(
                record["timestamp"], f"{evidence_id}.timestamp"
            )
            importance = cls._score(
                record["importance"], f"{evidence_id}.importance"
            )
            reliability = cls._score(
                record["reliability"], f"{evidence_id}.reliability"
            )
            if reliability > source_metadata["trust_score"]:
                raise EvidenceNormalizationError(
                    f"Evidence reliability exceeds source trust: {evidence_id}"
                )
            normalized.append(
                {
                    "id": evidence_id,
                    "source": source,
                    "timestamp": timestamp,
                    "importance": importance,
                    "reliability": reliability,
                    "region": cls._text(
                        record["region"], f"{evidence_id}.region"
                    ),
                    "theme": cls._text(
                        record["theme"], f"{evidence_id}.theme"
                    ),
                    "reference": cls._text(
                        record["reference"], f"{evidence_id}.reference"
                    ),
                }
            )
        return sorted(normalized, key=lambda item: item["id"])

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise EvidenceNormalizationError(f"{field} must not be blank")
        return " ".join(value.split())

    @staticmethod
    def _score(value: Any, field: str) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 0 <= value <= 100
        ):
            raise EvidenceNormalizationError(
                f"{field} must be an integer from 0 to 100"
            )
        return value

    @staticmethod
    def _timestamp(value: Any, field: str) -> str:
        if not isinstance(value, str):
            raise EvidenceNormalizationError(
                f"{field} must be an ISO date-time"
            )
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise EvidenceNormalizationError(
                f"{field} must be an ISO date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise EvidenceNormalizationError(f"{field} requires timezone")
        return value
