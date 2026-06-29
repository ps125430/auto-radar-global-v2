"""Immutable execution context for one North Star Runtime request."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping

from .immutability import deep_freeze, deep_thaw
from .loader import LoadedSnapshot


class RuntimeContextError(RuntimeError):
    """Raised when a Runtime Context violates the approved contract."""


@dataclass(frozen=True, slots=True)
class RuntimeContext:
    request_id: str
    session_id: str
    as_of: datetime
    runtime_mode: str
    snapshots: Mapping[str, LoadedSnapshot]
    payload: Mapping[str, Any]
    validation_status: str = "validated"

    def __post_init__(self) -> None:
        if not self.request_id.strip() or not self.session_id.strip():
            raise RuntimeContextError("Runtime identifiers must not be empty")
        if self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise RuntimeContextError("Runtime as_of must be timezone-aware")
        if self.runtime_mode != "shadow_candidate":
            raise RuntimeContextError("Only shadow_candidate Runtime is authorized")
        if self.validation_status != "validated":
            raise RuntimeContextError("Runtime input must be validated")

        snapshot_copy = dict(self.snapshots)
        if any(key != snapshot.reference for key, snapshot in snapshot_copy.items()):
            raise RuntimeContextError(
                "Runtime snapshot keys must match their canonical references"
            )
        object.__setattr__(
            self, "snapshots", MappingProxyType(snapshot_copy)
        )
        object.__setattr__(self, "payload", deep_freeze(self.payload))

    @property
    def source_refs(self) -> tuple[str, ...]:
        return tuple(self.snapshots)

    def snapshot(self, reference: str) -> LoadedSnapshot:
        try:
            return self.snapshots[reference]
        except KeyError as exc:
            raise RuntimeContextError(
                f"Runtime Context does not contain snapshot: {reference}"
            ) from exc

    def mutable_payload(self) -> dict[str, Any]:
        return deep_thaw(self.payload)
