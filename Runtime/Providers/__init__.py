"""Real Data Foundation provider boundary."""

from .artifacts import ArtifactWriteError, ArtifactWriter
from .base import ArchivedPayloadProvider, MarketProvider, ProviderError
from .evidence import EvidenceCollector
from .models import ProviderRecord, ProviderRequest
from .providers import (
    ETFProvider,
    MacroProvider,
    MockProvider,
    NewsProvider,
    ProviderRegistry,
    TaiwanProvider,
    USProvider,
    registry_from_payload,
)
from .quality import DataQualityEngine, DataQualityError
from .snapshot import (
    MarketSnapshotBuilder,
    MarketSnapshotReader,
    flatten_snapshot_records,
)

__all__ = [
    "ArchivedPayloadProvider",
    "ArtifactWriteError",
    "ArtifactWriter",
    "DataQualityEngine",
    "DataQualityError",
    "ETFProvider",
    "EvidenceCollector",
    "MacroProvider",
    "MarketProvider",
    "MarketSnapshotBuilder",
    "MarketSnapshotReader",
    "MockProvider",
    "NewsProvider",
    "ProviderError",
    "ProviderRecord",
    "ProviderRegistry",
    "ProviderRequest",
    "TaiwanProvider",
    "USProvider",
    "flatten_snapshot_records",
    "registry_from_payload",
]
