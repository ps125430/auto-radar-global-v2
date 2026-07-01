"""Real Ocean orchestration: Fetch -> Validate -> Normalize -> Snapshot -> Dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from .artifacts import ArtifactWriter
from .live_official import LiveProviderRegistry, ProviderFetch
from .snapshot_v3 import GlobalSnapshotBuilderV3, OfficialFallbackPolicy


class RealOceanError(RuntimeError):
    """Raised when the Real Ocean pipeline contract is violated."""


class RealOceanPipeline:
    """Run official Providers without exposing URLs to Runtime callers."""

    TRIGGER_SUFFIX = {
        "us_close": "0600",
        "macro": "0700",
        "taiwan_preopen": "0830",
        "taiwan_close": "1510",
        "manual": "MANUAL",
    }
    STAGES = (
        "fetch",
        "validate",
        "normalize",
        "snapshot",
        "dashboard",
    )

    def __init__(
        self,
        registry: LiveProviderRegistry,
        *,
        artifact_writer: ArtifactWriter | None = None,
    ) -> None:
        self.registry = registry
        self.artifact_writer = artifact_writer

    def run(
        self,
        trigger_id: str,
        *,
        generated_at: datetime,
        cached_snapshot: Mapping[str, Any] | None = None,
        archived_fixture: Mapping[str, Any] | None = None,
        purpose: str = "runtime",
    ) -> dict[str, Any]:
        if generated_at.tzinfo is None:
            raise RealOceanError("generated_at requires timezone")
        try:
            suffix = self.TRIGGER_SUFFIX[trigger_id]
        except KeyError as exc:
            raise RealOceanError(f"Unknown trigger_id: {trigger_id}") from exc

        stage_status: list[dict[str, str]] = []
        fetches = self.registry.fetch_all()
        stage_status.append({"stage": "fetch", "status": "completed"})
        self._validate_fetches(fetches)
        stage_status.append({"stage": "validate", "status": "completed"})
        payloads, modes = OfficialFallbackPolicy.resolve(
            fetches,
            cached_snapshot=cached_snapshot,
            archived_fixture=archived_fixture,
            purpose=purpose,
        )
        stage_status.append({"stage": "normalize", "status": "completed"})
        version = f"{generated_at.date().isoformat()}-{suffix}"
        snapshot = GlobalSnapshotBuilderV3.build(
            fetches,
            effective_payloads=payloads,
            source_modes=modes,
            version=version,
            generated_at=generated_at.isoformat(),
        )
        stage_status.append({"stage": "snapshot", "status": "completed"})
        dashboard_health = self.dashboard_projection(snapshot)
        stage_status.append({"stage": "dashboard", "status": "completed"})
        paths: dict[str, str] = {}
        if self.artifact_writer is not None:
            prefix = f"RealOcean/{version}"
            paths = {
                "snapshot": str(
                    self.artifact_writer.write_json(
                        f"{prefix}/global_snapshot_v3.json",
                        snapshot,
                    )
                ),
                "health": str(
                    self.artifact_writer.write_json(
                        f"{prefix}/provider_health.json",
                        dashboard_health,
                    )
                ),
            }
        return {
            "trigger_id": trigger_id,
            "version": version,
            "stages": stage_status,
            "snapshot": snapshot,
            "dashboard_health": dashboard_health,
            "artifact_paths": paths,
            "status": "shadow_real_ocean_run",
            "production_authorized": False,
        }

    @staticmethod
    def _validate_fetches(fetches: tuple[ProviderFetch, ...]) -> None:
        source_ids = [item.source_id for item in fetches]
        if len(source_ids) != len(set(source_ids)):
            raise RealOceanError("Provider fetch contains duplicate source")
        if set(source_ids) != LiveProviderRegistry.REQUIRED_SOURCE_IDS:
            raise RealOceanError("Provider fetch set is incomplete")

    @staticmethod
    def dashboard_projection(
        snapshot: Mapping[str, Any],
    ) -> dict[str, Any]:
        health = snapshot["market_health"]
        return {
            "snapshot_version": snapshot["version"],
            "snapshot_hash": snapshot["snapshot_hash"],
            "last_update": snapshot["generated_time"],
            "overall_status": health["overall_status"],
            "sources": [
                {
                    "source_id": item["source_id"],
                    "health_status": item["health_status"],
                    "last_update": item["last_update"],
                    "latency_ms": item["latency_ms"],
                    "source_mode": item["source_mode"],
                }
                for item in health["sources"]
            ],
            "status": "shadow_provider_health",
            "repository_write_authorized": False,
            "production_authorized": False,
        }
