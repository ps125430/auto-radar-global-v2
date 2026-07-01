"""Real Ocean Snapshot v3 and official-first fallback policy."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Mapping, Sequence

from .live_official import ProviderFetch


class SnapshotV3Error(ValueError):
    """Raised when Snapshot v3 or fallback input is invalid."""


class OfficialFallbackPolicy:
    """Resolve Official -> Cached; fixtures are Replay/Test only."""

    @classmethod
    def resolve(
        cls,
        fetches: Sequence[ProviderFetch],
        *,
        cached_snapshot: Mapping[str, Any] | None = None,
        archived_fixture: Mapping[str, Any] | None = None,
        purpose: str = "runtime",
    ) -> tuple[dict[str, Any], dict[str, str]]:
        cached_payloads = cls._payloads(cached_snapshot)
        fixture_payloads = (
            cls._payloads(archived_fixture)
            if purpose in {"replay", "test"}
            else {}
        )
        effective: dict[str, Any] = {}
        modes: dict[str, str] = {}
        for fetch in fetches:
            if fetch.ok:
                effective[fetch.source_id] = fetch.payload
                modes[fetch.source_id] = "official"
            elif fetch.source_id in cached_payloads:
                effective[fetch.source_id] = cached_payloads[
                    fetch.source_id
                ]
                modes[fetch.source_id] = "cached_snapshot"
            elif fetch.source_id in fixture_payloads:
                effective[fetch.source_id] = fixture_payloads[
                    fetch.source_id
                ]
                modes[fetch.source_id] = "archived_fixture"
            else:
                effective[fetch.source_id] = None
                modes[fetch.source_id] = "unavailable"
        if purpose == "runtime" and "archived_fixture" in modes.values():
            raise SnapshotV3Error(
                "Runtime cannot use archived fixtures directly"
            )
        return effective, modes

    @staticmethod
    def _payloads(snapshot: Mapping[str, Any] | None) -> Mapping[str, Any]:
        if snapshot is None:
            return {}
        payloads = snapshot.get("provider_payloads")
        return payloads if isinstance(payloads, Mapping) else {}


class GlobalSnapshotBuilderV3:
    """Build hash-addressed Global Snapshot v3 from Registry output."""

    VERSION_PATTERN = re.compile(
        r"^\d{4}-\d{2}-\d{2}-(0600|0700|0830|1510|MANUAL)$"
    )
    TRUST = {
        "TWSE": 98,
        "TPEX": 98,
        "MOPS": 99,
        "FRED": 97,
        "SEC_EDGAR": 98,
    }

    @classmethod
    def build(
        cls,
        fetches: Sequence[ProviderFetch],
        *,
        effective_payloads: Mapping[str, Any],
        source_modes: Mapping[str, str],
        version: str,
        generated_at: str,
    ) -> dict[str, Any]:
        if not cls.VERSION_PATTERN.fullmatch(version):
            raise SnapshotV3Error("Snapshot v3 version is invalid")
        cls._timestamp(generated_at)
        fetch_map = {item.source_id: item for item in fetches}
        if set(fetch_map) != set(cls.TRUST):
            raise SnapshotV3Error("Snapshot v3 Provider set mismatch")
        source_hashes: dict[str, str | None] = {}
        evidence: list[dict[str, Any]] = []
        health_sources: list[dict[str, Any]] = []
        for source_id in sorted(cls.TRUST):
            fetch = fetch_map[source_id]
            mode = source_modes.get(source_id, "unavailable")
            payload = effective_payloads.get(source_id)
            source_hash = (
                fetch.source_hash
                if mode == "official"
                else cls._payload_hash(payload)
            )
            source_hashes[source_id] = source_hash
            health_status = (
                "healthy"
                if mode == "official"
                else "degraded"
                if mode in {"cached_snapshot", "archived_fixture"}
                else "unavailable"
            )
            health_sources.append(
                {
                    "source_id": source_id,
                    "health_status": health_status,
                    "source_mode": mode,
                    "last_update": fetch.fetched_at,
                    "latency_ms": fetch.latency_ms,
                    "error": fetch.error,
                }
            )
            if payload is not None:
                evidence.append(
                    {
                        "id": f"REAL-{source_id}-{version}",
                        "source": source_id,
                        "timestamp": fetch.fetched_at,
                        "importance": 80,
                        "reliability": cls.TRUST[source_id],
                        "region": cls._region(source_id),
                        "theme": "Official Market Data",
                        "reference": f"provider-registry://{source_id}/{version}",
                        "source_hash": source_hash,
                        "source_mode": mode,
                    }
                )
        healthy_count = sum(
            item["health_status"] == "healthy" for item in health_sources
        )
        unavailable_count = sum(
            item["health_status"] == "unavailable"
            for item in health_sources
        )
        overall = (
            "healthy"
            if healthy_count == len(health_sources)
            else "degraded"
            if unavailable_count < len(health_sources)
            else "unavailable"
        )
        snapshot = {
            "document_id": f"GLOBAL-SNAPSHOT-v3-{version}",
            "version": version,
            "timestamp": generated_at,
            "generated_time": generated_at,
            "global": {
                "status": overall,
                "source_count": len(health_sources),
            },
            "us": {
                "sec_edgar": cls._summary(
                    effective_payloads.get("SEC_EDGAR")
                )
            },
            "taiwan": {
                "twse": cls._summary(effective_payloads.get("TWSE")),
                "tpex": cls._summary(effective_payloads.get("TPEX")),
                "mops": cls._summary(effective_payloads.get("MOPS")),
            },
            "macro": {
                "fred": cls._summary(effective_payloads.get("FRED"))
            },
            "evidence": evidence,
            "source_hash": source_hashes,
            "provider_payloads": dict(effective_payloads),
            "market_health": {
                "overall_status": overall,
                "healthy_sources": healthy_count,
                "total_sources": len(health_sources),
                "sources": health_sources,
            },
            "status": "validated_shadow_snapshot_v3",
            "model_impact": "official_data_only_not_production",
            "runtime_direct_api_access": False,
            "repository_write_authorized": False,
            "production_authorized": False,
        }
        snapshot["snapshot_hash"] = cls._payload_hash(snapshot)
        return snapshot

    @staticmethod
    def _summary(payload: Any) -> dict[str, Any]:
        if payload is None:
            return {"available": False, "record_count": 0}
        if isinstance(payload, list):
            count = len(payload)
        elif isinstance(payload, Mapping):
            count = len(payload)
        else:
            count = 1
        return {
            "available": True,
            "record_count": count,
            "payload_hash": GlobalSnapshotBuilderV3._payload_hash(payload),
        }

    @staticmethod
    def _payload_hash(payload: Any) -> str | None:
        if payload is None:
            return None
        raw = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _region(source_id: str) -> str:
        if source_id in {"TWSE", "TPEX", "MOPS"}:
            return "Taiwan"
        if source_id == "SEC_EDGAR":
            return "United States"
        return "Global"

    @staticmethod
    def _timestamp(value: str) -> None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise SnapshotV3Error(
                "generated_at must be an ISO date-time"
            ) from exc
        if parsed.tzinfo is None:
            raise SnapshotV3Error("generated_at requires timezone")
