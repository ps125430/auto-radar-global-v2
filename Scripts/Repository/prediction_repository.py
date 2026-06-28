"""Fail-fast Prediction Snapshot Repository.

This utility validates Snapshot metadata and repository references only. It
does not generate signals, decisions, confidence, or trading behavior.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


class PredictionRepositoryError(RuntimeError):
    """Base error for Prediction Repository failures."""


class PredictionValidationError(PredictionRepositoryError):
    """Raised when a Snapshot, template, schema, or reference is invalid."""


@dataclass(frozen=True, slots=True)
class PredictionSnapshot:
    prediction_id: str
    prediction_date: str
    generated_at: str
    state: str
    market: str
    playbook_refs: tuple[str, ...]
    experience_refs: tuple[str, ...]
    pattern_refs: tuple[str, ...]
    confidence_ref: str | None
    decision_status: str
    model_impact: str
    status: str
    source_path: Path
    body: str

    def to_registry_record(self, prediction_root: Path) -> dict[str, Any]:
        try:
            source_file = self.source_path.relative_to(prediction_root).as_posix()
        except ValueError:
            source_file = self.source_path.as_posix()
        return {
            "id": self.prediction_id,
            "prediction_date": self.prediction_date,
            "generated_at": self.generated_at,
            "state": self.state,
            "market": self.market,
            "status": self.status,
            "source_file": source_file,
        }


class PredictionRepository:
    """Snapshot scanner, validator, reference checker, and registry builder."""

    TEMPLATE_HEADINGS = (
        "## Prediction Summary",
        "## Evidence Summary",
        "## Referenced Entities",
        "## Validation",
        "## Notes",
    )

    def __init__(
        self,
        prediction_root: Path | str | None = None,
        schema_path: Path | str | None = None,
        registry_path: Path | str | None = None,
        playbook_index_path: Path | str | None = None,
        experience_index_path: Path | str | None = None,
        pattern_index_path: Path | str | None = None,
        *,
        auto_start: bool = True,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.prediction_root = Path(
            prediction_root or repository_root / "Knowledge" / "Prediction"
        )
        self.schema_path = Path(
            schema_path
            or repository_root / "Schemas" / "Prediction" / "prediction.schema.json"
        )
        self.registry_path = Path(
            registry_path
            or repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "prediction_registry.json"
        )
        self.playbook_index_path = Path(
            playbook_index_path
            or repository_root / "Knowledge" / "Playbook" / "index.json"
        )
        self.experience_index_path = Path(
            experience_index_path
            or repository_root / "Knowledge" / "Experience" / "index.json"
        )
        self.pattern_index_path = Path(
            pattern_index_path
            or repository_root / "Knowledge" / "Pattern" / "index.json"
        )
        self._schema = self._load_schema()
        self._playbook_ids = self._load_registry_ids(
            self.playbook_index_path, "playbooks", "Playbook"
        )
        self._experience_ids = self._load_registry_ids(
            self.experience_index_path, "experiences", "Experience"
        )
        self._pattern_ids = self._load_registry_ids(
            self.pattern_index_path, "patterns", "Pattern"
        )
        self._snapshots: dict[str, PredictionSnapshot] = {}

        if auto_start:
            self.start()

    def start(self) -> None:
        """Validate template and Snapshots before replacing the Registry."""
        self.validate_template(self.prediction_root / "TEMPLATE.md")
        snapshot_files = self._scan_snapshot_files()
        loaded_snapshots = [self.load_snapshot(path) for path in snapshot_files]

        registry: dict[str, PredictionSnapshot] = {}
        dates: dict[str, Path] = {}
        for snapshot in loaded_snapshots:
            if snapshot.prediction_id in registry:
                first = registry[snapshot.prediction_id].source_path
                raise PredictionValidationError(
                    f"Duplicate Prediction ID {snapshot.prediction_id}: "
                    f"{first} and {snapshot.source_path}"
                )
            if snapshot.prediction_date in dates:
                raise PredictionValidationError(
                    f"Duplicate daily Prediction for {snapshot.prediction_date}: "
                    f"{dates[snapshot.prediction_date]} and {snapshot.source_path}"
                )
            registry[snapshot.prediction_id] = snapshot
            dates[snapshot.prediction_date] = snapshot.source_path

        self._snapshots = registry
        self._build_registry()

    def list_predictions(self) -> list[PredictionSnapshot]:
        return [self._snapshots[key] for key in sorted(self._snapshots)]

    def get_prediction(self, prediction_id: str) -> PredictionSnapshot:
        try:
            return self._snapshots[prediction_id]
        except KeyError as exc:
            raise KeyError(f"Prediction not found: {prediction_id}") from exc

    def validate_template(self, path: Path | str) -> bool:
        template_path = Path(path)
        try:
            content = template_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PredictionValidationError(
                f"Unable to read Prediction template: {template_path}"
            ) from exc
        front_matter, body = self._parse_front_matter(content, template_path)
        missing = set(self._schema["required"]) - set(front_matter)
        if missing:
            raise PredictionValidationError(
                f"Prediction template missing YAML fields: "
                f"{', '.join(sorted(missing))}"
            )
        for heading in self.TEMPLATE_HEADINGS:
            if heading not in body:
                raise PredictionValidationError(
                    f"Prediction template missing heading: {heading}"
                )
        return True

    def load_snapshot(self, path: Path | str) -> PredictionSnapshot:
        snapshot_path = Path(path)
        try:
            content = snapshot_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PredictionValidationError(
                f"Unable to read Prediction Snapshot: {snapshot_path}"
            ) from exc

        front_matter, body = self._parse_front_matter(content, snapshot_path)
        self._validate_payload(front_matter, snapshot_path)
        snapshot = PredictionSnapshot(
            prediction_id=front_matter["prediction_id"],
            prediction_date=front_matter["prediction_date"],
            generated_at=front_matter["generated_at"],
            state=front_matter["state"],
            market=front_matter["market"],
            playbook_refs=tuple(front_matter["playbook_refs"]),
            experience_refs=tuple(front_matter["experience_refs"]),
            pattern_refs=tuple(front_matter["pattern_refs"]),
            confidence_ref=front_matter["confidence_ref"],
            decision_status=front_matter["decision_status"],
            model_impact=front_matter["model_impact"],
            status=front_matter["status"],
            source_path=snapshot_path,
            body=body,
        )
        self.validate_snapshot(snapshot)
        return snapshot

    def validate_snapshot(self, snapshot: PredictionSnapshot) -> bool:
        reference_sets = (
            ("Playbook", snapshot.playbook_refs, self._playbook_ids),
            ("Experience", snapshot.experience_refs, self._experience_ids),
            ("Pattern", snapshot.pattern_refs, self._pattern_ids),
        )
        for entity_name, references, available_ids in reference_sets:
            missing = sorted(set(references) - available_ids)
            if missing:
                raise PredictionValidationError(
                    f"{snapshot.source_path}: missing {entity_name} reference(s): "
                    f"{', '.join(missing)}"
                )

        parent = snapshot.source_path.parent.name
        if snapshot.status == "Archived":
            expected_parent = "archive"
        else:
            expected_parent = "daily"
        if parent != expected_parent:
            raise PredictionValidationError(
                f"{snapshot.source_path}: status {snapshot.status} must be stored "
                f"in {expected_parent}/"
            )
        return True

    def _scan_snapshot_files(self) -> list[Path]:
        folders = (
            self.prediction_root / "daily",
            self.prediction_root / "archive",
        )
        for folder in folders:
            if not folder.is_dir():
                raise PredictionRepositoryError(
                    f"Missing Prediction folder: {folder}"
                )
        return sorted(path for folder in folders for path in folder.glob("*.md"))

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PredictionValidationError(
                f"Unable to load Prediction schema: {self.schema_path}"
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
            raise PredictionValidationError(
                f"Prediction schema missing fields: {', '.join(sorted(missing))}"
            )
        if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            raise PredictionValidationError(
                "Prediction schema must use JSON Schema 2020-12"
            )
        if schema["type"] != "object" or schema["additionalProperties"] is not False:
            raise PredictionValidationError(
                "Prediction schema must define a closed object"
            )
        if schema["x-repository"].get("model_impact") != (
            "snapshot_only_not_production_scoring"
        ):
            raise PredictionValidationError(
                "Prediction schema must remain snapshot-only"
            )
        return schema

    @staticmethod
    def _load_registry_ids(
        path: Path, records_key: str, entity_name: str
    ) -> set[str]:
        try:
            registry = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PredictionValidationError(
                f"Unable to load {entity_name} Registry: {path}"
            ) from exc
        records = registry.get(records_key)
        if not isinstance(records, list):
            raise PredictionValidationError(
                f"{entity_name} Registry must contain a {records_key} array"
            )
        ids: list[str] = []
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str):
                raise PredictionValidationError(
                    f"Every {entity_name} Registry item must contain a string id"
                )
            ids.append(record["id"])
        if len(ids) != len(set(ids)):
            raise PredictionValidationError(
                f"{entity_name} Registry contains duplicate IDs"
            )
        return set(ids)

    def _validate_payload(self, payload: dict[str, Any], path: Path) -> None:
        required = set(self._schema["required"])
        missing = required - set(payload)
        if missing:
            raise PredictionValidationError(
                f"{path}: missing YAML fields: {', '.join(sorted(missing))}"
            )
        if self._schema["additionalProperties"] is False:
            extra = set(payload) - set(self._schema["properties"])
            if extra:
                raise PredictionValidationError(
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
        allowed_types = (
            set(expected_type) if isinstance(expected_type, list) else {expected_type}
        )
        if value is None:
            if "null" in allowed_types:
                return
            raise PredictionValidationError(f"{path}: {field} must not be null")

        if "array" in allowed_types:
            if not isinstance(value, list):
                raise PredictionValidationError(f"{path}: {field} must be array")
            if definition.get("uniqueItems") and len(value) != len(set(value)):
                raise PredictionValidationError(
                    f"{path}: {field} must contain unique references"
                )
            item_definition = definition.get("items", {})
            for index, item in enumerate(value):
                self._validate_value(
                    f"{field}[{index}]", item, item_definition, path
                )
            return

        if "string" not in allowed_types or not isinstance(value, str):
            raise PredictionValidationError(f"{path}: {field} must be string")
        if len(value) < definition.get("minLength", 0):
            raise PredictionValidationError(f"{path}: {field} must not be empty")
        pattern = definition.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            raise PredictionValidationError(
                f"{path}: {field} has an invalid format"
            )
        if "enum" in definition and value not in definition["enum"]:
            raise PredictionValidationError(
                f"{path}: invalid {field} {value!r}"
            )
        if "const" in definition and value != definition["const"]:
            raise PredictionValidationError(
                f"{path}: invalid {field} {value!r}"
            )
        if definition.get("format") == "date":
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise PredictionValidationError(
                    f"{path}: {field} must be an ISO date"
                ) from exc
        if definition.get("format") == "date-time":
            normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
            try:
                datetime.fromisoformat(normalized)
            except ValueError as exc:
                raise PredictionValidationError(
                    f"{path}: {field} must be an ISO date-time"
                ) from exc

    @classmethod
    def _parse_front_matter(
        cls, content: str, source_path: Path
    ) -> tuple[dict[str, Any], str]:
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            raise PredictionValidationError(
                f"{source_path}: YAML front matter must start on the first line"
            )
        try:
            end = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == "---"
            )
        except StopIteration as exc:
            raise PredictionValidationError(
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
                        raise PredictionValidationError(
                            f"{source_path}:{line_number}: list items must be strings"
                        )
                    if metadata[active_list_key] is None:
                        metadata[active_list_key] = []
                    metadata[active_list_key].append(item)
                    continue
                raise PredictionValidationError(
                    f"{source_path}:{line_number}: nested YAML is not supported"
                )
            if ":" not in raw_line:
                raise PredictionValidationError(
                    f"{source_path}:{line_number}: invalid YAML entry"
                )
            key, raw_value = raw_line.split(":", 1)
            key = key.strip()
            if not key or key in metadata:
                raise PredictionValidationError(
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
        if value.startswith(("[", '"')):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise PredictionValidationError(
                    f"{source_path}:{line_number}: invalid YAML scalar"
                ) from exc
        if value.startswith("'") and value.endswith("'") and len(value) >= 2:
            return value[1:-1].replace("''", "'")
        return value

    def _build_registry(self) -> None:
        records = [
            snapshot.to_registry_record(self.prediction_root)
            for snapshot in self.list_predictions()
        ]
        payload = {
            "document_id": "AR-PREDICTION-REGISTRY-v1",
            "version": "1.0",
            "status": "repository_index",
            "model_impact": "snapshot_only_not_production_scoring",
            "prediction_count": len(records),
            "predictions": records,
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
            raise PredictionRepositoryError(
                f"Unable to write Prediction Registry: {self.registry_path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Prediction Snapshot Registry."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    repository = PredictionRepository()
    print(f"Registered {len(repository.list_predictions())} Prediction(s).")
    print(f"Registry: {repository.registry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

