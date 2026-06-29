"""Dashboard binding for North Star Shadow Runtime output.

The binding maps an already-created Shadow output into a read-only UI
projection. It does not run Runtime engines, calculate scores, or write files.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


class DashboardBindingError(RuntimeError):
    """Raised when Shadow Dashboard data violates the approved boundary."""


WAITING_FOR_SHADOW_RUN = "Waiting for today's shadow run..."


def build_shadow_dashboard_projection(
    *,
    shadow_output: Mapping[str, Any] | None,
    explain_chain: Mapping[str, Any] | None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Return the E-131 through E-135 Dashboard data contract."""

    now = generated_at or datetime.now(timezone.utc)
    output = dict(shadow_output or {})
    chain = dict(explain_chain or {})
    if output and output.get("production_authorized") is not False:
        raise DashboardBindingError("Shadow Dashboard cannot show Production output")
    if output and output.get("trading_signal") is not False:
        raise DashboardBindingError("Shadow Dashboard cannot show trading signals")

    direction = _text(output.get("north_star_direction"))
    captain = _text(output.get("captain_mission"))
    risk = _string_list(output.get("risk"))
    top3 = _string_list(output.get("top3_candidate"))
    forbidden_zone = _string_list(output.get("forbidden_zone"))
    window = _text(output.get("window"))
    chain_id = _text(chain.get("chain_id"))
    nodes = _node_list(chain.get("nodes"))
    edges = _edge_list(chain.get("edges"))
    missing_refs = _string_list(chain.get("missing_refs"))

    status = "Healthy" if output else "Waiting"
    schema_status = "PASS" if output else "WAITING"
    story = _market_story(direction, top3, risk)

    return {
        "contract_version": "1.0",
        "status": "shadow_dashboard_projection",
        "model_impact": "shadow_candidate_not_production",
        "waiting_message": WAITING_FOR_SHADOW_RUN,
        "last_run": _text(output.get("generated_at")) or now.isoformat(),
        "mode": {
            "label": "Shadow Runtime",
            "status": status,
            "schema": schema_status,
            "repository": "Read Only",
            "production_authorized": False,
        },
        "today": {
            "direction": direction or WAITING_FOR_SHADOW_RUN,
            "captain_mission": captain or WAITING_FOR_SHADOW_RUN,
            "market_story": story,
            "daily_brief": _daily_brief(direction, captain, top3, risk),
            "risk_summary": risk or [WAITING_FOR_SHADOW_RUN],
            "window": window or WAITING_FOR_SHADOW_RUN,
            "top3": top3,
            "forbidden_zone": forbidden_zone,
        },
        "timeline": {
            "yesterday": "Waiting for previous shadow run...",
            "today": direction or WAITING_FOR_SHADOW_RUN,
            "tomorrow": "Waiting for next shadow projection...",
        },
        "explain": {
            "chain_id": chain_id or WAITING_FOR_SHADOW_RUN,
            "direction": direction or WAITING_FOR_SHADOW_RUN,
            "decision": _text(output.get("decision_ref")) or WAITING_FOR_SHADOW_RUN,
            "nodes": nodes,
            "edges": edges,
            "missing_refs": missing_refs,
            "layers": _explain_layers(nodes),
        },
    }


def _market_story(direction: str | None, top3: list[str], risk: list[str]) -> str:
    if not direction:
        return WAITING_FOR_SHADOW_RUN
    lead = top3[0] if top3 else "Shadow candidate"
    risk_text = risk[0] if risk else "仍需人工驗證"
    return f"今日 Shadow 方向為 {direction}；第一候選為 {lead}，主要風險是 {risk_text}。"


def _daily_brief(
    direction: str | None,
    captain: str | None,
    top3: list[str],
    risk: list[str],
) -> str:
    if not direction:
        return WAITING_FOR_SHADOW_RUN
    top3_text = ", ".join(top3) if top3 else "no Top3 candidate"
    risk_text = "、".join(risk) if risk else "尚無核准風險摘要"
    mission = captain or "尚無今日航向"
    return f"今日北極星：{direction}。今日航向：{mission}。今日 Top3：{top3_text}。今日風險：{risk_text}。"


def _explain_layers(nodes: list[dict[str, Any]]) -> dict[str, list[str]]:
    layers = {
        "direction": [],
        "decision": [],
        "regime": [],
        "capital_flow": [],
        "evidence": [],
        "repository": [],
    }
    for node in nodes:
        layer = node.get("layer")
        reference = node.get("reference")
        if not isinstance(reference, str):
            continue
        if layer == "decision":
            layers["decision"].append(reference)
        elif layer == "evidence":
            layers["evidence"].append(reference)
        elif layer == "pattern":
            layers["regime"].append(reference)
        elif layer == "experience":
            layers["capital_flow"].append(reference)
        elif layer == "repository":
            layers["repository"].append(reference)
    return layers


def _text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return " ".join(value.split())
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _node_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _edge_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
