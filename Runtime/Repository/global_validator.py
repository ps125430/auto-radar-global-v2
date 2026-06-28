"""Global fail-fast validator for all repository entities.

This module validates repository files and references only. It provides no
Prediction, Decision, Learning, trading, strategy, or scoring behavior.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from Scripts.Repository import (
    EvidenceRepository,
    ExperienceRepository,
    GraphRepository,
    OutcomeReviewRepository,
    PatternRepository,
    PlaybookRepository,
    PredictionRepository,
)

from .case_repository import CaseRepository


class GlobalValidationError(RuntimeError):
    """Raised after the first global repository validation failure."""


class GlobalRepositoryValidator:
    """Single entry point for repository-wide validation."""

    CHECKED_MODULES = (
        "Evidence",
        "Case",
        "Pattern",
        "Experience",
        "Graph",
        "Playbook",
        "Prediction",
        "Outcome",
        "OutcomeEvaluation",
        "DailyReview",
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
            or self.repository_root
            / "Runtime"
            / "Repository"
            / "index"
            / "validation_report.json"
        )
        self.schema_paths = {
            "Evidence": self.repository_root
            / "Schemas"
            / "Evidence"
            / "evidence.schema.json",
            "Case": self.repository_root
            / "Schemas"
            / "CaseLibrary"
            / "case_quality.schema.json",
            "Pattern": self.repository_root
            / "Schemas"
            / "Pattern"
            / "pattern.schema.json",
            "Experience": self.repository_root
            / "Schemas"
            / "Experience"
            / "experience.schema.json",
            "Graph": self.repository_root
            / "Schemas"
            / "Graph"
            / "graph.schema.json",
            "Playbook": self.repository_root
            / "Schemas"
            / "Playbook"
            / "playbook.schema.json",
            "Prediction": self.repository_root
            / "Schemas"
            / "Prediction"
            / "prediction.schema.json",
            "Outcome": self.repository_root
            / "Schemas"
            / "Outcome"
            / "outcome.schema.json",
            "OutcomeEvaluation": self.repository_root
            / "Schemas"
            / "OutcomeEvaluation"
            / "outcome_evaluation.schema.json",
            "DailyReview": self.repository_root
            / "Schemas"
            / "DailyDecision"
            / "review_record.schema.json",
        }
        self.index_specs = {
            "Evidence": self._index_spec(
                "Runtime/Repository/index/evidence_registry.json",
                "evidence",
                "evidence_count",
                "id",
            ),
            "Case": self._index_spec(
                "Runtime/Repository/index/case_index.json",
                "cases",
                "case_count",
                "id",
            ),
            "Pattern": self._index_spec(
                "Knowledge/Pattern/index.json",
                "patterns",
                "pattern_count",
                "id",
            ),
            "Experience": self._index_spec(
                "Knowledge/Experience/index.json",
                "experiences",
                "experience_count",
                "id",
            ),
            "Graph": self._index_spec(
                "Knowledge/Graph/index.json",
                "edges",
                "edge_count",
                None,
            ),
            "Playbook": self._index_spec(
                "Knowledge/Playbook/index.json",
                "playbooks",
                "playbook_count",
                "id",
            ),
            "Prediction": self._index_spec(
                "Runtime/Repository/index/prediction_registry.json",
                "predictions",
                "prediction_count",
                "id",
            ),
            "Outcome": self._index_spec(
                "Knowledge/Outcome/index.json",
                "outcomes",
                "outcome_count",
                "id",
            ),
            "OutcomeEvaluation": self._index_spec(
                "Knowledge/OutcomeEvaluation/index.json",
                "evaluations",
                "evaluation_count",
                "id",
            ),
            "DailyReview": self._index_spec(
                "Knowledge/DailyReview/index.json",
                "reviews",
                "review_count",
                "id",
            ),
        }
        self._index_payloads: dict[str, dict[str, Any]] = {}
        self._total_entities = 0
        self._warnings = [
            (
                "Confidence Repository is not established; confidence_ref is "
                "validated for format only when present."
            )
        ]

    def _index_spec(
        self,
        relative_path: str,
        records_key: str,
        count_key: str,
        id_key: str | None,
    ) -> dict[str, Any]:
        return {
            "path": self.repository_root / relative_path,
            "records_key": records_key,
            "count_key": count_key,
            "id_key": id_key,
        }

    def validate_all(self) -> dict[str, Any]:
        """Run every validation stage and write a PASS or FAIL report."""
        self._index_payloads = {}
        self._total_entities = 0
        try:
            self.validate_schemas()
            self.validate_indices()
            self.validate_registries()
            self.validate_cross_references()
        except Exception as exc:
            report = self._build_report(
                validation_status="FAIL",
                errors=[str(exc)],
            )
            self._write_report(report)
            if isinstance(exc, GlobalValidationError):
                raise
            raise GlobalValidationError(str(exc)) from exc

        report = self._build_report(validation_status="PASS", errors=[])
        self._write_report(report)
        return report

    def validate_schemas(self) -> bool:
        """Validate that every covered module has a readable schema."""
        for module in self.CHECKED_MODULES:
            path = Path(self.schema_paths[module])
            if not path.is_file():
                raise GlobalValidationError(
                    f"{module}: missing schema {path}"
                )
            try:
                schema = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                raise GlobalValidationError(
                    f"{module}: invalid schema JSON {path}"
                ) from exc
            if not isinstance(schema, dict):
                raise GlobalValidationError(
                    f"{module}: schema root must be an object"
                )
            if module == "Case":
                if (
                    schema.get("status") != "schema_candidate"
                    or not isinstance(schema.get("schema"), dict)
                ):
                    raise GlobalValidationError(
                        "Case: invalid schema candidate structure"
                    )
            elif schema.get("$schema") != (
                "https://json-schema.org/draft/2020-12/schema"
            ):
                raise GlobalValidationError(
                    f"{module}: schema must use JSON Schema 2020-12"
                )
        return True

    def validate_indices(self) -> bool:
        """Validate required index files, record arrays, counts, and IDs."""
        payloads: dict[str, dict[str, Any]] = {}
        total_entities = 0

        for module in self.CHECKED_MODULES:
            spec = self.index_specs[module]
            path = Path(spec["path"])
            if not path.is_file():
                raise GlobalValidationError(
                    f"{module}: missing index.json at {path}"
                )
            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                raise GlobalValidationError(
                    f"{module}: invalid index JSON {path}"
                ) from exc
            if not isinstance(payload, dict):
                raise GlobalValidationError(
                    f"{module}: index root must be an object"
                )

            records = payload.get(spec["records_key"])
            if not isinstance(records, list):
                raise GlobalValidationError(
                    f"{module}: index must contain "
                    f"{spec['records_key']} array"
                )
            if payload.get(spec["count_key"]) != len(records):
                raise GlobalValidationError(
                    f"{module}: index count does not match record array"
                )

            keys = [
                self._registry_key(module, record, spec["id_key"])
                for record in records
            ]
            if len(keys) != len(set(keys)):
                raise GlobalValidationError(
                    f"{module}: duplicate ID across registry"
                )

            payloads[module] = payload
            total_entities += len(records)

        self._index_payloads = payloads
        self._total_entities = total_entities
        return True

    def validate_registries(self) -> bool:
        """Compare every registry with its source files and lifecycle folder."""
        if not self._index_payloads:
            self.validate_indices()

        for module in self.CHECKED_MODULES:
            spec = self.index_specs[module]
            records = self._index_payloads[module][spec["records_key"]]
            registry_keys = {
                self._registry_key(module, record, spec["id_key"])
                for record in records
            }
            source_keys = self._source_keys(module)

            missing_files = registry_keys - source_keys
            if missing_files:
                raise GlobalValidationError(
                    f"{module}: registry item points to missing file: "
                    f"{self._format_keys(missing_files)}"
                )

            unindexed_files = source_keys - registry_keys
            if unindexed_files:
                raise GlobalValidationError(
                    f"{module}: entity file is missing from registry: "
                    f"{self._format_keys(unindexed_files)}"
                )
        return True

    def validate_cross_references(self) -> bool:
        """Run module validators in dependency order with fail-fast behavior."""
        root = self.repository_root
        EvidenceRepository(
            evidence_root=root / "Knowledge" / "Evidence",
            schema_path=self.schema_paths["Evidence"],
            registry_path=self.index_specs["Evidence"]["path"],
        )
        CaseRepository(
            case_root=root / "Knowledge" / "CaseLibrary",
            schema_path=self.schema_paths["Case"],
            index_path=self.index_specs["Case"]["path"],
        )
        PatternRepository(
            pattern_root=root / "Knowledge" / "Pattern",
            schema_path=self.schema_paths["Pattern"],
            case_index_path=self.index_specs["Case"]["path"],
            index_path=self.index_specs["Pattern"]["path"],
        )
        ExperienceRepository(
            experience_root=root / "Knowledge" / "Experience",
            schema_path=self.schema_paths["Experience"],
            pattern_index_path=self.index_specs["Pattern"]["path"],
            case_index_path=self.index_specs["Case"]["path"],
            index_path=self.index_specs["Experience"]["path"],
        )
        GraphRepository(
            graph_root=root / "Knowledge" / "Graph",
            schema_path=self.schema_paths["Graph"],
            index_path=self.index_specs["Graph"]["path"],
            registry_paths={
                "Case": (self.index_specs["Case"]["path"], "cases"),
                "Pattern": (self.index_specs["Pattern"]["path"], "patterns"),
                "Experience": (
                    self.index_specs["Experience"]["path"],
                    "experiences",
                ),
                "Playbook": (
                    self.index_specs["Playbook"]["path"],
                    "playbooks",
                ),
                "Rule": None,
                "Evidence": (
                    self.index_specs["Evidence"]["path"],
                    "evidence",
                ),
            },
        )
        PlaybookRepository(
            playbook_root=root / "Knowledge" / "Playbook",
            schema_path=self.schema_paths["Playbook"],
            graph_index_path=self.index_specs["Graph"]["path"],
            index_path=self.index_specs["Playbook"]["path"],
        )
        PredictionRepository(
            prediction_root=root / "Knowledge" / "Prediction",
            schema_path=self.schema_paths["Prediction"],
            registry_path=self.index_specs["Prediction"]["path"],
            playbook_index_path=self.index_specs["Playbook"]["path"],
            experience_index_path=self.index_specs["Experience"]["path"],
            pattern_index_path=self.index_specs["Pattern"]["path"],
        )
        OutcomeReviewRepository(
            outcome_root=root / "Knowledge" / "Outcome",
            evaluation_root=root / "Knowledge" / "OutcomeEvaluation",
            review_root=root / "Knowledge" / "DailyReview",
            outcome_schema_path=self.schema_paths["Outcome"],
            evaluation_schema_path=self.schema_paths["OutcomeEvaluation"],
            review_schema_path=self.schema_paths["DailyReview"],
        )
        self._validate_prediction_consumers()
        return True

    def _source_keys(self, module: str) -> set[Any]:
        if module == "Evidence":
            repository = EvidenceRepository(
                evidence_root=self.repository_root / "Knowledge" / "Evidence",
                schema_path=self.schema_paths["Evidence"],
                registry_path=self.index_specs["Evidence"]["path"],
                auto_start=False,
            )
            repository.validate_template(
                self.repository_root / "Knowledge" / "Evidence" / "TEMPLATE.md"
            )
            keys = [
                repository.load_evidence(path).evidence_id
                for folder in ("incoming", "verified", "rejected", "archive")
                for path in sorted(
                    (
                        self.repository_root
                        / "Knowledge"
                        / "Evidence"
                        / folder
                    ).glob("*.md")
                )
            ]
            return self._unique_source_keys(module, keys)

        if module == "Case":
            repository = CaseRepository(
                case_root=self.repository_root / "Knowledge" / "CaseLibrary",
                schema_path=self.schema_paths["Case"],
                index_path=self.index_specs["Case"]["path"],
                auto_start=False,
            )
            keys = [
                repository.load_case(path).id
                for path in sorted(
                    (self.repository_root / "Knowledge" / "CaseLibrary").rglob(
                        "CASE-*.md"
                    )
                )
                if path.name != "CASE_INDEX.md"
            ]
            return self._unique_source_keys(module, keys)

        if module == "Prediction":
            repository = PredictionRepository(
                prediction_root=self.repository_root / "Knowledge" / "Prediction",
                schema_path=self.schema_paths["Prediction"],
                registry_path=self.index_specs["Prediction"]["path"],
                playbook_index_path=self.index_specs["Playbook"]["path"],
                experience_index_path=self.index_specs["Experience"]["path"],
                pattern_index_path=self.index_specs["Pattern"]["path"],
                auto_start=False,
            )
            repository.validate_template(
                self.repository_root / "Knowledge" / "Prediction" / "TEMPLATE.md"
            )
            keys = [
                repository.load_snapshot(path).prediction_id
                for folder in ("daily", "archive")
                for path in sorted(
                    (
                        self.repository_root
                        / "Knowledge"
                        / "Prediction"
                        / folder
                    ).glob("*.md")
                )
            ]
            return self._unique_source_keys(module, keys)

        source_specs = {
            "Pattern": (
                self.repository_root / "Knowledge" / "Pattern",
                ("Draft", "Candidate", "Verified", "Deprecated", "Archived"),
                "pattern_id",
            ),
            "Experience": (
                self.repository_root / "Knowledge" / "Experience",
                ("Draft", "Candidate", "Verified", "Deprecated", "Archived"),
                "experience_id",
            ),
            "Playbook": (
                self.repository_root / "Knowledge" / "Playbook",
                (
                    "Draft",
                    "Candidate",
                    "Shadow",
                    "Verified",
                    "Deprecated",
                    "Archived",
                ),
                "playbook_id",
            ),
            "Outcome": (
                self.repository_root / "Knowledge" / "Outcome",
                ("Records",),
                "outcome_id",
            ),
            "OutcomeEvaluation": (
                self.repository_root / "Knowledge" / "OutcomeEvaluation",
                ("Records",),
                "evaluation_id",
            ),
            "DailyReview": (
                self.repository_root / "Knowledge" / "DailyReview",
                ("Records",),
                "review_id",
            ),
        }

        if module == "Graph":
            keys: list[tuple[str, str, str]] = []
            edges_root = self.repository_root / "Knowledge" / "Graph" / "Edges"
            for path in sorted(edges_root.glob("*.json")):
                payload = self._read_source_json(module, path)
                try:
                    key = (
                        payload["node_id"],
                        payload["relation"],
                        payload["target"],
                    )
                except KeyError as exc:
                    raise GlobalValidationError(
                        f"Graph: source file missing edge key {path}"
                    ) from exc
                keys.append(key)
            return self._unique_source_keys(module, keys)

        root, folders, id_field = source_specs[module]
        keys: list[str] = []
        for folder in folders:
            folder_path = root / folder
            if not folder_path.is_dir():
                raise GlobalValidationError(
                    f"{module}: missing repository folder {folder_path}"
                )
            for path in sorted(folder_path.glob("*.json")):
                payload = self._read_source_json(module, path)
                entity_id = payload.get(id_field)
                if not isinstance(entity_id, str):
                    raise GlobalValidationError(
                        f"{module}: source file missing {id_field}: {path}"
                    )
                if folder != "Records" and payload.get("status") != folder:
                    raise GlobalValidationError(
                        f"{module}: entity status not aligned with folder "
                        f"lifecycle: {path}"
                    )
                keys.append(entity_id)
        return self._unique_source_keys(module, keys)

    def _validate_prediction_consumers(self) -> None:
        prediction_ids = {
            self._registry_key("Prediction", record, "id")
            for record in self._read_index_records("Prediction")
        }
        for module in ("Outcome", "OutcomeEvaluation", "DailyReview"):
            for record in self._read_index_records(module):
                prediction_ref = record.get("prediction_ref")
                if not isinstance(prediction_ref, str):
                    raise GlobalValidationError(
                        f"{module}: registry item missing prediction_ref"
                    )
                if prediction_ref not in prediction_ids:
                    raise GlobalValidationError(
                        f"{module}: missing Prediction reference {prediction_ref}"
                    )

    def _read_index_records(self, module: str) -> list[dict[str, Any]]:
        spec = self.index_specs[module]
        try:
            payload = json.loads(
                Path(spec["path"]).read_text(encoding="utf-8-sig")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise GlobalValidationError(
                f"{module}: unable to reload registry"
            ) from exc
        records = payload.get(spec["records_key"])
        if not isinstance(records, list) or not all(
            isinstance(record, dict) for record in records
        ):
            raise GlobalValidationError(
                f"{module}: invalid registry record array"
            )
        return records

    @staticmethod
    def _read_source_json(module: str, path: Path) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise GlobalValidationError(
                f"{module}: invalid entity JSON {path}"
            ) from exc
        if not isinstance(payload, dict):
            raise GlobalValidationError(
                f"{module}: entity root must be object {path}"
            )
        return payload

    @staticmethod
    def _unique_source_keys(module: str, keys: list[Any]) -> set[Any]:
        if len(keys) != len(set(keys)):
            raise GlobalValidationError(
                f"{module}: duplicate ID across source files"
            )
        return set(keys)

    @staticmethod
    def _registry_key(
        module: str, record: Any, id_key: str | None
    ) -> Any:
        if not isinstance(record, dict):
            raise GlobalValidationError(
                f"{module}: every registry item must be an object"
            )
        if module == "Graph":
            try:
                values = (
                    record["node_id"],
                    record["relation"],
                    record["target"],
                )
            except KeyError as exc:
                raise GlobalValidationError(
                    "Graph: registry item missing edge key"
                ) from exc
            if not all(isinstance(value, str) for value in values):
                raise GlobalValidationError(
                    "Graph: registry edge key values must be strings"
                )
            return values

        value = record.get(id_key)
        if not isinstance(value, str):
            raise GlobalValidationError(
                f"{module}: registry item missing string {id_key}"
            )
        return value

    @staticmethod
    def _format_keys(keys: set[Any]) -> str:
        return ", ".join(str(key) for key in sorted(keys, key=str))

    def _build_report(
        self, validation_status: str, errors: list[str]
    ) -> dict[str, Any]:
        return {
            "validation_status": validation_status,
            "checked_modules": list(self.CHECKED_MODULES),
            "total_entities": self._total_entities,
            "total_errors": len(errors),
            "total_warnings": len(self._warnings),
            "errors": errors,
            "warnings": list(self._warnings),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _write_report(self, report: dict[str, Any]) -> None:
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.report_path.with_suffix(
            f"{self.report_path.suffix}.tmp"
        )
        try:
            temporary_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(self.report_path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise GlobalValidationError(
                f"Unable to write validation report: {self.report_path}"
            ) from exc


def validate_all(
    repository_root: Path | str | None = None,
    report_path: Path | str | None = None,
) -> dict[str, Any]:
    """Run global validation through the canonical module-level entry."""
    return GlobalRepositoryValidator(repository_root, report_path).validate_all()


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate all Auto Radar repository entities."
    )
    parser.parse_args(list(argv) if argv is not None else None)
    try:
        report = validate_all()
    except GlobalValidationError as exc:
        print(f"Global repository validation failed: {exc}")
        return 1
    print(
        "Global repository validation passed: "
        f"{report['total_entities']} entities, "
        f"{report['total_warnings']} warning(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
