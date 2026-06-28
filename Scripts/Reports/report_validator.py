"""Validate Morning Report structure and repository references."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable


class ReportValidationError(RuntimeError):
    """Raised when a Morning Report violates its presentation contract."""


class MorningReportValidator:
    """Read-only validator for the Morning Report Markdown artifact."""

    REQUIRED_SECTIONS = (
        "# Auto Radar Morning Report",
        "## System",
        "## Prediction",
        "## Knowledge Summary",
        "## Active References",
        "## Repository Health",
        "## Pending Review",
        "## Notes",
    )
    REQUIRED_FIELDS = (
        "Generated Time",
        "Repository Version",
        "Validation Status",
        "Prediction ID",
        "Prediction Status",
        "Market",
        "Generated At",
        "Case Count",
        "Pattern Count",
        "Experience Count",
        "Playbook Count",
        "Referenced Cases",
        "Referenced Patterns",
        "Referenced Experiences",
        "Referenced Playbooks",
        "Validation",
        "Errors",
        "Warnings",
        "Outcome Pending",
        "Evaluation Pending",
        "Review Pending",
    )
    PROHIBITED_WORDS = (
        "buy",
        "sell",
        "watch",
        "wait",
        "signal",
        "strategy",
    )

    def __init__(
        self,
        repository_root: Path | str | None = None,
        report_path: Path | str | None = None,
    ) -> None:
        self.repository_root = Path(
            repository_root or Path(__file__).resolve().parents[2]
        )
        self.report_path = Path(
            report_path
            or self.repository_root / "Reports" / "Morning" / "latest.md"
        )
        self.registry_specs = {
            "Prediction ID": (
                self.repository_root
                / "Runtime"
                / "Repository"
                / "index"
                / "prediction_registry.json",
                "predictions",
            ),
            "Referenced Cases": (
                self.repository_root
                / "Runtime"
                / "Repository"
                / "index"
                / "case_index.json",
                "cases",
            ),
            "Referenced Patterns": (
                self.repository_root / "Knowledge" / "Pattern" / "index.json",
                "patterns",
            ),
            "Referenced Experiences": (
                self.repository_root / "Knowledge" / "Experience" / "index.json",
                "experiences",
            ),
            "Referenced Playbooks": (
                self.repository_root / "Knowledge" / "Playbook" / "index.json",
                "playbooks",
            ),
        }

    def validate(self) -> dict[str, Any]:
        """Validate existence, sections, fields, terms, and entity references."""
        if not self.report_path.is_file():
            raise ReportValidationError(
                f"Morning Report does not exist: {self.report_path}"
            )
        try:
            markdown = self.report_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ReportValidationError(
                f"Unable to read Morning Report: {self.report_path}"
            ) from exc

        for section in self.REQUIRED_SECTIONS:
            if section not in markdown:
                raise ReportValidationError(f"Missing report section: {section}")

        fields = self._parse_fields(markdown)
        for field in self.REQUIRED_FIELDS:
            if field not in fields:
                raise ReportValidationError(f"Missing report field: {field}")

        for word in self.PROHIBITED_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", markdown, re.IGNORECASE):
                raise ReportValidationError(
                    f"Prohibited report term: {word}"
                )

        checked_references = 0
        for field, (path, records_key) in self.registry_specs.items():
            value = fields[field]
            references = (
                []
                if value in {"None", "N/A"}
                else [item.strip() for item in value.split(",") if item.strip()]
            )
            if not references:
                continue
            available = self._registry_ids(path, records_key)
            missing = sorted(set(references) - available)
            if missing:
                raise ReportValidationError(
                    f"{field} contains missing references: {', '.join(missing)}"
                )
            checked_references += len(references)

        return {
            "validation_status": "PASS",
            "sections_checked": len(self.REQUIRED_SECTIONS),
            "fields_checked": len(self.REQUIRED_FIELDS),
            "references_checked": checked_references,
        }

    @staticmethod
    def _parse_fields(markdown: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for line in markdown.splitlines():
            if not line.startswith("- ") or ": " not in line:
                continue
            key, value = line[2:].split(": ", 1)
            if key in fields:
                raise ReportValidationError(
                    f"Duplicate report field: {key}"
                )
            fields[key] = value.strip()
        return fields

    @staticmethod
    def _registry_ids(path: Path, records_key: str) -> set[str]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ReportValidationError(
                f"Unable to read Registry: {path}"
            ) from exc
        records = payload.get(records_key)
        if not isinstance(records, list):
            raise ReportValidationError(
                f"Registry must contain {records_key} array: {path}"
            )
        ids: list[str] = []
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str):
                raise ReportValidationError(
                    f"Registry item must contain string id: {path}"
                )
            ids.append(record["id"])
        if len(ids) != len(set(ids)):
            raise ReportValidationError(f"Registry contains duplicate IDs: {path}")
        return set(ids)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Auto Radar Morning Report."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    try:
        result = MorningReportValidator().validate()
    except ReportValidationError as exc:
        print(f"Morning Report validation failed: {exc}")
        return 1
    print(
        "Morning Report validation passed: "
        f"{result['sections_checked']} sections, "
        f"{result['references_checked']} references."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

