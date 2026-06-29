"""Disabled-by-default North Star Shadow Runtime framework."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from .context import RuntimeContext
from .dispatcher import RuntimeDispatcher, RuntimeHandler
from .loader import RuntimeLoader
from .session import RuntimeSession


class RuntimeFrameworkError(RuntimeError):
    """Raised when the Runtime Framework is not authorized or misconfigured."""


@dataclass(frozen=True, slots=True)
class RuntimeExecution:
    context: RuntimeContext
    session: RuntimeSession
    output: Mapping[str, Any]


class RuntimeFramework:
    """Coordinate loading, context creation, session lifecycle, and dispatch."""

    def __init__(
        self,
        repository_root: Path | str,
        *,
        enabled: bool = False,
        runtime_mode: str = "shadow_candidate",
    ) -> None:
        if runtime_mode != "shadow_candidate":
            raise RuntimeFrameworkError(
                "North Star Runtime supports shadow_candidate mode only"
            )
        self.enabled = enabled
        self.runtime_mode = runtime_mode
        self.loader = RuntimeLoader(repository_root)
        self.dispatcher = RuntimeDispatcher()

    def register(self, handler: RuntimeHandler) -> None:
        self.dispatcher.register(handler)

    def execute(
        self,
        engine_id: str,
        *,
        source_refs: tuple[str, ...],
        payload: Mapping[str, Any] | None = None,
        as_of: datetime | None = None,
    ) -> RuntimeExecution:
        if not self.enabled:
            raise RuntimeFrameworkError(
                "Runtime Framework is disabled; explicit Shadow enablement is required"
            )

        request_id = f"REQ-{uuid4()}"
        session_id = f"SES-{uuid4()}"
        snapshots = self.loader.load_many(source_refs)
        context = RuntimeContext(
            request_id=request_id,
            session_id=session_id,
            as_of=as_of or datetime.now(timezone.utc),
            runtime_mode=self.runtime_mode,
            snapshots=snapshots,
            payload=payload or {},
        )
        session = RuntimeSession(session_id=session_id, request_id=request_id)
        output = self.dispatcher.dispatch(engine_id, context, session)
        return RuntimeExecution(context=context, session=session, output=output)

    @staticmethod
    def rollback(execution: RuntimeExecution, reason: str) -> None:
        execution.session.rollback(reason)
