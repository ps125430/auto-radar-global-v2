"""Human Review to Verified Case materialization in the isolated Sandbox."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class ReviewPipelineError(RuntimeError):
    """Raised on the first invalid Review, Candidate, Case, or Registry."""


class SandboxReviewPipeline:
    """Validate human Reviews and materialize approved Case Candidates."""

    REVIEW_FOLDERS = {
        "pending": {"Pending"},
        "approved": {"Approved", "Verified"},
        "rejected": {"Rejected"},
    }
    VERIFIED_CASE_FIELDS = {
        "verified_case_id",
        "candidate_id",
        "evidence_id",
        "review_id",
        "title",
        "symbols",
        "tags",
        "source",
        "verified_at",
        "status",
        "model_impact",
    }

    def __init__(
        self,
        review_root: Path | str | None = None,
        candidate_root: Path | str | None = None,
        candidate_registry_path: Path | str | None = None,
        schema_path: Path | str | None = None,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.review_root = Path(review_root or Path(__file__).resolve().parent)
        self.candidate_root = Path(
            candidate_root
            or repository_root / "Sandbox" / "CaseCandidate" / "candidates"
        )
        self.candidate_registry_path = Path(
            candidate_registry_path
            or repository_root
            / "Sandbox"
            / "CaseCandidate"
            / "candidate_registry.json"
        )
        self.schema_path = Path(
            schema_path or self.review_root / "review.schema.json"
        )
        self.verified_root = self.review_root / "verified"
        self.registry_path = self.review_root / "verified_case_registry.json"
        self._schema = self._load_schema()

    def verify_all(self) -> dict[str, Any]:
        """Materialize every human-approved Review as a Verified Case."""
        candidates = self._load_candidates()
        reviews = self._load_reviews(candidates)
        existing = self._load_verified_cases()
        if existing:
            duplicate = sorted(existing)[0]
            raise ReviewPipelineError(f"Duplicate Verified Case: {duplicate}")

        verified_cases: list[dict[str, Any]] = []
        verified_ids: set[str] = set()
        for review_path, review in reviews:
            if review["review_status"] not in {"Approved", "Verified"}:
                continue
            verified_case = self._materialize(
                review, candidates[review["candidate_id"]]
            )
            verified_case_id = verified_case["verified_case_id"]
            if verified_case_id in verified_ids:
                raise ReviewPipelineError(
                    f"Duplicate Verified Case: {verified_case_id}"
                )
            self._validate_verified_case(
                verified_case, review, candidates[review["candidate_id"]], review_path
            )
            verified_ids.add(verified_case_id)
            verified_cases.append(verified_case)

        self.verified_root.mkdir(parents=True, exist_ok=True)
        for verified_case in verified_cases:
            path = (
                self.verified_root
                / f"{verified_case['verified_case_id']}.json"
            )
            path.write_text(
                json.dumps(verified_case, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        registry = self._build_registry(reviews, verified_cases)
        self._write_registry(registry)
        self.validate_existing()
        return registry

    def validate_existing(self) -> dict[str, Any]:
        """Validate the complete Candidate, Review, Case, and Registry chain."""
        candidates = self._load_candidates()
        reviews = self._load_reviews(candidates)
        review_by_id = {
            review["review_id"]: (path, review) for path, review in reviews
        }
        verified_cases = self._load_verified_cases()

        expected_verified_ids = {
            review["verified_case_id"]
            for _, review in reviews
            if review["review_status"] in {"Approved", "Verified"}
        }
        if set(verified_cases) != expected_verified_ids:
            missing = sorted(expected_verified_ids - set(verified_cases))
            extra = sorted(set(verified_cases) - expected_verified_ids)
            details = missing or extra
            raise ReviewPipelineError(
                "Verified Case lifecycle mismatch: " + ", ".join(details)
            )

        for verified_case_id, (path, verified_case) in verified_cases.items():
            review_id = self._required_text(
                verified_case, "review_id", path
            )
            if review_id not in review_by_id:
                raise ReviewPipelineError(
                    f"Broken Review reference: {review_id}"
                )
            review = review_by_id[review_id][1]
            candidate_id = review["candidate_id"]
            self._validate_verified_case(
                verified_case, review, candidates[candidate_id], path
            )
            if verified_case_id != verified_case["verified_case_id"]:
                raise ReviewPipelineError(
                    f"Verified Case filename mismatch: {path}"
                )

        registry = self._load_registry()
        self._validate_registry(registry, reviews, verified_cases)
        status_counts = self._status_counts(reviews)
        return {
            "validation_status": "PASS",
            "review_count": len(reviews),
            "verified_case_count": len(verified_cases),
            "approved": status_counts["Approved"],
            "rejected": status_counts["Rejected"],
            "pending": status_counts["Pending"],
        }

    def _load_candidates(self) -> dict[str, dict[str, Any]]:
        try:
            registry = json.loads(
                self.candidate_registry_path.read_text(encoding="utf-8-sig")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ReviewPipelineError("Missing Candidate Registry") from exc
        records = registry.get("candidates")
        if not isinstance(records, list):
            raise ReviewPipelineError(
                "Candidate Registry must contain candidates array"
            )

        candidates: dict[str, dict[str, Any]] = {}
        for record in records:
            if not isinstance(record, dict):
                raise ReviewPipelineError(
                    "Candidate Registry records must be objects"
                )
            candidate_id = self._required_text(
                record, "candidate_id", self.candidate_registry_path
            )
            file_value = self._required_text(
                record, "file", self.candidate_registry_path
            )
            path = self.candidate_root.parent / file_value
            try:
                candidate = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ReviewPipelineError(
                    f"Missing Candidate: {candidate_id}"
                ) from exc
            if not isinstance(candidate, dict):
                raise ReviewPipelineError(
                    f"Candidate must be an object: {candidate_id}"
                )
            if candidate.get("candidate_id") != candidate_id:
                raise ReviewPipelineError(
                    f"Broken Candidate Registry reference: {candidate_id}"
                )
            if candidate_id in candidates:
                raise ReviewPipelineError(
                    f"Duplicate Candidate: {candidate_id}"
                )
            candidates[candidate_id] = candidate
        return candidates

    def _load_reviews(
        self, candidates: dict[str, dict[str, Any]]
    ) -> list[tuple[Path, dict[str, Any]]]:
        reviews: list[tuple[Path, dict[str, Any]]] = []
        review_ids: set[str] = set()
        reviewed_candidates: set[str] = set()
        verified_ids: set[str] = set()

        for folder_name, allowed_statuses in self.REVIEW_FOLDERS.items():
            folder = self.review_root / folder_name
            if not folder.is_dir():
                raise ReviewPipelineError(
                    f"Missing Review lifecycle folder: {folder}"
                )
            for path in sorted(folder.glob("*.json")):
                review = self._load_json_object(path, "Review")
                self._validate_review(review, path)
                review_id = review["review_id"]
                candidate_id = review["candidate_id"]
                if review_id in review_ids:
                    raise ReviewPipelineError(
                        f"Duplicate Review: {review_id}"
                    )
                if candidate_id in reviewed_candidates:
                    raise ReviewPipelineError(
                        f"Duplicate Review for Candidate: {candidate_id}"
                    )
                if review["review_status"] not in allowed_statuses:
                    raise ReviewPipelineError(
                        f"Invalid Status folder: {path}"
                    )
                if candidate_id not in candidates:
                    raise ReviewPipelineError(
                        f"Broken Candidate reference: {candidate_id}"
                    )
                verified_case_id = review["verified_case_id"]
                if verified_case_id is not None:
                    if verified_case_id in verified_ids:
                        raise ReviewPipelineError(
                            f"Duplicate Verified Case: {verified_case_id}"
                        )
                    verified_ids.add(verified_case_id)
                review_ids.add(review_id)
                reviewed_candidates.add(candidate_id)
                reviews.append((path, review))
        return reviews

    def _load_verified_cases(
        self,
    ) -> dict[str, tuple[Path, dict[str, Any]]]:
        if not self.verified_root.exists():
            return {}
        verified_cases: dict[str, tuple[Path, dict[str, Any]]] = {}
        for path in sorted(self.verified_root.glob("*.json")):
            verified_case = self._load_json_object(path, "Verified Case")
            verified_case_id = self._required_text(
                verified_case, "verified_case_id", path
            )
            if verified_case_id in verified_cases:
                raise ReviewPipelineError(
                    f"Duplicate Verified Case: {verified_case_id}"
                )
            verified_cases[verified_case_id] = (path, verified_case)
        return verified_cases

    def _validate_review(
        self, review: dict[str, Any], path: Path
    ) -> None:
        required = set(self._schema["required"])
        missing = required - set(review)
        if missing:
            raise ReviewPipelineError(
                f"Missing Required Fields in {path}: "
                f"{', '.join(sorted(missing))}"
            )
        extra = set(review) - set(self._schema["properties"])
        if extra:
            raise ReviewPipelineError(
                f"Unexpected Review fields in {path}: "
                f"{', '.join(sorted(extra))}"
            )

        for field, definition in self._schema["properties"].items():
            value = review[field]
            allowed_types = definition.get("type")
            if isinstance(allowed_types, str):
                allowed_types = [allowed_types]
            if not isinstance(allowed_types, list):
                raise ReviewPipelineError(
                    f"Invalid Review schema type: {field}"
                )
            if value is None and "null" in allowed_types:
                continue
            if "string" not in allowed_types or not isinstance(value, str):
                raise ReviewPipelineError(f"Invalid {field}: {path}")
            if len(value) < definition.get("minLength", 0):
                raise ReviewPipelineError(f"Invalid {field}: {path}")
            pattern = definition.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                raise ReviewPipelineError(f"Invalid {field}: {path}")
            if "enum" in definition and value not in definition["enum"]:
                label = (
                    "Invalid Status"
                    if field == "review_status"
                    else f"Invalid {field}"
                )
                raise ReviewPipelineError(f"{label}: {path}")
            if "const" in definition and value != definition["const"]:
                raise ReviewPipelineError(f"Invalid {field}: {path}")
            if definition.get("format") == "date-time":
                self._validate_datetime(value, path)

        status = review["review_status"]
        decision = review["decision"]
        verified_case_id = review["verified_case_id"]
        expected_decision = {
            "Pending": "Pending",
            "Approved": "Approve",
            "Rejected": "Reject",
            "Verified": "Approve",
        }[status]
        if decision != expected_decision:
            raise ReviewPipelineError(
                f"Invalid Status decision pairing: {path}"
            )
        if status in {"Approved", "Verified"}:
            if not isinstance(verified_case_id, str):
                raise ReviewPipelineError(
                    f"Approved Review missing verified_case_id: {path}"
                )
        elif verified_case_id is not None:
            raise ReviewPipelineError(
                f"Invalid verified_case_id for {status}: {path}"
            )

    def _validate_verified_case(
        self,
        verified_case: dict[str, Any],
        review: dict[str, Any],
        candidate: dict[str, Any],
        path: Path,
    ) -> None:
        if set(verified_case) != self.VERIFIED_CASE_FIELDS:
            missing = self.VERIFIED_CASE_FIELDS - set(verified_case)
            raise ReviewPipelineError(
                f"Missing Verified Case fields in {path}: "
                f"{', '.join(sorted(missing))}"
            )
        expected = self._materialize(review, candidate)
        if verified_case != expected:
            raise ReviewPipelineError(
                f"Broken Verified Case reference or mapping: {path}"
            )

    def _load_schema(self) -> dict[str, Any]:
        schema = self._load_json_object(self.schema_path, "Review schema")
        if (
            schema.get("$schema")
            != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("type") != "object"
            or not isinstance(schema.get("required"), list)
            or not isinstance(schema.get("properties"), dict)
        ):
            raise ReviewPipelineError("Invalid Review schema")
        return schema

    def _load_registry(self) -> dict[str, Any]:
        registry = self._load_json_object(
            self.registry_path, "Verified Case Registry"
        )
        if not isinstance(registry.get("reviews"), list) or not isinstance(
            registry.get("verified_cases"), list
        ):
            raise ReviewPipelineError(
                "Verified Case Registry arrays are missing"
            )
        return registry

    def _validate_registry(
        self,
        registry: dict[str, Any],
        reviews: list[tuple[Path, dict[str, Any]]],
        verified_cases: dict[str, tuple[Path, dict[str, Any]]],
    ) -> None:
        expected = self._build_registry(
            reviews,
            [verified_case for _, verified_case in verified_cases.values()],
        )
        if registry != expected:
            raise ReviewPipelineError("Verified Case Registry mismatch")

    def _build_registry(
        self,
        reviews: list[tuple[Path, dict[str, Any]]],
        verified_cases: list[dict[str, Any]],
    ) -> dict[str, Any]:
        generated_at = max(
            (review["reviewed_at"] for _, review in reviews),
            default="1970-01-01T00:00:00+00:00",
        )
        review_records = [
            {
                "review_id": review["review_id"],
                "candidate_id": review["candidate_id"],
                "review_status": review["review_status"],
                "file": path.relative_to(self.review_root).as_posix(),
            }
            for path, review in reviews
        ]
        case_records = [
            {
                "verified_case_id": case["verified_case_id"],
                "candidate_id": case["candidate_id"],
                "review_id": case["review_id"],
                "status": case["status"],
                "file": f"verified/{case['verified_case_id']}.json",
            }
            for case in sorted(
                verified_cases, key=lambda item: item["verified_case_id"]
            )
        ]
        return {
            "generated_at": generated_at,
            "review_count": len(review_records),
            "reviews": review_records,
            "verified_case_count": len(case_records),
            "verified_cases": case_records,
        }

    @staticmethod
    def _materialize(
        review: dict[str, Any], candidate: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "verified_case_id": review["verified_case_id"],
            "candidate_id": review["candidate_id"],
            "evidence_id": candidate["evidence_id"],
            "review_id": review["review_id"],
            "title": candidate["title"],
            "symbols": candidate["symbols"],
            "tags": candidate["tags"],
            "source": candidate["source"],
            "verified_at": review["reviewed_at"],
            "status": "Verified",
            "model_impact": "repository_only",
        }

    @staticmethod
    def _status_counts(
        reviews: list[tuple[Path, dict[str, Any]]]
    ) -> dict[str, int]:
        counts = {"Pending": 0, "Approved": 0, "Rejected": 0, "Verified": 0}
        for _, review in reviews:
            counts[review["review_status"]] += 1
        return counts

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
            raise ReviewPipelineError(
                f"Unable to read {context}: {path}"
            ) from exc
        if not isinstance(payload, dict):
            raise ReviewPipelineError(f"{context} must be an object: {path}")
        return payload

    @staticmethod
    def _required_text(
        payload: dict[str, Any], field: str, path: Path
    ) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ReviewPipelineError(f"Missing {field}: {path}")
        return value

    @staticmethod
    def _validate_datetime(value: str, path: Path) -> None:
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ReviewPipelineError(f"Invalid reviewed_at: {path}") from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the human Sandbox Review Pipeline."
    )
    parser.add_argument("command", choices=("verify", "validate"))
    args = parser.parse_args(list(argv) if argv is not None else None)

    pipeline = SandboxReviewPipeline()
    try:
        result = (
            pipeline.verify_all()
            if args.command == "verify"
            else pipeline.validate_existing()
        )
    except ReviewPipelineError as exc:
        print(f"Sandbox Review failed: {exc}")
        return 1

    count = result.get(
        "verified_case_count", len(result.get("verified_cases", []))
    )
    print(f"Sandbox Review passed: {count} Verified Case(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
