"""Manual Evidence ingestion for the isolated Sandbox."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class IngestionError(RuntimeError):
    """Raised on the first invalid Sandbox import or output."""


class EvidenceIngestionSandbox:
    """Convert manual Markdown, JSON, and YAML input into Sandbox Evidence."""

    FORMAT_BY_SUFFIX = {
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
    }

    def __init__(
        self,
        sandbox_root: Path | str | None = None,
        schema_path: Path | str | None = None,
        *,
        imported_at: datetime | None = None,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        self.sandbox_root = Path(sandbox_root or Path(__file__).resolve().parent)
        self.schema_path = Path(
            schema_path
            or repository_root / "Schemas" / "Evidence" / "evidence.schema.json"
        )
        self.imports_root = self.sandbox_root / "imports"
        self.processed_root = self.sandbox_root / "processed"
        self.failed_root = self.sandbox_root / "failed"
        self.manifest_path = self.sandbox_root / "ingestion_manifest.json"
        self.imported_at = imported_at or datetime.now(timezone.utc)
        self._schema = self._load_schema()

    def ingest_all(self, input_root: Path | str | None = None) -> dict[str, Any]:
        """Ingest all supported files from one manual input directory."""
        source_root = Path(input_root or self.imports_root)
        if not source_root.is_dir():
            raise IngestionError(f"Input directory does not exist: {source_root}")
        self.processed_root.mkdir(parents=True, exist_ok=True)
        self.failed_root.mkdir(parents=True, exist_ok=True)

        manifest = self._load_manifest()
        existing_import_ids = {
            self._manifest_text(record, "import_id") for record in manifest["imports"]
        }
        existing_evidence_ids = {
            record["output_evidence"]
            for record in manifest["imports"]
            if record.get("status") == "processed"
            and isinstance(record.get("output_evidence"), str)
        }

        files = sorted(path for path in source_root.iterdir() if path.is_file())
        if not files:
            return manifest

        seen_import_ids: set[str] = set()
        for path in files:
            import_id = path.stem
            if import_id in existing_import_ids or import_id in seen_import_ids:
                raise IngestionError(f"Duplicate import: {import_id}")
            seen_import_ids.add(import_id)

            try:
                record = self._ingest_one(path, import_id, existing_evidence_ids)
            except IngestionError as exc:
                failure = {
                    "import_id": import_id,
                    "source": str(path),
                    "imported_at": self.imported_at.isoformat(),
                    "format": self.FORMAT_BY_SUFFIX.get(
                        path.suffix.casefold(), "unsupported"
                    ),
                    "status": "failed",
                    "output_evidence": None,
                    "error": str(exc),
                }
                manifest["imports"].append(failure)
                self._write_manifest(manifest)
                self._copy_failed(path)
                raise

            manifest["imports"].append(record)
            existing_import_ids.add(import_id)
            existing_evidence_ids.add(record["output_evidence"])
            self._write_manifest(manifest)

        return manifest

    def validate_existing(self) -> dict[str, Any]:
        """Validate the Manifest and every generated Sandbox Evidence file."""
        manifest = self._load_manifest()
        import_ids: list[str] = []
        output_ids: list[str] = []

        for record in manifest["imports"]:
            import_id = self._manifest_text(record, "import_id")
            import_ids.append(import_id)
            status = self._manifest_text(record, "status")
            if status != "processed":
                raise IngestionError(
                    f"Manifest contains non-processed import: {import_id}"
                )
            output_evidence = self._manifest_text(record, "output_evidence")
            output_ids.append(output_evidence)
            output_path = self.processed_root / f"{output_evidence}.md"
            if not output_path.is_file():
                raise IngestionError(
                    f"Manifest output does not exist: {output_evidence}"
                )
            metadata, _ = self._parse_markdown(output_path)
            self._validate_evidence(metadata, output_path)
            if metadata["evidence_id"] != output_evidence:
                raise IngestionError(
                    f"Manifest output ID mismatch: {output_evidence}"
                )

        if len(import_ids) != len(set(import_ids)):
            raise IngestionError("Manifest contains duplicate import IDs")
        if len(output_ids) != len(set(output_ids)):
            raise IngestionError("Manifest contains duplicate Evidence IDs")
        return {
            "validation_status": "PASS",
            "imports_checked": len(import_ids),
            "outputs_checked": len(output_ids),
        }

    def _ingest_one(
        self,
        path: Path,
        import_id: str,
        existing_evidence_ids: set[str],
    ) -> dict[str, Any]:
        suffix = path.suffix.casefold()
        format_name = self.FORMAT_BY_SUFFIX.get(suffix)
        if format_name is None:
            raise IngestionError(f"Unsupported format: {path.suffix or '<none>'}")

        raw = self._load_input(path, format_name)
        self._require_input(raw, "title", path)
        self._require_input(raw, "timestamp", path)
        self._require_input(raw, "source", path)
        evidence_id = self._require_input(raw, "evidence_id", path)
        if evidence_id in existing_evidence_ids:
            raise IngestionError(f"Duplicate Evidence output: {evidence_id}")

        evidence = {
            "evidence_id": evidence_id,
            "source": raw["source"],
            "source_type": raw.get("source_type"),
            "published_at": raw["timestamp"],
            "collected_at": self.imported_at.isoformat(),
            "title": raw["title"],
            "summary": raw.get("summary"),
            "language": raw.get("language"),
            "region": raw.get("region"),
            "symbols": raw.get("symbols"),
            "tags": raw.get("tags"),
            "importance": raw.get("importance"),
            "reliability": raw.get("reliability"),
            "status": "Incoming",
            "model_impact": "evidence_only_not_production",
        }
        self._validate_evidence(evidence, path)

        output_path = self.processed_root / f"{evidence_id}.md"
        if output_path.exists():
            raise IngestionError(f"Output already exists: {evidence_id}")
        output_path.write_text(
            self._render_evidence(evidence),
            encoding="utf-8",
        )

        generated, _ = self._parse_markdown(output_path)
        self._validate_evidence(generated, output_path)
        if generated != evidence:
            output_path.unlink(missing_ok=True)
            raise IngestionError(f"Invalid output round trip: {evidence_id}")

        return {
            "import_id": import_id,
            "source": path.as_posix(),
            "imported_at": self.imported_at.isoformat(),
            "format": format_name,
            "status": "processed",
            "output_evidence": evidence_id,
        }

    def _load_input(self, path: Path, format_name: str) -> dict[str, Any]:
        if format_name == "json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                raise IngestionError(f"Invalid JSON input: {path}") from exc
        elif format_name == "markdown":
            payload, _ = self._parse_markdown(path)
        else:
            try:
                content = path.read_text(encoding="utf-8-sig")
            except OSError as exc:
                raise IngestionError(f"Unable to read YAML input: {path}") from exc
            payload = self._parse_flat_yaml(content, path, 1)
        if not isinstance(payload, dict):
            raise IngestionError(f"Input root must be an object: {path}")
        return payload

    def _load_schema(self) -> dict[str, Any]:
        try:
            schema = json.loads(self.schema_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise IngestionError(
                f"Unable to load Evidence schema: {self.schema_path}"
            ) from exc
        if (
            schema.get("$schema")
            != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("type") != "object"
            or not isinstance(schema.get("properties"), dict)
            or not isinstance(schema.get("required"), list)
        ):
            raise IngestionError("Invalid Evidence schema")
        return schema

    def _load_manifest(self) -> dict[str, Any]:
        try:
            manifest = json.loads(
                self.manifest_path.read_text(encoding="utf-8-sig")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise IngestionError(
                f"Unable to load ingestion Manifest: {self.manifest_path}"
            ) from exc
        if not isinstance(manifest, dict) or not isinstance(
            manifest.get("imports"), list
        ):
            raise IngestionError("Ingestion Manifest must contain imports array")
        if not all(isinstance(record, dict) for record in manifest["imports"]):
            raise IngestionError("Manifest imports must be objects")
        return manifest

    def _validate_evidence(self, payload: dict[str, Any], path: Path) -> None:
        required = set(self._schema["required"])
        missing = required - set(payload)
        if missing:
            raise IngestionError(
                f"Invalid output; missing fields in {path}: "
                f"{', '.join(sorted(missing))}"
            )
        extra = set(payload) - set(self._schema["properties"])
        if extra:
            raise IngestionError(
                f"Invalid output; unexpected fields in {path}: "
                f"{', '.join(sorted(extra))}"
            )

        for field, definition in self._schema["properties"].items():
            value = payload[field]
            expected_type = definition.get("type")
            if expected_type == "integer":
                if isinstance(value, bool) or not isinstance(value, int):
                    raise IngestionError(f"Invalid output {field}: {path}")
                if value < definition.get("minimum", value) or value > definition.get(
                    "maximum", value
                ):
                    raise IngestionError(f"Invalid output {field}: {path}")
                continue
            if expected_type == "array":
                if not isinstance(value, list) or not all(
                    isinstance(item, str) for item in value
                ):
                    raise IngestionError(f"Invalid output {field}: {path}")
                if definition.get("uniqueItems") and len(value) != len(set(value)):
                    raise IngestionError(f"Invalid output {field}: {path}")
                continue
            if expected_type != "string" or not isinstance(value, str):
                raise IngestionError(f"Invalid output {field}: {path}")
            if len(value) < definition.get("minLength", 0):
                raise IngestionError(f"Invalid output {field}: {path}")
            pattern = definition.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                raise IngestionError(f"Invalid output {field}: {path}")
            if "enum" in definition and value not in definition["enum"]:
                raise IngestionError(f"Invalid output {field}: {path}")
            if "const" in definition and value != definition["const"]:
                raise IngestionError(f"Invalid output {field}: {path}")
            if definition.get("format") == "date-time":
                normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
                try:
                    datetime.fromisoformat(normalized)
                except ValueError as exc:
                    raise IngestionError(f"Invalid output {field}: {path}") from exc

    @staticmethod
    def _require_input(payload: dict[str, Any], field: str, path: Path) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise IngestionError(f"Missing {field}: {path}")
        return value

    @staticmethod
    def _manifest_text(record: dict[str, Any], field: str) -> str:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise IngestionError(f"Manifest record missing {field}")
        return value

    def _parse_markdown(self, path: Path) -> tuple[dict[str, Any], str]:
        try:
            content = path.read_text(encoding="utf-8-sig")
        except OSError as exc:
            raise IngestionError(f"Unable to read Markdown input: {path}") from exc
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            raise IngestionError(f"Markdown front matter missing: {path}")
        try:
            end = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == "---"
            )
        except StopIteration as exc:
            raise IngestionError(f"Markdown front matter is not closed: {path}") from exc
        metadata = self._parse_flat_yaml(
            "\n".join(lines[1:end]), path, 2
        )
        body = "\n".join(lines[end + 1 :]).lstrip("\n")
        return metadata, body

    def _parse_flat_yaml(
        self, content: str, path: Path, first_line: int
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for offset, raw_line in enumerate(content.splitlines()):
            line_number = first_line + offset
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if raw_line.startswith((" ", "\t")) or ":" not in raw_line:
                raise IngestionError(f"Invalid flat YAML at {path}:{line_number}")
            key, raw_value = raw_line.split(":", 1)
            key = key.strip()
            if not key or key in payload:
                raise IngestionError(f"Duplicate YAML key at {path}:{line_number}")
            payload[key] = self._parse_scalar(
                raw_value.strip(), path, line_number
            )
        return payload

    @staticmethod
    def _parse_scalar(value: str, path: Path, line_number: int) -> Any:
        if value in {"null", "Null", "NULL", "~", ""}:
            return None
        if re.fullmatch(r"-?[0-9]+", value):
            return int(value)
        if re.fullmatch(r"-?[0-9]+\.[0-9]+", value):
            return float(value)
        if value.startswith(("[", '"')):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise IngestionError(
                    f"Invalid YAML scalar at {path}:{line_number}"
                ) from exc
        if value.startswith("'") and value.endswith("'") and len(value) >= 2:
            return value[1:-1].replace("''", "'")
        return value

    @staticmethod
    def _render_evidence(evidence: dict[str, Any]) -> str:
        lines = ["---"]
        for key in (
            "evidence_id",
            "source",
            "source_type",
            "published_at",
            "collected_at",
            "title",
            "summary",
            "language",
            "region",
            "symbols",
            "tags",
            "importance",
            "reliability",
            "status",
            "model_impact",
        ):
            value = evidence[key]
            rendered = (
                json.dumps(value, ensure_ascii=False)
                if isinstance(value, list)
                else str(value)
            )
            lines.append(f"{key}: {rendered}")
        lines.extend(
            [
                "---",
                "",
                "# Evidence Record",
                "",
                "## Original Source",
                "",
                str(evidence["source"]),
                "",
                "## Summary",
                "",
                str(evidence["summary"]),
                "",
                "## Tags",
                "",
                ", ".join(evidence["tags"]) or "None",
                "",
                "## Symbols",
                "",
                ", ".join(evidence["symbols"]) or "None",
                "",
                "## Evidence Notes",
                "",
                "Manual Sandbox import.",
                "",
                "## Validation",
                "",
                "Schema-compatible Sandbox output.",
                "",
            ]
        )
        return "\n".join(lines)

    def _copy_failed(self, path: Path) -> None:
        self.failed_root.mkdir(parents=True, exist_ok=True)
        destination = self.failed_root / path.name
        try:
            shutil.copy2(path, destination)
        except OSError as exc:
            raise IngestionError(f"Unable to preserve failed input: {path}") from exc

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        temporary_path = self.manifest_path.with_suffix(
            f"{self.manifest_path.suffix}.tmp"
        )
        try:
            temporary_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(self.manifest_path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise IngestionError("Unable to write ingestion Manifest") from exc


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the manual Evidence Ingestion Sandbox."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("--input", type=Path)
    subparsers.add_parser("validate")
    args = parser.parse_args(list(argv) if argv is not None else None)

    sandbox = EvidenceIngestionSandbox()
    try:
        if args.command == "ingest":
            manifest = sandbox.ingest_all(args.input)
            print(f"Sandbox imports: {len(manifest['imports'])}")
        else:
            result = sandbox.validate_existing()
            print(
                "Sandbox validation passed: "
                f"{result['outputs_checked']} Evidence output(s)."
            )
    except IngestionError as exc:
        print(f"Sandbox validation failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
