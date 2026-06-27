from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Scripts.Repository.playbook_repository import (
    PlaybookRepository,
    PlaybookValidationError,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPOSITORY_ROOT / "Schemas" / "Playbook" / "playbook.schema.json"
LIFECYCLE_FOLDERS = (
    "Draft",
    "Candidate",
    "Shadow",
    "Verified",
    "Deprecated",
    "Archived",
)


def create_playbook_root(root: Path) -> Path:
    playbook_root = root / "Playbook"
    for folder in LIFECYCLE_FOLDERS:
        (playbook_root / folder).mkdir(parents=True)
    return playbook_root


def create_graph_index(root: Path) -> Path:
    path = root / "graph_index.json"
    path.write_text(
        json.dumps(
            {
                "edges": [
                    {
                        "node_id": "EXP-001",
                        "relation": "DERIVED_FROM",
                        "target": "PAT-001",
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def playbook_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "playbook_id": "PB-001",
        "version": "1.0",
        "status": "Draft",
        "title": "Repository Validation Playbook",
        "description": "A static repository-only test Playbook.",
        "graph_reference": {
            "node_id": "EXP-001",
            "relation": "DERIVED_FROM",
            "target": "PAT-001",
        },
        "lifecycle_state": "Draft",
        "created_at": "2026-06-27T00:00:00+08:00",
        "updated_at": "2026-06-27T00:00:00+08:00",
    }
    payload.update(overrides)
    return payload


def write_playbook(
    playbook_root: Path, name: str, payload: dict[str, object]
) -> Path:
    path = playbook_root / str(payload["status"]) / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class PlaybookRepositoryTests(unittest.TestCase):
    def create_repository(
        self, root: Path, playbook_root: Path
    ) -> PlaybookRepository:
        return PlaybookRepository(
            playbook_root=playbook_root,
            schema_path=SCHEMA_PATH,
            graph_index_path=create_graph_index(root),
            index_path=playbook_root / "index.json",
        )

    def test_empty_repository_builds_valid_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            playbook_root = create_playbook_root(root)

            repository = self.create_repository(root, playbook_root)

            self.assertEqual([], repository.list_playbooks())
            index = json.loads(
                (playbook_root / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(0, index["playbook_count"])
            self.assertEqual([], index["playbooks"])

    def test_valid_playbook_is_registered_and_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            playbook_root = create_playbook_root(root)
            write_playbook(
                playbook_root,
                "PB-001.json",
                playbook_payload(),
            )

            repository = self.create_repository(root, playbook_root)

            playbook = repository.get_playbook("PB-001")
            self.assertEqual(
                ("EXP-001", "DERIVED_FROM", "PAT-001"),
                playbook.graph_reference.key,
            )
            index = json.loads(
                (playbook_root / "index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {"id", "version", "status", "graph_reference", "created_at"},
                set(index["playbooks"][0]),
            )

    def test_duplicate_playbook_id_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            playbook_root = create_playbook_root(root)
            write_playbook(
                playbook_root,
                "PB-001_FIRST.json",
                playbook_payload(),
            )
            write_playbook(
                playbook_root,
                "PB-001_SECOND.json",
                playbook_payload(),
            )

            with self.assertRaises(PlaybookValidationError):
                self.create_repository(root, playbook_root)

    def test_missing_graph_reference_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            playbook_root = create_playbook_root(root)
            write_playbook(
                playbook_root,
                "PB-001.json",
                playbook_payload(
                    graph_reference={
                        "node_id": "EXP-001",
                        "relation": "REFERENCES",
                        "target": "PAT-001",
                    }
                ),
            )

            with self.assertRaises(PlaybookValidationError):
                self.create_repository(root, playbook_root)

    def test_invalid_status_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            playbook_root = create_playbook_root(root)
            payload = playbook_payload(status="Invalid", lifecycle_state="Invalid")
            invalid_path = playbook_root / "Draft" / "PB-001.json"
            invalid_path.write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(PlaybookValidationError):
                self.create_repository(root, playbook_root)

    def test_missing_required_field_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            playbook_root = create_playbook_root(root)
            payload = playbook_payload()
            del payload["description"]
            write_playbook(playbook_root, "PB-001.json", payload)

            with self.assertRaises(PlaybookValidationError):
                self.create_repository(root, playbook_root)

    def test_lifecycle_mismatch_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            playbook_root = create_playbook_root(root)
            write_playbook(
                playbook_root,
                "PB-001.json",
                playbook_payload(lifecycle_state="Candidate"),
            )

            with self.assertRaises(PlaybookValidationError):
                self.create_repository(root, playbook_root)


if __name__ == "__main__":
    unittest.main()

