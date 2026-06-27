"""Fail-fast Playbook Repository Engine.

The repository validates static Playbook templates and their declared Graph
edge references. It provides no Runtime, decision, or strategy behavior.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class PlaybookRepositoryError(RuntimeError):
    """Base error for Playbook Repository failures."""


class PlaybookValidationError(PlaybookRepositoryError):
    """Raised when a Playbook, schema, or Graph reference is invalid."""


@dataclass(frozen=True, slots=True)
class GraphReference:
    node_id: str
    relation: str
    target: str

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.node_id, self.relation, self.target)

    def to_dict(self) -> dict[str, str]:
        return {
            "node_id": self.node_id,
            "relation": self.relation,
            "target": self.target,
        }


@dataclass(frozen=True, slots=True)
class Playbook:
    playbook_id: str
    version: str
    status: str
    title: str
    description: str
    graph_reference: GraphReference
    lifecycle_state: str
    created_at: str
    updated_at: str
    source_path: Path

    def to_index_record(self) -> dict[str, Any]:
        return {
            "id": self.playbook_id,
            "version": self.version,
            "status": self.status,
            "graph_reference": self.graph_reference.to_dict(),
            "created_at": self.created_at,
        }


class PlaybookRepository:
    """Playbook scanner, validator, registry, and index builder."""

    LIFECYCLE_FOLDERS = (
        "Draft",
        "Candidate",
        "Shadow",
        "Verified",
        "Deprecated",
        "Archived",
    )

    def __init__(
        self,
        playbook_root: Path | str | None = None,
        schema_path: Path | str | None = None,
        graph_index_path: Path | str | None = None,
        index_path: Path | str | None = None,
        *,
        auto_start: bool = True,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.playbook_root = Path(
            playbook_root or repository_root / "Knowledge" / "Playbook"
        )
        self.schema_path = Path(
            schema_path
            or repository_root / "Schemas" / "Playbook" / "playbook.schema.json"
        )
        self.graph_index_path = Path(
            graph_index_path
            or repository_root / "Knowledge" / "Graph" / "index.json"
        )
        self.index_path = Path(index_path or self.playbook_root / "index.json")
        self._schema = self._load_schema()
        self._graph_edges = self._load_graph_edges()
        self._playbooks: dict[str, Playbook] = {}

        if auto_start:
            self.start()

    def start(self) -> None:
        """Scan, validate, register, and index all Playbooks atomically."""
        playbook_files = self._scan_playbook_files()
        loaded_playbooks = [
            self.load_playbook(path) for path in playbook_files
        ]

        new_registry: dict[str, Playbook] = {}
        for playbook in loaded_playbooks:
            if playbook.playbook_id in new_registry:
                first = new_registry[playbook.playbook_id].source_path
                raise PlaybookValidationError(
                    f"Duplicate Playbook ID {playbook.playbook_id}: "
                    f"{first} and {playbook.source_path}"
                )
            new_registry[playbook.playbook_id] = playbook

        self._playbooks = new_registry
        self._build_index()

    def get_playbook(self, playbook_id: str) -> Playbook:
        try:
            return self._playbooks[playbook_id]
        except KeyError as exc:
            raise KeyError(f"Playbook not found: {playbook_id}") from exc

    def list_playbooks(self) -> list[Playbook]:
        return [
            self._playbooks[playbook_id]
            for playbook_id in sorted(self._playbooks)
        ]

    def load_playbook(self, path: Path | str) -> Playbook:
        playbook_path = Path(path)
        try:
            payload = json.loads(playbook_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PlaybookValidationError(
                f"Unable to load Playbook JSON: {playbook_path}"
            ) from exc

        self._validate_payload(payload, playbook_path)
        reference_payload = payload["graph_reference"]
        graph_reference = GraphReference(
            node_id=reference_payload["node_id"],
            relation=reference_payload["relation"],
            target=reference_payload["target"],
        )
        playbook = Playbook(
            playbook_id=payload["playbook_id"],
            version=payload["version"],
            status=payload["status"],
            title=payload["title"],
            description=payload["description"],
            graph_reference=graph_reference,
            lifecycle_state=payload["lifecycle_state"],
            created_at=payload["created_at"],
            updated_at=payload["updated_at"],
            source_path=playbook_path,
        )
        self.validate_playbook(playbook)
        return playbook

    def validate_playbook(self, playbook: Playbook) -> bool:
        if playbook.graph_reference.key not in self._graph_edges:
            raise PlaybookValidationError(
                f"{playbook.source_path}: missing Graph reference "
                f"{playbook.graph_reference.key}"
            )
        if playbook.status != playbook.lifecycle_state:
            raise PlaybookValidationError(
                f"{playbook.source_path}: status and lifecycle_state must match"
            )
        if playbook.source_path.parent.name != playbook.status:
            raise PlaybookValidationError(
                f"{playbook.source_path}: status {playbook.status} must be stored "
                f"in {playbook.status}/"
            )
        return True

    def _scan_playbook_files(self) -> list[Path]:
        if not self.playbook_root.is_dir():
            raise PlaybookRepositoryError(
                f"Playbook directory does not exist: {self.playbook_root}"
            )

        missing_folders = [
            name
            for name in self.LIFECYCLE_FOLDERS
            if not (self.playbook_root / name).is_dir()
        ]
        if missing_folders:
            raise PlaybookRepositoryError(
                f"Missing Playbook lifecycle folders: {', '.join(missing_folders)}"
            )

        return sorted(
            path
            for folder in self.LIFECYCLE_FOLDERS
            for path in (self.playbook_root / folder).glob("*.json")
        )

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PlaybookValidationError(
                f"Unable to load Playbook schema: {self.schema_path}"
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
            raise PlaybookValidationError(
                f"Playbook schema missing fields: {', '.join(sorted(missing))}"
            )
        if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            raise PlaybookValidationError(
                "Playbook schema must use JSON Schema 2020-12"
            )
        if schema["type"] != "object" or schema["additionalProperties"] is not False:
            raise PlaybookValidationError(
                "Playbook schema must define a closed object"
            )
        if schema["x-repository"].get("model_impact") != (
            "repository_only_not_production"
        ):
            raise PlaybookValidationError(
                "Playbook schema must remain repository-only"
            )
        return schema

    def _load_graph_edges(self) -> set[tuple[str, str, str]]:
        try:
            graph_index = json.loads(
                self.graph_index_path.read_text(encoding="utf-8-sig")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise PlaybookValidationError(
                f"Unable to load Graph Registry: {self.graph_index_path}"
            ) from exc

        edges = graph_index.get("edges")
        if not isinstance(edges, list):
            raise PlaybookValidationError(
                "Graph Registry must contain an edges array"
            )

        edge_keys: list[tuple[str, str, str]] = []
        for edge in edges:
            if not isinstance(edge, dict):
                raise PlaybookValidationError(
                    "Every Graph Registry edge must be an object"
                )
            try:
                key = (edge["node_id"], edge["relation"], edge["target"])
            except KeyError as exc:
                raise PlaybookValidationError(
                    "Graph Registry edge is missing its static key"
                ) from exc
            if not all(isinstance(value, str) for value in key):
                raise PlaybookValidationError(
                    "Graph Registry edge key values must be strings"
                )
            edge_keys.append(key)

        if len(edge_keys) != len(set(edge_keys)):
            raise PlaybookValidationError(
                "Graph Registry contains duplicate edges"
            )
        return set(edge_keys)

    def _validate_payload(self, payload: Any, source_path: Path) -> None:
        if not isinstance(payload, dict):
            raise PlaybookValidationError(
                f"{source_path}: Playbook must be an object"
            )

        required = set(self._schema["required"])
        missing = required - set(payload)
        if missing:
            raise PlaybookValidationError(
                f"{source_path}: missing fields: {', '.join(sorted(missing))}"
            )

        if self._schema["additionalProperties"] is False:
            extra = set(payload) - set(self._schema["properties"])
            if extra:
                raise PlaybookValidationError(
                    f"{source_path}: unexpected fields: {', '.join(sorted(extra))}"
                )

        for field, definition in self._schema["properties"].items():
            if field not in payload:
                continue
            self._validate_value(field, payload[field], definition, source_path)

    def _validate_value(
        self,
        field: str,
        value: Any,
        definition: dict[str, Any],
        source_path: Path,
    ) -> None:
        expected_type = definition.get("type")
        if expected_type == "object":
            if not isinstance(value, dict):
                raise PlaybookValidationError(
                    f"{source_path}: {field} must be object"
                )
            required = set(definition.get("required", []))
            missing = required - set(value)
            if missing:
                raise PlaybookValidationError(
                    f"{source_path}: {field} missing fields: "
                    f"{', '.join(sorted(missing))}"
                )
            if definition.get("additionalProperties") is False:
                extra = set(value) - set(definition.get("properties", {}))
                if extra:
                    raise PlaybookValidationError(
                        f"{source_path}: {field} has unexpected fields: "
                        f"{', '.join(sorted(extra))}"
                    )
            for nested_field, nested_definition in definition.get(
                "properties", {}
            ).items():
                if nested_field in value:
                    self._validate_value(
                        f"{field}.{nested_field}",
                        value[nested_field],
                        nested_definition,
                        source_path,
                    )
            return

        if expected_type != "string" or not isinstance(value, str):
            raise PlaybookValidationError(
                f"{source_path}: {field} must be string"
            )
        if len(value) < definition.get("minLength", 0):
            raise PlaybookValidationError(
                f"{source_path}: {field} must not be empty"
            )
        pattern = definition.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            raise PlaybookValidationError(
                f"{source_path}: {field} has an invalid format"
            )
        allowed = definition.get("enum")
        if allowed and value not in allowed:
            raise PlaybookValidationError(
                f"{source_path}: invalid {field} {value!r}"
            )
        if definition.get("format") == "date-time":
            self._validate_datetime(field, value, source_path)

    @staticmethod
    def _validate_datetime(field: str, value: str, source_path: Path) -> None:
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise PlaybookValidationError(
                f"{source_path}: {field} must be an ISO 8601 date-time"
            ) from exc

    def _build_index(self) -> None:
        records = [
            playbook.to_index_record() for playbook in self.list_playbooks()
        ]
        payload = {
            "document_id": "AR-PLAYBOOK-REPOSITORY-INDEX-v1",
            "version": "1.0",
            "status": "repository_index",
            "model_impact": "repository_only_not_production",
            "playbook_count": len(records),
            "playbooks": records,
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
            raise PlaybookRepositoryError(
                f"Unable to write Playbook index: {self.index_path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Playbook Repository index."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    repository = PlaybookRepository()
    print(f"Registered {len(repository.list_playbooks())} Playbook(s).")
    print(f"Index: {repository.index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

