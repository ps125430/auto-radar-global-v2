"""Fail-fast Case Repository Engine.

The engine scans Markdown Case files, parses YAML front matter, validates the
approved Case Quality schema candidate, registers unique Cases, and writes a
deterministic repository index. It has no market-runtime authority.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

from .models.case import Case, CaseGrade, CaseMetadata, CaseQuality, CaseStatus


class CaseRepositoryError(RuntimeError):
    """Base error for repository startup and access failures."""


class CaseValidationError(CaseRepositoryError):
    """Raised when a Case or its governing schema is invalid."""


class CaseRepository:
    """Repository-only API for governed Case records."""

    CASE_FILE_PATTERN = re.compile(r"^CASE-\d{3}(?:_[^.]+)?\.md$")
    CASE_ID_PATTERN = re.compile(r"^CASE-\d{3}$")
    NON_PRODUCTION_IMPACTS = {
        "research_only_not_production",
        "review_only_not_production",
        "review_only_not_production_scoring",
    }
    QUALITY_VALUES = {"low", "medium", "high"}

    def __init__(
        self,
        case_root: Path | str | None = None,
        schema_path: Path | str | None = None,
        index_path: Path | str | None = None,
        *,
        auto_start: bool = True,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.case_root = Path(case_root or repository_root / "Knowledge" / "CaseLibrary")
        self.schema_path = Path(
            schema_path
            or repository_root / "Schemas" / "CaseLibrary" / "case_quality.schema.json"
        )
        self.index_path = Path(
            index_path
            or repository_root / "Runtime" / "Repository" / "index" / "case_index.json"
        )
        self._schema = self._load_schema()
        self._cases: dict[str, Case] = {}

        if auto_start:
            self.start()

    def start(self) -> None:
        """Scan, validate, register, and index all Cases as one fail-fast startup."""
        case_files = self._scan_case_files()
        loaded_cases = [self.load_case(path) for path in case_files]

        new_registry: dict[str, Case] = {}
        for case in loaded_cases:
            if case.id in new_registry:
                first = new_registry[case.id].source_path
                raise CaseValidationError(
                    f"Duplicate Case ID {case.id}: {first} and {case.source_path}"
                )
            new_registry[case.id] = case

        self._cases = new_registry
        self._build_index()

    def get_case(self, case_id: str) -> Case:
        """Return one registered Case by exact ID."""
        try:
            return self._cases[case_id]
        except KeyError as exc:
            raise KeyError(f"Case not found: {case_id}") from exc

    def list_cases(self) -> list[Case]:
        """Return all registered Cases ordered by ID."""
        return [self._cases[case_id] for case_id in sorted(self._cases)]

    def find_case(self, query: str) -> list[Case]:
        """Find Cases by ID, title, theme, or tag."""
        normalized = query.strip().casefold()
        if not normalized:
            return self.list_cases()

        matches: list[Case] = []
        for case in self.list_cases():
            searchable = (
                case.id,
                case.title,
                case.metadata.theme,
                *case.metadata.tags,
            )
            if any(normalized in value.casefold() for value in searchable):
                matches.append(case)
        return matches

    def load_case(self, path: Path | str) -> Case:
        """Parse and validate a Case file without registering it."""
        case_path = Path(path)
        try:
            content = case_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise CaseRepositoryError(f"Unable to read Case file: {case_path}") from exc

        front_matter, body = self._parse_front_matter(content, case_path)
        case = self._to_case(front_matter, body, case_path)
        self.validate_case(case)
        return case

    def validate_case(self, case: Case) -> bool:
        """Validate one Case against the Case Quality schema candidate."""
        metadata = case.metadata
        quality = case.quality

        if not self.CASE_ID_PATTERN.fullmatch(metadata.case_id):
            raise CaseValidationError(
                f"{case.source_path}: invalid case_id {metadata.case_id!r}"
            )
        if not metadata.title.strip():
            raise CaseValidationError(f"{case.source_path}: title must not be empty")

        allowed_categories = self._schema_values("case_category")
        if metadata.category not in allowed_categories:
            raise CaseValidationError(
                f"{case.source_path}: case_category must be one of "
                f"{sorted(allowed_categories)}"
            )

        allowed_statuses = self._schema_values("status")
        if metadata.status.value not in allowed_statuses:
            raise CaseValidationError(
                f"{case.source_path}: status must be one of {sorted(allowed_statuses)}"
            )

        if metadata.model_impact not in self.NON_PRODUCTION_IMPACTS:
            raise CaseValidationError(
                f"{case.source_path}: model_impact must remain non-production"
            )

        expected_version = str(self._schema["schema"]["quality_standard_version"])
        if metadata.quality_standard_version != expected_version:
            raise CaseValidationError(
                f"{case.source_path}: quality_standard_version must be "
                f"{expected_version}"
            )

        quality_fields = {
            "novelty": quality.novelty,
            "evidence_quality": quality.evidence_quality,
            "prediction_confidence": quality.prediction_confidence,
        }
        for field, value in quality_fields.items():
            if field not in case.front_matter:
                raise CaseValidationError(
                    f"{case.source_path}: missing YAML field {field}"
                )
            if value is not None and value not in self.QUALITY_VALUES:
                raise CaseValidationError(
                    f"{case.source_path}: {field} must be low, medium, high, or null"
                )

        if not metadata.theme.strip():
            raise CaseValidationError(f"{case.source_path}: theme must not be empty")
        if any(not tag.strip() for tag in metadata.tags):
            raise CaseValidationError(f"{case.source_path}: tags must not contain blanks")

        return True

    def _scan_case_files(self) -> list[Path]:
        if not self.case_root.is_dir():
            raise CaseRepositoryError(
                f"Case Library directory does not exist: {self.case_root}"
            )
        return sorted(
            path
            for path in self.case_root.rglob("*.md")
            if self.CASE_FILE_PATTERN.fullmatch(path.name)
        )

    def _build_index(self) -> None:
        records = [case.to_index_record() for case in self.list_cases()]
        payload = {
            "document_id": "AR-CASE-REPOSITORY-INDEX-v1",
            "version": "1.0",
            "status": "repository_index",
            "model_impact": "repository_only_not_production",
            "case_count": len(records),
            "cases": records,
        }

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.index_path.with_suffix(f"{self.index_path.suffix}.tmp")
        try:
            temporary_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(self.index_path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise CaseRepositoryError(
                f"Unable to write Case index: {self.index_path}"
            ) from exc

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CaseValidationError(
                f"Unable to load Case schema: {self.schema_path}"
            ) from exc

        required_paths = (
            ("status",),
            ("model_impact",),
            ("schema", "case_id"),
            ("schema", "case_title"),
            ("schema", "case_category"),
            ("schema", "status"),
            ("schema", "quality_standard_version"),
            ("schema", "yaml_fields", "novelty"),
            ("schema", "yaml_fields", "evidence_quality"),
            ("schema", "yaml_fields", "prediction_confidence"),
            ("schema", "grade", "quality_grade"),
        )
        for path in required_paths:
            current: Any = schema
            for key in path:
                if not isinstance(current, dict) or key not in current:
                    raise CaseValidationError(
                        f"Case schema is missing {'.'.join(path)}"
                    )
                current = current[key]

        if schema["status"] != "schema_candidate":
            raise CaseValidationError("Case schema status must be schema_candidate")
        if schema["model_impact"] != "research_only_not_production":
            raise CaseValidationError("Case schema must remain research-only")
        return schema

    def _schema_values(self, field: str) -> set[str]:
        definition = self._schema["schema"][field]
        if not isinstance(definition, str) or " / " not in definition:
            raise CaseValidationError(
                f"Case schema field {field} does not define allowed values"
            )
        return {value.strip() for value in definition.split(" / ")}

    def _to_case(
        self,
        front_matter: dict[str, Any],
        body: str,
        source_path: Path,
    ) -> Case:
        required = (
            "case_id",
            "title",
            "case_category",
            "status",
            "model_impact",
            "quality_standard_version",
            "novelty",
            "evidence_quality",
            "prediction_confidence",
            "grade",
            "theme",
            "tags",
        )
        missing = [field for field in required if field not in front_matter]
        if missing:
            raise CaseValidationError(
                f"{source_path}: missing YAML fields: {', '.join(missing)}"
            )

        tags = front_matter["tags"]
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise CaseValidationError(f"{source_path}: tags must be a YAML list")

        try:
            status = CaseStatus(str(front_matter["status"]))
        except ValueError as exc:
            raise CaseValidationError(
                f"{source_path}: invalid status {front_matter['status']!r}"
            ) from exc

        grade_value = front_matter["grade"]
        try:
            grade = CaseGrade(str(grade_value)) if grade_value is not None else None
        except ValueError as exc:
            raise CaseValidationError(
                f"{source_path}: invalid grade {grade_value!r}"
            ) from exc

        quality_values = (
            front_matter["novelty"],
            front_matter["evidence_quality"],
            front_matter["prediction_confidence"],
        )
        if any(value is not None and not isinstance(value, str) for value in quality_values):
            raise CaseValidationError(
                f"{source_path}: quality fields must be strings or null"
            )

        metadata = CaseMetadata(
            case_id=str(front_matter["case_id"]),
            title=str(front_matter["title"]),
            category=str(front_matter["case_category"]),
            status=status,
            model_impact=str(front_matter["model_impact"]),
            quality_standard_version=str(front_matter["quality_standard_version"]),
            theme=str(front_matter["theme"]),
            tags=tuple(tags),
        )
        quality = CaseQuality(
            novelty=front_matter["novelty"],
            evidence_quality=front_matter["evidence_quality"],
            prediction_confidence=front_matter["prediction_confidence"],
        )
        return Case(
            metadata=metadata,
            quality=quality,
            grade=grade,
            source_path=source_path,
            body=body,
            front_matter=front_matter,
        )

    @classmethod
    def _parse_front_matter(
        cls, content: str, source_path: Path
    ) -> tuple[dict[str, Any], str]:
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            raise CaseValidationError(
                f"{source_path}: YAML front matter must start on the first line"
            )

        try:
            end = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == "---"
            )
        except StopIteration as exc:
            raise CaseValidationError(
                f"{source_path}: YAML front matter is not closed"
            ) from exc

        metadata: dict[str, Any] = {}
        active_list_key: str | None = None

        for line_number, raw_line in enumerate(lines[1:end], start=2):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if raw_line.startswith((" ", "\t")):
                if active_list_key and stripped.startswith("- "):
                    item = cls._parse_scalar(stripped[2:].strip(), source_path, line_number)
                    if not isinstance(item, str):
                        raise CaseValidationError(
                            f"{source_path}:{line_number}: list items must be strings"
                        )
                    if metadata[active_list_key] is None:
                        metadata[active_list_key] = []
                    metadata[active_list_key].append(item)
                    continue
                raise CaseValidationError(
                    f"{source_path}:{line_number}: nested YAML mappings are not supported"
                )

            if ":" not in raw_line:
                raise CaseValidationError(
                    f"{source_path}:{line_number}: invalid YAML entry"
                )

            key, raw_value = raw_line.split(":", 1)
            key = key.strip()
            if not key or key in metadata:
                raise CaseValidationError(
                    f"{source_path}:{line_number}: empty or duplicate YAML key"
                )

            value_text = raw_value.strip()
            if not value_text:
                metadata[key] = None
                active_list_key = key
                continue

            value = cls._parse_scalar(value_text, source_path, line_number)
            metadata[key] = value
            active_list_key = key if isinstance(value, list) else None

        body = "\n".join(lines[end + 1 :]).lstrip("\n")
        return metadata, body

    @staticmethod
    def _parse_scalar(value: str, source_path: Path, line_number: int) -> Any:
        if value in {"null", "Null", "NULL", "~"}:
            return None
        if value in {"true", "True", "TRUE"}:
            return True
        if value in {"false", "False", "FALSE"}:
            return False
        if value.startswith(("[", "{", '"')):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise CaseValidationError(
                    f"{source_path}:{line_number}: invalid YAML scalar"
                ) from exc
        if value.startswith("'") and value.endswith("'") and len(value) >= 2:
            return value[1:-1].replace("''", "'")
        return value


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Case Repository index.")
    parser.parse_args(list(argv) if argv is not None else None)
    repository = CaseRepository()
    print(f"Registered {len(repository.list_cases())} Case(s).")
    print(f"Index: {repository.index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
