"""North Star Shadow Runtime infrastructure.

The package contains no Decision Logic, Strategy, Scoring, trading execution,
or direct Repository write capability.
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
    "DailyShadowDecisionRun",
    "ExplainRuntime",
    "ExplainRuntimeError",
    "LearningRuntime",
    "LearningRuntimeError",
    "LoadedSnapshot",
    "MergeAuthorization",
    "NorthStarDecisionValidator",
    "NorthStarShadowDailyBrief",
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
    "WAITING_FOR_SHADOW_RUN",
    "build_shadow_dashboard_projection",
]
