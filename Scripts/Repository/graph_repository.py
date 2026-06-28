"""Fail-fast Knowledge Graph Repository.

The repository validates and indexes declared static entity relationships.
It intentionally provides no traversal, inference, reasoning, or decision API.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class GraphRepositoryError(RuntimeError):
    """Base error for Knowledge Graph Repository failures."""


class GraphValidationError(GraphRepositoryError):
    """Raised when an edge, schema, or entity reference is invalid."""


@dataclass(frozen=True, slots=True)
class GraphEdge:
    node_id: str
    node_type: str
    relation: str
    target: str
    status: str
    created_at: str
    source_path: Path

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.node_id, self.relation, self.target)

    def to_index_record(self) -> dict[str, str]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "relation": self.relation,
            "target": self.target,
            "status": self.status,
            "created_at": self.created_at,
        }


class GraphRepository:
    """Static edge scanner, validator, registry, and index builder."""

    NODE_PREFIXES = {
        "Case": "CASE-",
        "Pattern": "PAT-",
        "Experience": "EXP-",
        "Playbook": "PB-",
        "Rule": "RULE-",
        "Evidence": "EV-",
    }

    def __init__(
        self,
        graph_root: Path | str | None = None,
        schema_path: Path | str | None = None,
        index_path: Path | str | None = None,
        registry_paths: dict[str, tuple[Path | str, str] | None] | None = None,
        *,
        auto_start: bool = True,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.graph_root = Path(graph_root or repository_root / "Knowledge" / "Graph")
        self.edges_root = self.graph_root / "Edges"
        self.schema_path = Path(
            schema_path or repository_root / "Schemas" / "Graph" / "graph.schema.json"
        )
        self.index_path = Path(index_path or self.graph_root / "index.json")
        defaults: dict[str, tuple[Path | str, str] | None] = {
            "Case": (
                repository_root
                / "Runtime"
                / "Repository"
                / "index"
                / "case_index.json",
                "cases",
            ),
            "Pattern": (
                repository_root / "Knowledge" / "Pattern" / "index.json",
                "patterns",
            ),
            "Experience": (
                repository_root / "Knowledge" / "Experience" / "index.json",
                "experiences",
            ),
            "Playbook": None,
            "Rule": None,
            "Evidence": (
                repository_root
                / "Runtime"
                / "Repository"
                / "index"
                / "evidence_registry.json",
                "evidence",
            ),
        }
        if registry_paths:
            defaults.update(registry_paths)
        self.registry_paths = defaults
        self._schema = self._load_schema()
        self._entity_ids = self._load_entity_ids()
        self._edges: dict[tuple[str, str, str], GraphEdge] = {}

        if auto_start:
            self.start()

    def start(self) -> None:
        """Scan, validate, register, and index all graph edges atomically."""
        edge_files = self._scan_edge_files()
        loaded_edges = [self.load_edge(path) for path in edge_files]

        new_registry: dict[tuple[str, str, str], GraphEdge] = {}
        for edge in loaded_edges:
            if edge.key in new_registry:
                first = new_registry[edge.key].source_path
                raise GraphValidationError(
                    f"Duplicate edge {edge.key}: {first} and {edge.source_path}"
                )
            new_registry[edge.key] = edge

        self._edges = new_registry
        self._build_index()

    def list_edges(self) -> list[GraphEdge]:
        return [self._edges[key] for key in sorted(self._edges)]

    def load_edge(self, path: Path | str) -> GraphEdge:
        edge_path = Path(path)
        try:
            payload = json.loads(edge_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise GraphValidationError(
                f"Unable to load Graph edge JSON: {edge_path}"
            ) from exc

        self._validate_payload(payload, edge_path)
        edge = GraphEdge(
            node_id=payload["node_id"],
            node_type=payload["node_type"],
            relation=payload["relation"],
            target=payload["target"],
            status=payload["status"],
            created_at=payload["created_at"],
            source_path=edge_path,
        )
        self.validate_edge(edge)
        return edge

    def validate_edge(self, edge: GraphEdge) -> bool:
        expected_prefix = self.NODE_PREFIXES[edge.node_type]
        if not edge.node_id.startswith(expected_prefix):
            raise GraphValidationError(
                f"{edge.source_path}: node_id {edge.node_id} does not match "
                f"node_type {edge.node_type}"
            )
        if edge.node_id not in self._entity_ids[edge.node_type]:
            raise GraphValidationError(
                f"{edge.source_path}: invalid or missing source Node {edge.node_id}"
            )

        target_type = self._node_type_for_id(edge.target)
        if target_type is None or edge.target not in self._entity_ids[target_type]:
            raise GraphValidationError(
                f"{edge.source_path}: missing target Entity {edge.target}"
            )

        if edge.node_id == edge.target:
            raise GraphValidationError(
                f"{edge.source_path}: circular self-reference is forbidden"
            )
        return True

    def _scan_edge_files(self) -> list[Path]:
        if not self.graph_root.is_dir():
            raise GraphRepositoryError(
                f"Knowledge Graph directory does not exist: {self.graph_root}"
            )
        if not self.edges_root.is_dir():
            raise GraphRepositoryError(
                f"Knowledge Graph Edges directory does not exist: {self.edges_root}"
            )
        return sorted(self.edges_root.glob("*.json"))

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise GraphValidationError(
                f"Unable to load Graph schema: {self.schema_path}"
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
            raise GraphValidationError(
                f"Graph schema missing fields: {', '.join(sorted(missing))}"
            )
        if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            raise GraphValidationError("Graph schema must use JSON Schema 2020-12")
        if schema["type"] != "object" or schema["additionalProperties"] is not False:
            raise GraphValidationError("Graph schema must define a closed object")
        if schema["x-repository"].get("model_impact") != (
            "repository_only_not_production"
        ):
            raise GraphValidationError("Graph schema must remain repository-only")
        return schema

    def _load_entity_ids(self) -> dict[str, set[str]]:
        entity_ids: dict[str, set[str]] = {}
        for node_type in self.NODE_PREFIXES:
            registry_config = self.registry_paths.get(node_type)
            if registry_config is None:
                entity_ids[node_type] = set()
                continue

            path_value, records_key = registry_config
            path = Path(path_value)
            try:
                registry = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                raise GraphValidationError(
                    f"Unable to load {node_type} Registry: {path}"
                ) from exc

            records = registry.get(records_key)
            if not isinstance(records, list):
                raise GraphValidationError(
                    f"{node_type} Registry must contain a {records_key} array"
                )

            ids: list[str] = []
            for record in records:
                if not isinstance(record, dict) or not isinstance(
                    record.get("id"), str
                ):
                    raise GraphValidationError(
                        f"Every {node_type} Registry record must contain a string id"
                    )
                ids.append(record["id"])
            if len(ids) != len(set(ids)):
                raise GraphValidationError(
                    f"{node_type} Registry contains duplicate IDs"
                )
            entity_ids[node_type] = set(ids)
        return entity_ids

    def _validate_payload(self, payload: Any, source_path: Path) -> None:
        if not isinstance(payload, dict):
            raise GraphValidationError(f"{source_path}: edge must be an object")

        required = set(self._schema["required"])
        missing = required - set(payload)
        if missing:
            raise GraphValidationError(
                f"{source_path}: missing fields: {', '.join(sorted(missing))}"
            )

        if self._schema["additionalProperties"] is False:
            extra = set(payload) - set(self._schema["properties"])
            if extra:
                raise GraphValidationError(
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
        if definition.get("type") != "string" or not isinstance(value, str):
            raise GraphValidationError(f"{source_path}: {field} must be string")
        if len(value) < definition.get("minLength", 0):
            raise GraphValidationError(f"{source_path}: {field} must not be empty")
        pattern = definition.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            raise GraphValidationError(
                f"{source_path}: {field} has an invalid format"
            )
        allowed = definition.get("enum")
        if allowed and value not in allowed:
            raise GraphValidationError(
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
            raise GraphValidationError(
                f"{source_path}: {field} must be an ISO 8601 date-time"
            ) from exc

    def _node_type_for_id(self, entity_id: str) -> str | None:
        for node_type, prefix in self.NODE_PREFIXES.items():
            if entity_id.startswith(prefix):
                return node_type
        return None

    def _build_index(self) -> None:
        records = [edge.to_index_record() for edge in self.list_edges()]
        payload = {
            "document_id": "AR-KNOWLEDGE-GRAPH-INDEX-v1",
            "version": "1.0",
            "status": "repository_index",
            "model_impact": "repository_only_not_production",
            "edge_count": len(records),
            "edges": records,
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
            raise GraphRepositoryError(
                f"Unable to write Knowledge Graph index: {self.index_path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Knowledge Graph Repository index."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    repository = GraphRepository()
    print(f"Registered {len(repository.list_edges())} edge(s).")
    print(f"Index: {repository.index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
