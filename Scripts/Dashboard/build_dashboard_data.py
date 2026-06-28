"""Build a read-only Dashboard projection from approved Repository records."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DashboardDataError(RuntimeError):
    """Raised when a required Repository source cannot be projected safely."""


class DashboardDataBuilder:
    """Project Repository state without calculating strategy or scores."""

    def __init__(
        self,
        repository_root: Path | str | None = None,
        output_path: Path | str | None = None,
        *,
        generated_at: datetime | None = None,
    ) -> None:
        self.repository_root = Path(
            repository_root or Path(__file__).resolve().parents[2]
        )
        self.output_path = Path(
            output_path
            or self.repository_root / "Dashboard" / "dashboard-data.js"
        )
        self.generated_at = generated_at or datetime.now(timezone.utc)

    def build(self) -> dict[str, Any]:
        """Read source records and return one UI-only projection."""
        validation = self._load_json(
            "Runtime/Repository/index/validation_report.json",
            "Global validation report",
        )
        prediction = self._load_latest_json(
            "Knowledge/Daily",
            "prediction.json",
            "latest Daily Prediction",
        )
        market_mind = self._load_latest_json(
            "Knowledge/MarketMind",
            "market_mind.json",
            "latest MarketMind record",
        )
        pattern_registry = self._load_json(
            "Sandbox/PatternDiscovery/pattern_candidate_registry.json",
            "Pattern Candidate Registry",
        )
        review_registry = self._load_json(
            "Sandbox/Review/verified_case_registry.json",
            "Verified Case Registry",
        )
        graph_nodes = self._load_json(
            "Data/KnowledgeGraph/NODES.json", "Knowledge Graph nodes"
        )
        graph_edges = self._load_json(
            "Data/KnowledgeGraph/EDGES.json", "Knowledge Graph edges"
        )

        verified_cases = self._load_verified_cases(review_registry)
        opportunities = self._load_opportunities(
            pattern_registry, verified_cases
        )
        nodes = self._object_array(graph_nodes, "nodes", "Knowledge Graph")
        edges = self._object_array(graph_edges, "edges", "Knowledge Graph")

        unavailable = "Not provided by an approved Repository record."
        strategy_name = self._optional_text(prediction.get("expected_scenario"))
        confidence = prediction.get("prediction_probability")
        if isinstance(confidence, bool) or not isinstance(
            confidence, (int, float)
        ):
            confidence = None
        window = self._optional_text(prediction.get("prediction_window"))
        expected_risks = self._string_array(prediction.get("expected_risk"))

        warnings = self._string_array(validation.get("warnings"))
        repository_status = self._optional_text(
            validation.get("validation_status")
        ) or "UNKNOWN"
        data_gaps = [
            label
            for label, value in (
                ("Daily strategy", strategy_name),
                ("Strategy confidence", confidence),
                ("Strategy window", window),
                ("Macro regime", None),
                ("Sector regime", None),
                ("Micro regime", None),
                ("Capital flow graph", nodes if nodes and edges else None),
                (
                    "Opportunity scores",
                    [
                        item["opportunity_score"]
                        for item in opportunities
                        if item["opportunity_score"] is not None
                    ],
                ),
            )
            if not value
        ]

        return {
            "meta": {
                "generated_at": self.generated_at.isoformat(),
                "mode": "read_only_repository",
                "repository_status": repository_status,
                "validation_errors": self._integer_or_zero(
                    validation.get("total_errors")
                ),
                "validation_warnings": self._integer_or_zero(
                    validation.get("total_warnings")
                ),
                "data_gaps": data_gaps,
                "sources": [
                    "Daily Prediction draft",
                    "MarketMind draft",
                    "Pattern Candidate Registry",
                    "Verified Case Registry",
                    "Evidence Sandbox",
                    "Knowledge Graph",
                    "Global Validation Report",
                ],
            },
            "strategy": {
                "name": strategy_name,
                "confidence": confidence,
                "window": window,
                "why_now": self._optional_text(prediction.get("notes")),
                "status": self._optional_text(prediction.get("status"))
                or "unknown",
                "fallback": unavailable,
            },
            "regime": {
                "macro": None,
                "sector": None,
                "micro": None,
                "market_mood": self._optional_text(
                    market_mind.get("market_mood")
                ),
                "dominant_narrative": self._optional_text(
                    market_mind.get("dominant_narrative")
                ),
                "status": self._optional_text(market_mind.get("status"))
                or "unknown",
                "fallback": unavailable,
            },
            "opportunities": opportunities[:3],
            "capital_flow": {
                "status": "available" if nodes and edges else "not_available",
                "nodes": nodes,
                "edges": edges,
                "message": (
                    None
                    if nodes and edges
                    else "No validated capital-flow nodes or edges are stored."
                ),
            },
            "tactical": {
                "strategy": strategy_name,
                "risk": expected_risks,
                "window": window,
                "watch": [
                    f"{item['id']} · research review required"
                    for item in opportunities[:3]
                ],
                "avoid": [],
                "fallback": unavailable,
            },
            "repository": {
                "pattern_candidates": len(opportunities),
                "verified_cases": len(verified_cases),
                "evidence_records": len(
                    {
                        evidence_id
                        for case in verified_cases.values()
                        for evidence_id in [case["evidence_id"]]
                    }
                ),
                "graph_nodes": len(nodes),
                "graph_edges": len(edges),
                "warnings": warnings,
            },
        }

    def write(self) -> dict[str, Any]:
        """Write a local-file-safe JavaScript data artifact."""
        payload = self.build()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            "window.AUTO_RADAR_DASHBOARD_DATA = "
            + json.dumps(payload, ensure_ascii=False, indent=2)
            + ";\n"
        )
        self.output_path.write_text(content, encoding="utf-8")
        return payload

    def _load_verified_cases(
        self, registry: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        records = self._object_array(
            registry, "verified_cases", "Verified Case Registry"
        )
        if registry.get("verified_case_count") != len(records):
            raise DashboardDataError("Verified Case Registry count mismatch")
        cases: dict[str, dict[str, Any]] = {}
        for record in records:
            case_id = self._required_text(
                record, "verified_case_id", "Verified Case Registry"
            )
            file_value = self._required_text(
                record, "file", "Verified Case Registry"
            )
            case = self._load_json(
                f"Sandbox/Review/{file_value}", f"Verified Case {case_id}"
            )
            if case.get("verified_case_id") != case_id:
                raise DashboardDataError(
                    f"Verified Case reference mismatch: {case_id}"
                )
            evidence_id = self._required_text(
                case, "evidence_id", f"Verified Case {case_id}"
            )
            evidence_path = (
                self.repository_root
                / "Sandbox"
                / "Ingestion"
                / "processed"
                / f"{evidence_id}.md"
            )
            if not evidence_path.is_file():
                raise DashboardDataError(
                    f"Evidence reference is missing: {evidence_id}"
                )
            cases[case_id] = case
        return cases

    def _load_opportunities(
        self,
        registry: dict[str, Any],
        verified_cases: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        records = self._object_array(
            registry,
            "pattern_candidates",
            "Pattern Candidate Registry",
        )
        if registry.get("pattern_candidate_count") != len(records):
            raise DashboardDataError(
                "Pattern Candidate Registry count mismatch"
            )
        opportunities: list[dict[str, Any]] = []
        for record in records:
            pattern_id = self._required_text(
                record,
                "pattern_candidate_id",
                "Pattern Candidate Registry",
            )
            file_value = self._required_text(
                record, "file", "Pattern Candidate Registry"
            )
            pattern = self._load_json(
                f"Sandbox/PatternDiscovery/{file_value}",
                f"Pattern Candidate {pattern_id}",
            )
            source_cases = self._string_array(pattern.get("source_cases"))
            missing_cases = sorted(set(source_cases) - set(verified_cases))
            if missing_cases:
                raise DashboardDataError(
                    f"Pattern {pattern_id} has missing Cases: "
                    + ", ".join(missing_cases)
                )
            evidence_ids = [
                verified_cases[case_id]["evidence_id"]
                for case_id in source_cases
            ]
            pattern_tags = self._string_array(pattern.get("pattern_tags"))
            display_name = (
                pattern_tags[0].replace("_", " ").title()
                if pattern_tags
                else pattern_id
            )
            feature_summary = self._optional_text(
                pattern.get("feature_summary")
            )
            opportunities.append(
                {
                    "id": pattern_id,
                    "name": display_name,
                    "opportunity_score": None,
                    "why_now": feature_summary,
                    "money_flow": None,
                    "window": None,
                    "crowded": None,
                    "risk": (
                        "Pattern Candidate only; human review required."
                    ),
                    "status": self._optional_text(pattern.get("status")),
                    "source_cases": source_cases,
                    "evidence_ids": evidence_ids,
                    "explainability": {
                        "why_score": (
                            "No approved Opportunity Score exists. "
                            "Similarity is intentionally not reused."
                        ),
                        "evidence": evidence_ids,
                        "money": (
                            "No validated money-flow record is linked."
                        ),
                        "history": source_cases,
                        "risk": (
                            "Candidate status; no Production or trading use."
                        ),
                    },
                }
            )
        return sorted(
            opportunities,
            key=lambda item: (
                item["opportunity_score"] is None,
                -(
                    item["opportunity_score"]
                    if item["opportunity_score"] is not None
                    else 0
                ),
                item["id"],
            ),
        )

    def _load_json(self, relative_path: str, context: str) -> dict[str, Any]:
        path = self.repository_root / relative_path
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DashboardDataError(
                f"Unable to read {context}: {path}"
            ) from exc
        if not isinstance(payload, dict):
            raise DashboardDataError(f"{context} must be an object")
        return payload

    def _load_latest_json(
        self, root_relative: str, filename: str, context: str
    ) -> dict[str, Any]:
        root = self.repository_root / root_relative
        candidates = sorted(root.rglob(filename))
        if not candidates:
            raise DashboardDataError(f"No {context} is available")
        latest = candidates[-1]
        return self._load_json(
            latest.relative_to(self.repository_root).as_posix(),
            context,
        )

    @staticmethod
    def _object_array(
        payload: dict[str, Any], field: str, context: str
    ) -> list[dict[str, Any]]:
        records = payload.get(field)
        if not isinstance(records, list) or not all(
            isinstance(item, dict) for item in records
        ):
            raise DashboardDataError(
                f"{context} must contain a {field} array"
            )
        return records

    @staticmethod
    def _string_array(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, str) and item]

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None
        return " ".join(value.split())

    @staticmethod
    def _required_text(
        payload: dict[str, Any], field: str, context: str
    ) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise DashboardDataError(f"{context} is missing {field}")
        return value

    @staticmethod
    def _integer_or_zero(value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            return 0
        return max(0, value)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the read-only Auto Radar Dashboard data."
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    builder = DashboardDataBuilder(output_path=args.output)
    payload = builder.write()
    print(
        "Dashboard data built: "
        f"{len(payload['opportunities'])} Top3 candidate record(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
