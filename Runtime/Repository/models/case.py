"""Case Repository data entities.

These models describe repository records only. They do not expose decision,
prediction, strategy, confidence, or market-runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class CaseStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    TRACKING = "tracking"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class CaseGrade(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    REFERENCE_ONLY = "Reference Only"


@dataclass(frozen=True, slots=True)
class CaseMetadata:
    case_id: str
    title: str
    category: str
    status: CaseStatus
    model_impact: str
    quality_standard_version: str
    theme: str
    tags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CaseQuality:
    novelty: str | None
    evidence_quality: str | None
    prediction_confidence: str | None


@dataclass(frozen=True, slots=True)
class Case:
    metadata: CaseMetadata
    quality: CaseQuality
    grade: CaseGrade | None
    source_path: Path
    body: str
    front_matter: dict[str, Any]

    @property
    def id(self) -> str:
        return self.metadata.case_id

    @property
    def title(self) -> str:
        return self.metadata.title

    @property
    def status(self) -> CaseStatus:
        return self.metadata.status

    def to_index_record(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "grade": self.grade.value if self.grade else None,
            "status": self.status.value,
            "theme": self.metadata.theme,
            "tags": list(self.metadata.tags),
        }

