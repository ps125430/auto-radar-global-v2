"""Automatic Evidence candidates derived only from validated provider records."""

from __future__ import annotations

from typing import Any

from .snapshot import flatten_snapshot_records


class EvidenceCollector:
    """Convert a validated Market Snapshot into read-only Evidence candidates."""

    @classmethod
    def collect(cls, snapshot: dict[str, Any]) -> dict[str, Any]:
        if snapshot.get("quality", {}).get("status") != "PASS":
            raise ValueError("Evidence requires a validated Market Snapshot")
        records = flatten_snapshot_records(snapshot)
        evidence = [
            {
                "evidence_id": f"PROVIDER-{record.record_id}",
                "source": record.source,
                "timestamp": record.timestamp,
                "category": record.category,
                "importance": record.importance,
                "reliability": record.reliability,
                "reference": record.reference,
                "provider": record.provider,
                "market": record.market,
                "symbol": record.symbol,
                "status": "runtime_evidence_candidate",
                "model_impact": "evidence_only_not_production",
                "repository_write_authorized": False,
            }
            for record in records
        ]
        return {
            "collection_id": (
                f"EVIDENCE-COLLECTION-"
                f"{snapshot['snapshot_date'].replace('-', '')}"
            ),
            "snapshot_ref": snapshot["snapshot_id"],
            "generated_at": snapshot["as_of"],
            "status": "shadow_evidence_collection",
            "evidence_count": len(evidence),
            "evidence": evidence,
            "manual_entry": False,
            "repository_write_authorized": False,
            "production_authorized": False,
        }
