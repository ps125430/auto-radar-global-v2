"""Explicit Engine registry and dispatcher for the Shadow Runtime."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from .context import RuntimeContext
from .immutability import deep_thaw
from .session import RuntimeSession


class RuntimeDispatchError(RuntimeError):
    """Raised when dispatch fails or an Engine violates its output contract."""


class RuntimeHandler(Protocol):
    engine_id: str

    def run(self, context: RuntimeContext) -> Mapping[str, Any]:
        """Return one candidate output without side effects."""


class RuntimeDispatcher:
    """Dispatch one request to one registered Engine; no Engine chaining."""

    def __init__(self) -> None:
        self._handlers: dict[str, RuntimeHandler] = {}

    def register(self, handler: RuntimeHandler) -> None:
        engine_id = getattr(handler, "engine_id", "")
        if not isinstance(engine_id, str) or not engine_id.strip():
            raise RuntimeDispatchError("Runtime handler must declare engine_id")
        if engine_id in self._handlers:
            raise RuntimeDispatchError(
                f"Runtime handler is already registered: {engine_id}"
            )
        self._handlers[engine_id] = handler

    def list_engines(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    def dispatch(
        self,
        engine_id: str,
        context: RuntimeContext,
        session: RuntimeSession,
    ) -> dict[str, Any]:
        try:
            handler = self._handlers[engine_id]
        except KeyError as exc:
            raise RuntimeDispatchError(
                f"Runtime handler is not registered: {engine_id}"
            ) from exc

        if context.session_id != session.session_id:
            raise RuntimeDispatchError("Context and Session IDs do not match")
        if context.request_id != session.request_id:
            raise RuntimeDispatchError("Context and Session request IDs do not match")

        session.start(engine_id)
        try:
            output = handler.run(context)
            if not isinstance(output, Mapping):
                raise RuntimeDispatchError(
                    f"Runtime handler {engine_id} must return a mapping"
                )
            mutable_output = deep_thaw(output)
            session.complete(mutable_output)
            return mutable_output
        except Exception as exc:
            if session.status.value == "running":
                session.fail(str(exc) or exc.__class__.__name__)
            if isinstance(exc, RuntimeDispatchError):
                raise
            raise RuntimeDispatchError(
                f"Runtime handler failed: {engine_id}"
            ) from exc
