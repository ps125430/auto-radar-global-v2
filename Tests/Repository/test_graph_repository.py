from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Scripts.Repository.graph_repository import (
    GraphRepository,
    GraphValidationError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "Schemas" / "Graph" / "graph.schema.json"


def create_graph_root(root: Path) -> Path:
    graph_root = root / "Graph"
    (graph_root / "Edges").mkdir(parents=True)
    return graph_root


def write_registry(root: Path, name: str, key: str, ids: list[str]) -> Path:
    path = root / f"{name}.json"
    path.write_text(
        json.dumps({key: [{"id": entity_id} for entity_id in ids]}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return path


def registry_paths(root: Path) -> dict[str, tuple[Path, str] | None]:
    return {
        "Case": (write_registry(root, "cases", "cases", ["CASE-001"]), "cases"),
        "Pattern": (
            write_registry(root, "patterns", "patterns", ["PAT-001"]),
            "patterns",
        ),
        "Experience": (
            write_registry(root, "experiences", "experiences", ["EXP-001"]),
            "experiences",
        ),
        "Playbook": None,
        "Rule": None,
        "Evidence": None,
    }


def edge_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "node_id": "PAT-001",
        "node_type": "Pattern",
        "relation": "DERIVED_FROM",
        "target": "CASE-001",
        "status": "Active",
        "created_at": "2026-06-27T00:00:00+08:00",
    }
    payload.update(overrides)
    return payload


def write_edge(graph_root: Path, name: str, payload: dict[str, object]) -> Path:
    path = graph_root / "Edges" / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class GraphRepositoryTests(unittest.TestCase):
    def create_repository(
        self, root: Path, graph_root: Path
    ) -> GraphRepository:
        return GraphRepository(
            graph_root=graph_root,
            schema_path=SCHEMA_PATH,
            index_path=graph_root / "index.json",
            registry_paths=registry_paths(root),
        )

    def test_empty_repository_builds_valid_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            graph_root = create_graph_root(root)

            repository = self.create_repository(root, graph_root)

            self.assertEqual([], repository.list_edges())
            index = json.loads(
                (graph_root / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(0, index["edge_count"])
            self.assertEqual([], index["edges"])

    def test_valid_edge_is_registered_and_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            graph_root = create_graph_root(root)
            write_edge(graph_root, "PAT-001_DERIVED_FROM_CASE-001.json", edge_payload())

            repository = self.create_repository(root, graph_root)

            self.assertEqual(1, len(repository.list_edges()))
            index = json.loads(
                (graph_root / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {
                    "node_id",
                    "node_type",
                    "relation",
                    "target",
                    "status",
                    "created_at",
                },
                set(index["edges"][0]),
            )

    def test_invalid_node_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            graph_root = create_graph_root(root)
            write_edge(
                graph_root,
                "invalid_node.json",
                edge_payload(node_id="PAT-999"),
            )

            with self.assertRaises(GraphValidationError):
                self.create_repository(root, graph_root)

    def test_invalid_relation_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            graph_root = create_graph_root(root)
            write_edge(
                graph_root,
                "invalid_relation.json",
                edge_payload(relation="INFERS"),
            )

            with self.assertRaises(GraphValidationError):
                self.create_repository(root, graph_root)

    def test_missing_target_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            graph_root = create_graph_root(root)
            write_edge(
                graph_root,
                "missing_target.json",
                edge_payload(target="CASE-999"),
            )

            with self.assertRaises(GraphValidationError):
                self.create_repository(root, graph_root)

    def test_duplicate_edge_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            graph_root = create_graph_root(root)
            write_edge(graph_root, "edge_one.json", edge_payload())
            write_edge(graph_root, "edge_two.json", edge_payload())

            with self.assertRaises(GraphValidationError):
                self.create_repository(root, graph_root)

    def test_circular_self_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            graph_root = create_graph_root(root)
            write_edge(
                graph_root,
                "self_reference.json",
                edge_payload(
                    node_id="PAT-001",
                    node_type="Pattern",
                    relation="RELATED_TO",
                    target="PAT-001",
                ),
            )

            with self.assertRaises(GraphValidationError):
                self.create_repository(root, graph_root)

    def test_missing_required_field_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            graph_root = create_graph_root(root)
            payload = edge_payload()
            del payload["target"]
            write_edge(graph_root, "missing_field.json", payload)

            with self.assertRaises(GraphValidationError):
                self.create_repository(root, graph_root)


if __name__ == "__main__":
    unittest.main()

