"""In-memory lifecycle for one North Star Runtime session."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from .immutability import deep_freeze, deep_thaw


class RuntimeSessionError(RuntimeError):
    """Raised when a Runtime Session transition is invalid."""


class SessionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True, slots=True)
class SessionEvent:
    event: str
    timestamp: datetime
    details: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "timestamp": self.timestamp.isoformat(),
            "details": deep_thaw(self.details),
        }


class RuntimeSession:
    """Track lifecycle without persisting or mutating Repository state."""

    def __init__(self, session_id: str, request_id: str) -> None:
        if not session_id.strip() or not request_id.strip():
            raise RuntimeSessionError("Session identifiers must not be empty")
        self.session_id = session_id
        self.request_id = request_id
        self.status = SessionStatus.CREATED
        self.engine_id: str | None = None
        self.output: Mapping[str, Any] | None = None
        self.error: str | None = None
        self._events: list[SessionEvent] = []
        self._record("created", {})

    @property
    def events(self) -> tuple[SessionEvent, ...]:
        return tuple(self._events)

    def start(self, engine_id: str) -> None:
        if self.status is not SessionStatus.CREATED:
            raise RuntimeSessionError(
                f"Session cannot start from {self.status.value}"
            )
        if not engine_id.strip():
            raise RuntimeSessionError("Engine ID must not be empty")
        self.engine_id = engine_id
        self.status = SessionStatus.RUNNING
        self._record("started", {"engine_id": engine_id})

    def complete(self, output: Mapping[str, Any]) -> None:
        if self.status is not SessionStatus.RUNNING:
            raise RuntimeSessionError(
                f"Session cannot complete from {self.status.value}"
            )
        self.output = deep_freeze(output)
        self.status = SessionStatus.COMPLETED
        self._record("completed", {"engine_id": self.engine_id})

    def fail(self, error: str) -> None:
        if self.status is not SessionStatus.RUNNING:
            raise RuntimeSessionError(
                f"Session cannot fail from {self.status.value}"
            )
        if not error.strip():
            raise RuntimeSessionError("Session error must not be empty")
        self.error = error
        self.status = SessionStatus.FAILED
        self._record("failed", {"engine_id": self.engine_id, "error": error})

    def rollback(self, reason: str) -> None:
        if self.status is SessionStatus.ROLLED_BACK:
            raise RuntimeSessionError("Session is already rolled back")
        if not reason.strip():
            raise RuntimeSessionError("Rollback reason must not be empty")
        previous = self.status
        self.status = SessionStatus.ROLLED_BACK
        self._record(
            "rolled_back",
            {"previous_status": previous.value, "reason": reason},
        )

    def output_dict(self) -> dict[str, Any] | None:
        return deep_thaw(self.output) if self.output is not None else None

    def _record(self, event: str, details: Mapping[str, Any]) -> None:
        self._events.append(
            SessionEvent(
                event=event,
                timestamp=datetime.now(timezone.utc),
                details=deep_freeze(details),
            )
        )
