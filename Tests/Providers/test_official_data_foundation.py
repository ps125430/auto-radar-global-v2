from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from Runtime.Providers import (
    DataProviderRegistry,
    EvidenceNormalizationError,
    MarketSnapshotBuilderV2,
    OceanHealthEngine,
    ProviderRegistryError,
    SnapshotV2Error,
)
from Scripts.Dashboard.build_dashboard_data import DashboardDataBuilder
from Scripts.Providers.build_official_snapshot import build


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = (
    REPOSITORY_ROOT / "Data/OfficialProvider/provider_registry.json"
)
INPUT_PATH = (
    REPOSITORY_ROOT
    / "Data/OfficialProvider/snapshot_input_2026-07-01-AM.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class OfficialDataFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry_payload = load_json(REGISTRY_PATH)
        self.input_payload = load_json(INPUT_PATH)
        self.registry = DataProviderRegistry(self.registry_payload)

    def test_registry_has_all_sources_and_no_network_locations(self) -> None:
        records = self.registry.list()

        self.assertEqual(
            {
                "TWSE",
                "TPEX",
                "MOPS",
                "US_MARKET",
                "MACRO",
                "ETF",
                "NEWS",
            },
            {record["source_id"] for record in records},
        )
        self.assertTrue(
            all(
                record["source_class"] == "official"
                for record in records
                if record["source_id"] != "NEWS"
            )
        )
        serialized = json.dumps(self.registry.export()).lower()
        for forbidden in ('"url"', '"endpoint"', '"api_url"', '"base_url"'):
            self.assertNotIn(forbidden, serialized)
        self.assertFalse(self.registry.export()["runtime_network_access"])

    def test_registry_rejects_url_and_duplicate_source(self) -> None:
        with_url = deepcopy(self.registry_payload)
        with_url["providers"][0]["url"] = "https://invalid.example"
        with self.assertRaisesRegex(
            ProviderRegistryError, "cannot expose network"
        ):
            DataProviderRegistry(with_url)

        duplicate = deepcopy(self.registry_payload)
        duplicate["providers"][1]["source_id"] = "TWSE"
        with self.assertRaisesRegex(
            ProviderRegistryError, "Duplicate source_id"
        ):
            DataProviderRegistry(duplicate)

    def test_snapshot_v2_supports_am_and_pm_versions(self) -> None:
        morning = MarketSnapshotBuilderV2.build(
            self.input_payload, self.registry
        )
        evening_input = deepcopy(self.input_payload)
        evening_input["snapshot_version"] = "2026-07-01-PM"
        evening = MarketSnapshotBuilderV2.build(
            evening_input, self.registry
        )

        self.assertEqual("2026-07-01-AM", morning["snapshot_version"])
        self.assertEqual("2026-07-01-PM", evening["snapshot_version"])
        for section in (
            "us",
            "taiwan",
            "macro",
            "sector",
            "theme",
            "evidence",
            "market_health",
        ):
            self.assertIn(section, morning["global"])
        self.assertFalse(morning["runtime_network_access"])
        self.assertFalse(morning["repository_write_authorized"])

        invalid = deepcopy(self.input_payload)
        invalid["snapshot_version"] = "2026-07-01"
        with self.assertRaisesRegex(
            SnapshotV2Error, "YYYY-MM-DD-AM"
        ):
            MarketSnapshotBuilderV2.build(invalid, self.registry)

    def test_evidence_is_normalized_to_exact_contract(self) -> None:
        snapshot = MarketSnapshotBuilderV2.build(
            self.input_payload, self.registry
        )
        expected_fields = {
            "id",
            "source",
            "timestamp",
            "importance",
            "reliability",
            "region",
            "theme",
            "reference",
        }

        self.assertEqual(7, len(snapshot["global"]["evidence"]))
        self.assertTrue(
            all(
                set(record) == expected_fields
                for record in snapshot["global"]["evidence"]
            )
        )

        excessive_reliability = deepcopy(self.input_payload)
        excessive_reliability["evidence"][-1]["reliability"] = 100
        with self.assertRaisesRegex(
            EvidenceNormalizationError, "exceeds source trust"
        ):
            MarketSnapshotBuilderV2.build(
                excessive_reliability, self.registry
            )

    def test_ocean_health_degrades_without_changing_formal_confidence(self) -> None:
        degraded_registry_payload = deepcopy(self.registry_payload)
        degraded_registry_payload["providers"][0][
            "health_status"
        ] = "unavailable"
        degraded_registry = DataProviderRegistry(degraded_registry_payload)
        snapshot = MarketSnapshotBuilderV2.build(
            self.input_payload, degraded_registry
        )
        health = snapshot["global"]["market_health"]

        self.assertLess(health["health_score"], 100)
        self.assertGreater(
            health["data_confidence_adjustment_candidate"][
                "maximum_reduction_percent"
            ],
            0,
        )
        self.assertFalse(
            health["data_confidence_adjustment_candidate"][
                "applied_to_decision_confidence"
            ]
        )
        self.assertFalse(health["production_authorized"])

    def test_artifacts_are_deterministic_and_replayable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_root = Path(temporary_directory)
            first = build(
                REPOSITORY_ROOT,
                registry_ref=(
                    "Data/OfficialProvider/provider_registry.json"
                ),
                input_ref=(
                    "Data/OfficialProvider/"
                    "snapshot_input_2026-07-01-AM.json"
                ),
                artifact_root=artifact_root,
            )
            second = build(
                REPOSITORY_ROOT,
                registry_ref=(
                    "Data/OfficialProvider/provider_registry.json"
                ),
                input_ref=(
                    "Data/OfficialProvider/"
                    "snapshot_input_2026-07-01-AM.json"
                ),
                artifact_root=artifact_root,
            )

            self.assertEqual(first["snapshot"], second["snapshot"])
            self.assertTrue(first["paths"]["manifest"].is_file())
            self.assertTrue(first["paths"]["snapshot"].is_file())
            manifest = load_json(first["paths"]["manifest"])
            self.assertEqual(7, len(manifest["source_hashes"]))
            self.assertEqual(3, len(manifest["output_hashes"]))

    def test_dashboard_contains_living_ocean_monitor_data(self) -> None:
        payload = DashboardDataBuilder(REPOSITORY_ROOT).build()
        ocean = payload["living_ocean"]

        self.assertEqual(
            "shadow_real_ocean_monitor", ocean["status"]
        )
        self.assertEqual(
            "2026-07-01-MANUAL", ocean["snapshot_version"]
        )
        self.assertEqual(5, len(ocean["sources"]))
        self.assertFalse(ocean["formal_confidence_modified"])
        self.assertFalse(ocean["repository_write_authorized"])

        html = (REPOSITORY_ROOT / "Dashboard/index.html").read_text(
            encoding="utf-8"
        )
        javascript = (REPOSITORY_ROOT / "Dashboard/app.js").read_text(
            encoding="utf-8"
        )
        self.assertIn("官方資料來源監控", html)
        self.assertIn("source-health-grid", html)
        self.assertIn("renderLivingOcean", javascript)
        self.assertIn("正式信心度未修改", javascript)

    def test_new_schemas_are_valid_json_and_preserve_boundaries(self) -> None:
        schema_names = (
            "official_provider_registry.schema.json",
            "normalized_evidence.schema.json",
            "global_snapshot_v2.schema.json",
            "ocean_health.schema.json",
        )
        schemas = [
            load_json(REPOSITORY_ROOT / "Schemas/MarketData" / name)
            for name in schema_names
        ]

        self.assertTrue(all(schema["$schema"] for schema in schemas))
        self.assertFalse(
            schemas[0]["x-runtime"]["network_access"]
        )
        self.assertFalse(
            schemas[0]["x-runtime"]["production_authorized"]
        )
        self.assertEqual(
            False,
            schemas[-1]["properties"][
                "data_confidence_adjustment_candidate"
            ]["properties"]["applied_to_decision_confidence"]["const"],
        )


if __name__ == "__main__":
    unittest.main()
