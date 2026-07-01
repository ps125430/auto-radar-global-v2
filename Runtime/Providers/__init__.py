"""Real Data Foundation provider boundary."""

from .artifacts import ArtifactWriteError, ArtifactWriter
from .base import ArchivedPayloadProvider, MarketProvider, ProviderError
from .evidence import EvidenceCollector
from .evidence_normalizer import (
    EvidenceNormalizationError,
    EvidenceNormalizer,
)
from .models import ProviderRecord, ProviderRequest
from .live_official import (
    FREDProvider,
    HttpTransport,
    LiveProviderError,
    LiveProviderRegistry,
    MOPSProvider,
    ProviderFetch,
    RequestsTransport,
    SECEdgarProvider,
    TPExProvider,
    TWSEProvider,
)
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
from .snapshot_v3 import (
    GlobalSnapshotBuilderV3,
    OfficialFallbackPolicy,
    SnapshotV3Error,
)
from .real_ocean import RealOceanError, RealOceanPipeline
from .scheduler import RealOceanScheduler, ScheduleEntry

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
    "FREDProvider",
    "GlobalSnapshotBuilderV3",
    "HttpTransport",
    "LiveProviderError",
    "LiveProviderRegistry",
    "MacroProvider",
    "MarketProvider",
    "MarketSnapshotBuilder",
    "MarketSnapshotBuilderV2",
    "MarketSnapshotReader",
    "MOPSProvider",
    "MockProvider",
    "NewsProvider",
    "ProviderError",
    "ProviderFetch",
    "ProviderRegistryError",
    "ProviderRecord",
    "ProviderRegistry",
    "ProviderRequest",
    "RealOceanError",
    "RealOceanPipeline",
    "RealOceanScheduler",
    "RequestsTransport",
    "SECEdgarProvider",
    "ScheduleEntry",
    "DataProviderRegistry",
    "OceanHealthEngine",
    "SnapshotV2Error",
    "SnapshotV3Error",
    "OfficialFallbackPolicy",
    "TPExProvider",
    "TWSEProvider",
    "TaiwanProvider",
    "USProvider",
    "flatten_snapshot_records",
    "registry_from_payload",
]
