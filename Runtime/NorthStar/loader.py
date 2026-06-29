"""Read-only snapshot loader for the North Star Shadow Runtime."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .immutability import deep_freeze, deep_thaw


class RuntimeLoaderError(RuntimeError):
    """Raised when a Runtime snapshot cannot be loaded safely."""


@dataclass(frozen=True, slots=True)
class LoadedSnapshot:
    reference: str
    source_path: Path
    sha256: str
    loaded_at: datetime
    payload: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return deep_thaw(self.payload)


class RuntimeLoader:
    """Load immutable JSON snapshots from explicitly allowed Repository roots."""

    DEFAULT_ALLOWED_ROOTS = (
        "Knowledge",
        "Data",
        "Schemas",
        "Runtime/Repository/index",
    )

    def __init__(
        self,
        repository_root: Path | str,
        *,
        allowed_roots: tuple[str, ...] | None = None,
    ) -> None:
        self.repository_root = Path(repository_root).resolve()
        roots = allowed_roots or self.DEFAULT_ALLOWED_ROOTS
        self.allowed_roots = tuple(
            (self.repository_root / root).resolve() for root in roots
        )

    def load_json(self, reference: str) -> LoadedSnapshot:
        normalized = self._normalize_reference(reference)
        path = (self.repository_root / normalized).resolve()
        self._validate_allowed_path(path)

        if path.suffix.lower() != ".json":
            raise RuntimeLoaderError(
                f"Runtime Loader accepts JSON snapshots only: {reference}"
            )
        if not path.is_file():
            raise RuntimeLoaderError(f"Runtime snapshot does not exist: {reference}")

        try:
            raw = path.read_bytes()
            payload = json.loads(raw.decode("utf-8-sig"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeLoaderError(
                f"Unable to load Runtime snapshot: {reference}"
            ) from exc

        if not isinstance(payload, dict):
            raise RuntimeLoaderError(
                f"Runtime snapshot must contain a JSON object: {reference}"
            )

        return LoadedSnapshot(
            reference=normalized.as_posix(),
            source_path=path,
            sha256=hashlib.sha256(raw).hexdigest(),
            loaded_at=datetime.now(timezone.utc),
            payload=deep_freeze(payload),
        )

    def load_many(self, references: tuple[str, ...]) -> dict[str, LoadedSnapshot]:
        if len(set(references)) != len(references):
            raise RuntimeLoaderError("Runtime snapshot references must be unique")
        return {reference: self.load_json(reference) for reference in references}

    @staticmethod
    def _normalize_reference(reference: str) -> Path:
        if not isinstance(reference, str) or not reference.strip():
            raise RuntimeLoaderError("Runtime snapshot reference must not be empty")
        path = Path(reference.replace("\\", "/"))
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeLoaderError(
                f"Runtime snapshot reference escapes Repository scope: {reference}"
            )
        return path

    def _validate_allowed_path(self, path: Path) -> None:
        if not path.is_relative_to(self.repository_root):
            raise RuntimeLoaderError(
                f"Runtime snapshot is outside Repository: {path}"
            )
        if not any(path.is_relative_to(root) for root in self.allowed_roots):
            raise RuntimeLoaderError(
                f"Runtime snapshot root is not authorized: {path}"
            )
