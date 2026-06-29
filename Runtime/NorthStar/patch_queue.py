"""In-memory Repository Patch Queue with explicit manager approval."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from typing import Any, Mapping
from uuid import uuid4

from .immutability import deep_freeze, deep_thaw


class PatchQueueError(RuntimeError):
    """Raised when a Patch Queue operation violates governance."""


class PatchStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGE_AUTHORIZED = "merge_authorized"


@dataclass(frozen=True, slots=True)
class PatchQueueEntry:
    patch_id: str
    suggestion: Mapping[str, Any]
    status: PatchStatus
    submitted_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    target_repository: str | None = None
    review_notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "patch_id": self.patch_id,
            "suggestion": deep_thaw(self.suggestion),
            "status": self.status.value,
            "submitted_at": self.submitted_at.isoformat(),
            "reviewed_at": (
                self.reviewed_at.isoformat() if self.reviewed_at else None
            ),
            "reviewed_by": self.reviewed_by,
            "target_repository": self.target_repository,
            "review_notes": self.review_notes,
        }


@dataclass(frozen=True, slots=True)
class MergeAuthorization:
    authorization_id: str
    patch_id: str
    target_repository: str
    authorized_by: str
    authorized_at: datetime
    production_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "patch_id": self.patch_id,
            "target_repository": self.target_repository,
            "authorized_by": self.authorized_by,
            "authorized_at": self.authorized_at.isoformat(),
            "production_authorized": self.production_authorized,
        }


class RepositoryPatchQueue:
    """Queue suggestions; it has no filesystem write or merge implementation."""

    def __init__(self) -> None:
        self._entries: dict[str, PatchQueueEntry] = {}
        self._lock = RLock()

    def enqueue(self, suggestion: Mapping[str, Any]) -> PatchQueueEntry:
        self._validate_suggestion(suggestion)
        patch_id = str(suggestion["suggestion_id"])
        with self._lock:
            if patch_id in self._entries:
                raise PatchQueueError(f"Duplicate Patch ID: {patch_id}")
            entry = PatchQueueEntry(
                patch_id=patch_id,
                suggestion=deep_freeze(suggestion),
                status=PatchStatus.PENDING,
                submitted_at=datetime.now(timezone.utc),
            )
            self._entries[patch_id] = entry
            return entry

    def get(self, patch_id: str) -> PatchQueueEntry:
        try:
            return self._entries[patch_id]
        except KeyError as exc:
            raise PatchQueueError(f"Patch is not queued: {patch_id}") from exc

    def list_entries(self) -> tuple[PatchQueueEntry, ...]:
        return tuple(self._entries[key] for key in sorted(self._entries))

    def review(
        self,
        patch_id: str,
        *,
        repository_manager: str,
        approved: bool,
        target_repository: str | None = None,
        notes: str,
    ) -> PatchQueueEntry:
        if not repository_manager.strip():
            raise PatchQueueError("Repository Manager must be identified")
        if not notes.strip():
            raise PatchQueueError("Patch review notes must not be empty")
        if approved and (
            not isinstance(target_repository, str)
            or not target_repository.strip()
        ):
            raise PatchQueueError(
                "Approved Patch requires an explicit target_repository"
            )

        with self._lock:
            current = self.get(patch_id)
            if current.status is not PatchStatus.PENDING:
                raise PatchQueueError(
                    f"Patch cannot be reviewed from {current.status.value}"
                )
            updated = replace(
                current,
                status=(
                    PatchStatus.APPROVED if approved else PatchStatus.REJECTED
                ),
                reviewed_at=datetime.now(timezone.utc),
                reviewed_by=repository_manager,
                target_repository=target_repository if approved else None,
                review_notes=notes,
            )
            self._entries[patch_id] = updated
            return updated

    def authorize_merge(
        self,
        patch_id: str,
        *,
        repository_manager: str,
    ) -> MergeAuthorization:
        with self._lock:
            current = self.get(patch_id)
            if current.status is not PatchStatus.APPROVED:
                raise PatchQueueError(
                    "Patch must be approved before Merge Authorization"
                )
            if current.reviewed_by != repository_manager:
                raise PatchQueueError(
                    "Only the reviewing Repository Manager may authorize Merge"
                )
            if not current.target_repository:
                raise PatchQueueError("Approved Patch has no target_repository")

            updated = replace(current, status=PatchStatus.MERGE_AUTHORIZED)
            self._entries[patch_id] = updated
            return MergeAuthorization(
                authorization_id=f"MERGE-AUTH-{uuid4()}",
                patch_id=patch_id,
                target_repository=current.target_repository,
                authorized_by=repository_manager,
                authorized_at=datetime.now(timezone.utc),
            )

    @staticmethod
    def _validate_suggestion(suggestion: Mapping[str, Any]) -> None:
        required = {
            "suggestion_id",
            "suggestion_type",
            "generated_at",
            "source_refs",
            "description",
            "uncertainty",
            "validation_required",
            "target_repository",
            "status",
            "production_authorized",
        }
        missing = sorted(required - set(suggestion))
        if missing:
            raise PatchQueueError(
                f"Patch suggestion is missing fields: {', '.join(missing)}"
            )
        if suggestion["status"] != "candidate":
            raise PatchQueueError("Patch suggestion must have candidate status")
        if suggestion["target_repository"] is not None:
            raise PatchQueueError(
                "Runtime suggestion target_repository must start as null"
            )
        if suggestion["validation_required"] is not True:
            raise PatchQueueError("Patch suggestion must require validation")
        if suggestion["production_authorized"] is not False:
            raise PatchQueueError("Patch suggestion cannot authorize Production")
