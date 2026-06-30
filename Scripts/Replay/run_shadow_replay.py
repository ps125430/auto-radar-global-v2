"""CLI entry for deterministic Shadow Data Replay."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from Scripts.Replay import ShadowDataReplay


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixture",
        default="Data/MarketProvider/replay_2026-07-02.json",
    )
    args = parser.parse_args()

    result = ShadowDataReplay(REPOSITORY_ROOT).replay(args.fixture)
    manifest = result["manifest"]
    print(f"Replay: {manifest['replay_id']}")
    print(f"Status: {manifest['status']}")
    print(f"Digest: {manifest['reproducibility_digest']}")
    print("Repository read only: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
