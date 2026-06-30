"""Build immutable Living Ocean Shadow artifacts from archived input."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from Runtime.Providers import (
    ArtifactWriter,
    DataProviderRegistry,
    MarketSnapshotBuilderV2,
)

ENGINE_SOURCE_REFS = (
    "Runtime/Providers/official_registry.py",
    "Runtime/Providers/evidence_normalizer.py",
    "Runtime/Providers/ocean_health.py",
    "Runtime/Providers/snapshot_v2.py",
    "Scripts/Providers/build_official_snapshot.py",
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object: {path}")
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(
    repository_root: Path,
    *,
    registry_ref: str,
    input_ref: str,
    artifact_root: Path | None = None,
) -> dict[str, Any]:
    registry_path = repository_root / registry_ref
    input_path = repository_root / input_ref
    registry = DataProviderRegistry(_load_json(registry_path))
    snapshot = MarketSnapshotBuilderV2.build(
        _load_json(input_path),
        registry,
    )
    version = snapshot["snapshot_version"]
    health = snapshot["global"]["market_health"]
    evidence = {
        "document_id": f"NORMALIZED-EVIDENCE-{version}",
        "snapshot_version": version,
        "evidence": snapshot["global"]["evidence"],
        "status": "normalized_shadow_evidence",
        "model_impact": "evidence_only_not_production",
        "repository_write_authorized": False,
    }
    writer = ArtifactWriter(
        artifact_root or repository_root / "Runtime/Artifacts"
    )
    prefix = f"OfficialData/{version}"
    paths = {
        "snapshot": writer.write_json(
            f"{prefix}/global_snapshot.json", snapshot
        ),
        "evidence": writer.write_json(
            f"{prefix}/normalized_evidence.json", evidence
        ),
        "health": writer.write_json(
            f"{prefix}/ocean_health.json", health
        ),
    }
    manifest = {
        "document_id": f"LIVING-OCEAN-MANIFEST-{version}",
        "snapshot_version": version,
        "generated_at": snapshot["generated_at"],
        "source_hashes": {
            registry_ref: _sha256(registry_path),
            input_ref: _sha256(input_path),
            **{
                reference: _sha256(repository_root / reference)
                for reference in ENGINE_SOURCE_REFS
            },
        },
        "output_hashes": {
            key: _sha256(path) for key, path in sorted(paths.items())
        },
        "status": "shadow_artifact_manifest",
        "model_impact": "provider_data_only_not_production",
        "repository_write_authorized": False,
    }
    paths["manifest"] = writer.write_json(
        f"{prefix}/manifest.json", manifest
    )
    return {"snapshot": snapshot, "health": health, "paths": paths}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        default="Data/OfficialProvider/provider_registry.json",
    )
    parser.add_argument(
        "--input",
        default="Data/OfficialProvider/snapshot_input_2026-07-01-AM.json",
    )
    args = parser.parse_args()
    result = build(
        REPOSITORY_ROOT,
        registry_ref=args.registry,
        input_ref=args.input,
    )
    print(
        f"Living Ocean snapshot built: "
        f"{result['snapshot']['snapshot_version']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
