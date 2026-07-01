from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from Runtime.Providers import (
    ArtifactWriteError,
    ArtifactWriter,
    DataQualityEngine,
    DataQualityError,
    EvidenceCollector,
    MarketSnapshotBuilder,
    MarketSnapshotReader,
    ProviderRequest,
    registry_from_payload,
)
from Scripts.Replay import ShadowDataReplay


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    REPOSITORY_ROOT / "Data/MarketProvider/replay_2026-07-02.json"
)
AS_OF = "2026-07-02T21:00:00+00:00"


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def raw_records(fixture: dict) -> list[dict]:
    return [
        dict(record)
        for provider_records in fixture["providers"].values()
        for record in provider_records
    ]


def tree_fingerprint(root: Path) -> list[tuple[str, str]]:
    return [
        (
            path.relative_to(root).as_posix(),
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]


class RealDataFoundationTests(unittest.TestCase):
    def test_provider_interface_covers_all_six_adapters(self) -> None:
        fixture = load_fixture()
        registry = registry_from_payload(fixture["providers"])
        collected = registry.collect_all(
            ProviderRequest(snapshot_date="2026-07-02", as_of=AS_OF)
        )

        self.assertEqual(10, len(collected))
        self.assertEqual(
            {"taiwan", "us", "macro", "news", "etf", "mock"},
            {record["provider"] for record in collected},
        )

    def test_provider_layer_contains_no_direct_api_client(self) -> None:
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((REPOSITORY_ROOT / "Runtime/Providers").glob("*.py"))
            if path.name != "live_official.py"
        ).lower()

        for forbidden in (
            "import requests",
            "import yfinance",
            "import httpx",
            "from urllib",
            "import urllib",
        ):
            self.assertNotIn(forbidden, source)

    def test_market_snapshot_contains_all_required_segments(self) -> None:
        fixture = load_fixture()
        snapshot = MarketSnapshotBuilder().build(
            registry_from_payload(fixture["providers"]),
            snapshot_date="2026-07-02",
            as_of=AS_OF,
        )

        self.assertEqual("PASS", snapshot["quality"]["status"])
        self.assertEqual(10, snapshot["record_count"])
        for segment in ("global", "us", "taiwan", "crypto", "macro"):
            self.assertTrue(snapshot[segment])
        self.assertFalse(snapshot["runtime_api_access"])
        self.assertFalse(snapshot["repository_write_authorized"])
        runtime_snapshot = MarketSnapshotReader.read(snapshot)
        self.assertEqual(snapshot, runtime_snapshot)
        self.assertIsNot(snapshot, runtime_snapshot)

    def test_evidence_collector_is_automatic_and_read_only(self) -> None:
        fixture = load_fixture()
        snapshot = MarketSnapshotBuilder().build(
            registry_from_payload(fixture["providers"]),
            snapshot_date="2026-07-02",
            as_of=AS_OF,
        )
        evidence = EvidenceCollector.collect(snapshot)

        self.assertEqual(10, evidence["evidence_count"])
        self.assertFalse(evidence["manual_entry"])
        self.assertFalse(evidence["repository_write_authorized"])
        self.assertTrue(
            all(
                item["evidence_id"].startswith("PROVIDER-")
                for item in evidence["evidence"]
            )
        )

    def test_data_quality_fails_fast_for_all_required_categories(self) -> None:
        fixture = load_fixture()
        baseline = raw_records(fixture)

        cases: list[tuple[str, list[dict], str]] = []
        missing = json.loads(json.dumps(baseline))
        missing[0].pop("source")
        cases.append(("missing", missing, "missing fields"))

        duplicate = json.loads(json.dumps(baseline))
        duplicate.append(dict(duplicate[0]))
        cases.append(("duplicate", duplicate, "Duplicate record_id"))

        invalid = json.loads(json.dumps(baseline))
        invalid[0]["market"] = "INVALID"
        cases.append(("invalid", invalid, "Invalid market"))

        outlier = json.loads(json.dumps(baseline))
        outlier[0]["value"] = 999999
        cases.append(("outlier", outlier, "Outlier value"))

        timestamp = json.loads(json.dumps(baseline))
        timestamp[0]["timestamp"] = "2026-07-03T00:00:00+00:00"
        cases.append(("timestamp", timestamp, "Future timestamp"))

        for name, records, message in cases:
            with self.subTest(name=name):
                with self.assertRaisesRegex(DataQualityError, message):
                    DataQualityEngine.validate(records, as_of=AS_OF)

    def test_artifact_writer_is_whitelisted_and_immutable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            writer = ArtifactWriter(temporary_directory)
            first = writer.write_json("Replays/2026-07-02/test.json", {"a": 1})
            second = writer.write_json("Replays/2026-07-02/test.json", {"a": 1})

            self.assertEqual(first, second)
            with self.assertRaisesRegex(
                ArtifactWriteError, "Immutable artifact conflict"
            ):
                writer.write_json("Replays/2026-07-02/test.json", {"a": 2})
            with self.assertRaisesRegex(ArtifactWriteError, "escaped"):
                writer.write_json("../Knowledge/test.json", {"a": 1})

    def test_shadow_replay_is_byte_identical_and_repository_read_only(self) -> None:
        knowledge_before = tree_fingerprint(REPOSITORY_ROOT / "Knowledge")
        with tempfile.TemporaryDirectory() as temporary_directory:
            replay = ShadowDataReplay(
                REPOSITORY_ROOT,
                artifact_root=temporary_directory,
            )
            first = replay.replay(
                "Data/MarketProvider/replay_2026-07-02.json"
            )
            first_tree = tree_fingerprint(Path(temporary_directory))
            second = replay.replay(
                "Data/MarketProvider/replay_2026-07-02.json"
            )
            second_tree = tree_fingerprint(Path(temporary_directory))

            self.assertEqual(
                first["manifest"]["reproducibility_digest"],
                second["manifest"]["reproducibility_digest"],
            )
            self.assertEqual(first_tree, second_tree)
            self.assertTrue(first["paths"]["dashboard_html"].is_file())
            self.assertTrue(first["paths"]["reflection"].is_file())
            self.assertEqual(
                "AI 基礎建設接力觀察",
                first["dashboard"]["shadow_runtime"]["today"]["direction"],
            )
            self.assertEqual(
                "draft_suggestion_only",
                first["reflection"]["hypothesis_suggestion"]["status"],
            )

        self.assertEqual(
            knowledge_before,
            tree_fingerprint(REPOSITORY_ROOT / "Knowledge"),
        )

    def test_provider_and_snapshot_schemas_are_candidates(self) -> None:
        provider_schema = json.loads(
            (
                REPOSITORY_ROOT
                / "Schemas/Providers/provider_record.schema.json"
            ).read_text(encoding="utf-8")
        )
        snapshot_schema = json.loads(
            (
                REPOSITORY_ROOT
                / "Schemas/MarketData/market_snapshot.schema.json"
            ).read_text(encoding="utf-8")
        )
        evidence_schema = json.loads(
            (
                REPOSITORY_ROOT
                / "Schemas/MarketData/evidence_collection.schema.json"
            ).read_text(encoding="utf-8")
        )
        replay_schema = json.loads(
            (
                REPOSITORY_ROOT
                / "Schemas/MarketData/replay_manifest.schema.json"
            ).read_text(encoding="utf-8")
        )

        self.assertFalse(provider_schema["x-runtime"]["network_access"])
        self.assertFalse(provider_schema["x-runtime"]["production_authorized"])
        self.assertFalse(snapshot_schema["x-runtime"]["scoring_change"])
        self.assertFalse(snapshot_schema["x-runtime"]["production_authorized"])
        self.assertFalse(
            evidence_schema["x-runtime"]["repository_auto_write"]
        )
        self.assertTrue(replay_schema["x-runtime"]["deterministic_replay"])


if __name__ == "__main__":
    unittest.main()
