"""Market Snapshot builder. Runtime consumes snapshots, never Provider APIs."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime
from typing import Any

from .models import ProviderRequest, ProviderRecord
from .providers import ProviderRegistry
from .quality import DataQualityEngine


class MarketSnapshotBuilder:
    """Build a deterministic, validated Market Snapshot."""

    SEGMENTS = ("GLOBAL", "US", "TAIWAN", "CRYPTO", "MACRO")

    def __init__(self, quality_engine: type[DataQualityEngine] = DataQualityEngine):
        self.quality_engine = quality_engine

    def build(
        self,
        registry: ProviderRegistry,
        *,
        snapshot_date: str,
        as_of: str,
    ) -> dict[str, Any]:
        self._validate_snapshot_date(snapshot_date)
        request = ProviderRequest(snapshot_date=snapshot_date, as_of=as_of)
        raw_records = registry.collect_all(request)
        records = self.quality_engine.validate(raw_records, as_of=as_of)
        segments = {
            segment.lower(): [
                record.to_dict()
                for record in records
                if record.market == segment
            ]
            for segment in self.SEGMENTS
        }
        missing_segments = [
            segment for segment, items in segments.items() if not items
        ]
        if missing_segments:
            raise ValueError(
                "Market Snapshot missing segments: "
                + ", ".join(missing_segments)
            )
        counts = Counter(record.provider for record in records)
        return {
            "snapshot_id": f"MARKET-SNAPSHOT-{snapshot_date.replace('-', '')}",
            "snapshot_date": snapshot_date,
            "as_of": as_of,
            "status": "validated_shadow_snapshot",
            "model_impact": "provider_data_only_not_production",
            "global": segments["global"],
            "us": segments["us"],
            "taiwan": segments["taiwan"],
            "crypto": segments["crypto"],
            "macro": segments["macro"],
            "provider_summary": dict(sorted(counts.items())),
            "record_count": len(records),
            "quality": {
                "status": "PASS",
                "missing": 0,
                "duplicate": 0,
                "invalid": 0,
                "outlier": 0,
                "timestamp_errors": 0,
            },
            "runtime_api_access": False,
            "production_authorized": False,
            "repository_write_authorized": False,
        }

    @staticmethod
    def _validate_snapshot_date(value: str) -> None:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except (TypeError, ValueError) as exc:
            raise ValueError("snapshot_date must use YYYY-MM-DD") from exc


class MarketSnapshotReader:
    """Runtime gateway that accepts validated snapshots, never Providers."""

    @staticmethod
    def read(snapshot: dict[str, Any]) -> dict[str, Any]:
        if snapshot.get("status") != "validated_shadow_snapshot":
            raise ValueError("Runtime requires a validated Market Snapshot")
        if snapshot.get("quality", {}).get("status") != "PASS":
            raise ValueError("Runtime requires Market Snapshot quality PASS")
        if snapshot.get("runtime_api_access") is not False:
            raise ValueError("Market Snapshot cannot authorize Runtime API access")
        if snapshot.get("production_authorized") is not False:
            raise ValueError("Market Snapshot cannot authorize Production")
        for segment in MarketSnapshotBuilder.SEGMENTS:
            records = snapshot.get(segment.lower())
            if not isinstance(records, list) or not records:
                raise ValueError(f"Market Snapshot missing segment: {segment}")
        return deepcopy(snapshot)


def flatten_snapshot_records(
    snapshot: dict[str, Any],
) -> tuple[ProviderRecord, ...]:
    """Return normalized records from an already validated snapshot."""

    snapshot = MarketSnapshotReader.read(snapshot)
    records: list[ProviderRecord] = []
    for segment in MarketSnapshotBuilder.SEGMENTS:
        for item in snapshot[segment.lower()]:
            records.append(ProviderRecord(**item))
    return tuple(sorted(records, key=lambda item: item.record_id))
