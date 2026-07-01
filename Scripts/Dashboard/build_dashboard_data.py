"""Build a read-only Dashboard projection from approved Repository records."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from Runtime.NorthStar import (
    ShadowInputValidationError,
    ShadowInputValidator,
    build_shadow_dashboard_projection,
)


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
        shadow_input_path: str = (
            "Data/ShadowInput/sample_real_input_v1.json"
        ),
    ) -> None:
        self.repository_root = Path(
            repository_root or Path(__file__).resolve().parents[2]
        )
        self.output_path = Path(
            output_path
            or self.repository_root / "Dashboard" / "dashboard-data.js"
        )
        self.generated_at = generated_at or datetime.now(timezone.utc)
        normalized_shadow_path = Path(
            shadow_input_path.replace("\\", "/")
        )
        if (
            normalized_shadow_path.is_absolute()
            or ".." in normalized_shadow_path.parts
            or not normalized_shadow_path.as_posix().startswith(
                "Data/ShadowInput/"
            )
        ):
            raise DashboardDataError(
                "Shadow input path must remain under Data/ShadowInput"
            )
        self.shadow_input_path = normalized_shadow_path.as_posix()

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
        try:
            shadow_input = ShadowInputValidator.validate(
                self._load_json(
                    self.shadow_input_path,
                    "Shadow Runtime input",
                ),
                repository_root=self.repository_root,
            )
        except ShadowInputValidationError as exc:
            raise DashboardDataError(
                f"Shadow input validation failed: {exc}"
            ) from exc

        verified_cases = self._load_verified_cases(review_registry)
        repository_opportunities = self._load_opportunities(
            pattern_registry, verified_cases
        )
        repository_nodes = self._object_array(
            graph_nodes, "nodes", "Knowledge Graph"
        )
        repository_edges = self._object_array(
            graph_edges, "edges", "Knowledge Graph"
        )
        opportunities = self._build_shadow_opportunities(shadow_input)
        nodes, edges = self._build_shadow_capital_flow(shadow_input)

        unavailable = "等待核准資料建立。"
        north_star_input = shadow_input["north_star_input"]
        regime_input = shadow_input["market_regime_input"]
        strategy_name = self._optional_text(north_star_input.get("direction"))
        confidence = prediction.get("prediction_probability")
        if isinstance(confidence, bool) or not isinstance(
            confidence, (int, float)
        ):
            confidence = None
        window = f"{north_star_input['window_days']} 天"
        expected_risks = self._string_array(shadow_input["risk_input"]["items"])

        warnings = self._string_array(validation.get("warnings"))
        repository_status = {
            "PASS": "通過",
            "FAIL": "未通過",
        }.get(
            self._optional_text(validation.get("validation_status")),
            "未知",
        )
        data_gaps = [
            label
            for label, value in (
                ("今日策略", strategy_name),
                ("策略信心度", confidence),
                ("預估有效天數", window),
                ("總經環境", regime_input.get("macro")),
                ("產業狀態", regime_input.get("sector")),
                ("市場情緒", regime_input.get("micro")),
                ("資金流地圖", nodes if nodes and edges else None),
                (
                    "機會分數",
                    [
                        item["opportunity_score"]
                        for item in opportunities
                        if item["opportunity_score"] is not None
                    ],
                ),
            )
            if not value
        ]

        shadow_output = self._build_shadow_output(
            shadow_input=shadow_input,
            generated_at=self.generated_at,
        )
        explain_chain = self._build_explain_chain(
            shadow_input=shadow_input,
            nodes=nodes,
            generated_at=self.generated_at,
        )
        shadow_runtime = build_shadow_dashboard_projection(
            shadow_output=shadow_output,
            explain_chain=explain_chain,
            generated_at=self.generated_at,
        )
        living_ocean = self._load_living_ocean()

        return {
            "meta": {
                "generated_at": self.generated_at.isoformat(),
                "mode": "知識庫唯讀",
                "repository_status": repository_status,
                "validation_errors": self._integer_or_zero(
                    validation.get("total_errors")
                ),
                "validation_warnings": self._integer_or_zero(
                    validation.get("total_warnings")
                ),
                "data_gaps": data_gaps,
                "sources": [
                    "每日預測草稿",
                    "市場認知草稿",
                    "模式候選清冊",
                    "驗證案例清冊",
                    "證據沙盒",
                    "知識圖譜",
                    "全域驗證報告",
                    "Shadow Runtime 半真實輸入包",
                    "Living Ocean 官方來源快照",
                ],
            },
            "strategy": {
                "name": strategy_name,
                "confidence": confidence,
                "window": window,
                "why_now": self._optional_text(north_star_input.get("why_now")),
                "status": {
                    "draft": "草稿",
                    "candidate": "候選",
                }.get(
                    self._optional_text(prediction.get("status")),
                    "未知",
                ),
                "fallback": unavailable,
            },
            "regime": {
                "macro": self._optional_text(regime_input.get("macro")),
                "sector": self._optional_text(regime_input.get("sector")),
                "micro": self._optional_text(regime_input.get("micro")),
                "market_mood": self._optional_text(
                    market_mind.get("market_mood")
                ),
                "dominant_narrative": self._optional_text(
                    market_mind.get("dominant_narrative")
                ),
                "status": {
                    "draft": "草稿",
                    "candidate": "候選",
                }.get(
                    self._optional_text(market_mind.get("status")),
                    "未知",
                ),
                "fallback": unavailable,
            },
            "opportunities": opportunities[:3],
            "capital_flow": {
                "status": "已有資料" if nodes and edges else "尚無資料",
                "nodes": nodes,
                "edges": edges,
                "message": (
                    None
                    if nodes and edges
                    else "目前尚無已驗證資金流資料。"
                ),
            },
            "tactical": {
                "strategy": strategy_name,
                "risk": expected_risks,
                "window": window,
                "watch": [
                    f"{item['id']} · 等待研究審查"
                    for item in opportunities[:3]
                ],
                "avoid": [],
                "fallback": unavailable,
            },
            "repository": {
                "pattern_candidates": len(repository_opportunities),
                "verified_cases": len(verified_cases),
                "evidence_records": len(
                    {
                        evidence_id
                        for case in verified_cases.values()
                        for evidence_id in [case["evidence_id"]]
                    }
                ),
                "graph_nodes": len(repository_nodes),
                "graph_edges": len(repository_edges),
                "warnings": [
                    "信心度知識庫尚未建立。"
                    if "Confidence Repository" in warning
                    else warning
                    for warning in warnings
                ],
            },
            "shadow_runtime": shadow_runtime,
            "living_ocean": living_ocean,
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
            display_names = {
                "corporate_disclosure": "公司公告訊號",
                "macro_calendar": "總經事件時程",
                "manual_news": "人工新聞樣本",
            }
            why_now_text = {
                "corporate_disclosure": (
                    "公司申報與交易所公告案例符合既定標籤規則。"
                ),
                "macro_calendar": (
                    "總經事件與行事曆案例符合既定標籤規則。"
                ),
                "manual_news": "人工彙整新聞案例符合既定標籤規則。",
            }
            primary_tag = pattern_tags[0] if pattern_tags else ""
            display_name = display_names.get(primary_tag, pattern_id)
            feature_summary = why_now_text.get(
                primary_tag,
                self._optional_text(pattern.get("feature_summary")),
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
                        "模式候選資料，仍需人工審查。"
                    ),
                    "status": {
                        "Candidate": "候選",
                        "Verified": "已驗證",
                    }.get(
                        self._optional_text(pattern.get("status")),
                        "未知",
                    ),
                    "source_cases": source_cases,
                    "evidence_ids": evidence_ids,
                    "explainability": {
                        "why_score": (
                            "目前尚無核准的機會分數，且不會以相似度替代。"
                        ),
                        "evidence": evidence_ids,
                        "money": (
                            "目前尚未連結已驗證的資金流紀錄。"
                        ),
                        "history": source_cases,
                        "risk": (
                            "目前仍為候選狀態，不供正式交易使用。"
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

    def _build_shadow_output(
        self,
        *,
        shadow_input: dict[str, Any],
        generated_at: datetime,
    ) -> dict[str, Any]:
        north_star = shadow_input["north_star_input"]
        timeline = shadow_input["timeline_input"]
        risk = shadow_input["risk_input"]
        top3 = [
            item["theme"] for item in shadow_input["opportunity_input"][:3]
        ]
        return {
            "contract_version": "1.0",
            "shadow_run_id": f"SHADOW-DASHBOARD-{generated_at.strftime('%Y%m%d')}",
            "generated_at": generated_at.isoformat(),
            "status": "shadow_output_only",
            "north_star_direction": north_star["direction"],
            "captain_mission": north_star["captain_mission"],
            "top3_candidate": top3,
            "forbidden_zone": list(risk["forbidden_zones"]),
            "risk": list(risk["items"]),
            "window": f"{north_star['window_days']} 天",
            "why_now": north_star["why_now"],
            "timeline": {
                "yesterday": timeline["yesterday"],
                "today": timeline["today"],
                "tomorrow": timeline["tomorrow_projection"],
            },
            "decision_ref": f"NSD-DASHBOARD-{generated_at.strftime('%Y%m%d')}",
            "formal_decision": False,
            "trading_signal": False,
            "production_authorized": False,
            "model_impact": "shadow_candidate_not_production",
        }

    def _build_explain_chain(
        self,
        *,
        shadow_input: dict[str, Any],
        nodes: list[dict[str, Any]],
        generated_at: datetime,
    ) -> dict[str, Any]:
        evidence_refs = [
            item["evidence_id"]
            for item in shadow_input["evidence_reference_input"]
        ]
        graph_refs = [
            str(node.get("id") or node.get("name"))
            for node in nodes[:5]
            if node.get("id") or node.get("name")
        ]
        layer_nodes = [
            {
                "node_id": "decision:NSD-DASHBOARD",
                "layer": "decision",
                "reference": f"NSD-DASHBOARD-{generated_at.strftime('%Y%m%d')}",
                "available": True,
            },
        ]
        layer_nodes.extend(
            {
                "node_id": f"evidence:{reference}",
                "layer": "evidence",
                "reference": reference,
                "available": True,
            }
            for reference in evidence_refs
        )
        layer_nodes.extend(
            {
                "node_id": f"pattern:market-regime:{index}",
                "layer": "pattern",
                "reference": f"{label}：{reference}",
                "available": True,
            }
            for index, (label, reference) in enumerate(
                (
                    ("總經", shadow_input["market_regime_input"]["macro"]),
                    ("產業", shadow_input["market_regime_input"]["sector"]),
                    ("市場", shadow_input["market_regime_input"]["micro"]),
                ),
                start=1,
            )
        )
        layer_nodes.extend(
            {
                "node_id": f"experience:{reference}",
                "layer": "experience",
                "reference": reference,
                "available": True,
            }
            for reference in graph_refs
        )
        layer_nodes.append(
            {
                "node_id": "repository:dashboard-projection",
                "layer": "repository",
                "reference": "Dashboard/dashboard-data.js",
                "available": True,
            }
        )
        return {
            "chain_id": f"EXPLAIN-DASHBOARD-{generated_at.strftime('%Y%m%d')}",
            "decision_ref": f"NSD-DASHBOARD-{generated_at.strftime('%Y%m%d')}",
            "layer_order": [
                "decision",
                "evidence",
                "pattern",
                "experience",
                "repository",
            ],
            "nodes": layer_nodes,
            "edges": [],
            "missing_layers": [],
            "missing_refs": [],
        }

    def _build_shadow_opportunities(
        self,
        shadow_input: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Map authored Shadow inputs without calculating or sorting scores."""
        return [
            {
                "id": item["id"],
                "name": item["theme"],
                "opportunity_score": item["display_score"],
                "expectation_stars": item["expectation_stars"],
                "score_status": "sample_shadow_input",
                "window": f"{item['window_days']} 天",
                "money_flow": "半真實 Shadow 輸入",
                "risk": item["risk"],
                "crowded": None,
                "why_now": item["why_now"],
                "status": "Shadow 候選",
                "source_cases": [],
                "evidence_ids": list(item["evidence_refs"]),
                "explainability": {
                    "why_score": (
                        "顯示分數來自半真實測試輸入，不是 Runtime 計算結果。"
                    ),
                    "evidence": list(item["evidence_refs"]),
                    "money": "資料流展示用途，尚待人工市場驗證。",
                    "history": [],
                    "risk": item["risk"],
                },
            }
            for item in shadow_input["opportunity_input"][:3]
        ]

    def _build_shadow_capital_flow(
        self,
        shadow_input: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Map the authored flow path into display nodes and edges."""
        flow = shadow_input["capital_flow_input"]
        nodes = [
            {
                "id": f"SHADOW-FLOW-{index:02d}",
                "name": name,
                "category": "Shadow 資金路徑",
                "status": "shadow_input_candidate",
            }
            for index, name in enumerate(flow["path"], start=1)
        ]
        edges = [
            {
                "source": nodes[index]["id"],
                "target": nodes[index + 1]["id"],
                "edge_type": "SHADOW_FLOWS_TO",
                "status": "shadow_input_candidate",
            }
            for index in range(len(nodes) - 1)
        ]
        return nodes, edges

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

    def _load_living_ocean(self) -> dict[str, Any]:
        real_root = self.repository_root / "Runtime/Artifacts/RealOcean"
        real_candidates = sorted(
            real_root.glob("*/global_snapshot_v3.json")
        )
        if real_candidates:
            path = real_candidates[-1]
            snapshot = self._load_json(
                path.relative_to(self.repository_root).as_posix(),
                "Real Ocean Global Snapshot",
            )
            if snapshot.get("status") != "validated_shadow_snapshot_v3":
                raise DashboardDataError(
                    "Real Ocean snapshot is not validated"
                )
            health = snapshot.get("market_health")
            if not isinstance(health, dict):
                raise DashboardDataError(
                    "Real Ocean snapshot is missing market health"
                )
            sources = health.get("sources")
            if not isinstance(sources, list):
                raise DashboardDataError(
                    "Real Ocean health sources must be an array"
                )
            evidence = snapshot.get("evidence")
            evidence_count = len(evidence) if isinstance(evidence, list) else 0
            return {
                "status": "shadow_real_ocean_monitor",
                "snapshot_version": snapshot.get("version"),
                "snapshot_hash": snapshot.get("snapshot_hash"),
                "generated_at": snapshot.get("generated_time"),
                "overall_status": health.get("overall_status"),
                "health_score": round(
                    100
                    * sum(
                        item.get("health_status") == "healthy"
                        for item in sources
                    )
                    / len(sources)
                )
                if sources
                else 0,
                "evidence_coverage": round(
                    100 * evidence_count / len(sources)
                )
                if sources
                else 0,
                "sources": sources,
                "formal_confidence_modified": False,
                "repository_write_authorized": False,
            }

        registry_path = (
            self.repository_root / "Data/RealOcean/provider_registry.json"
        )
        if registry_path.is_file():
            registry = self._load_json(
                "Data/RealOcean/provider_registry.json",
                "Real Ocean Provider Registry",
            )
            providers = registry.get("providers")
            if not isinstance(providers, list):
                raise DashboardDataError(
                    "Real Ocean Provider Registry requires providers"
                )
            return {
                "status": "waiting_for_first_real_ocean_run",
                "snapshot_version": None,
                "snapshot_hash": None,
                "generated_at": None,
                "overall_status": "unavailable",
                "health_score": 0,
                "evidence_coverage": 0,
                "sources": [
                    {
                        "source_id": item.get("source_id"),
                        "health_status": "unavailable",
                        "source_mode": "not_run",
                        "last_update": None,
                        "latency_ms": None,
                    }
                    for item in providers
                    if isinstance(item, dict)
                ],
                "formal_confidence_modified": False,
                "repository_write_authorized": False,
            }

        root = self.repository_root / "Runtime/Artifacts/OfficialData"
        candidates = sorted(root.glob("*/global_snapshot.json"))
        if not candidates:
            return {
                "status": "waiting_for_shadow_snapshot",
                "snapshot_version": None,
                "generated_at": None,
                "overall_status": "waiting",
                "health_score": None,
                "evidence_coverage": None,
                "sources": [],
                "formal_confidence_modified": False,
                "repository_write_authorized": False,
            }
        path = candidates[-1]
        snapshot = self._load_json(
            path.relative_to(self.repository_root).as_posix(),
            "Living Ocean Global Snapshot",
        )
        if snapshot.get("status") != "validated_shadow_snapshot_v2":
            raise DashboardDataError(
                "Living Ocean snapshot is not validated"
            )
        global_data = snapshot.get("global")
        if not isinstance(global_data, dict):
            raise DashboardDataError(
                "Living Ocean snapshot is missing global data"
            )
        health = global_data.get("market_health")
        if not isinstance(health, dict):
            raise DashboardDataError(
                "Living Ocean snapshot is missing market health"
            )
        sources = health.get("sources")
        if not isinstance(sources, list):
            raise DashboardDataError(
                "Living Ocean health sources must be an array"
            )
        return {
            "status": "shadow_data_monitor",
            "snapshot_version": snapshot.get("snapshot_version"),
            "generated_at": snapshot.get("generated_at"),
            "overall_status": health.get("overall_status"),
            "health_score": health.get("health_score"),
            "evidence_coverage": health.get("evidence_coverage"),
            "sources": sources,
            "formal_confidence_modified": bool(
                health.get(
                    "data_confidence_adjustment_candidate", {}
                ).get("applied_to_decision_confidence")
            ),
            "repository_write_authorized": bool(
                snapshot.get("repository_write_authorized")
            ),
        }

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
