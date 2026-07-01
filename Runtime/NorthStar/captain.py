"""Captain Intelligence contracts for Shadow Runtime only."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import Any, Mapping, Sequence


class CaptainRuntimeError(ValueError):
    """Raised when Captain Intelligence input violates its contract."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaptainRuntimeError(f"{field} must not be blank")
    return " ".join(value.split())


def _money(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CaptainRuntimeError(f"{field} must be a non-negative number")
    if value < 0:
        raise CaptainRuntimeError(f"{field} must be a non-negative number")
    return float(value)


def _ratio(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 0 <= value <= 1
    ):
        raise CaptainRuntimeError(f"{field} must be from 0 to 1")
    return float(value)


def _integer(value: Any, field: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise CaptainRuntimeError(
            f"{field} must be an integer >= {minimum}"
        )
    return value


def _timestamp(value: Any, field: str) -> str:
    text = _text(value, field)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CaptainRuntimeError(f"{field} must be an ISO date-time") from exc
    if parsed.tzinfo is None:
        raise CaptainRuntimeError(f"{field} requires timezone")
    return text


def _currency(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_DOWN))


@dataclass(frozen=True, slots=True)
class CaptainProfile:
    profile_id: str
    market: tuple[str, ...]
    budget: float
    risk_profile: str
    holding_period: Mapping[str, int]
    compound_mode: str
    cash_reserve: float
    max_exposure: float
    allocation_policy: Mapping[str, float]
    status: str
    model_impact: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "market": list(self.market),
            "budget": self.budget,
            "risk_profile": self.risk_profile,
            "holding_period": dict(self.holding_period),
            "compound_mode": self.compound_mode,
            "cash_reserve": self.cash_reserve,
            "max_exposure": self.max_exposure,
            "allocation_policy": dict(self.allocation_policy),
            "status": self.status,
            "model_impact": self.model_impact,
        }


class CaptainProfileEngine:
    """Validate authored Captain configuration without adding defaults."""

    RISK_PROFILES = {"conservative", "balanced", "growth", "custom"}
    COMPOUND_MODES = {"off", "review_required", "reinvest_reviewed"}
    STATUS = "shadow_profile"
    MODEL_IMPACT = "captain_context_only_not_production"

    @classmethod
    def load(cls, payload: Mapping[str, Any]) -> CaptainProfile:
        if not isinstance(payload, Mapping):
            raise CaptainRuntimeError("Captain Profile must be an object")
        markets = payload.get("market")
        if (
            not isinstance(markets, Sequence)
            or isinstance(markets, (str, bytes))
            or not markets
        ):
            raise CaptainRuntimeError("market must be a non-empty array")
        market = tuple(_text(item, "market[]") for item in markets)
        if len(set(market)) != len(market):
            raise CaptainRuntimeError("market contains duplicates")

        risk_profile = _text(payload.get("risk_profile"), "risk_profile")
        if risk_profile not in cls.RISK_PROFILES:
            raise CaptainRuntimeError("risk_profile is invalid")
        compound_mode = _text(
            payload.get("compound_mode"), "compound_mode"
        )
        if compound_mode not in cls.COMPOUND_MODES:
            raise CaptainRuntimeError("compound_mode is invalid")

        holding = payload.get("holding_period")
        if not isinstance(holding, Mapping):
            raise CaptainRuntimeError("holding_period must be an object")
        minimum_days = _integer(
            holding.get("minimum_days"),
            "holding_period.minimum_days",
            minimum=1,
        )
        maximum_days = _integer(
            holding.get("maximum_days"),
            "holding_period.maximum_days",
            minimum=minimum_days,
        )

        policy = payload.get("allocation_policy")
        if not isinstance(policy, Mapping):
            raise CaptainRuntimeError("allocation_policy must be an object")
        position_budget_unit = _money(
            policy.get("position_budget_unit"),
            "allocation_policy.position_budget_unit",
        )
        if position_budget_unit <= 0:
            raise CaptainRuntimeError(
                "allocation_policy.position_budget_unit must be > 0"
            )
        risk_budget_ratio = _ratio(
            policy.get("risk_budget_ratio"),
            "allocation_policy.risk_budget_ratio",
        )

        status = _text(payload.get("status"), "status")
        model_impact = _text(payload.get("model_impact"), "model_impact")
        if status != cls.STATUS or model_impact != cls.MODEL_IMPACT:
            raise CaptainRuntimeError(
                "Captain Profile must remain Shadow context only"
            )
        cash_reserve = _ratio(
            payload.get("cash_reserve"), "cash_reserve"
        )
        max_exposure = _ratio(
            payload.get("max_exposure"), "max_exposure"
        )
        if cash_reserve + max_exposure > 1:
            raise CaptainRuntimeError(
                "cash_reserve plus max_exposure cannot exceed 1"
            )
        return CaptainProfile(
            profile_id=_text(payload.get("profile_id"), "profile_id"),
            market=market,
            budget=_money(payload.get("budget"), "budget"),
            risk_profile=risk_profile,
            holding_period={
                "minimum_days": minimum_days,
                "maximum_days": maximum_days,
            },
            compound_mode=compound_mode,
            cash_reserve=cash_reserve,
            max_exposure=max_exposure,
            allocation_policy={
                "position_budget_unit": position_budget_unit,
                "risk_budget_ratio": risk_budget_ratio,
            },
            status=status,
            model_impact=model_impact,
        )


@dataclass(frozen=True, slots=True)
class ShipState:
    ship_state_id: str
    as_of: str
    cash: float
    buying_power: float
    current_holdings: tuple[Mapping[str, Any], ...]
    risk_exposure: float
    estimated_holding_days: int
    mission_status: str
    status: str
    model_impact: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ship_state_id": self.ship_state_id,
            "as_of": self.as_of,
            "cash": self.cash,
            "buying_power": self.buying_power,
            "current_holdings": [dict(item) for item in self.current_holdings],
            "risk_exposure": self.risk_exposure,
            "estimated_holding_days": self.estimated_holding_days,
            "mission_status": self.mission_status,
            "status": self.status,
            "model_impact": self.model_impact,
        }


class ShipStateEngine:
    """Create a serializable, read-only view of My Ship."""

    MISSION_STATUSES = {
        "idle",
        "active",
        "completed",
        "expired",
        "cancelled",
    }

    @classmethod
    def load(cls, payload: Mapping[str, Any]) -> ShipState:
        if not isinstance(payload, Mapping):
            raise CaptainRuntimeError("Ship State must be an object")
        holdings = payload.get("current_holdings")
        if (
            not isinstance(holdings, Sequence)
            or isinstance(holdings, (str, bytes))
        ):
            raise CaptainRuntimeError("current_holdings must be an array")
        normalized_holdings: list[dict[str, Any]] = []
        for index, holding in enumerate(holdings):
            if not isinstance(holding, Mapping):
                raise CaptainRuntimeError(
                    f"current_holdings[{index}] must be an object"
                )
            normalized_holdings.append(dict(holding))
        mission_status = _text(
            payload.get("mission_status"), "mission_status"
        )
        if mission_status not in cls.MISSION_STATUSES:
            raise CaptainRuntimeError("mission_status is invalid")
        status = _text(payload.get("status"), "status")
        model_impact = _text(payload.get("model_impact"), "model_impact")
        if (
            status != "shadow_ship_state"
            or model_impact != "captain_context_only_not_production"
        ):
            raise CaptainRuntimeError(
                "Ship State must remain Shadow context only"
            )
        return ShipState(
            ship_state_id=_text(
                payload.get("ship_state_id"), "ship_state_id"
            ),
            as_of=_timestamp(payload.get("as_of"), "as_of"),
            cash=_money(payload.get("cash"), "cash"),
            buying_power=_money(
                payload.get("buying_power"), "buying_power"
            ),
            current_holdings=tuple(normalized_holdings),
            risk_exposure=_ratio(
                payload.get("risk_exposure"), "risk_exposure"
            ),
            estimated_holding_days=_integer(
                payload.get("estimated_holding_days"),
                "estimated_holding_days",
            ),
            mission_status=mission_status,
            status=status,
            model_impact=model_impact,
        )


class BudgetAllocationEngine:
    """Calculate deploy boundaries from Captain-authored policy only."""

    @classmethod
    def calculate(
        cls,
        profile: CaptainProfile,
        ship_state: ShipState,
    ) -> dict[str, Any]:
        budget = Decimal(str(profile.budget))
        available = min(budget, Decimal(str(ship_state.buying_power)))
        reserve = budget * Decimal(str(profile.cash_reserve))
        exposure_cap = budget * Decimal(str(profile.max_exposure))
        deploy = max(Decimal("0"), min(available - reserve, exposure_cap))
        unit = Decimal(
            str(profile.allocation_policy["position_budget_unit"])
        )
        position_count = int(deploy // unit)
        risk_budget = budget * Decimal(
            str(profile.allocation_policy["risk_budget_ratio"])
        )
        return {
            "allocation_id": f"ALLOCATION-{profile.profile_id}",
            "profile_ref": profile.profile_id,
            "ship_state_ref": ship_state.ship_state_id,
            "budget": _currency(budget),
            "deploy_budget": _currency(deploy),
            "reserve_budget": _currency(reserve),
            "suggested_position_count": position_count,
            "risk_budget": _currency(risk_budget),
            "calculation_basis": {
                "cash_reserve": profile.cash_reserve,
                "max_exposure": profile.max_exposure,
                "position_budget_unit": float(unit),
                "risk_budget_ratio": profile.allocation_policy[
                    "risk_budget_ratio"
                ],
            },
            "selects_securities": False,
            "order_generation": False,
            "status": "shadow_budget_candidate",
            "model_impact": "capital_boundary_only_not_production",
        }


@dataclass(frozen=True, slots=True)
class Mission:
    mission_id: str
    mission_status: str
    mission_window: Mapping[str, str]
    mission_confidence: float | None
    confidence_source: str | None
    mission_expiration: str
    summary: str
    status: str
    model_impact: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "mission_status": self.mission_status,
            "mission_window": dict(self.mission_window),
            "mission_confidence": self.mission_confidence,
            "confidence_source": self.confidence_source,
            "mission_expiration": self.mission_expiration,
            "summary": self.summary,
            "status": self.status,
            "model_impact": self.model_impact,
        }


class MissionEngine:
    """Maintain at most one authored Active Mission in memory."""

    VALID_STATUSES = {
        "draft",
        "active",
        "completed",
        "expired",
        "cancelled",
    }

    def __init__(self) -> None:
        self._missions: dict[str, Mission] = {}

    def create(self, payload: Mapping[str, Any]) -> Mission:
        mission = self._validate(payload)
        if mission.mission_id in self._missions:
            raise CaptainRuntimeError(
                f"Duplicate mission_id: {mission.mission_id}"
            )
        if mission.mission_status == "active" and self.active() is not None:
            raise CaptainRuntimeError(
                "Only one Active Mission may exist per day"
            )
        self._missions[mission.mission_id] = mission
        return mission

    def active(self) -> Mission | None:
        active = [
            mission
            for mission in self._missions.values()
            if mission.mission_status == "active"
        ]
        if len(active) > 1:
            raise CaptainRuntimeError(
                "Mission registry contains multiple Active Missions"
            )
        return active[0] if active else None

    @classmethod
    def _validate(cls, payload: Mapping[str, Any]) -> Mission:
        if not isinstance(payload, Mapping):
            raise CaptainRuntimeError("Mission must be an object")
        mission_status = _text(
            payload.get("mission_status"), "mission_status"
        )
        if mission_status not in cls.VALID_STATUSES:
            raise CaptainRuntimeError("mission_status is invalid")
        window = payload.get("mission_window")
        if not isinstance(window, Mapping):
            raise CaptainRuntimeError("mission_window must be an object")
        starts_at = _timestamp(
            window.get("starts_at"), "mission_window.starts_at"
        )
        ends_at = _timestamp(
            window.get("ends_at"), "mission_window.ends_at"
        )
        if datetime.fromisoformat(
            ends_at.replace("Z", "+00:00")
        ) <= datetime.fromisoformat(starts_at.replace("Z", "+00:00")):
            raise CaptainRuntimeError(
                "mission_window.ends_at must follow starts_at"
            )
        expiration = _timestamp(
            payload.get("mission_expiration"), "mission_expiration"
        )
        confidence = payload.get("mission_confidence")
        if confidence is not None:
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not 0 <= confidence <= 100
            ):
                raise CaptainRuntimeError(
                    "mission_confidence must be null or 0-100"
                )
            confidence = float(confidence)
        confidence_source = payload.get("confidence_source")
        if confidence is not None:
            confidence_source = _text(
                confidence_source, "confidence_source"
            )
        elif confidence_source is not None:
            raise CaptainRuntimeError(
                "confidence_source requires mission_confidence"
            )
        status = _text(payload.get("status"), "status")
        model_impact = _text(payload.get("model_impact"), "model_impact")
        if (
            status != "shadow_mission"
            or model_impact != "mission_context_only_not_production"
        ):
            raise CaptainRuntimeError(
                "Mission must remain Shadow context only"
            )
        return Mission(
            mission_id=_text(payload.get("mission_id"), "mission_id"),
            mission_status=mission_status,
            mission_window={
                "starts_at": starts_at,
                "ends_at": ends_at,
            },
            mission_confidence=confidence,
            confidence_source=confidence_source,
            mission_expiration=expiration,
            summary=_text(payload.get("summary"), "summary"),
            status=status,
            model_impact=model_impact,
        )


class CaptainBriefGenerator:
    """Combine authored Shadow records into one Captain Brief."""

    @staticmethod
    def generate(
        *,
        generated_at: str,
        ocean: Mapping[str, Any],
        north_star: Mapping[str, Any],
        mission: Mission,
        weather: Mapping[str, Any],
        budget: Mapping[str, Any],
        ship_state: ShipState,
        confidence: Mapping[str, Any],
    ) -> dict[str, Any]:
        _timestamp(generated_at, "generated_at")
        if mission.mission_status != "active":
            raise CaptainRuntimeError(
                "Captain Brief requires one Active Mission"
            )
        if budget.get("status") != "shadow_budget_candidate":
            raise CaptainRuntimeError(
                "Captain Brief requires validated Shadow budget"
            )
        return {
            "brief_id": f"CAPTAIN-BRIEF-{mission.mission_id}",
            "title": "Good Morning Captain",
            "generated_at": generated_at,
            "ocean": dict(ocean),
            "north_star": dict(north_star),
            "mission": mission.to_dict(),
            "weather": dict(weather),
            "budget": dict(budget),
            "ship_status": ship_state.to_dict(),
            "confidence": dict(confidence),
            "trading_signal": False,
            "order_generation": False,
            "repository_write_authorized": False,
            "status": "shadow_captain_brief",
            "model_impact": "captain_context_only_not_production",
        }

    @staticmethod
    def render_markdown(brief: Mapping[str, Any]) -> str:
        mission = brief["mission"]
        budget = brief["budget"]
        ship = brief["ship_status"]
        return "\n".join(
            [
                "# Good Morning Captain",
                "",
                f"Generated At: {brief['generated_at']}",
                "Status: Shadow Runtime Only",
                "",
                "## Ocean",
                str(brief["ocean"].get("summary", "等待資料")),
                "",
                "## North Star",
                str(brief["north_star"].get("direction", "等待資料")),
                "",
                "## Mission",
                str(mission["summary"]),
                "",
                "## Weather",
                str(brief["weather"].get("summary", "等待資料")),
                "",
                "## Budget",
                f"Deploy: {budget['deploy_budget']}",
                f"Reserve: {budget['reserve_budget']}",
                f"Risk Budget: {budget['risk_budget']}",
                "",
                "## Ship Status",
                f"Cash: {ship['cash']}",
                f"Buying Power: {ship['buying_power']}",
                "",
                "## Confidence",
                str(brief["confidence"].get("value", "等待驗證")),
                "",
                "Trading Signal: false",
                "Order Generation: false",
            ]
        )
