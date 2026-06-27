"""Fail-fast Pattern Repository Engine.

This utility scans Pattern JSON records, validates their schema and Case
references, registers unique entities, and generates a deterministic index.
It has no market-runtime or trading authority.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class PatternRepositoryError(RuntimeError):
    """Base error for Pattern Repository failures."""


class PatternValidationError(PatternRepositoryError):
    """Raised when a schema, Pattern, or source Case reference is invalid."""


@dataclass(frozen=True, slots=True)
class Pattern:
    pattern_id: str
    version: str
    status: str
    title: str
    description: str
    source_cases: tuple[str, ...]
    feature_vector: dict[str, Any]
    created_at: str
    updated_at: str
    source_path: Path

    def to_index_record(self) -> dict[str, str]:
        return {
            "id": self.pattern_id,
            "status": self.status,
            "version": self.version,
            "created_at": self.created_at,
        }


class PatternRepository:
    """Repository-only Pattern scanner, validator, registry, and index builder."""

    LIFECYCLE_FOLDERS = (
        "Draft",
        "Candidate",
        "Verified",
        "Deprecated",
        "Archived",
    )

    def __init__(
        self,
        pattern_root: Path | str | None = None,
        schema_path: Path | str | None = None,
        case_index_path: Path | str | None = None,
        index_path: Path | str | None = None,
        *,
        auto_start: bool = True,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.pattern_root = Path(
            pattern_root or repository_root / "Knowledge" / "Pattern"
        )
        self.schema_path = Path(
            schema_path
            or repository_root / "Schemas" / "Pattern" / "pattern.schema.json"
        )
        self.case_index_path = Path(
            case_index_path
            or repository_root / "Runtime" / "Repository" / "index" / "case_index.json"
        )
        self.index_path = Path(index_path or self.pattern_root / "index.json")
        self._schema = self._load_schema()
        self._case_ids = self._load_case_ids()
        self._patterns: dict[str, Pattern] = {}

        if auto_start:
            self.start()

    def start(self) -> None:
        """Scan, validate, register, and index all Patterns as one transaction."""
        pattern_files = self._scan_pattern_files()
        loaded_patterns = [self.load_pattern(path) for path in pattern_files]

        new_registry: dict[str, Pattern] = {}
        for pattern in loaded_patterns:
            if pattern.pattern_id in new_registry:
                first = new_registry[pattern.pattern_id].source_path
                raise PatternValidationError(
                    f"Duplicate Pattern ID {pattern.pattern_id}: "
                    f"{first} and {pattern.source_path}"
                )
            new_registry[pattern.pattern_id] = pattern

        self._patterns = new_registry
        self._build_index()

    def get_pattern(self, pattern_id: str) -> Pattern:
        try:
            return self._patterns[pattern_id]
        except KeyError as exc:
            raise KeyError(f"Pattern not found: {pattern_id}") from exc

    def list_patterns(self) -> list[Pattern]:
        return [self._patterns[pattern_id] for pattern_id in sorted(self._patterns)]

    def load_pattern(self, path: Path | str) -> Pattern:
        pattern_path = Path(path)
        try:
            payload = json.loads(pattern_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PatternValidationError(
                f"Unable to load Pattern JSON: {pattern_path}"
            ) from exc

        self._validate_payload(payload, pattern_path)
        pattern = Pattern(
            pattern_id=payload["pattern_id"],
            version=payload["version"],
            status=payload["status"],
            title=payload["title"],
            description=payload["description"],
            source_cases=tuple(payload["source_cases"]),
            feature_vector=payload["feature_vector"],
            created_at=payload["created_at"],
            updated_at=payload["updated_at"],
            source_path=pattern_path,
        )
        self.validate_pattern(pattern)
        return pattern

    def validate_pattern(self, pattern: Pattern) -> bool:
        missing_cases = sorted(set(pattern.source_cases) - self._case_ids)
        if missing_cases:
            raise PatternValidationError(
                f"{pattern.source_path}: missing source Case(s): "
                f"{', '.join(missing_cases)}"
            )

        expected_folder = pattern.status
        if pattern.source_path.parent.name != expected_folder:
            raise PatternValidationError(
                f"{pattern.source_path}: status {pattern.status} must be stored "
                f"in {expected_folder}/"
            )
        return True

    def _scan_pattern_files(self) -> list[Path]:
        if not self.pattern_root.is_dir():
            raise PatternRepositoryError(
                f"Pattern directory does not exist: {self.pattern_root}"
            )

        missing_folders = [
            name
            for name in self.LIFECYCLE_FOLDERS
            if not (self.pattern_root / name).is_dir()
        ]
        if missing_folders:
            raise PatternRepositoryError(
                f"Missing Pattern lifecycle folders: {', '.join(missing_folders)}"
            )

        return sorted(
            path
            for folder in self.LIFECYCLE_FOLDERS
            for path in (self.pattern_root / folder).glob("*.json")
        )

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PatternValidationError(
                f"Unable to load Pattern schema: {self.schema_path}"
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
            raise PatternValidationError(
                f"Pattern schema missing fields: {', '.join(sorted(missing))}"
            )
        if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            raise PatternValidationError("Pattern schema must use JSON Schema 2020-12")
        if schema["type"] != "object" or schema["additionalProperties"] is not False:
            raise PatternValidationError(
                "Pattern schema must define a closed object"
            )
        if schema["x-repository"].get("model_impact") != (
            "repository_only_not_production"
        ):
            raise PatternValidationError(
                "Pattern schema must remain repository-only"
            )
        return schema

    def _load_case_ids(self) -> set[str]:
        try:
            case_index = json.loads(
                self.case_index_path.read_text(encoding="utf-8-sig")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise PatternValidationError(
                f"Unable to load Case Registry: {self.case_index_path}"
            ) from exc

        cases = case_index.get("cases")
        if not isinstance(cases, list):
            raise PatternValidationError("Case Registry must contain a cases array")

        case_ids: list[str] = []
        for record in cases:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str):
                raise PatternValidationError(
                    "Every Case Registry record must contain a string id"
                )
            case_ids.append(record["id"])
        if len(case_ids) != len(set(case_ids)):
            raise PatternValidationError("Case Registry contains duplicate IDs")
        return set(case_ids)

    def _validate_payload(self, payload: Any, source_path: Path) -> None:
        if not isinstance(payload, dict):
            raise PatternValidationError(f"{source_path}: Pattern must be an object")

        required = set(self._schema["required"])
        missing = required - set(payload)
        if missing:
            raise PatternValidationError(
                f"{source_path}: missing fields: {', '.join(sorted(missing))}"
            )

        if self._schema["additionalProperties"] is False:
            extra = set(payload) - set(self._schema["properties"])
            if extra:
                raise PatternValidationError(
                    f"{source_path}: unexpected fields: {', '.join(sorted(extra))}"
                )

        for field, definition in self._schema["properties"].items():
            if field not in payload:
                continue
            self._validate_value(field, payload[field], definition, source_path)

        if len(payload["source_cases"]) != len(set(payload["source_cases"])):
            raise PatternValidationError(
                f"{source_path}: source_cases must contain unique IDs"
            )

    def _validate_value(
        self,
        field: str,
        value: Any,
        definition: dict[str, Any],
        source_path: Path,
    ) -> None:
        expected_type = definition.get("type")
        type_map = {
            "string": str,
            "array": list,
            "object": dict,
        }
        python_type = type_map.get(expected_type)
        if python_type is None or not isinstance(value, python_type):
            raise PatternValidationError(
                f"{source_path}: {field} must be {expected_type}"
            )

        if expected_type == "string":
            if len(value) < definition.get("minLength", 0):
                raise PatternValidationError(
                    f"{source_path}: {field} must not be empty"
                )
            pattern = definition.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                raise PatternValidationError(
                    f"{source_path}: {field} has an invalid format"
                )
            allowed = definition.get("enum")
            if allowed and value not in allowed:
                raise PatternValidationError(
                    f"{source_path}: invalid {field} {value!r}"
                )
            if definition.get("format") == "date-time":
                self._validate_datetime(field, value, source_path)

        if expected_type == "array":
            if len(value) < definition.get("minItems", 0):
                raise PatternValidationError(
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
            raise PatternValidationError(
                f"{source_path}: {field} must be an ISO 8601 date-time"
            ) from exc

    def _build_index(self) -> None:
        records = [pattern.to_index_record() for pattern in self.list_patterns()]
        payload = {
            "document_id": "AR-PATTERN-REPOSITORY-INDEX-v1",
            "version": "1.0",
            "status": "repository_index",
            "model_impact": "repository_only_not_production",
            "pattern_count": len(records),
            "patterns": records,
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
            raise PatternRepositoryError(
                f"Unable to write Pattern index: {self.index_path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Pattern Repository index.")
    parser.parse_args(list(argv) if argv is not None else None)
    repository = PatternRepository()
    print(f"Registered {len(repository.list_patterns())} Pattern(s).")
    print(f"Index: {repository.index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

