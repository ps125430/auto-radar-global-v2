from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from Runtime.Providers import (
    ArtifactWriteError,
    ArtifactWriter,
    FREDProvider,
    LiveProviderRegistry,
    MOPSProvider,
    OfficialFallbackPolicy,
    ProviderFetch,
    RealOceanPipeline,
    RealOceanScheduler,
    SECEdgarProvider,
    TPExProvider,
    TWSEProvider,
)
from Scripts.Dashboard.build_dashboard_data import DashboardDataBuilder


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
NOW = datetime.fromisoformat("2026-07-01T08:30:00+08:00")


class FakeTransport:
    def get_json(
        self,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[Any, float]:
        if "twse" in url:
            return [{"Code": "2330", "ClosingPrice": "1000"}], 21.5
        if "tpex" in url:
            return [{"SecuritiesCompanyCode": "6488"}], 22.5
        if "stlouisfed" in url:
            return {
                "observations": [
                    {
                        "date": "2026-06-30",
                        "value": "4.20",
                        "series_id": (params or {}).get("series_id"),
                    }
                ]
            }, 23.5
        if "sec.gov" in url:
            return {
                "fields": ["cik", "name", "ticker", "exchange"],
                "data": [[1045810, "NVIDIA CORP", "NVDA", "Nasdaq"]],
            }, 24.5
        raise AssertionError(f"Unexpected URL: {url}")

    def get_text(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[str, float]:
        if "mops.twse.com.tw" not in url:
            raise AssertionError(f"Unexpected URL: {url}")
        return "<html>MOPS official disclosure portal</html>", 25.5


class FailedTransport(FakeTransport):
    def get_json(self, url: str, **kwargs: Any) -> tuple[Any, float]:
        if "stlouisfed" in url:
            raise TimeoutError("FRED unavailable")
        return super().get_json(url, **kwargs)


class FakeScheduler:
    def __init__(self) -> None:
        self.jobs: list[dict[str, Any]] = []
        self.running = False

    def add_job(self, function: Any, trigger: str, **kwargs: Any) -> None:
        self.jobs.append(
            {"function": function, "trigger": trigger, **kwargs}
        )

    def start(self) -> None:
        self.running = True


def registry(transport: Any | None = None) -> LiveProviderRegistry:
    shared = transport or FakeTransport()
    return LiveProviderRegistry(
        (
            TWSEProvider(shared),
            TPExProvider(shared),
            MOPSProvider(shared),
            FREDProvider(shared, api_key="test-key"),
            SECEdgarProvider(
                shared,
                user_agent="Auto Radar test@example.com",
            ),
        )
    )


class RealOceanTests(unittest.TestCase):
    def test_all_official_providers_pass_through_registry(self) -> None:
        fetches = registry().fetch_all()

        self.assertEqual(
            {"TWSE", "TPEX", "MOPS", "FRED", "SEC_EDGAR"},
            {item.source_id for item in fetches},
        )
        self.assertTrue(all(item.ok for item in fetches))
        self.assertTrue(all(item.source_hash for item in fetches))
        self.assertTrue(all(item.latency_ms for item in fetches))

    def test_registry_metadata_contains_no_url_or_secret(self) -> None:
        payload = json.loads(
            (
                REPOSITORY_ROOT
                / "Data/RealOcean/provider_registry.json"
            ).read_text(encoding="utf-8")
        )
        serialized = json.dumps(payload).lower()

        self.assertNotIn('"url"', serialized)
        self.assertNotIn('"endpoint"', serialized)
        self.assertNotIn("test-key", serialized)
        self.assertFalse(payload["runtime_direct_api_access"])

    def test_pipeline_builds_snapshot_v3_and_health(self) -> None:
        result = RealOceanPipeline(registry()).run(
            "taiwan_preopen", generated_at=NOW
        )
        snapshot = result["snapshot"]

        self.assertEqual("2026-07-01-0830", snapshot["version"])
        self.assertEqual(64, len(snapshot["snapshot_hash"]))
        self.assertEqual(5, len(snapshot["source_hash"]))
        self.assertEqual(5, len(snapshot["evidence"]))
        self.assertEqual("healthy", snapshot["market_health"]["overall_status"])
        self.assertFalse(snapshot["runtime_direct_api_access"])
        self.assertEqual(
            [item["stage"] for item in result["stages"]],
            ["fetch", "validate", "normalize", "snapshot", "dashboard"],
        )

    def test_provider_failure_uses_cached_snapshot_without_stopping(self) -> None:
        healthy = RealOceanPipeline(registry()).run(
            "macro", generated_at=NOW
        )["snapshot"]
        result = RealOceanPipeline(registry(FailedTransport())).run(
            "macro",
            generated_at=NOW,
            cached_snapshot=healthy,
        )
        fred = next(
            item
            for item in result["snapshot"]["market_health"]["sources"]
            if item["source_id"] == "FRED"
        )

        self.assertEqual("degraded", fred["health_status"])
        self.assertEqual("cached_snapshot", fred["source_mode"])
        self.assertEqual(
            "degraded",
            result["snapshot"]["market_health"]["overall_status"],
        )

    def test_runtime_never_uses_archived_fixture_directly(self) -> None:
        failed = tuple(
            ProviderFetch(
                source_id=source_id,
                fetched_at=NOW.isoformat(),
                health_status="unavailable",
                latency_ms=None,
                payload=None,
                source_hash=None,
                error="offline",
            )
            for source_id in sorted(
                LiveProviderRegistry.REQUIRED_SOURCE_IDS
            )
        )
        fixture = {
            "provider_payloads": {
                source_id: {"fixture": True}
                for source_id in LiveProviderRegistry.REQUIRED_SOURCE_IDS
            }
        }
        runtime_payloads, runtime_modes = OfficialFallbackPolicy.resolve(
            failed,
            archived_fixture=fixture,
            purpose="runtime",
        )
        replay_payloads, replay_modes = OfficialFallbackPolicy.resolve(
            failed,
            archived_fixture=fixture,
            purpose="replay",
        )

        self.assertTrue(
            all(value is None for value in runtime_payloads.values())
        )
        self.assertNotIn("archived_fixture", runtime_modes.values())
        self.assertTrue(all(replay_payloads.values()))
        self.assertEqual(
            {"archived_fixture"}, set(replay_modes.values())
        )

    def test_scheduler_registers_all_taipei_jobs(self) -> None:
        fake = FakeScheduler()
        scheduler = RealOceanScheduler(
            lambda trigger_id: trigger_id,
            scheduler=fake,  # type: ignore[arg-type]
        )
        scheduler.register()

        self.assertEqual(4, len(fake.jobs))
        self.assertEqual(
            {
                ("us_close", 6, 0),
                ("macro", 7, 0),
                ("taiwan_preopen", 8, 30),
                ("taiwan_close", 15, 10),
            },
            {
                (job["args"][0], job["hour"], job["minute"])
                for job in fake.jobs
            },
        )

    def test_versioned_artifacts_reject_changed_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            writer = ArtifactWriter(temporary_directory)
            pipeline = RealOceanPipeline(
                registry(), artifact_writer=writer
            )
            first = pipeline.run(
                "taiwan_close", generated_at=NOW
            )
            self.assertTrue(first["artifact_paths"]["snapshot"])
            with self.assertRaises(ArtifactWriteError):
                pipeline.run("taiwan_close", generated_at=NOW)

    def test_dashboard_prefers_real_ocean_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            writer = ArtifactWriter(root / "Runtime/Artifacts")
            result = RealOceanPipeline(
                registry(), artifact_writer=writer
            ).run("taiwan_preopen", generated_at=NOW)
            ocean = DashboardDataBuilder(root)._load_living_ocean()

            self.assertEqual(
                "shadow_real_ocean_monitor", ocean["status"]
            )
            self.assertEqual(result["version"], ocean["snapshot_version"])
            self.assertEqual(5, len(ocean["sources"]))
            self.assertTrue(
                all(
                    isinstance(item["latency_ms"], float)
                    for item in ocean["sources"]
                )
            )

    def test_real_ocean_schemas_and_dashboard_labels_exist(self) -> None:
        for name in (
            "global_snapshot_v3.schema.json",
            "provider_health_v2.schema.json",
        ):
            payload = json.loads(
                (
                    REPOSITORY_ROOT / "Schemas/MarketData" / name
                ).read_text(encoding="utf-8")
            )
            self.assertTrue(payload["$schema"])
        javascript = (
            REPOSITORY_ROOT / "Dashboard/app.js"
        ).read_text(encoding="utf-8")
        self.assertIn('FRED: "FRED"', javascript)
        self.assertIn('SEC_EDGAR: "SEC"', javascript)
        self.assertIn("latency_ms", javascript)


if __name__ == "__main__":
    unittest.main()
