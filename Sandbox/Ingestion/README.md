# Evidence Ingestion Sandbox

Status: sandbox_active
Model Impact: sandbox_only_not_production

## Purpose

This Sandbox converts manually supplied Markdown, JSON, or YAML files into Evidence-compatible Markdown.

```text
Raw Input -> Validation -> Sandbox Evidence Output
```

Generated files remain in `processed/`. They are not automatically promoted to `Knowledge/Evidence/` and cannot create Cases.

## Structure

| Path | Purpose |
|---|---|
| `samples/` | Five valid example inputs |
| `imports/` | Manual files waiting for ingestion |
| `processed/` | Evidence-compatible Markdown output |
| `failed/` | Copies of rejected raw inputs |
| `ingestion_manifest.json` | Import audit trail |
| `import_evidence.py` | Sandbox importer and validator |

## Supported Formats

* Markdown with YAML Front Matter
* JSON object
* Flat YAML using scalar values and inline arrays

Each filename stem is the `import_id`. Every input must provide an `evidence_id` and all fields required by `Schemas/Evidence/evidence.schema.json`.

The input field `timestamp` becomes Evidence `published_at`. Ingestion time becomes `collected_at`.

## Commands

Ingest the sample dataset:

```text
python Sandbox/Ingestion/import_evidence.py ingest --input Sandbox/Ingestion/samples
```

Validate the committed Manifest and outputs:

```text
python Sandbox/Ingestion/import_evidence.py validate
```

## Fail-Fast Rules

Ingestion stops on:

* unsupported file format;
* duplicate import ID;
* duplicate Evidence ID;
* missing title;
* missing timestamp;
* missing source;
* Evidence Schema mismatch;
* invalid generated output.

## Boundary

This Sandbox does not connect to RSS, search engines, regulatory APIs, exchange APIs, or any external feed. It does not crawl, summarize with AI, generate Cases, make decisions, or execute trading behavior.
