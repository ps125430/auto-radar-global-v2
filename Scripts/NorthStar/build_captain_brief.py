"""Build the Sprint 10 Shadow Captain Brief artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from Runtime.NorthStar import (
    BudgetAllocationEngine,
    CaptainBriefGenerator,
    CaptainProfileEngine,
    MissionEngine,
    ShipStateEngine,
)
from Runtime.Providers import ArtifactWriter


SOURCE_REFS = (
    "Data/Captain/captain_profile.json",
    "Data/Captain/ship_state_2026-07-01.json",
    "Data/Captain/mission_2026-07-01.json",
    "Data/ShadowInput/sample_real_input_v1.json",
    "Runtime/Artifacts/OfficialData/2026-07-01-AM/ocean_health.json",
    "Runtime/NorthStar/captain.py",
    "Scripts/NorthStar/build_captain_brief.py",
)


def _load_json(root: Path, reference: str) -> dict[str, Any]:
    payload = json.loads((root / reference).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object: {reference}")
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(
    repository_root: Path | str,
    *,
    artifact_root: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    profile = CaptainProfileEngine.load(
        _load_json(root, SOURCE_REFS[0])
    )
    ship_state = ShipStateEngine.load(
        _load_json(root, SOURCE_REFS[1])
    )
    mission_engine = MissionEngine()
    mission = mission_engine.create(_load_json(root, SOURCE_REFS[2]))
    shadow_input = _load_json(root, SOURCE_REFS[3])
    ocean_health = _load_json(root, SOURCE_REFS[4])
    allocation = BudgetAllocationEngine.calculate(profile, ship_state)
    generated_at = "2026-07-01T08:20:00+08:00"
    brief = CaptainBriefGenerator.generate(
        generated_at=generated_at,
        ocean={
            "summary": (
                f"Ocean Health {ocean_health['health_score']}%; "
                f"Evidence {ocean_health['evidence_coverage']}%."
            ),
            "status": ocean_health["overall_status"],
            "snapshot_ref": ocean_health["snapshot_version"],
        },
        north_star={
            "direction": shadow_input["north_star_input"]["direction"],
            "source_ref": SOURCE_REFS[3],
        },
        mission=mission,
        weather={
            "summary": " · ".join(
                shadow_input["market_regime_input"].values()
            ),
            "source_ref": SOURCE_REFS[3],
        },
        budget=allocation,
        ship_state=ship_state,
        confidence={
            "value": None,
            "status": "unavailable",
            "source": "No approved Confidence methodology",
        },
    )
    writer = ArtifactWriter(
        artifact_root or root / "Runtime/Artifacts"
    )
    prefix = "Captain/2026-07-01"
    paths = {
        "budget": writer.write_json(
            f"{prefix}/budget_allocation.json", allocation
        ),
        "mission": writer.write_json(
            f"{prefix}/mission.json", mission.to_dict()
        ),
        "ship_state": writer.write_json(
            f"{prefix}/ship_state.json", ship_state.to_dict()
        ),
        "brief_json": writer.write_json(
            f"{prefix}/captain_brief.json", brief
        ),
        "brief_markdown": writer.write_text(
            f"{prefix}/captain_brief.md",
            CaptainBriefGenerator.render_markdown(brief) + "\n",
        ),
    }
    manifest = {
        "document_id": "CAPTAIN-ARTIFACT-MANIFEST-20260701",
        "generated_at": generated_at,
        "source_hashes": {
            reference: _sha256(root / reference)
            for reference in SOURCE_REFS
        },
        "output_hashes": {
            key: _sha256(path) for key, path in sorted(paths.items())
        },
        "status": "shadow_captain_artifact",
        "model_impact": "captain_context_only_not_production",
        "repository_write_authorized": False,
    }
    paths["manifest"] = writer.write_json(
        f"{prefix}/manifest.json", manifest
    )
    return {
        "profile": profile.to_dict(),
        "ship_state": ship_state.to_dict(),
        "allocation": allocation,
        "mission": mission.to_dict(),
        "brief": brief,
        "paths": paths,
    }


def main() -> int:
    result = build(REPOSITORY_ROOT)
    print(
        "Captain Brief built: "
        f"{result['brief']['brief_id']} / "
        f"deploy {result['allocation']['deploy_budget']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
