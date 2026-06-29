"""Immutable JSON-compatible values used by the Shadow Runtime."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any


def deep_freeze(value: Any) -> Any:
    """Return a recursively immutable copy of a JSON-compatible value."""
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): deep_freeze(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(deep_freeze(item) for item in value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Runtime values must be JSON-compatible, got {type(value)!r}")


def deep_thaw(value: Any) -> Any:
    """Return a mutable JSON-compatible copy of an immutable value."""
    if isinstance(value, Mapping):
        return {str(key): deep_thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [deep_thaw(item) for item in value]
    return value
