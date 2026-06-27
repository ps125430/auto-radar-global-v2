"""Fail-fast Experience Repository Engine.

This utility scans Experience JSON records, validates their schema and source
references, registers unique entities, and generates a deterministic index.
It has no market-runtime or trading authority.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class ExperienceRepositoryError(RuntimeError):
    """Base error for Experience Repository failures."""


class ExperienceValidationError(ExperienceRepositoryError):
    """Raised when an Experience or its source references are invalid."""


@dataclass(frozen=True, slots=True)
class Experience:
    experience_id: str
    version: str
    status: str
    title: str
    description: str
    source_patterns: tuple[str, ...]
    source_cases: tuple[str, ...]
    health: float
    health_state: str
    created_at: str
    updated_at: str
    source_path: Path

    def to_index_record(self) -> dict[str, Any]:
        return {
            "id": self.experience_id,
            "version": self.version,
            "status": self.status,
            "health_state": self.health_state,
            "created_at": self.created_at,
        }


class ExperienceRepository:
    """Experience scanner, validator, registry, and index builder."""

    LIFECYCLE_FOLDERS = (
        "Draft",
        "Candidate",
        "Verified",
        "Deprecated",
        "Archived",
    )

    def __init__(
        self,
        experience_root: Path | str | None = None,
        schema_path: Path | str | None = None,
        pattern_index_path: Path | str | None = None,
        case_index_path: Path | str | None = None,
        index_path: Path | str | None = None,
        *,
        auto_start: bool = True,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.experience_root = Path(
            experience_root or repository_root / "Knowledge" / "Experience"
        )
        self.schema_path = Path(
            schema_path
            or repository_root / "Schemas" / "Experience" / "experience.schema.json"
        )
        self.pattern_index_path = Path(
            pattern_index_path
            or repository_root / "Knowledge" / "Pattern" / "index.json"
        )
        self.case_index_path = Path(
            case_index_path
            or repository_root / "Runtime" / "Repository" / "index" / "case_index.json"
        )
        self.index_path = Path(index_path or self.experience_root / "index.json")
        self._schema = self._load_schema()
        self._pattern_ids = self._load_registry_ids(
            self.pattern_index_path, "patterns", "Pattern"
        )
        self._case_ids = self._load_registry_ids(
            self.case_index_path, "cases", "Case"
        )
        self._experiences: dict[str, Experience] = {}

        if auto_start:
            self.start()

    def start(self) -> None:
        """Scan, validate, register, and index all Experiences atomically."""
        experience_files = self._scan_experience_files()
        loaded_experiences = [
            self.load_experience(path) for path in experience_files
        ]

        new_registry: dict[str, Experience] = {}
        for experience in loaded_experiences:
            if experience.experience_id in new_registry:
                first = new_registry[experience.experience_id].source_path
                raise ExperienceValidationError(
                    f"Duplicate Experience ID {experience.experience_id}: "
                    f"{first} and {experience.source_path}"
                )
            new_registry[experience.experience_id] = experience

        self._experiences = new_registry
        self._build_index()

    def get_experience(self, experience_id: str) -> Experience:
        try:
            return self._experiences[experience_id]
        except KeyError as exc:
            raise KeyError(f"Experience not found: {experience_id}") from exc

    def list_experiences(self) -> list[Experience]:
        return [
            self._experiences[experience_id]
            for experience_id in sorted(self._experiences)
        ]

    def load_experience(self, path: Path | str) -> Experience:
        experience_path = Path(path)
        try:
            payload = json.loads(experience_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExperienceValidationError(
                f"Unable to load Experience JSON: {experience_path}"
            ) from exc

        self._validate_payload(payload, experience_path)
        experience = Experience(
            experience_id=payload["experience_id"],
            version=payload["version"],
            status=payload["status"],
            title=payload["title"],
            description=payload["description"],
            source_patterns=tuple(payload["source_patterns"]),
            source_cases=tuple(payload["source_cases"]),
            health=float(payload["health"]),
            health_state=payload["health_state"],
            created_at=payload["created_at"],
            updated_at=payload["updated_at"],
            source_path=experience_path,
        )
        self.validate_experience(experience)
        return experience

    def validate_experience(self, experience: Experience) -> bool:
        missing_patterns = sorted(
            set(experience.source_patterns) - self._pattern_ids
        )
        if missing_patterns:
            raise ExperienceValidationError(
                f"{experience.source_path}: missing source Pattern(s): "
                f"{', '.join(missing_patterns)}"
            )

        missing_cases = sorted(set(experience.source_cases) - self._case_ids)
        if missing_cases:
            raise ExperienceValidationError(
                f"{experience.source_path}: missing source Case(s): "
                f"{', '.join(missing_cases)}"
            )

        if experience.source_path.parent.name != experience.status:
            raise ExperienceValidationError(
                f"{experience.source_path}: status {experience.status} must be "
                f"stored in {experience.status}/"
            )
        return True

    def _scan_experience_files(self) -> list[Path]:
        if not self.experience_root.is_dir():
            raise ExperienceRepositoryError(
                f"Experience directory does not exist: {self.experience_root}"
            )

        missing_folders = [
            name
            for name in self.LIFECYCLE_FOLDERS
            if not (self.experience_root / name).is_dir()
        ]
        if missing_folders:
            raise ExperienceRepositoryError(
                f"Missing Experience lifecycle folders: {', '.join(missing_folders)}"
            )

        return sorted(
            path
            for folder in self.LIFECYCLE_FOLDERS
            for path in (self.experience_root / folder).glob("*.json")
        )

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExperienceValidationError(
                f"Unable to load Experience schema: {self.schema_path}"
            ) from exc

        required_schema_keys = {
            "$schema",
            "$id",
            "type",
            "additionalProperties",
            "required",
            "properties",
            "x-repository",
        }
        missing = required_schema_keys - set(schema)
        if missing:
            raise ExperienceValidationError(
                f"Experience schema missing fields: {', '.join(sorted(missing))}"
            )
        if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            raise ExperienceValidationError(
                "Experience schema must use JSON Schema 2020-12"
            )
        if schema["type"] != "object" or schema["additionalProperties"] is not False:
            raise ExperienceValidationError(
                "Experience schema must define a closed object"
            )
        if schema["x-repository"].get("model_impact") != (
            "repository_only_not_production"
        ):
            raise ExperienceValidationError(
                "Experience schema must remain repository-only"
            )
        return schema

    @staticmethod
    def _load_registry_ids(
        path: Path, records_key: str, entity_name: str
    ) -> set[str]:
        try:
            registry = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExperienceValidationError(
                f"Unable to load {entity_name} Registry: {path}"
            ) from exc

        records = registry.get(records_key)
        if not isinstance(records, list):
            raise ExperienceValidationError(
                f"{entity_name} Registry must contain a {records_key} array"
            )

        entity_ids: list[str] = []
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str):
                raise ExperienceValidationError(
                    f"Every {entity_name} Registry record must contain a string id"
                )
            entity_ids.append(record["id"])
        if len(entity_ids) != len(set(entity_ids)):
            raise ExperienceValidationError(
                f"{entity_name} Registry contains duplicate IDs"
            )
        return set(entity_ids)

    def _validate_payload(self, payload: Any, source_path: Path) -> None:
        if not isinstance(payload, dict):
            raise ExperienceValidationError(
                f"{source_path}: Experience must be an object"
            )

        required = set(self._schema["required"])
        missing = required - set(payload)
        if missing:
            raise ExperienceValidationError(
                f"{source_path}: missing fields: {', '.join(sorted(missing))}"
            )

        if self._schema["additionalProperties"] is False:
            extra = set(payload) - set(self._schema["properties"])
            if extra:
                raise ExperienceValidationError(
                    f"{source_path}: unexpected fields: {', '.join(sorted(extra))}"
                )

        for field, definition in self._schema["properties"].items():
            if field not in payload:
                continue
            self._validate_value(field, payload[field], definition, source_path)

        for field in ("source_patterns", "source_cases"):
            if len(payload[field]) != len(set(payload[field])):
                raise ExperienceValidationError(
                    f"{source_path}: {field} must contain unique IDs"
                )

    def _validate_value(
        self,
        field: str,
        value: Any,
        definition: dict[str, Any],
        source_path: Path,
    ) -> None:
        expected_type = definition.get("type")
        if expected_type == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ExperienceValidationError(
                    f"{source_path}: {field} must be number"
                )
            if not math.isfinite(value):
                raise ExperienceValidationError(
                    f"{source_path}: {field} must be a finite number"
                )
            minimum = definition.get("minimum")
            maximum = definition.get("maximum")
            if minimum is not None and value < minimum:
                raise ExperienceValidationError(
                    f"{source_path}: {field} must be at least {minimum}"
                )
            if maximum is not None and value > maximum:
                raise ExperienceValidationError(
                    f"{source_path}: {field} must be at most {maximum}"
                )
            return

        type_map = {
            "string": str,
            "array": list,
            "object": dict,
        }
        python_type = type_map.get(expected_type)
        if python_type is None or not isinstance(value, python_type):
            raise ExperienceValidationError(
                f"{source_path}: {field} must be {expected_type}"
            )

        if expected_type == "string":
            if len(value) < definition.get("minLength", 0):
                raise ExperienceValidationError(
                    f"{source_path}: {field} must not be empty"
                )
            pattern = definition.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                raise ExperienceValidationError(
                    f"{source_path}: {field} has an invalid format"
                )
            allowed = definition.get("enum")
            if allowed and value not in allowed:
                raise ExperienceValidationError(
                    f"{source_path}: invalid {field} {value!r}"
                )
            if definition.get("format") == "date-time":
                self._validate_datetime(field, value, source_path)

        if expected_type == "array":
            if len(value) < definition.get("minItems", 0):
                raise ExperienceValidationError(
                    f"{source_path}: {field} has too few items"
                )
            item_definition = definition.get("items", {})
            for index, item in enumerate(value):
                self._validate_value(
                    f"{field}[{index}]",
                    item,
                    item_definition,
                    source_path,
                )

    @staticmethod
    def _validate_datetime(field: str, value: str, source_path: Path) -> None:
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ExperienceValidationError(
                f"{source_path}: {field} must be an ISO 8601 date-time"
            ) from exc

    def _build_index(self) -> None:
        records = [
            experience.to_index_record() for experience in self.list_experiences()
        ]
        payload = {
            "document_id": "AR-EXPERIENCE-REPOSITORY-INDEX-v1",
            "version": "1.0",
            "status": "repository_index",
            "model_impact": "repository_only_not_production",
            "experience_count": len(records),
            "experiences": records,
        }

        temporary_path = self.index_path.with_suffix(f"{self.index_path.suffix}.tmp")
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(self.index_path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise ExperienceRepositoryError(
                f"Unable to write Experience index: {self.index_path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Experience Repository index."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    repository = ExperienceRepository()
    print(f"Registered {len(repository.list_experiences())} Experience(s).")
    print(f"Index: {repository.index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
