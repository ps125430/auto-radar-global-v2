"""Immutable provider records used before Market Snapshot creation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    """One deterministic request for archived provider data."""

    snapshot_date: str
    as_of: str


@dataclass(frozen=True, slots=True)
class ProviderRecord:
    """Normalized record accepted by the Data Quality Engine."""

    record_id: str
    provider: str
    market: str
    timestamp: str
    category: str
    symbol: str | None
    value: str | float
    unit: str
    source: str
    importance: int
    reliability: int
    reference: str
    expected_min: float | None = None
    expected_max: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "provider": self.provider,
            "market": self.market,
            "timestamp": self.timestamp,
            "category": self.category,
            "symbol": self.symbol,
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "importance": self.importance,
            "reliability": self.reliability,
            "reference": self.reference,
            "expected_min": self.expected_min,
            "expected_max": self.expected_max,
        }
