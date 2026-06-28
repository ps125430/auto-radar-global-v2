"""Rule-based Evidence to Case Candidate mapping in the isolated Sandbox."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class CaseCandidateError(RuntimeError):
    """Raised on the first invalid Candidate, Evidence, or Registry record."""


class CaseCandidateSandbox:
    """Map Sandbox Evidence records to review-required Case Candidates."""

    def __init__(
        self,
        sandbox_root: Path | str | None = None,
        evidence_root: Path | str | None = None,
        schema_path: Path | str | None = None,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.sandbox_root = Path(sandbox_root or Path(__file__).resolve().parent)
        self.evidence_root = Path(
            evidence_root
            or repository_root / "Sandbox" / "Ingestion" / "processed"
        )
        self.schema_path = Path(
            schema_path or self.sandbox_root / "case_candidate.schema.json"
        )
        self.candidates_root = self.sandbox_root / "candidates"
        self.processed_root = self.sandbox_root / "processed"
        self.failed_root = self.sandbox_root / "failed"
        self.registry_path = self.sandbox_root / "candidate_registry.json"
        self._schema = self._load_schema()

    def generate_all(self) -> dict[str, Any]:
        """Generate one deterministic Candidate for every Sandbox Evidence."""
        evidence = self._load_all_evidence()
        if not evidence:
            raise CaseCandidateError("No Evidence records found")

        existing_candidates = self._load_candidate_files()
        existing_ids = {
            self._required_text(item, "candidate_id", path)
            for path, item in existing_candidates
        }

        candidates: list[dict[str, Any]] = []
        candidate_ids: set[str] = set()
        for evidence_id in sorted(evidence):
            candidate = self._map_evidence(evidence[evidence_id])
            candidate_id = candidate["candidate_id"]
            if candidate_id in existing_ids or candidate_id in candidate_ids:
                raise CaseCandidateError(
                    f"Duplicate candidate: {candidate_id}"
                )
            self._validate_candidate(candidate, self.schema_path)
            candidate_ids.add(candidate_id)
            candidates.append(candidate)

        self.candidates_root.mkdir(parents=True, exist_ok=True)
        self.processed_root.mkdir(parents=True, exist_ok=True)
        self.failed_root.mkdir(parents=True, exist_ok=True)
        for candidate in candidates:
            output = self.candidates_root / f"{candidate['candidate_id']}.json"
            output.write_text(
                json.dumps(candidate, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        registry = self._build_registry(candidates)
        self._write_registry(registry)
        self.validate_existing()
        return registry

    def validate_existing(self) -> dict[str, Any]:
        """Validate Candidates, Evidence references, and Registry alignment."""
        evidence = self._load_all_evidence()
        candidate_files = self._load_candidate_files()
        candidate_by_id: dict[str, tuple[Path, dict[str, Any]]] = {}

        for path, candidate in candidate_files:
            self._validate_candidate(candidate, path)
            candidate_id = candidate["candidate_id"]
            if candidate_id in candidate_by_id:
                raise CaseCandidateError(
                    f"Duplicate candidate: {candidate_id}"
                )
            evidence_id = candidate["evidence_id"]
            if evidence_id not in evidence:
                raise CaseCandidateError(
                    f"Broken Evidence reference: {evidence_id}"
                )
            self._validate_rule_mapping(candidate, evidence[evidence_id], path)
            candidate_by_id[candidate_id] = (path, candidate)

        registry = self._load_registry()
        records = registry["candidates"]
        registry_ids: set[str] = set()
        for record in records:
            if not isinstance(record, dict):
                raise CaseCandidateError("Candidate Registry records must be objects")
            candidate_id = self._required_text(
                record, "candidate_id", self.registry_path
            )
            if candidate_id in registry_ids:
                raise CaseCandidateError(
                    f"Duplicate candidate in Registry: {candidate_id}"
                )
            registry_ids.add(candidate_id)
            if candidate_id not in candidate_by_id:
                raise CaseCandidateError(
                    f"Registry points to missing Candidate: {candidate_id}"
                )
            path, candidate = candidate_by_id[candidate_id]
            expected = {
                "candidate_id": candidate_id,
                "evidence_id": candidate["evidence_id"],
                "status": candidate["status"],
                "file": path.relative_to(self.sandbox_root).as_posix(),
            }
            if record != expected:
                raise CaseCandidateError(
                    f"Candidate Registry mismatch: {candidate_id}"
                )

        if registry.get("candidate_count") != len(records):
            raise CaseCandidateError("Candidate Registry count mismatch")
        if registry_ids != set(candidate_by_id):
            raise CaseCandidateError("Candidate Registry is incomplete")

        return {
            "validation_status": "PASS",
            "candidate_count": len(candidate_by_id),
            "evidence_references_checked": len(candidate_by_id),
        }

    def _load_all_evidence(self) -> dict[str, dict[str, Any]]:
        if not self.evidence_root.is_dir():
            raise CaseCandidateError(
                f"Evidence directory does not exist: {self.evidence_root}"
            )
        evidence: dict[str, dict[str, Any]] = {}
        for path in sorted(self.evidence_root.glob("*.md")):
            payload = self._parse_markdown_metadata(path)
            evidence_id = self._required_text(payload, "evidence_id", path)
            if evidence_id in evidence:
                raise CaseCandidateError(f"Duplicate Evidence: {evidence_id}")
            for field in (
                "title",
                "source",
                "collected_at",
                "symbols",
                "tags",
            ):
                if field not in payload:
                    raise CaseCandidateError(
                        f"Missing Evidence field {field}: {path}"
                    )
            if not isinstance(payload["symbols"], list) or not all(
                isinstance(item, str) for item in payload["symbols"]
            ):
                raise CaseCandidateError(f"Invalid Evidence symbols: {path}")
            if not isinstance(payload["tags"], list) or not all(
                isinstance(item, str) for item in payload["tags"]
            ):
                raise CaseCandidateError(f"Invalid Evidence tags: {path}")
            evidence[evidence_id] = payload
        return evidence

    def _load_candidate_files(self) -> list[tuple[Path, dict[str, Any]]]:
        if not self.candidates_root.exists():
            return []
        records: list[tuple[Path, dict[str, Any]]] = []
        for path in sorted(self.candidates_root.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                raise CaseCandidateError(
                    f"Invalid Candidate JSON: {path}"
                ) from exc
            if not isinstance(payload, dict):
                raise CaseCandidateError(
                    f"Candidate root must be an object: {path}"
                )
            records.append((path, payload))
        return records

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CaseCandidateError(
                f"Unable to load Case Candidate schema: {self.schema_path}"
            ) from exc
        if (
            schema.get("$schema")
            != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("type") != "object"
            or not isinstance(schema.get("required"), list)
            or not isinstance(schema.get("properties"), dict)
        ):
            raise CaseCandidateError("Invalid Case Candidate schema")
        return schema

    def _load_registry(self) -> dict[str, Any]:
        try:
            registry = json.loads(
                self.registry_path.read_text(encoding="utf-8-sig")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise CaseCandidateError(
                f"Unable to load Candidate Registry: {self.registry_path}"
            ) from exc
        if not isinstance(registry, dict) or not isinstance(
            registry.get("candidates"), list
        ):
            raise CaseCandidateError(
                "Candidate Registry must contain candidates array"
            )
        generated_at = registry.get("generated_at")
        if not isinstance(generated_at, str):
            raise CaseCandidateError("Candidate Registry missing generated_at")
        self._validate_datetime(generated_at, self.registry_path)
        return registry

    def _validate_candidate(
        self, candidate: dict[str, Any], path: Path
    ) -> None:
        required = set(self._schema["required"])
        missing = required - set(candidate)
        if missing:
            raise CaseCandidateError(
                f"Missing required fields in {path}: "
                f"{', '.join(sorted(missing))}"
            )
        extra = set(candidate) - set(self._schema["properties"])
        if extra:
            raise CaseCandidateError(
                f"Unexpected Candidate fields in {path}: "
                f"{', '.join(sorted(extra))}"
            )

        for field, definition in self._schema["properties"].items():
            value = candidate[field]
            value_type = definition.get("type")
            if value_type == "null":
                if value is not None:
                    raise CaseCandidateError(f"Invalid {field}: {path}")
                continue
            if value_type == "boolean":
                if not isinstance(value, bool):
                    raise CaseCandidateError(f"Invalid {field}: {path}")
            elif value_type == "array":
                if not isinstance(value, list) or not all(
                    isinstance(item, str) for item in value
                ):
                    raise CaseCandidateError(f"Invalid {field}: {path}")
                if definition.get("uniqueItems") and len(value) != len(set(value)):
                    raise CaseCandidateError(f"Invalid {field}: {path}")
            elif value_type == "string":
                if not isinstance(value, str):
                    raise CaseCandidateError(f"Invalid {field}: {path}")
                if len(value) < definition.get("minLength", 0):
                    raise CaseCandidateError(f"Invalid {field}: {path}")
                pattern = definition.get("pattern")
                if pattern and not re.fullmatch(pattern, value):
                    raise CaseCandidateError(f"Invalid {field}: {path}")
                if definition.get("format") == "date-time":
                    self._validate_datetime(value, path)
            else:
                raise CaseCandidateError(
                    f"Unsupported schema type for {field}: {value_type}"
                )
            if "const" in definition and value != definition["const"]:
                label = (
                    "Invalid lifecycle"
                    if field == "status"
                    else f"Invalid {field}"
                )
                raise CaseCandidateError(f"{label}: {path}")

    @staticmethod
    def _validate_rule_mapping(
        candidate: dict[str, Any],
        evidence: dict[str, Any],
        path: Path,
    ) -> None:
        mappings = {
            "evidence_id": "evidence_id",
            "title": "title",
            "symbols": "symbols",
            "tags": "tags",
            "source": "source",
            "generated_at": "collected_at",
        }
        for candidate_field, evidence_field in mappings.items():
            if candidate[candidate_field] != evidence[evidence_field]:
                raise CaseCandidateError(
                    f"Broken rule mapping for {candidate_field}: {path}"
                )

    @staticmethod
    def _map_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
        evidence_id = evidence["evidence_id"]
        match = re.fullmatch(r"EV-([0-9]{3,})", evidence_id)
        if match is None:
            raise CaseCandidateError(
                f"Invalid Evidence identifier: {evidence_id}"
            )
        return {
            "candidate_id": f"CC-{match.group(1)}",
            "evidence_id": evidence_id,
            "title": evidence["title"],
            "symbols": evidence["symbols"],
            "tags": evidence["tags"],
            "source": evidence["source"],
            "generated_at": evidence["collected_at"],
            "status": "Candidate",
            "confidence": None,
            "grade": None,
            "review_required": True,
            "model_impact": "repository_only",
        }

    def _build_registry(
        self, candidates: list[dict[str, Any]]
    ) -> dict[str, Any]:
        generated_at = max(
            candidate["generated_at"] for candidate in candidates
        )
        records = [
            {
                "candidate_id": candidate["candidate_id"],
                "evidence_id": candidate["evidence_id"],
                "status": candidate["status"],
                "file": f"candidates/{candidate['candidate_id']}.json",
            }
            for candidate in candidates
        ]
        return {
            "generated_at": generated_at,
            "candidate_count": len(records),
            "candidates": records,
        }

    def _write_registry(self, registry: dict[str, Any]) -> None:
        self.registry_path.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _required_text(
        payload: dict[str, Any], field: str, path: Path
    ) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise CaseCandidateError(f"Missing {field}: {path}")
        return value

    @staticmethod
    def _validate_datetime(value: str, path: Path) -> None:
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise CaseCandidateError(f"Invalid timestamp: {path}") from exc

    @classmethod
    def _parse_markdown_metadata(cls, path: Path) -> dict[str, Any]:
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError as exc:
            raise CaseCandidateError(f"Unable to read Evidence: {path}") from exc
        if not lines or lines[0].strip() != "---":
            raise CaseCandidateError(f"Evidence front matter missing: {path}")
        try:
            end = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == "---"
            )
        except StopIteration as exc:
            raise CaseCandidateError(
                f"Evidence front matter is not closed: {path}"
            ) from exc

        payload: dict[str, Any] = {}
        for line_number, raw_line in enumerate(lines[1:end], start=2):
            if not raw_line.strip():
                continue
            if ":" not in raw_line or raw_line.startswith((" ", "\t")):
                raise CaseCandidateError(
                    f"Invalid Evidence metadata at {path}:{line_number}"
                )
            key, raw_value = raw_line.split(":", 1)
            key = key.strip()
            if not key or key in payload:
                raise CaseCandidateError(
                    f"Duplicate Evidence metadata at {path}:{line_number}"
                )
            payload[key] = cls._parse_scalar(
                raw_value.strip(), path, line_number
            )
        return payload

    @staticmethod
    def _parse_scalar(value: str, path: Path, line_number: int) -> Any:
        if value in {"null", "Null", "NULL", "~", ""}:
            return None
        if value.startswith(("[", '"')):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise CaseCandidateError(
                    f"Invalid Evidence value at {path}:{line_number}"
                ) from exc
        return value


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the Evidence to Case Candidate Sandbox."
    )
    parser.add_argument("command", choices=("generate", "validate"))
    args = parser.parse_args(list(argv) if argv is not None else None)

    sandbox = CaseCandidateSandbox()
    try:
        result = (
            sandbox.generate_all()
            if args.command == "generate"
            else sandbox.validate_existing()
        )
    except CaseCandidateError as exc:
        print(f"Case Candidate Sandbox failed: {exc}")
        return 1

    count = result.get("candidate_count", 0)
    print(f"Case Candidate Sandbox passed: {count} Candidate(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
