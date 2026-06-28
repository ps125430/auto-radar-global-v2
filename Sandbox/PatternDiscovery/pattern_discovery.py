"""Rule-based Verified Case to Pattern Candidate discovery Sandbox."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class PatternDiscoveryError(RuntimeError):
    """Raised on the first invalid rule, Candidate, reference, or Registry."""


class PatternDiscoverySandbox:
    """Group Verified Cases with explicit, mutually exclusive tag rules."""

    RULES = (
        {
            "pattern_candidate_id": "PC-001",
            "case_tags": {"filing", "exchange"},
            "pattern_tags": ["corporate_disclosure"],
            "feature_summary": (
                "Rule-matched Verified Case tags: filing or exchange."
            ),
        },
        {
            "pattern_candidate_id": "PC-002",
            "case_tags": {"macro", "calendar"},
            "pattern_tags": ["macro_calendar"],
            "feature_summary": (
                "Rule-matched Verified Case tags: macro or calendar."
            ),
        },
        {
            "pattern_candidate_id": "PC-003",
            "case_tags": {"manual"},
            "pattern_tags": ["manual_news"],
            "feature_summary": "Rule-matched Verified Case tag: manual.",
        },
    )

    def __init__(
        self,
        sandbox_root: Path | str | None = None,
        verified_root: Path | str | None = None,
        verified_registry_path: Path | str | None = None,
        evidence_root: Path | str | None = None,
        schema_path: Path | str | None = None,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.sandbox_root = Path(sandbox_root or Path(__file__).resolve().parent)
        self.verified_root = Path(
            verified_root
            or repository_root / "Sandbox" / "Review" / "verified"
        )
        self.verified_registry_path = Path(
            verified_registry_path
            or repository_root
            / "Sandbox"
            / "Review"
            / "verified_case_registry.json"
        )
        self.evidence_root = Path(
            evidence_root
            or repository_root / "Sandbox" / "Ingestion" / "processed"
        )
        self.schema_path = Path(
            schema_path
            or self.sandbox_root / "pattern_candidate.schema.json"
        )
        self.candidates_root = self.sandbox_root / "candidates"
        self.processed_root = self.sandbox_root / "processed"
        self.failed_root = self.sandbox_root / "failed"
        self.registry_path = (
            self.sandbox_root / "pattern_candidate_registry.json"
        )
        self._schema = self._load_schema()

    def discover_all(self) -> dict[str, Any]:
        """Create one Pattern Candidate for each populated discovery rule."""
        verified_cases = self._load_verified_cases()
        expected = self._discover(verified_cases)
        existing = self._load_pattern_candidates()
        if existing:
            duplicate = sorted(existing)[0]
            raise PatternDiscoveryError(f"Duplicate Pattern: {duplicate}")

        self.candidates_root.mkdir(parents=True, exist_ok=True)
        self.processed_root.mkdir(parents=True, exist_ok=True)
        self.failed_root.mkdir(parents=True, exist_ok=True)
        for candidate in expected.values():
            self._validate_candidate(candidate, self.schema_path)
            path = (
                self.candidates_root
                / f"{candidate['pattern_candidate_id']}.json"
            )
            path.write_text(
                json.dumps(candidate, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        registry = self._build_registry(expected)
        self._write_registry(registry)
        self.validate_existing()
        return registry

    def validate_existing(self) -> dict[str, Any]:
        """Validate Candidates and Pattern -> Case -> Evidence traceability."""
        verified_cases = self._load_verified_cases()
        expected = self._discover(verified_cases)
        actual = self._load_pattern_candidates()

        if set(actual) != set(expected):
            missing = sorted(set(expected) - set(actual))
            extra = sorted(set(actual) - set(expected))
            raise PatternDiscoveryError(
                "Pattern Candidate set mismatch: "
                + ", ".join(missing or extra)
            )

        traced_cases: set[str] = set()
        traced_evidence: set[str] = set()
        for pattern_id, (path, candidate) in actual.items():
            self._validate_candidate(candidate, path)
            for case_id in candidate["source_cases"]:
                if case_id not in verified_cases:
                    raise PatternDiscoveryError(
                        f"Broken Case reference: {case_id}"
                    )
                traced_cases.add(case_id)
                traced_evidence.add(verified_cases[case_id]["evidence_id"])
            if candidate != expected[pattern_id]:
                raise PatternDiscoveryError(
                    f"Broken Pattern rule mapping: {pattern_id}"
                )

        registry = self._load_registry()
        if registry != self._build_registry(expected):
            raise PatternDiscoveryError("Pattern Candidate Registry mismatch")

        return {
            "validation_status": "PASS",
            "pattern_candidate_count": len(actual),
            "verified_cases_traced": len(traced_cases),
            "evidence_records_traced": len(traced_evidence),
        }

    def _load_verified_cases(self) -> dict[str, dict[str, Any]]:
        registry = self._load_json_object(
            self.verified_registry_path, "Verified Case Registry"
        )
        records = registry.get("verified_cases")
        if not isinstance(records, list):
            raise PatternDiscoveryError(
                "Verified Case Registry must contain verified_cases array"
            )
        if registry.get("verified_case_count") != len(records):
            raise PatternDiscoveryError("Verified Case Registry count mismatch")

        evidence_ids = self._load_evidence_ids()
        verified_cases: dict[str, dict[str, Any]] = {}
        for record in records:
            if not isinstance(record, dict):
                raise PatternDiscoveryError(
                    "Verified Case Registry records must be objects"
                )
            case_id = self._required_text(
                record, "verified_case_id", self.verified_registry_path
            )
            file_value = self._required_text(
                record, "file", self.verified_registry_path
            )
            path = self.verified_root.parent / file_value
            case = self._load_json_object(path, "Verified Case")
            if case.get("verified_case_id") != case_id:
                raise PatternDiscoveryError(
                    f"Broken Verified Case Registry reference: {case_id}"
                )
            if case_id in verified_cases:
                raise PatternDiscoveryError(f"Duplicate Case: {case_id}")
            evidence_id = self._required_text(case, "evidence_id", path)
            if evidence_id not in evidence_ids:
                raise PatternDiscoveryError(
                    f"Broken Evidence reference: {evidence_id}"
                )
            tags = case.get("tags")
            if not isinstance(tags, list) or not all(
                isinstance(tag, str) for tag in tags
            ):
                raise PatternDiscoveryError(
                    f"Verified Case tags are invalid: {case_id}"
                )
            if case.get("status") != "Verified":
                raise PatternDiscoveryError(
                    f"Invalid Verified Case status: {case_id}"
                )
            self._required_text(case, "verified_at", path)
            verified_cases[case_id] = case
        return verified_cases

    def _load_evidence_ids(self) -> set[str]:
        if not self.evidence_root.is_dir():
            raise PatternDiscoveryError(
                f"Missing Evidence directory: {self.evidence_root}"
            )
        evidence_ids: set[str] = set()
        for path in sorted(self.evidence_root.glob("*.md")):
            evidence_id = self._front_matter_id(path, "evidence_id")
            if evidence_id in evidence_ids:
                raise PatternDiscoveryError(
                    f"Duplicate Evidence: {evidence_id}"
                )
            evidence_ids.add(evidence_id)
        return evidence_ids

    def _discover(
        self, verified_cases: dict[str, dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = {
            rule["pattern_candidate_id"]: [] for rule in self.RULES
        }
        for case_id in sorted(verified_cases):
            case = verified_cases[case_id]
            tags = set(case["tags"])
            matches = [
                rule
                for rule in self.RULES
                if tags.intersection(rule["case_tags"])
            ]
            if len(matches) != 1:
                raise PatternDiscoveryError(
                    f"Verified Case must match exactly one rule: {case_id}"
                )
            groups[matches[0]["pattern_candidate_id"]].append(case)

        candidates: dict[str, dict[str, Any]] = {}
        for rule in self.RULES:
            pattern_id = rule["pattern_candidate_id"]
            cases = groups[pattern_id]
            if not cases:
                continue
            candidate = {
                "pattern_candidate_id": pattern_id,
                "source_cases": sorted(
                    case["verified_case_id"] for case in cases
                ),
                "generated_at": max(
                    case["verified_at"] for case in cases
                ),
                "status": "Candidate",
                "pattern_tags": rule["pattern_tags"],
                "feature_summary": rule["feature_summary"],
                "similarity_score": 1.0,
                "review_required": True,
                "model_impact": "repository_only",
            }
            candidates[pattern_id] = candidate
        return candidates

    def _load_pattern_candidates(
        self,
    ) -> dict[str, tuple[Path, dict[str, Any]]]:
        if not self.candidates_root.exists():
            return {}
        candidates: dict[str, tuple[Path, dict[str, Any]]] = {}
        for path in sorted(self.candidates_root.glob("*.json")):
            candidate = self._load_json_object(path, "Pattern Candidate")
            pattern_id = self._required_text(
                candidate, "pattern_candidate_id", path
            )
            if pattern_id in candidates:
                raise PatternDiscoveryError(
                    f"Duplicate Pattern: {pattern_id}"
                )
            candidates[pattern_id] = (path, candidate)
        return candidates

    def _validate_candidate(
        self, candidate: dict[str, Any], path: Path
    ) -> None:
        required = set(self._schema["required"])
        missing = required - set(candidate)
        if missing:
            raise PatternDiscoveryError(
                f"Missing Fields in {path}: {', '.join(sorted(missing))}"
            )
        extra = set(candidate) - set(self._schema["properties"])
        if extra:
            raise PatternDiscoveryError(
                f"Unexpected Pattern fields in {path}: "
                f"{', '.join(sorted(extra))}"
            )

        for field, definition in self._schema["properties"].items():
            value = candidate[field]
            value_type = definition.get("type")
            if value_type == "string":
                if not isinstance(value, str):
                    raise PatternDiscoveryError(f"Invalid {field}: {path}")
                if len(value) < definition.get("minLength", 0):
                    raise PatternDiscoveryError(f"Invalid {field}: {path}")
                pattern = definition.get("pattern")
                if pattern and not re.fullmatch(pattern, value):
                    raise PatternDiscoveryError(f"Invalid {field}: {path}")
                if definition.get("format") == "date-time":
                    self._validate_datetime(value, path)
            elif value_type == "array":
                if not isinstance(value, list) or not all(
                    isinstance(item, str) for item in value
                ):
                    raise PatternDiscoveryError(f"Invalid {field}: {path}")
                if len(value) < definition.get("minItems", 0):
                    label = (
                        "Missing Case"
                        if field == "source_cases"
                        else f"Invalid {field}"
                    )
                    raise PatternDiscoveryError(f"{label}: {path}")
                if definition.get("uniqueItems") and len(value) != len(set(value)):
                    raise PatternDiscoveryError(f"Invalid {field}: {path}")
                item_pattern = definition.get("items", {}).get("pattern")
                if item_pattern and any(
                    re.fullmatch(item_pattern, item) is None for item in value
                ):
                    raise PatternDiscoveryError(f"Invalid {field}: {path}")
            elif value_type == "number":
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or value < definition.get("minimum", value)
                    or value > definition.get("maximum", value)
                ):
                    label = (
                        "Invalid Similarity"
                        if field == "similarity_score"
                        else f"Invalid {field}"
                    )
                    raise PatternDiscoveryError(f"{label}: {path}")
            elif value_type == "boolean":
                if not isinstance(value, bool):
                    raise PatternDiscoveryError(f"Invalid {field}: {path}")
            else:
                raise PatternDiscoveryError(
                    f"Unsupported Pattern schema type: {field}"
                )
            if "const" in definition and value != definition["const"]:
                label = (
                    "Invalid Status"
                    if field == "status"
                    else f"Invalid {field}"
                )
                raise PatternDiscoveryError(f"{label}: {path}")

    def _load_schema(self) -> dict[str, Any]:
        schema = self._load_json_object(
            self.schema_path, "Pattern Candidate schema"
        )
        if (
            schema.get("$schema")
            != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("type") != "object"
            or not isinstance(schema.get("required"), list)
            or not isinstance(schema.get("properties"), dict)
        ):
            raise PatternDiscoveryError("Invalid Pattern Candidate schema")
        return schema

    def _load_registry(self) -> dict[str, Any]:
        registry = self._load_json_object(
            self.registry_path, "Pattern Candidate Registry"
        )
        if not isinstance(registry.get("pattern_candidates"), list):
            raise PatternDiscoveryError(
                "Pattern Candidate Registry array is missing"
            )
        return registry

    def _build_registry(
        self, candidates: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        generated_at = max(
            (
                candidate["generated_at"]
                for candidate in candidates.values()
            ),
            default="1970-01-01T00:00:00+00:00",
        )
        records = [
            {
                "pattern_candidate_id": pattern_id,
                "source_cases": candidate["source_cases"],
                "status": candidate["status"],
                "file": f"candidates/{pattern_id}.json",
            }
            for pattern_id, candidate in sorted(candidates.items())
        ]
        return {
            "generated_at": generated_at,
            "pattern_candidate_count": len(records),
            "pattern_candidates": records,
        }

    def _write_registry(self, registry: dict[str, Any]) -> None:
        self.registry_path.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _load_json_object(path: Path, context: str) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PatternDiscoveryError(
                f"Unable to read {context}: {path}"
            ) from exc
        if not isinstance(payload, dict):
            raise PatternDiscoveryError(f"{context} must be an object: {path}")
        return payload

    @staticmethod
    def _required_text(
        payload: dict[str, Any], field: str, path: Path
    ) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise PatternDiscoveryError(f"Missing {field}: {path}")
        return value

    @staticmethod
    def _front_matter_id(path: Path, field: str) -> str:
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError as exc:
            raise PatternDiscoveryError(
                f"Unable to read Evidence: {path}"
            ) from exc
        if not lines or lines[0].strip() != "---":
            raise PatternDiscoveryError(
                f"Evidence front matter missing: {path}"
            )
        prefix = f"{field}:"
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith(prefix):
                value = line[len(prefix) :].strip()
                if value:
                    return value
        raise PatternDiscoveryError(f"Evidence missing {field}: {path}")

    @staticmethod
    def _validate_datetime(value: str, path: Path) -> None:
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise PatternDiscoveryError(
                f"Invalid generated_at: {path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the rule-based Pattern Discovery Sandbox."
    )
    parser.add_argument("command", choices=("discover", "validate"))
    args = parser.parse_args(list(argv) if argv is not None else None)

    sandbox = PatternDiscoverySandbox()
    try:
        result = (
            sandbox.discover_all()
            if args.command == "discover"
            else sandbox.validate_existing()
        )
    except PatternDiscoveryError as exc:
        print(f"Pattern Discovery failed: {exc}")
        return 1

    count = result.get(
        "pattern_candidate_count",
        len(result.get("pattern_candidates", [])),
    )
    print(f"Pattern Discovery passed: {count} Pattern Candidate(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
