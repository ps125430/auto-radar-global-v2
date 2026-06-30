"""Versioned Global Snapshot v2 for deterministic AM/PM replay."""

from __future__ import annotations

import re
from copy import deepcopy
from datetime import datetime
from typing import Any

from .evidence_normalizer import EvidenceNormalizer
from .ocean_health import OceanHealthEngine
from .official_registry import DataProviderRegistry


class SnapshotV2Error(ValueError):
    """Raised when a Global Snapshot v2 input is invalid."""


class MarketSnapshotBuilderV2:
    """Build a complete versioned Shadow snapshot from archived inputs."""

    VERSION_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}-(AM|PM)$")
    REQUIRED_SECTIONS = {"us", "taiwan", "macro", "sector", "theme"}

    @classmethod
    def build(
        cls,
        payload: dict[str, Any],
        registry: DataProviderRegistry,
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise SnapshotV2Error("Snapshot input must be an object")
        snapshot_version = payload.get("snapshot_version")
        if (
            not isinstance(snapshot_version, str)
            or not cls.VERSION_PATTERN.fullmatch(snapshot_version)
        ):
            raise SnapshotV2Error(
                "snapshot_version must use YYYY-MM-DD-AM or YYYY-MM-DD-PM"
            )
        try:
            datetime.strptime(snapshot_version[:10], "%Y-%m-%d")
        except ValueError as exc:
            raise SnapshotV2Error("snapshot_version date is invalid") from exc
        generated_at = cls._timestamp(payload.get("generated_at"))
        market_data = payload.get("market_data")
        if not isinstance(market_data, dict):
            raise SnapshotV2Error("market_data must be an object")
        missing = cls.REQUIRED_SECTIONS - market_data.keys()
        if missing:
            raise SnapshotV2Error(
                "Snapshot missing sections: " + ", ".join(sorted(missing))
            )
        for section in cls.REQUIRED_SECTIONS:
            value = market_data[section]
            if not isinstance(value, (dict, list)) or not value:
                raise SnapshotV2Error(
                    f"Snapshot section must not be empty: {section}"
                )
        raw_evidence = payload.get("evidence")
        evidence = EvidenceNormalizer.normalize(raw_evidence, registry)
        health = OceanHealthEngine.evaluate(
            registry,
            evidence,
            snapshot_version=snapshot_version,
            generated_at=generated_at,
        )
        return {
            "document_id": f"GLOBAL-SNAPSHOT-{snapshot_version}",
            "snapshot_version": snapshot_version,
            "generated_at": generated_at,
            "global": {
                "us": deepcopy(market_data["us"]),
                "taiwan": deepcopy(market_data["taiwan"]),
                "macro": deepcopy(market_data["macro"]),
                "sector": deepcopy(market_data["sector"]),
                "theme": deepcopy(market_data["theme"]),
                "evidence": evidence,
                "market_health": health,
            },
            "status": "validated_shadow_snapshot_v2",
            "model_impact": "provider_data_only_not_production",
            "runtime_network_access": False,
            "production_authorized": False,
            "repository_write_authorized": False,
        }

    @staticmethod
    def _timestamp(value: Any) -> str:
        if not isinstance(value, str):
            raise SnapshotV2Error("generated_at must be an ISO date-time")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise SnapshotV2Error(
                "generated_at must be an ISO date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise SnapshotV2Error("generated_at requires timezone")
        return value
