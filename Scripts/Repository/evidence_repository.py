"""Fail-fast Evidence Repository.

This utility validates sourced Evidence records and lifecycle placement only.
It does not collect external data, summarize content, or generate Cases.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class EvidenceRepositoryError(RuntimeError):
    """Base error for Evidence Repository failures."""


class EvidenceValidationError(EvidenceRepositoryError):
    """Raised when Evidence, schema, template, or lifecycle is invalid."""


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    source: str
    source_type: str
    published_at: str
    collected_at: str
    title: str
    summary: str
    language: str
    region: str
    symbols: tuple[str, ...]
    tags: tuple[str, ...]
    importance: int
    reliability: int
    status: str
    model_impact: str
    source_path: Path

    def to_registry_record(self, evidence_root: Path) -> dict[str, Any]:
        try:
            source_file = self.source_path.relative_to(evidence_root).as_posix()
        except ValueError:
            source_file = self.source_path.as_posix()
        return {
            "id": self.evidence_id,
            "source": self.source,
            "source_type": self.source_type,
            "published_at": self.published_at,
            "status": self.status,
            "importance": self.importance,
            "reliability": self.reliability,
            "source_file": source_file,
        }


class EvidenceRepository:
    """Evidence parser, validator, lifecycle checker, and Registry builder."""

    FOLDER_STATUS = {
        "incoming": "Incoming",
        "verified": "Verified",
        "rejected": "Rejected",
        "archive": "Archived",
    }
    TEMPLATE_HEADINGS = (
        "## Original Source",
        "## Summary",
        "## Tags",
        "## Symbols",
        "## Evidence Notes",
        "## Validation",
    )

    def __init__(
        self,
        evidence_root: Path | str | None = None,
        schema_path: Path | str | None = None,
        registry_path: Path | str | None = None,
        *,
        auto_start: bool = True,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.evidence_root = Path(
            evidence_root or repository_root / "Knowledge" / "Evidence"
        )
        self.schema_path = Path(
            schema_path
            or repository_root / "Schemas" / "Evidence" / "evidence.schema.json"
        )
        self.registry_path = Path(
            registry_path
            or repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "evidence_registry.json"
        )
        self._schema = self._load_schema()
        self._records: dict[str, EvidenceRecord] = {}

        if auto_start:
            self.start()

    def start(self) -> None:
        """Validate template and all Evidence before replacing the Registry."""
        self.validate_template(self.evidence_root / "TEMPLATE.md")
        files = self._scan_files()
        loaded = [self.load_evidence(path) for path in files]

        registry: dict[str, EvidenceRecord] = {}
        for record in loaded:
            if record.evidence_id in registry:
                first = registry[record.evidence_id].source_path
                raise EvidenceValidationError(
                    f"Duplicate Evidence ID {record.evidence_id}: "
                    f"{first} and {record.source_path}"
                )
            registry[record.evidence_id] = record

        self._records = registry
        self._build_registry()

    def list_evidence(self) -> list[EvidenceRecord]:
        return [self._records[key] for key in sorted(self._records)]

    def get_evidence(self, evidence_id: str) -> EvidenceRecord:
        try:
            return self._records[evidence_id]
        except KeyError as exc:
            raise KeyError(f"Evidence not found: {evidence_id}") from exc

    def validate_template(self, path: Path | str) -> bool:
        template_path = Path(path)
        try:
            content = template_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise EvidenceValidationError(
                f"Unable to read Evidence template: {template_path}"
            ) from exc
        metadata, body = self._parse_front_matter(content, template_path)
        missing = set(self._schema["required"]) - set(metadata)
        if missing:
            raise EvidenceValidationError(
                f"Evidence template missing YAML fields: "
                f"{', '.join(sorted(missing))}"
            )
        for heading in self.TEMPLATE_HEADINGS:
            if heading not in body:
                raise EvidenceValidationError(
                    f"Evidence template missing heading: {heading}"
                )
        return True

    def load_evidence(self, path: Path | str) -> EvidenceRecord:
        evidence_path = Path(path)
        try:
            content = evidence_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise EvidenceValidationError(
                f"Unable to read Evidence record: {evidence_path}"
            ) from exc

        metadata, _ = self._parse_front_matter(content, evidence_path)
        self._validate_payload(metadata, evidence_path)
        record = EvidenceRecord(
            evidence_id=metadata["evidence_id"],
            source=metadata["source"],
            source_type=metadata["source_type"],
            published_at=metadata["published_at"],
            collected_at=metadata["collected_at"],
            title=metadata["title"],
            summary=metadata["summary"],
            language=metadata["language"],
            region=metadata["region"],
            symbols=tuple(metadata["symbols"]),
            tags=tuple(metadata["tags"]),
            importance=metadata["importance"],
            reliability=metadata["reliability"],
            status=metadata["status"],
            model_impact=metadata["model_impact"],
            source_path=evidence_path,
        )
        self.validate_evidence(record)
        return record

    def validate_evidence(self, record: EvidenceRecord) -> bool:
        folder = record.source_path.parent.name
        expected_status = self.FOLDER_STATUS.get(folder)
        if expected_status is None:
            raise EvidenceValidationError(
                f"{record.source_path}: invalid lifecycle folder {folder}"
            )
        if record.status != expected_status:
            raise EvidenceValidationError(
                f"{record.source_path}: status {record.status} must be stored "
                f"in {folder}/"
            )
        return True

    def _scan_files(self) -> list[Path]:
        files: list[Path] = []
        for folder in self.FOLDER_STATUS:
            path = self.evidence_root / folder
            if not path.is_dir():
                raise EvidenceRepositoryError(
                    f"Missing Evidence lifecycle folder: {path}"
                )
            files.extend(sorted(path.glob("*.md")))
        return sorted(files)

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EvidenceValidationError(
                f"Unable to load Evidence schema: {self.schema_path}"
            ) from exc
        required = {
            "$schema",
            "$id",
            "type",
            "additionalProperties",
            "required",
            "properties",
            "x-repository",
        }
        missing = required - set(schema)
        if missing:
            raise EvidenceValidationError(
                f"Evidence schema missing fields: {', '.join(sorted(missing))}"
            )
        if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            raise EvidenceValidationError(
                "Evidence schema must use JSON Schema 2020-12"
            )
        if schema["type"] != "object" or schema["additionalProperties"] is not False:
            raise EvidenceValidationError(
                "Evidence schema must define a closed object"
            )
        if schema["x-repository"].get("model_impact") != (
            "evidence_only_not_production"
        ):
            raise EvidenceValidationError(
                "Evidence schema must remain repository-only"
            )
        return schema

    def _validate_payload(self, payload: dict[str, Any], path: Path) -> None:
        required = set(self._schema["required"])
        missing = required - set(payload)
        if missing:
            raise EvidenceValidationError(
                f"{path}: missing YAML fields: {', '.join(sorted(missing))}"
            )
        extra = set(payload) - set(self._schema["properties"])
        if extra:
            raise EvidenceValidationError(
                f"{path}: unexpected YAML fields: {', '.join(sorted(extra))}"
            )
        for field, definition in self._schema["properties"].items():
            self._validate_value(field, payload[field], definition, path)

    def _validate_value(
        self,
        field: str,
        value: Any,
        definition: dict[str, Any],
        path: Path,
    ) -> None:
        expected_type = definition.get("type")
        if expected_type == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise EvidenceValidationError(
                    f"{path}: {field} must be integer"
                )
            if value < definition.get("minimum", value):
                raise EvidenceValidationError(
                    f"{path}: {field} is below its minimum"
                )
            if value > definition.get("maximum", value):
                raise EvidenceValidationError(
                    f"{path}: {field} is above its maximum"
                )
            return

        if expected_type == "array":
            if not isinstance(value, list) or not all(
                isinstance(item, str) for item in value
            ):
                raise EvidenceValidationError(
                    f"{path}: {field} must be an array of strings"
                )
            if definition.get("uniqueItems") and len(value) != len(set(value)):
                raise EvidenceValidationError(
                    f"{path}: {field} must contain unique values"
                )
            return

        if expected_type != "string" or not isinstance(value, str):
            raise EvidenceValidationError(f"{path}: {field} must be string")
        if len(value) < definition.get("minLength", 0):
            raise EvidenceValidationError(f"{path}: {field} must not be empty")
        pattern = definition.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            raise EvidenceValidationError(
                f"{path}: {field} has an invalid format"
            )
        if "enum" in definition and value not in definition["enum"]:
            raise EvidenceValidationError(
                f"{path}: invalid {field} {value!r}"
            )
        if "const" in definition and value != definition["const"]:
            raise EvidenceValidationError(
                f"{path}: invalid {field} {value!r}"
            )
        if definition.get("format") == "date-time":
            normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
            try:
                datetime.fromisoformat(normalized)
            except ValueError as exc:
                raise EvidenceValidationError(
                    f"{path}: {field} must be an ISO date-time"
                ) from exc

    @classmethod
    def _parse_front_matter(
        cls, content: str, source_path: Path
    ) -> tuple[dict[str, Any], str]:
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            raise EvidenceValidationError(
                f"{source_path}: YAML front matter must start on the first line"
            )
        try:
            end = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == "---"
            )
        except StopIteration as exc:
            raise EvidenceValidationError(
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
                    item = cls._parse_scalar(
                        stripped[2:].strip(), source_path, line_number
                    )
                    if not isinstance(item, str):
                        raise EvidenceValidationError(
                            f"{source_path}:{line_number}: list items must be strings"
                        )
                    if metadata[active_list_key] is None:
                        metadata[active_list_key] = []
                    metadata[active_list_key].append(item)
                    continue
                raise EvidenceValidationError(
                    f"{source_path}:{line_number}: nested YAML is not supported"
                )
            if ":" not in raw_line:
                raise EvidenceValidationError(
                    f"{source_path}:{line_number}: invalid YAML entry"
                )
            key, raw_value = raw_line.split(":", 1)
            key = key.strip()
            if not key or key in metadata:
                raise EvidenceValidationError(
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
        return metadata, "\n".join(lines[end + 1 :]).lstrip("\n")

    @staticmethod
    def _parse_scalar(value: str, source_path: Path, line_number: int) -> Any:
        if value in {"null", "Null", "NULL", "~"}:
            return None
        if re.fullmatch(r"-?[0-9]+", value):
            return int(value)
        if value.startswith(("[", '"')):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise EvidenceValidationError(
                    f"{source_path}:{line_number}: invalid YAML scalar"
                ) from exc
        if value.startswith("'") and value.endswith("'") and len(value) >= 2:
            return value[1:-1].replace("''", "'")
        return value

    def _build_registry(self) -> None:
        records = [
            record.to_registry_record(self.evidence_root)
            for record in self.list_evidence()
        ]
        payload = {
            "document_id": "AR-EVIDENCE-REGISTRY-v1",
            "version": "1.0",
            "status": "repository_index",
            "model_impact": "evidence_only_not_production",
            "evidence_count": len(records),
            "evidence": records,
        }
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.registry_path.with_suffix(
            f"{self.registry_path.suffix}.tmp"
        )
        try:
            temporary_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(self.registry_path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise EvidenceRepositoryError(
                f"Unable to write Evidence Registry: {self.registry_path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Evidence Repository Registry."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    repository = EvidenceRepository()
    print(f"Registered {len(repository.list_evidence())} Evidence record(s).")
    print(f"Registry: {repository.registry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

