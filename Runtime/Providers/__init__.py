"""Real Data Foundation provider boundary."""

from .artifacts import ArtifactWriteError, ArtifactWriter
from .base import ArchivedPayloadProvider, MarketProvider, ProviderError
from .evidence import EvidenceCollector
from .evidence_normalizer import (
    EvidenceNormalizationError,
    EvidenceNormalizer,
)
from .models import ProviderRecord, ProviderRequest
from .ocean_health import OceanHealthEngine
from .official_registry import (
    DataProviderRegistry,
    ProviderRegistryError,
)
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
from .snapshot_v2 import MarketSnapshotBuilderV2, SnapshotV2Error

__all__ = [
    "ArchivedPayloadProvider",
    "ArtifactWriteError",
    "ArtifactWriter",
    "DataQualityEngine",
    "DataQualityError",
    "ETFProvider",
    "EvidenceCollector",
    "EvidenceNormalizationError",
    "EvidenceNormalizer",
    "MacroProvider",
    "MarketProvider",
    "MarketSnapshotBuilder",
    "MarketSnapshotBuilderV2",
    "MarketSnapshotReader",
    "MockProvider",
    "NewsProvider",
    "ProviderError",
    "ProviderRegistryError",
    "ProviderRecord",
    "ProviderRegistry",
    "ProviderRequest",
    "DataProviderRegistry",
    "OceanHealthEngine",
    "SnapshotV2Error",
    "TaiwanProvider",
    "USProvider",
    "flatten_snapshot_records",
    "registry_from_payload",
]
