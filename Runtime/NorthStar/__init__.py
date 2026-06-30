"""North Star Shadow Runtime infrastructure.

The package contains no Decision Logic, Strategy, production Scoring, trading
execution, or direct Knowledge Repository write capability.
"""

from .context import RuntimeContext, RuntimeContextError
from .decision import (
    DecisionRuntime,
    DecisionRuntimeError,
    NorthStarDecisionValidator,
)
from .dashboard_binding import (
    DashboardBindingError,
    WAITING_FOR_SHADOW_RUN,
    build_shadow_dashboard_projection,
)
from .daily_intelligence import (
    DailyIntelligenceError,
    DailyIntelligenceLoop,
    DailyReflection,
    DecisionResidualEngine,
    DecisionSnapshot,
    OutcomeCollector,
    RootCauseAnalyzer,
    ShadowRecordWriter,
)
from .dispatcher import RuntimeDispatcher, RuntimeDispatchError
from .explain import ExplainRuntime, ExplainRuntimeError
from .framework import RuntimeExecution, RuntimeFramework, RuntimeFrameworkError
from .learning import LearningRuntime, LearningRuntimeError
from .loader import LoadedSnapshot, RuntimeLoader, RuntimeLoaderError
from .patch_queue import (
    MergeAuthorization,
    PatchQueueEntry,
    PatchQueueError,
    PatchStatus,
    RepositoryPatchQueue,
)
from .session import (
    RuntimeSession,
    RuntimeSessionError,
    SessionEvent,
    SessionStatus,
)
from .shadow import (
    DailyShadowDecisionRun,
    NorthStarShadowDailyBrief,
    PatchSuggestionFlow,
    ShadowIntegrationError,
    ShadowReviewPipeline,
    ShadowRunResult,
    ShadowRuntimeOrchestrator,
)
from .shadow_quality import (
    ShadowInputValidationError,
    ShadowInputValidator,
    ShadowOutputQualityError,
    ShadowOutputQualityGate,
)

__all__ = [
    "DecisionRuntime",
    "DecisionRuntimeError",
    "DashboardBindingError",
    "DailyIntelligenceError",
    "DailyIntelligenceLoop",
    "DailyReflection",
    "DailyShadowDecisionRun",
    "DecisionResidualEngine",
    "DecisionSnapshot",
    "ExplainRuntime",
    "ExplainRuntimeError",
    "LearningRuntime",
    "LearningRuntimeError",
    "LoadedSnapshot",
    "MergeAuthorization",
    "NorthStarDecisionValidator",
    "NorthStarShadowDailyBrief",
    "OutcomeCollector",
    "PatchSuggestionFlow",
    "PatchQueueEntry",
    "PatchQueueError",
    "PatchStatus",
    "RepositoryPatchQueue",
    "RuntimeContext",
    "RuntimeContextError",
    "RuntimeDispatchError",
    "RuntimeDispatcher",
    "RuntimeExecution",
    "RuntimeFramework",
    "RuntimeFrameworkError",
    "RuntimeLoader",
    "RuntimeLoaderError",
    "RuntimeSession",
    "RuntimeSessionError",
    "RootCauseAnalyzer",
    "SessionEvent",
    "SessionStatus",
    "ShadowIntegrationError",
    "ShadowInputValidationError",
    "ShadowInputValidator",
    "ShadowOutputQualityError",
    "ShadowOutputQualityGate",
    "ShadowReviewPipeline",
    "ShadowRunResult",
    "ShadowRuntimeOrchestrator",
    "ShadowRecordWriter",
    "WAITING_FOR_SHADOW_RUN",
    "build_shadow_dashboard_projection",
]
