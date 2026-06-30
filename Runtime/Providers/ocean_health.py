"""Read-only health projection for official-first market data."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .official_registry import DataProviderRegistry


class OceanHealthEngine:
    """Describe source health without changing formal Decision confidence."""

    STATUS_WEIGHTS = {
        "healthy": 1.0,
        "warning": 0.75,
        "degraded": 0.45,
        "unavailable": 0.0,
    }

    @classmethod
    def evaluate(
        cls,
        registry: DataProviderRegistry,
        evidence: list[dict[str, Any]],
        *,
        snapshot_version: str,
        generated_at: str,
    ) -> dict[str, Any]:
        providers = registry.list()
        evidence_sources = Counter(item["source"] for item in evidence)
        source_health = []
        weighted_health = 0.0
        for provider in providers:
            status = provider["health_status"]
            weighted_health += (
                cls.STATUS_WEIGHTS[status] * provider["trust_score"]
            )
            source_health.append(
                {
                    "source_id": provider["source_id"],
                    "source_class": provider["source_class"],
                    "health_status": status,
                    "trust_score": provider["trust_score"],
                    "evidence_count": evidence_sources[
                        provider["source_id"]
                    ],
                    "last_success": provider["last_success"],
                    "last_failure": provider["last_failure"],
                }
            )

        evidence_coverage = round(
            100
            * sum(1 for item in source_health if item["evidence_count"] > 0)
            / len(source_health)
        )
        health_score = round(weighted_health / len(providers))
        if health_score >= 85 and evidence_coverage >= 80:
            overall = "healthy"
        elif health_score >= 65 and evidence_coverage >= 60:
            overall = "warning"
        elif health_score > 0:
            overall = "degraded"
        else:
            overall = "unavailable"
        reduction_candidate = max(0, 100 - health_score)

        return {
            "document_id": f"OCEAN-HEALTH-{snapshot_version}",
            "snapshot_version": snapshot_version,
            "generated_at": generated_at,
            "overall_status": overall,
            "health_score": health_score,
            "evidence_coverage": evidence_coverage,
            "sources": source_health,
            "data_confidence_adjustment_candidate": {
                "direction": "reduce_only",
                "maximum_reduction_percent": reduction_candidate,
                "requires_architecture_validation": True,
                "applied_to_decision_confidence": False,
            },
            "status": "shadow_health_candidate",
            "model_impact": "data_health_only_not_production",
            "production_authorized": False,
            "repository_write_authorized": False,
        }
