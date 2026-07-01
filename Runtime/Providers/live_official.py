"""Official live providers behind a single Registry gateway."""

from __future__ import annotations

import hashlib
import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Sequence

class LiveProviderError(RuntimeError):
    """Raised when an official provider cannot return valid data."""


class HttpTransport(Protocol):
    def get_json(
        self,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[Any, float]: ...

    def get_text(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[str, float]: ...


class RequestsTransport:
    """The only network boundary used by official Providers."""

    def __init__(self, *, timeout_seconds: float = 12) -> None:
        self.timeout_seconds = timeout_seconds

    def get_json(
        self,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[Any, float]:
        started = time.perf_counter()
        query = urlencode(dict(params or {}))
        target = f"{url}?{query}" if query else url
        request = Request(target, headers=dict(headers or {}))
        with urlopen(
            request,
            timeout=self.timeout_seconds,
        ) as response:
            payload = json.loads(response.read().decode("utf-8-sig"))
        return payload, round(
            (time.perf_counter() - started) * 1000, 2
        )

    def get_text(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[str, float]:
        started = time.perf_counter()
        request = Request(url, headers=dict(headers or {}))
        with urlopen(
            request,
            timeout=self.timeout_seconds,
        ) as response:
            body = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
        return body.decode(charset, errors="replace"), round(
            (time.perf_counter() - started) * 1000, 2
        )


@dataclass(frozen=True, slots=True)
class ProviderFetch:
    source_id: str
    fetched_at: str
    health_status: str
    latency_ms: float | None
    payload: Any
    source_hash: str | None
    error: str | None
    official: bool = True

    @property
    def ok(self) -> bool:
        return self.health_status == "healthy"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "fetched_at": self.fetched_at,
            "health_status": self.health_status,
            "latency_ms": self.latency_ms,
            "payload": self.payload,
            "source_hash": self.source_hash,
            "error": self.error,
            "official": self.official,
        }


class OfficialLiveProvider:
    source_id = ""

    def __init__(self, transport: HttpTransport) -> None:
        self.transport = transport

    def fetch(self) -> ProviderFetch:
        fetched_at = datetime.now(timezone.utc).isoformat()
        try:
            payload, latency = self._fetch()
            if payload in (None, "", [], {}):
                raise LiveProviderError("Official source returned empty payload")
            serialized = json.dumps(
                payload, ensure_ascii=False, sort_keys=True
            ).encode("utf-8")
            return ProviderFetch(
                source_id=self.source_id,
                fetched_at=fetched_at,
                health_status="healthy",
                latency_ms=latency,
                payload=payload,
                source_hash=hashlib.sha256(serialized).hexdigest(),
                error=None,
            )
        except Exception as exc:
            return ProviderFetch(
                source_id=self.source_id,
                fetched_at=fetched_at,
                health_status="unavailable",
                latency_ms=None,
                payload=None,
                source_hash=None,
                error=f"{type(exc).__name__}: {exc}",
            )

    def _fetch(self) -> tuple[Any, float]:
        raise NotImplementedError


class TWSEProvider(OfficialLiveProvider):
    source_id = "TWSE"
    ENDPOINT = (
        "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    )

    def _fetch(self) -> tuple[Any, float]:
        return self.transport.get_json(self.ENDPOINT)


class TPExProvider(OfficialLiveProvider):
    source_id = "TPEX"
    ENDPOINT = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"

    def _fetch(self) -> tuple[Any, float]:
        return self.transport.get_json(self.ENDPOINT)


class MOPSProvider(OfficialLiveProvider):
    source_id = "MOPS"
    ENDPOINT = "https://mops.twse.com.tw/mops/"

    def _fetch(self) -> tuple[Any, float]:
        text, latency = self.transport.get_text(self.ENDPOINT)
        return {
            "document": "MOPS official disclosure portal",
            "content_hash": hashlib.sha256(
                text.encode("utf-8")
            ).hexdigest(),
            "content_length": len(text),
        }, latency


class FREDProvider(OfficialLiveProvider):
    source_id = "FRED"
    ENDPOINT = (
        "https://api.stlouisfed.org/fred/series/observations"
    )
    SERIES_IDS = ("DGS10", "DFF", "UNRATE")

    def __init__(
        self,
        transport: HttpTransport,
        *,
        api_key: str | None = None,
    ) -> None:
        super().__init__(transport)
        self.api_key = api_key or os.getenv("FRED_API_KEY")

    def _fetch(self) -> tuple[Any, float]:
        if not self.api_key:
            raise LiveProviderError("FRED_API_KEY is not configured")
        observations: dict[str, Any] = {}
        total_latency = 0.0
        for series_id in self.SERIES_IDS:
            payload, latency = self.transport.get_json(
                self.ENDPOINT,
                params={
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1,
                },
            )
            rows = payload.get("observations") if isinstance(
                payload, Mapping
            ) else None
            if not isinstance(rows, list) or not rows:
                raise LiveProviderError(
                    f"FRED returned no observation for {series_id}"
                )
            observations[series_id] = rows[0]
            total_latency += latency
        return {"series": observations}, round(total_latency, 2)


class SECEdgarProvider(OfficialLiveProvider):
    source_id = "SEC_EDGAR"
    TICKERS_ENDPOINT = (
        "https://www.sec.gov/files/company_tickers_exchange.json"
    )
    SUBMISSIONS_ENDPOINT = (
        "https://data.sec.gov/submissions/CIK{cik}.json"
    )

    def __init__(
        self,
        transport: HttpTransport,
        *,
        user_agent: str | None = None,
        ciks: Sequence[str] | None = None,
    ) -> None:
        super().__init__(transport)
        self.user_agent = user_agent or os.getenv("SEC_USER_AGENT")
        configured_ciks = ciks or tuple(
            item.strip()
            for item in os.getenv("SEC_EDGAR_CIKS", "").split(",")
            if item.strip()
        )
        self.ciks = tuple(configured_ciks)

    def _fetch(self) -> tuple[Any, float]:
        if not self.user_agent:
            raise LiveProviderError("SEC_USER_AGENT is not configured")
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate",
        }
        if not self.ciks:
            payload, latency = self.transport.get_json(
                self.TICKERS_ENDPOINT, headers=headers
            )
            return {"company_ticker_framework": payload}, latency
        submissions = {}
        total_latency = 0.0
        for cik in self.ciks:
            normalized = str(cik).zfill(10)
            payload, latency = self.transport.get_json(
                self.SUBMISSIONS_ENDPOINT.format(cik=normalized),
                headers=headers,
            )
            submissions[normalized] = payload
            total_latency += latency
        return {"submissions": submissions}, round(total_latency, 2)


class LiveProviderRegistry:
    """The sole gateway from Real Ocean to official network Providers."""

    REQUIRED_SOURCE_IDS = {
        "TWSE",
        "TPEX",
        "MOPS",
        "FRED",
        "SEC_EDGAR",
    }

    def __init__(self, providers: Sequence[OfficialLiveProvider]) -> None:
        mapping: dict[str, OfficialLiveProvider] = {}
        for provider in providers:
            if provider.source_id in mapping:
                raise LiveProviderError(
                    f"Duplicate Provider: {provider.source_id}"
                )
            mapping[provider.source_id] = provider
        missing = self.REQUIRED_SOURCE_IDS - mapping.keys()
        extra = mapping.keys() - self.REQUIRED_SOURCE_IDS
        if missing or extra:
            raise LiveProviderError(
                f"Provider Registry mismatch; "
                f"missing={sorted(missing)}, extra={sorted(extra)}"
            )
        self._providers = mapping

    @classmethod
    def official(
        cls,
        *,
        transport: HttpTransport | None = None,
    ) -> "LiveProviderRegistry":
        shared = transport or RequestsTransport()
        return cls(
            (
                TWSEProvider(shared),
                TPExProvider(shared),
                MOPSProvider(shared),
                FREDProvider(shared),
                SECEdgarProvider(shared),
            )
        )

    def fetch_all(self) -> tuple[ProviderFetch, ...]:
        return tuple(
            self._providers[source_id].fetch()
            for source_id in sorted(self._providers)
        )
