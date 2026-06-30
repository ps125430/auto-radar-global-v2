"""Approved no-network Provider adapters."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .base import ArchivedPayloadProvider, MarketProvider, ProviderError
from .models import ProviderRequest


class TaiwanProvider(ArchivedPayloadProvider):
    provider_id = "taiwan"


class USProvider(ArchivedPayloadProvider):
    provider_id = "us"


class MacroProvider(ArchivedPayloadProvider):
    provider_id = "macro"


class NewsProvider(ArchivedPayloadProvider):
    provider_id = "news"


class ETFProvider(ArchivedPayloadProvider):
    provider_id = "etf"


class MockProvider(ArchivedPayloadProvider):
    provider_id = "mock"


class ProviderRegistry:
    """Single entry point for all provider reads."""

    REQUIRED_PROVIDER_IDS = {
        "taiwan",
        "us",
        "macro",
        "news",
        "etf",
        "mock",
    }

    def __init__(self, providers: Sequence[MarketProvider]) -> None:
        provider_map: dict[str, MarketProvider] = {}
        for provider in providers:
            provider_id = getattr(provider, "provider_id", None)
            if not isinstance(provider_id, str) or not provider_id:
                raise ProviderError("Provider is missing provider_id")
            if provider_id in provider_map:
                raise ProviderError(f"Duplicate provider: {provider_id}")
            provider_map[provider_id] = provider
        missing = sorted(self.REQUIRED_PROVIDER_IDS - provider_map.keys())
        extra = sorted(provider_map.keys() - self.REQUIRED_PROVIDER_IDS)
        if missing or extra:
            raise ProviderError(
                f"Provider registry mismatch; missing={missing}, extra={extra}"
            )
        self._providers = provider_map

    def collect_all(
        self,
        request: ProviderRequest,
    ) -> tuple[Mapping[str, Any], ...]:
        records: list[Mapping[str, Any]] = []
        for provider_id in sorted(self._providers):
            provider = self._providers[provider_id]
            for record in provider.collect(request):
                if record.get("provider") != provider_id:
                    raise ProviderError(
                        f"Provider identity mismatch: {provider_id}"
                    )
                records.append(record)
        return tuple(records)


PROVIDER_TYPES = {
    "taiwan": TaiwanProvider,
    "us": USProvider,
    "macro": MacroProvider,
    "news": NewsProvider,
    "etf": ETFProvider,
    "mock": MockProvider,
}


def registry_from_payload(
    payload: Mapping[str, Sequence[Mapping[str, Any]]],
) -> ProviderRegistry:
    """Build all approved Provider adapters from an archived payload."""

    if not isinstance(payload, Mapping):
        raise ProviderError("providers payload must be an object")
    providers: list[MarketProvider] = []
    for provider_id, provider_type in PROVIDER_TYPES.items():
        records = payload.get(provider_id)
        if records is None:
            raise ProviderError(f"Missing provider payload: {provider_id}")
        providers.append(provider_type(records))
    return ProviderRegistry(providers)
