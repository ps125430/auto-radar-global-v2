"""Idempotent writer limited to Runtime/Artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ArtifactWriteError(RuntimeError):
    """Raised when a Runtime artifact write violates its whitelist."""


class ArtifactWriter:
    """Write immutable or byte-identical replay artifacts only."""

    def __init__(self, artifact_root: Path | str) -> None:
        self.artifact_root = Path(artifact_root).resolve()

    def write_json(self, relative_path: str, payload: Any) -> Path:
        content = (
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
            + "\n"
        )
        return self.write_text(relative_path, content)

    def write_text(self, relative_path: str, content: str) -> Path:
        if not isinstance(content, str):
            raise ArtifactWriteError("Artifact content must be text")
        destination = (self.artifact_root / relative_path).resolve()
        if not destination.is_relative_to(self.artifact_root):
            raise ArtifactWriteError("Artifact path escaped Runtime/Artifacts")
        if destination.exists():
            existing = destination.read_text(encoding="utf-8")
            if existing != content:
                raise ArtifactWriteError(
                    f"Immutable artifact conflict: {relative_path}"
                )
            return destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        return destination
