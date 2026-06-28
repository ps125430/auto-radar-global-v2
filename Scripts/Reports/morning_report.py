"""Generate the read-only Auto Radar Morning Report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class MorningReportError(RuntimeError):
    """Raised when Morning Report input or output is invalid."""


class MorningReportGenerator:
    """Render repository state as a fixed Markdown morning report."""

    def __init__(
        self,
        repository_root: Path | str | None = None,
        output_path: Path | str | None = None,
        *,
        generated_at: datetime | None = None,
        repository_version: str | None = None,
    ) -> None:
        self.repository_root = Path(
            repository_root or Path(__file__).resolve().parents[2]
        )
        self.output_path = Path(
            output_path
            or self.repository_root / "Reports" / "Morning" / "latest.md"
        )
        self.generated_at = generated_at or datetime.now().astimezone()
        self.repository_version = (
            repository_version or self._read_repository_version()
        )
        self.paths = {
            "Prediction": self.repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "prediction_registry.json",
            "Case": self.repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "case_index.json",
            "Pattern": self.repository_root / "Knowledge" / "Pattern" / "index.json",
            "Experience": self.repository_root
            / "Knowledge"
            / "Experience"
            / "index.json",
            "Playbook": self.repository_root
            / "Knowledge"
            / "Playbook"
            / "index.json",
            "Validation": self.repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "validation_report.json",
            "Outcome": self.repository_root / "Knowledge" / "Outcome" / "index.json",
            "Evaluation": self.repository_root
            / "Knowledge"
            / "OutcomeEvaluation"
            / "index.json",
            "Review": self.repository_root
            / "Knowledge"
            / "DailyReview"
            / "index.json",
            "SandboxReview": self.repository_root
            / "Sandbox"
            / "Review"
            / "verified_case_registry.json",
        }

    def generate(self) -> str:
        """Build and persist one Markdown Morning Report."""
        prediction_registry = self._load_json(
            self.paths["Prediction"], "Prediction Registry"
        )
        predictions = self._records(
            prediction_registry, "predictions", "Prediction Registry"
        )
        self._check_count(
            prediction_registry, "prediction_count", predictions, "Prediction"
        )
        prediction = self._latest(predictions)

        case_registry = self._load_json(self.paths["Case"], "Case Registry")
        pattern_registry = self._load_json(
            self.paths["Pattern"], "Pattern Registry"
        )
        experience_registry = self._load_json(
            self.paths["Experience"], "Experience Registry"
        )
        playbook_registry = self._load_json(
            self.paths["Playbook"], "Playbook Registry"
        )
        validation = self._load_json(
            self.paths["Validation"], "Validation Report"
        )
        outcome_registry = self._load_json(
            self.paths["Outcome"], "Outcome Registry"
        )
        evaluation_registry = self._load_json(
            self.paths["Evaluation"], "Evaluation Registry"
        )
        review_registry = self._load_json(
            self.paths["Review"], "Review Registry"
        )
        sandbox_review_registry = self._load_json(
            self.paths["SandboxReview"], "Sandbox Review Registry"
        )

        cases = self._records(case_registry, "cases", "Case Registry")
        patterns = self._records(
            pattern_registry, "patterns", "Pattern Registry"
        )
        experiences = self._records(
            experience_registry, "experiences", "Experience Registry"
        )
        playbooks = self._records(
            playbook_registry, "playbooks", "Playbook Registry"
        )
        outcomes = self._records(
            outcome_registry, "outcomes", "Outcome Registry"
        )
        evaluations = self._records(
            evaluation_registry, "evaluations", "Evaluation Registry"
        )
        reviews = self._records(review_registry, "reviews", "Review Registry")
        sandbox_reviews = self._records(
            sandbox_review_registry, "reviews", "Sandbox Review Registry"
        )
        verified_cases = self._records(
            sandbox_review_registry,
            "verified_cases",
            "Sandbox Review Registry",
        )
        self._check_count(
            sandbox_review_registry,
            "review_count",
            sandbox_reviews,
            "Sandbox Review",
        )
        self._check_count(
            sandbox_review_registry,
            "verified_case_count",
            verified_cases,
            "Sandbox Verified Case",
        )

        prediction_data = self._prediction_data(prediction)
        active_patterns = prediction_data["pattern_refs"]
        active_experiences = prediction_data["experience_refs"]
        active_playbooks = prediction_data["playbook_refs"]
        active_cases = sorted(
            self._collect_case_refs(active_patterns, active_experiences)
        )

        validation_status = self._text_or_default(
            validation.get("validation_status"), "Unavailable"
        )
        errors = self._nonnegative_integer(
            validation.get("total_errors"), "Validation errors"
        )
        warnings = self._nonnegative_integer(
            validation.get("total_warnings"), "Validation warnings"
        )

        report = self._render(
            generated_time=self.generated_at.isoformat(),
            repository_version=self.repository_version,
            validation_status=validation_status,
            prediction=prediction_data,
            counts={
                "Case": len(cases),
                "Pattern": len(patterns),
                "Experience": len(experiences),
                "Playbook": len(playbooks),
            },
            references={
                "Case": active_cases,
                "Pattern": active_patterns,
                "Experience": active_experiences,
                "Playbook": active_playbooks,
            },
            errors=errors,
            warnings=warnings,
            pending={
                "Outcome": self._pending_count(outcomes),
                "Evaluation": self._pending_count(evaluations),
                "Review": self._pending_count(reviews),
            },
            verified_case_summary={
                "Approved": self._sandbox_review_count(
                    sandbox_reviews, "Approved"
                ),
                "Rejected": self._sandbox_review_count(
                    sandbox_reviews, "Rejected"
                ),
                "Pending": self._sandbox_review_count(
                    sandbox_reviews, "Pending"
                ),
                "Verified": len(verified_cases),
            },
        )
        self._write_report(report)
        return report

    def _prediction_data(
        self, prediction: dict[str, Any] | None
    ) -> dict[str, Any]:
        if prediction is None:
            return {
                "id": "N/A",
                "status": "No Snapshot",
                "market": "N/A",
                "generated_at": "N/A",
                "playbook_refs": [],
                "experience_refs": [],
                "pattern_refs": [],
            }
        return {
            "id": self._required_text(prediction, "id", "Prediction"),
            "status": self._required_text(prediction, "status", "Prediction"),
            "market": self._required_text(prediction, "market", "Prediction"),
            "generated_at": self._required_text(
                prediction, "generated_at", "Prediction"
            ),
            "playbook_refs": self._reference_list(
                prediction, "playbook_refs", "Prediction"
            ),
            "experience_refs": self._reference_list(
                prediction, "experience_refs", "Prediction"
            ),
            "pattern_refs": self._reference_list(
                prediction, "pattern_refs", "Prediction"
            ),
        }

    def _collect_case_refs(
        self, pattern_refs: list[str], experience_refs: list[str]
    ) -> set[str]:
        cases: set[str] = set()
        specs = (
            (
                self.repository_root / "Knowledge" / "Pattern",
                "pattern_id",
                set(pattern_refs),
            ),
            (
                self.repository_root / "Knowledge" / "Experience",
                "experience_id",
                set(experience_refs),
            ),
        )
        for root, id_field, requested in specs:
            if not requested:
                continue
            for path in sorted(root.rglob("*.json")):
                if path.name == "index.json":
                    continue
                payload = self._load_json(path, "Referenced entity")
                if payload.get(id_field) not in requested:
                    continue
                source_cases = payload.get("source_cases", [])
                if not isinstance(source_cases, list) or not all(
                    isinstance(case_id, str) for case_id in source_cases
                ):
                    raise MorningReportError(
                        f"Invalid source_cases in {path}"
                    )
                cases.update(source_cases)
        return cases

    def _read_repository_version(self) -> str:
        git_root = self.repository_root / ".git"
        head_path = git_root / "HEAD"
        try:
            head = head_path.read_text(encoding="utf-8").strip()
        except OSError:
            return "Unavailable"
        if head.startswith("ref: "):
            return Path(head[5:]).name
        return head[:7] if head else "Unavailable"

    @staticmethod
    def _latest(records: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not records:
            return None
        return max(
            records,
            key=lambda record: (
                str(record.get("prediction_date", "")),
                str(record.get("generated_at", "")),
                str(record.get("id", "")),
            ),
        )

    @staticmethod
    def _pending_count(records: list[dict[str, Any]]) -> int:
        completed = {"reviewed", "archived"}
        count = 0
        for record in records:
            status = record.get("status")
            if not isinstance(status, str):
                raise MorningReportError(
                    "Pending-review Registry item is missing status"
                )
            if status.casefold() not in completed:
                count += 1
        return count

    @staticmethod
    def _sandbox_review_count(
        records: list[dict[str, Any]], expected_status: str
    ) -> int:
        allowed = {"Pending", "Approved", "Rejected", "Verified"}
        count = 0
        for record in records:
            status = record.get("review_status")
            if status not in allowed:
                raise MorningReportError(
                    "Sandbox Review Registry item has invalid review_status"
                )
            if status == expected_status:
                count += 1
        return count

    @staticmethod
    def _reference_list(
        record: dict[str, Any], field: str, context: str
    ) -> list[str]:
        value = record.get(field, [])
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise MorningReportError(
                f"{context}: {field} must be an array of strings"
            )
        return value

    @staticmethod
    def _required_text(
        record: dict[str, Any], field: str, context: str
    ) -> str:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise MorningReportError(
                f"{context}: missing required field {field}"
            )
        return MorningReportGenerator._single_line(value)

    @staticmethod
    def _text_or_default(value: Any, default: str) -> str:
        if not isinstance(value, str) or not value.strip():
            return default
        return MorningReportGenerator._single_line(value)

    @staticmethod
    def _nonnegative_integer(value: Any, context: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise MorningReportError(f"{context} must be a nonnegative integer")
        return value

    @staticmethod
    def _check_count(
        payload: dict[str, Any],
        count_field: str,
        records: list[dict[str, Any]],
        context: str,
    ) -> None:
        if payload.get(count_field) != len(records):
            raise MorningReportError(
                f"{context} Registry count does not match its record array"
            )

    @staticmethod
    def _records(
        payload: dict[str, Any], field: str, context: str
    ) -> list[dict[str, Any]]:
        records = payload.get(field)
        if not isinstance(records, list) or not all(
            isinstance(record, dict) for record in records
        ):
            raise MorningReportError(f"{context} must contain a {field} array")
        return records

    @staticmethod
    def _load_json(path: Path, context: str) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MorningReportError(f"Unable to read {context}: {path}") from exc
        if not isinstance(payload, dict):
            raise MorningReportError(f"{context} must be a JSON object")
        return payload

    @staticmethod
    def _single_line(value: str) -> str:
        return " ".join(value.split())

    @staticmethod
    def _render_refs(values: list[str]) -> str:
        if not values:
            return "None"
        return ", ".join(MorningReportGenerator._single_line(value) for value in values)

    @staticmethod
    def _render(
        *,
        generated_time: str,
        repository_version: str,
        validation_status: str,
        prediction: dict[str, Any],
        counts: dict[str, int],
        references: dict[str, list[str]],
        errors: int,
        warnings: int,
        pending: dict[str, int],
        verified_case_summary: dict[str, int],
    ) -> str:
        repository_note = (
            "Repository validation is current."
            if validation_status == "PASS"
            else "Repository validation requires review."
        )
        lines = [
            "# Auto Radar Morning Report",
            "",
            "## System",
            "",
            f"- Generated Time: {generated_time}",
            f"- Repository Version: {repository_version}",
            f"- Validation Status: {validation_status}",
            "",
            "## Prediction",
            "",
            f"- Prediction ID: {prediction['id']}",
            f"- Prediction Status: {prediction['status']}",
            f"- Market: {prediction['market']}",
            f"- Generated At: {prediction['generated_at']}",
            "",
            "## Knowledge Summary",
            "",
            f"- Case Count: {counts['Case']}",
            f"- Pattern Count: {counts['Pattern']}",
            f"- Experience Count: {counts['Experience']}",
            f"- Playbook Count: {counts['Playbook']}",
            "",
            "## Active References",
            "",
            f"- Referenced Cases: {MorningReportGenerator._render_refs(references['Case'])}",
            f"- Referenced Patterns: {MorningReportGenerator._render_refs(references['Pattern'])}",
            f"- Referenced Experiences: {MorningReportGenerator._render_refs(references['Experience'])}",
            f"- Referenced Playbooks: {MorningReportGenerator._render_refs(references['Playbook'])}",
            "",
            "## Repository Health",
            "",
            f"- Validation: {validation_status}",
            f"- Errors: {errors}",
            f"- Warnings: {warnings}",
            "",
            "## Pending Review",
            "",
            f"- Outcome Pending: {pending['Outcome']}",
            f"- Evaluation Pending: {pending['Evaluation']}",
            f"- Review Pending: {pending['Review']}",
            "",
            "## Verified Case Summary",
            "",
            f"- Approved: {verified_case_summary['Approved']}",
            f"- Rejected: {verified_case_summary['Rejected']}",
            f"- Pending: {verified_case_summary['Pending']}",
            f"- Verified Count: {verified_case_summary['Verified']}",
            "",
            "## Notes",
            "",
            f"- {repository_note}",
            "",
        ]
        return "\n".join(lines)

    def _write_report(self, report: str) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.output_path.with_suffix(
            f"{self.output_path.suffix}.tmp"
        )
        try:
            temporary_path.write_text(report, encoding="utf-8")
            temporary_path.replace(self.output_path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise MorningReportError(
                f"Unable to write Morning Report: {self.output_path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the read-only Auto Radar Morning Report."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    generator = MorningReportGenerator()
    generator.generate()
    print(f"Morning Report: {generator.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
