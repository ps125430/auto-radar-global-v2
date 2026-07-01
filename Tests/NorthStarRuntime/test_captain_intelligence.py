from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from Runtime.NorthStar import (
    BudgetAllocationEngine,
    CaptainBriefGenerator,
    CaptainProfileEngine,
    CaptainRuntimeError,
    MissionEngine,
    ShipStateEngine,
)
from Scripts.NorthStar.build_captain_brief import build


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = REPOSITORY_ROOT / "Data/Captain/captain_profile.json"
SHIP_PATH = (
    REPOSITORY_ROOT / "Data/Captain/ship_state_2026-07-01.json"
)
MISSION_PATH = (
    REPOSITORY_ROOT / "Data/Captain/mission_2026-07-01.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint(root: Path) -> list[tuple[str, str]]:
    return [
        (
            path.relative_to(root).as_posix(),
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]


class CaptainIntelligenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile_payload = load_json(PROFILE_PATH)
        self.ship_payload = load_json(SHIP_PATH)
        self.mission_payload = load_json(MISSION_PATH)
        self.profile = CaptainProfileEngine.load(self.profile_payload)
        self.ship = ShipStateEngine.load(self.ship_payload)

    def test_captain_profile_loads_all_required_fields(self) -> None:
        profile = self.profile.to_dict()

        for field in (
            "market",
            "budget",
            "risk_profile",
            "holding_period",
            "compound_mode",
            "cash_reserve",
            "max_exposure",
        ):
            self.assertIn(field, profile)
        self.assertEqual(20000.0, profile["budget"])
        self.assertEqual("balanced", profile["risk_profile"])
        self.assertEqual("shadow_profile", profile["status"])

    def test_profile_has_no_runtime_defaults_for_allocation_policy(self) -> None:
        missing = deepcopy(self.profile_payload)
        missing.pop("allocation_policy")
        with self.assertRaisesRegex(
            CaptainRuntimeError, "allocation_policy"
        ):
            CaptainProfileEngine.load(missing)

        invalid = deepcopy(self.profile_payload)
        invalid["cash_reserve"] = 0.5
        invalid["max_exposure"] = 0.6
        with self.assertRaisesRegex(
            CaptainRuntimeError, "cannot exceed 1"
        ):
            CaptainProfileEngine.load(invalid)

    def test_ship_state_is_json_serializable(self) -> None:
        payload = self.ship.to_dict()
        serialized = json.dumps(payload, ensure_ascii=False)

        self.assertIn("SHIP-STATE-20260701-AM", serialized)
        self.assertEqual([], payload["current_holdings"])
        self.assertEqual(0.0, payload["risk_exposure"])
        self.assertEqual("active", payload["mission_status"])

    def test_budget_allocation_uses_profile_policy_and_selects_no_stock(self) -> None:
        allocation = BudgetAllocationEngine.calculate(
            self.profile, self.ship
        )

        self.assertEqual(20000.0, allocation["budget"])
        self.assertEqual(14000.0, allocation["deploy_budget"])
        self.assertEqual(6000.0, allocation["reserve_budget"])
        self.assertEqual(2, allocation["suggested_position_count"])
        self.assertEqual(400.0, allocation["risk_budget"])
        self.assertFalse(allocation["selects_securities"])
        self.assertFalse(allocation["order_generation"])

    def test_budget_changes_only_when_authored_profile_changes(self) -> None:
        changed = deepcopy(self.profile_payload)
        changed["cash_reserve"] = 0.5
        changed["max_exposure"] = 0.5
        changed["allocation_policy"]["position_budget_unit"] = 5000
        changed["allocation_policy"]["risk_budget_ratio"] = 0.01
        allocation = BudgetAllocationEngine.calculate(
            CaptainProfileEngine.load(changed), self.ship
        )

        self.assertEqual(10000.0, allocation["deploy_budget"])
        self.assertEqual(10000.0, allocation["reserve_budget"])
        self.assertEqual(2, allocation["suggested_position_count"])
        self.assertEqual(200.0, allocation["risk_budget"])

    def test_mission_engine_allows_only_one_active_mission(self) -> None:
        engine = MissionEngine()
        mission = engine.create(self.mission_payload)

        self.assertEqual("active", mission.mission_status)
        second = deepcopy(self.mission_payload)
        second["mission_id"] = "MISSION-20260701-002"
        with self.assertRaisesRegex(
            CaptainRuntimeError, "Only one Active Mission"
        ):
            engine.create(second)

    def test_captain_brief_contains_required_sections_and_boundaries(self) -> None:
        mission = MissionEngine().create(self.mission_payload)
        allocation = BudgetAllocationEngine.calculate(
            self.profile, self.ship
        )
        brief = CaptainBriefGenerator.generate(
            generated_at="2026-07-01T08:20:00+08:00",
            ocean={"summary": "Healthy"},
            north_star={"direction": "Shadow Direction"},
            mission=mission,
            weather={"summary": "Neutral"},
            budget=allocation,
            ship_state=self.ship,
            confidence={"value": None, "status": "unavailable"},
        )
        markdown = CaptainBriefGenerator.render_markdown(brief)

        for field in (
            "ocean",
            "north_star",
            "mission",
            "weather",
            "budget",
            "ship_status",
            "confidence",
        ):
            self.assertIn(field, brief)
        for heading in (
            "Good Morning Captain",
            "Ocean",
            "North Star",
            "Mission",
            "Weather",
            "Budget",
            "Ship Status",
            "Confidence",
        ):
            self.assertIn(heading, markdown)
        self.assertFalse(brief["trading_signal"])
        self.assertFalse(brief["order_generation"])
        self.assertFalse(brief["repository_write_authorized"])

    def test_artifact_build_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = build(REPOSITORY_ROOT, artifact_root=root)
            first_fingerprint = fingerprint(root)
            second = build(REPOSITORY_ROOT, artifact_root=root)
            second_fingerprint = fingerprint(root)

            self.assertEqual(first["brief"], second["brief"])
            self.assertEqual(first_fingerprint, second_fingerprint)
            self.assertTrue(first["paths"]["manifest"].is_file())
            manifest = load_json(first["paths"]["manifest"])
            self.assertEqual(7, len(manifest["source_hashes"]))
            self.assertEqual(5, len(manifest["output_hashes"]))

    def test_captain_schemas_are_valid_json_and_shadow_only(self) -> None:
        schemas = [
            load_json(path)
            for path in sorted(
                (REPOSITORY_ROOT / "Schemas/Captain").glob("*.json")
            )
        ]

        self.assertEqual(5, len(schemas))
        self.assertTrue(all(schema["$schema"] for schema in schemas))
        brief_schema = next(
            item for item in schemas if item["title"] == "Captain Brief"
        )
        self.assertFalse(
            brief_schema["x-runtime"]["order_generation"]
        )
        self.assertFalse(
            brief_schema["x-runtime"]["strategy_change"]
        )
        self.assertFalse(
            brief_schema["x-runtime"]["scoring_change"]
        )


if __name__ == "__main__":
    unittest.main()
