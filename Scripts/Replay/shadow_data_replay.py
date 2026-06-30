"""Deterministic E-155 Shadow Data Replay orchestrator."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from Runtime.NorthStar import (
    DailyReflection,
    DecisionResidualEngine,
    DecisionSnapshot,
    OutcomeCollector,
    RootCauseAnalyzer,
)
from Runtime.Providers import (
    ArtifactWriter,
    EvidenceCollector,
    MarketSnapshotBuilder,
    MarketSnapshotReader,
    registry_from_payload,
)
from Scripts.Dashboard.build_dashboard_data import DashboardDataBuilder


class ReplayError(RuntimeError):
    """Raised when replay inputs or reproducibility checks fail."""


class ShadowDataReplay:
    """Replay archived Provider data into Shadow review artifacts."""

    DASHBOARD_SOURCE_PATHS = (
        "Runtime/Repository/index/validation_report.json",
        "Knowledge/Daily/2026/2026-06/2026-06-26/prediction.json",
        "Knowledge/MarketMind/2026/2026-06/2026-06-26/market_mind.json",
        "Sandbox/PatternDiscovery/pattern_candidate_registry.json",
        "Sandbox/PatternDiscovery/candidates/PC-001.json",
        "Sandbox/PatternDiscovery/candidates/PC-002.json",
        "Sandbox/PatternDiscovery/candidates/PC-003.json",
        "Sandbox/Review/verified_case_registry.json",
        "Sandbox/Review/verified/VC-101.json",
        "Sandbox/Review/verified/VC-102.json",
        "Sandbox/Review/verified/VC-103.json",
        "Sandbox/Review/verified/VC-104.json",
        "Sandbox/Review/verified/VC-105.json",
        "Sandbox/Ingestion/processed/EV-101.md",
        "Sandbox/Ingestion/processed/EV-102.md",
        "Sandbox/Ingestion/processed/EV-103.md",
        "Sandbox/Ingestion/processed/EV-104.md",
        "Sandbox/Ingestion/processed/EV-105.md",
        "Data/KnowledgeGraph/NODES.json",
        "Data/KnowledgeGraph/EDGES.json",
        "Dashboard/index.html",
        "Dashboard/styles.css",
        "Dashboard/app.js",
    )
    ENGINE_SOURCE_PATHS = (
        "Runtime/Providers/artifacts.py",
        "Runtime/Providers/base.py",
        "Runtime/Providers/evidence.py",
        "Runtime/Providers/models.py",
        "Runtime/Providers/providers.py",
        "Runtime/Providers/quality.py",
        "Runtime/Providers/snapshot.py",
        "Runtime/NorthStar/daily_intelligence.py",
        "Runtime/NorthStar/dashboard_binding.py",
        "Runtime/NorthStar/shadow_quality.py",
        "Scripts/Dashboard/build_dashboard_data.py",
        "Scripts/Replay/shadow_data_replay.py",
    )

    def __init__(
        self,
        repository_root: Path | str,
        *,
        artifact_root: Path | str | None = None,
    ) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.writer = ArtifactWriter(
            artifact_root or self.repository_root / "Runtime/Artifacts"
        )

    def replay(self, fixture_ref: str) -> dict[str, Any]:
        fixture_path = self._data_path(fixture_ref)
        fixture = self._load_json(fixture_path, "Replay fixture")
        replay_date = self._text(fixture.get("replay_date"), "replay_date")
        as_of = self._date_time(fixture.get("as_of"), "as_of")
        replay_id = self._text(fixture.get("replay_id"), "replay_id")
        if fixture.get("status") != "archived_provider_fixture":
            raise ReplayError("Replay fixture status is invalid")
        if fixture.get("model_impact") != "provider_data_only_not_production":
            raise ReplayError("Replay fixture model impact is invalid")

        provider_payload = fixture.get("providers")
        if not isinstance(provider_payload, dict):
            raise ReplayError("Replay fixture providers must be an object")
        registry = registry_from_payload(provider_payload)
        snapshot = MarketSnapshotBuilder().build(
            registry,
            snapshot_date=replay_date,
            as_of=as_of.isoformat(),
        )
        snapshot = MarketSnapshotReader.read(snapshot)
        evidence = EvidenceCollector.collect(snapshot)

        shadow_input_ref = self._text(
            fixture.get("shadow_input_ref"), "shadow_input_ref"
        )
        outcome_ref = self._text(fixture.get("outcome_ref"), "outcome_ref")
        shadow_input_path = self._data_path(shadow_input_ref)
        outcome_path = self._data_path(outcome_ref)
        manual_outcome = self._load_json(outcome_path, "Replay Outcome")

        dashboard = DashboardDataBuilder(
            self.repository_root,
            generated_at=as_of,
            shadow_input_path=shadow_input_ref,
        ).build()
        decision_snapshot = DecisionSnapshot.create(
            dashboard,
            record_date=replay_date,
            generated_at=as_of,
        )
        outcome = OutcomeCollector.collect_manual(
            manual_outcome,
            generated_at=as_of,
        )
        residual = DecisionResidualEngine.calculate(
            decision_snapshot,
            outcome,
            generated_at=as_of,
        )
        root_cause = RootCauseAnalyzer.analyze(
            residual,
            outcome,
            generated_at=as_of,
        )
        reflection = DailyReflection.generate(
            residual,
            root_cause,
            outcome,
            generated_at=as_of,
        )

        prefix = f"Replays/{replay_date}"
        paths = {
            "market_snapshot": self.writer.write_json(
                f"{prefix}/market_snapshot.json",
                snapshot,
            ),
            "evidence": self.writer.write_json(
                f"{prefix}/evidence_collection.json",
                evidence,
            ),
            "dashboard_json": self.writer.write_json(
                f"{prefix}/Dashboard/dashboard-data.json",
                dashboard,
            ),
            "dashboard_js": self.writer.write_text(
                f"{prefix}/Dashboard/dashboard-data.js",
                "window.AUTO_RADAR_DASHBOARD_DATA = "
                + json.dumps(
                    dashboard,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + ";\n",
            ),
            "decision_snapshot": self.writer.write_json(
                f"{prefix}/DailyIntelligence/Snapshots/{replay_date}.json",
                decision_snapshot,
            ),
            "outcome": self.writer.write_json(
                f"{prefix}/DailyIntelligence/Outcomes/{replay_date}.json",
                outcome,
            ),
            "residual": self.writer.write_json(
                f"{prefix}/DailyIntelligence/Residuals/{replay_date}.json",
                residual,
            ),
            "root_cause": self.writer.write_json(
                f"{prefix}/DailyIntelligence/RootCauses/{replay_date}.json",
                root_cause,
            ),
            "reflection": self.writer.write_json(
                f"{prefix}/DailyIntelligence/Reflections/{replay_date}.json",
                reflection,
            ),
        }
        paths.update(self._write_dashboard_assets(prefix))

        input_paths = {
            "fixture": fixture_path,
            "shadow_input": shadow_input_path,
            "outcome": outcome_path,
        }
        input_paths.update(
            {
                f"repository:{relative}": self.repository_root / relative
                for relative in self.DASHBOARD_SOURCE_PATHS
            }
        )
        input_paths.update(
            {
                f"engine:{relative}": self.repository_root / relative
                for relative in self.ENGINE_SOURCE_PATHS
            }
        )
        input_hashes = {
            name: self._file_hash(path)
            for name, path in sorted(input_paths.items())
        }
        output_hashes = {
            name: self._file_hash(path)
            for name, path in sorted(paths.items())
        }
        digest = self._object_hash(
            {
                "replay_id": replay_id,
                "engine_version": fixture.get("engine_version"),
                "input_hashes": input_hashes,
                "output_hashes": output_hashes,
            }
        )
        manifest = {
            "replay_id": replay_id,
            "replay_date": replay_date,
            "as_of": as_of.isoformat(),
            "engine_version": fixture.get("engine_version"),
            "repository_baseline": fixture.get("repository_baseline"),
            "status": "replay_complete",
            "input_hashes": input_hashes,
            "output_hashes": output_hashes,
            "reproducibility_digest": digest,
            "runtime_api_access": False,
            "repository_write_authorized": False,
            "production_authorized": False,
            "trading_signal": False,
            "strategy_change": False,
            "scoring_change": False,
        }
        manifest_path = self.writer.write_json(
            f"{prefix}/replay_manifest.json",
            manifest,
        )
        paths["manifest"] = manifest_path
        return {
            "manifest": manifest,
            "paths": paths,
            "market_snapshot": snapshot,
            "evidence": evidence,
            "dashboard": dashboard,
            "reflection": reflection,
        }

    def _write_dashboard_assets(self, prefix: str) -> dict[str, Path]:
        index = (
            self.repository_root / "Dashboard/index.html"
        ).read_text(encoding="utf-8")
        index = index.replace(
            '<script src="https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js"></script>',
            "<!-- Offline Replay: external icon script intentionally omitted. -->",
        )
        return {
            "dashboard_html": self.writer.write_text(
                f"{prefix}/Dashboard/index.html",
                index,
            ),
            "dashboard_css": self.writer.write_text(
                f"{prefix}/Dashboard/styles.css",
                (self.repository_root / "Dashboard/styles.css").read_text(
                    encoding="utf-8"
                ),
            ),
            "dashboard_app": self.writer.write_text(
                f"{prefix}/Dashboard/app.js",
                (self.repository_root / "Dashboard/app.js").read_text(
                    encoding="utf-8"
                ),
            ),
        }

    def _data_path(self, reference: str) -> Path:
        path = (self.repository_root / reference).resolve()
        data_root = (self.repository_root / "Data").resolve()
        if not path.is_relative_to(data_root) or not path.is_file():
            raise ReplayError(f"Replay input is outside Data or missing: {reference}")
        return path

    @staticmethod
    def _load_json(path: Path, context: str) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ReplayError(f"Unable to load {context}: {path}") from exc
        if not isinstance(payload, dict):
            raise ReplayError(f"{context} must be an object")
        return payload

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ReplayError(f"{field} must not be blank")
        return value.strip()

    @staticmethod
    def _date_time(value: Any, field: str) -> datetime:
        if not isinstance(value, str):
            raise ReplayError(f"{field} must be an ISO date-time")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ReplayError(f"{field} must be an ISO date-time") from exc
        if parsed.tzinfo is None:
            raise ReplayError(f"{field} requires timezone")
        return parsed

    @staticmethod
    def _file_hash(path: Path) -> str:
        if not path.is_file():
            raise ReplayError(f"Replay source is missing: {path}")
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _object_hash(payload: Any) -> str:
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()
