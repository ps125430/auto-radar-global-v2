"""Generate a read-only Markdown summary from repository registries."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Iterable


class ReportGenerationError(RuntimeError):
    """Raised when required report input cannot be read safely."""


class DailyReportGenerator:
    """Load the latest Prediction record and render repository content."""

    def __init__(
        self,
        repository_root: Path | str | None = None,
        output_path: Path | str | None = None,
        *,
        report_date: date | None = None,
    ) -> None:
        self.repository_root = Path(
            repository_root or Path(__file__).resolve().parents[2]
        )
        self.output_path = Path(
            output_path
            or self.repository_root / "Reports" / "Daily" / "latest_report.md"
        )
        self.report_date = report_date or date.today()
        self.paths = {
            "Prediction": self.repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "prediction_registry.json",
            "Playbook": self.repository_root
            / "Knowledge"
            / "Playbook"
            / "index.json",
            "Experience": self.repository_root
            / "Knowledge"
            / "Experience"
            / "index.json",
            "Pattern": self.repository_root
            / "Knowledge"
            / "Pattern"
            / "index.json",
            "Case": self.repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "case_index.json",
            "Validation": self.repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "validation_report.json",
        }

    def generate(self) -> str:
        """Render and persist the latest read-only daily report."""
        prediction_registry = self._load_json(
            self.paths["Prediction"], "Prediction Registry"
        )
        predictions = self._record_array(
            prediction_registry, "predictions", "Prediction Registry"
        )
        if prediction_registry.get("prediction_count") != len(predictions):
            raise ReportGenerationError(
                "Prediction Registry count does not match its record array"
            )
        prediction = self._latest_prediction(predictions)

        missing: list[str] = []
        if prediction is None:
            report = self._render_empty_report(missing)
        else:
            report = self._render_prediction_report(prediction, missing)

        self._write_report(report)
        return report

    def _render_empty_report(self, missing: list[str]) -> str:
        validation_status = self._validation_status(missing)
        return self._render(
            report_date=self.report_date.isoformat(),
            prediction_id="N/A",
            prediction_status="No Snapshot",
            playbooks=[],
            experiences=[],
            patterns=[],
            cases=[],
            validation_status=validation_status,
            missing=missing,
            notes=["No Prediction Snapshot is currently registered."],
        )

    def _render_prediction_report(
        self, prediction: dict[str, Any], missing: list[str]
    ) -> str:
        prediction_id = self._required_text(
            prediction, "id", "Prediction Registry item"
        )
        prediction_date = self._required_text(
            prediction, "prediction_date", prediction_id
        )
        prediction_status = self._required_text(
            prediction, "status", prediction_id
        )

        playbook_refs = self._reference_list(
            prediction, "playbook_refs", prediction_id
        )
        experience_refs = self._reference_list(
            prediction, "experience_refs", prediction_id
        )
        pattern_refs = self._reference_list(
            prediction, "pattern_refs", prediction_id
        )

        playbooks = self._resolve_references(
            "Playbook", "playbooks", playbook_refs, missing
        )
        experiences = self._resolve_references(
            "Experience", "experiences", experience_refs, missing
        )
        patterns = self._resolve_references(
            "Pattern", "patterns", pattern_refs, missing
        )

        case_refs = self._collect_case_refs(
            experience_refs, pattern_refs, missing
        )
        cases = self._resolve_references(
            "Case", "cases", sorted(case_refs), missing
        )
        validation_status = self._validation_status(missing)
        notes = self._prediction_notes(prediction, missing)
        if not notes:
            notes = ["Generated from repository content only."]

        return self._render(
            report_date=self.report_date.isoformat(),
            prediction_id=prediction_id,
            prediction_status=prediction_status,
            playbooks=playbooks,
            experiences=experiences,
            patterns=patterns,
            cases=cases,
            validation_status=validation_status,
            missing=missing,
            notes=notes,
        )

    @staticmethod
    def _latest_prediction(
        predictions: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if not predictions:
            return None
        for record in predictions:
            if not isinstance(record, dict):
                raise ReportGenerationError(
                    "Prediction Registry items must be objects"
                )
        return max(
            predictions,
            key=lambda record: (
                str(record.get("prediction_date", "")),
                str(record.get("generated_at", "")),
                str(record.get("id", "")),
            ),
        )

    def _resolve_references(
        self,
        entity_name: str,
        records_key: str,
        references: list[str],
        missing: list[str],
    ) -> list[str]:
        registry = self._load_json(
            self.paths[entity_name], f"{entity_name} Registry"
        )
        records = self._record_array(
            registry, records_key, f"{entity_name} Registry"
        )
        by_id: dict[str, dict[str, Any]] = {}
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str):
                raise ReportGenerationError(
                    f"{entity_name} Registry item must contain a string id"
                )
            by_id[record["id"]] = record

        resolved: list[str] = []
        for reference in references:
            record = by_id.get(reference)
            if record is None:
                missing.append(f"{entity_name}: {reference}")
                continue
            title = record.get("title")
            if isinstance(title, str) and title.strip():
                resolved.append(f"{reference} - {self._single_line(title)}")
            else:
                resolved.append(reference)
        return resolved

    def _collect_case_refs(
        self,
        experience_refs: list[str],
        pattern_refs: list[str],
        missing: list[str],
    ) -> set[str]:
        cases: set[str] = set()
        source_specs = (
            (
                "Experience",
                self.repository_root / "Knowledge" / "Experience",
                "experience_id",
                set(experience_refs),
            ),
            (
                "Pattern",
                self.repository_root / "Knowledge" / "Pattern",
                "pattern_id",
                set(pattern_refs),
            ),
        )
        for entity_name, root, id_field, requested in source_specs:
            if not requested:
                continue
            found: set[str] = set()
            for path in sorted(root.rglob("*.json")):
                if path.name == "index.json":
                    continue
                payload = self._load_json(path, f"{entity_name} entity")
                entity_id = payload.get(id_field)
                if entity_id not in requested:
                    continue
                found.add(entity_id)
                source_cases = payload.get("source_cases", [])
                if not isinstance(source_cases, list) or not all(
                    isinstance(case_id, str) for case_id in source_cases
                ):
                    missing.append(f"{entity_name} source_cases: {entity_id}")
                    continue
                cases.update(source_cases)
            for unresolved in sorted(requested - found):
                missing.append(f"{entity_name} source file: {unresolved}")
        return cases

    def _validation_status(self, missing: list[str]) -> str:
        try:
            report = self._load_json(
                self.paths["Validation"], "Validation Report"
            )
        except ReportGenerationError:
            missing.append("Validation Report")
            return "Unavailable"
        status = report.get("validation_status")
        if not isinstance(status, str) or not status.strip():
            missing.append("Validation status")
            return "Unavailable"
        return self._single_line(status)

    def _prediction_notes(
        self, prediction: dict[str, Any], missing: list[str]
    ) -> list[str]:
        source_file = prediction.get("source_file")
        if not isinstance(source_file, str) or not source_file.strip():
            missing.append("Prediction source file")
            return []

        root = (self.repository_root / "Knowledge" / "Prediction").resolve()
        path = (root / source_file).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            missing.append("Prediction source path")
            return []
        if not path.is_file():
            missing.append(f"Prediction source file: {source_file}")
            return []

        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            missing.append(f"Prediction source file: {source_file}")
            return []

        marker = "## Notes"
        if marker not in content:
            return []
        section = content.split(marker, 1)[1]
        next_heading = section.find("\n## ")
        if next_heading >= 0:
            section = section[:next_heading]
        return [
            self._single_line(line.lstrip("- ").strip())
            for line in section.splitlines()
            if line.strip() and self._single_line(line.lstrip("- ").strip())
        ]

    @staticmethod
    def _reference_list(
        record: dict[str, Any], field: str, context: str
    ) -> list[str]:
        value = record.get(field, [])
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ReportGenerationError(
                f"{context}: {field} must be an array of strings"
            )
        return value

    @staticmethod
    def _required_text(
        record: dict[str, Any], field: str, context: str
    ) -> str:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ReportGenerationError(
                f"{context}: missing required field {field}"
            )
        return DailyReportGenerator._single_line(value)

    @staticmethod
    def _record_array(
        payload: dict[str, Any], field: str, context: str
    ) -> list[dict[str, Any]]:
        value = payload.get(field)
        if not isinstance(value, list):
            raise ReportGenerationError(
                f"{context}: missing {field} array"
            )
        return value

    @staticmethod
    def _load_json(path: Path, context: str) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ReportGenerationError(
                f"Unable to read {context}: {path}"
            ) from exc
        if not isinstance(payload, dict):
            raise ReportGenerationError(f"{context} must be a JSON object")
        return payload

    @staticmethod
    def _single_line(value: str) -> str:
        return " ".join(value.split())

    @staticmethod
    def _list_lines(values: list[str]) -> list[str]:
        if not values:
            return ["- None"]
        return [f"- {DailyReportGenerator._single_line(value)}" for value in values]

    def _render(
        self,
        *,
        report_date: str,
        prediction_id: str,
        prediction_status: str,
        playbooks: list[str],
        experiences: list[str],
        patterns: list[str],
        cases: list[str],
        validation_status: str,
        missing: list[str],
        notes: list[str],
    ) -> str:
        sections = [
            "# Auto Radar Daily Report",
            "",
            "## Report Date",
            "",
            self._single_line(report_date),
            "",
            "## Prediction ID",
            "",
            self._single_line(prediction_id),
            "",
            "## Prediction Status",
            "",
            self._single_line(prediction_status),
            "",
            "## Referenced Playbooks",
            "",
            *self._list_lines(playbooks),
            "",
            "## Referenced Experiences",
            "",
            *self._list_lines(experiences),
            "",
            "## Referenced Patterns",
            "",
            *self._list_lines(patterns),
            "",
            "## Referenced Cases",
            "",
            *self._list_lines(cases),
            "",
            "## Validation Status",
            "",
            self._single_line(validation_status),
            "",
            "## Missing References",
            "",
            *self._list_lines(sorted(set(missing))),
            "",
            "## Notes",
            "",
            *self._list_lines(notes),
            "",
        ]
        return "\n".join(sections)

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
            raise ReportGenerationError(
                f"Unable to write Daily Report: {self.output_path}"
            ) from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the read-only Auto Radar Daily Report."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    generator = DailyReportGenerator()
    generator.generate()
    print(f"Daily Report: {generator.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
