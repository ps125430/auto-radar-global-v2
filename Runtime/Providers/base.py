"""Provider interface. Runtime code never accesses external APIs directly."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

from .models import ProviderRequest


class ProviderError(RuntimeError):
    """Raised when a Provider violates the unified interface."""


class MarketProvider(ABC):
    """Unified provider contract with no network implementation."""

    provider_id: str

    @abstractmethod
    def collect(self, request: ProviderRequest) -> tuple[Mapping[str, Any], ...]:
        """Return raw records for validation without calling Runtime engines."""


class ArchivedPayloadProvider(MarketProvider):
    """No-network adapter backed by an immutable archived payload."""

    provider_id = "archived"

    def __init__(self, records: Sequence[Mapping[str, Any]]) -> None:
        if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
            raise ProviderError("Provider records must be a sequence")
        self._records = tuple(deepcopy(dict(record)) for record in records)

    def collect(self, request: ProviderRequest) -> tuple[Mapping[str, Any], ...]:
        if not request.snapshot_date or not request.as_of:
            raise ProviderError("ProviderRequest requires snapshot_date and as_of")
        return tuple(deepcopy(record) for record in self._records)
