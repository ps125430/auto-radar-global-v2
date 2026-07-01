"""Run one official-first Real Ocean Shadow refresh."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from Runtime.Providers import (
    ArtifactWriter,
    LiveProviderRegistry,
    RealOceanPipeline,
)


def _latest_snapshot() -> dict | None:
    candidates = sorted(
        (
            REPOSITORY_ROOT / "Runtime/Artifacts/RealOcean"
        ).glob("*/global_snapshot_v3.json")
    )
    if not candidates:
        return None
    return json.loads(candidates[-1].read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trigger",
        choices=tuple(RealOceanPipeline.TRIGGER_SUFFIX),
        default="manual",
    )
    args = parser.parse_args()
    pipeline = RealOceanPipeline(
        LiveProviderRegistry.official(),
        artifact_writer=ArtifactWriter(
            REPOSITORY_ROOT / "Runtime/Artifacts"
        ),
    )
    result = pipeline.run(
        args.trigger,
        generated_at=datetime.now(ZoneInfo("Asia/Taipei")),
        cached_snapshot=_latest_snapshot(),
        purpose="runtime",
    )
    print(
        json.dumps(
            {
                "version": result["version"],
                "status": result["snapshot"]["market_health"][
                    "overall_status"
                ],
                "sources": result["dashboard_health"]["sources"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
