# Prediction Snapshot Repository

Status: repository_active
Model Impact: snapshot_only_not_production_scoring

## Purpose

The Prediction Repository stores the single daily Snapshot that bridges validated Repository knowledge and future external Runtime observation.

It records state and references only. It does not infer, recommend, or execute a decision.

## Lifecycle

```text
Draft -> Candidate -> Generated -> Archived
```

One `prediction_date` may have only one Snapshot entity.

## Folder Structure

| Path | Purpose |
|---|---|
| `daily/` | Draft, Candidate, and Generated Snapshot files |
| `archive/` | Archived Snapshot files |
| `TEMPLATE.md` | Required Markdown and YAML structure |
| `Runtime/Repository/index/prediction_registry.json` | Generated Registry |

Snapshot files validate against `Schemas/Prediction/prediction.schema.json`.

## References

* `playbook_refs` must resolve to the Playbook Registry.
* `experience_refs` must resolve to the Experience Registry.
* `pattern_refs` must resolve to the Pattern Registry.
* `confidence_ref` may be `null` until a separate Confidence Repository exists.

## Boundary

Prediction Snapshots cannot generate or modify decisions, trading signals, confidence values, Learning, Runtime Strategy, Pipeline, Scoring, Dashboard behavior, or Production Rules.

`decision_status` records external workflow state only and cannot contain trading commands.

## Repository Only

This Repository supports Snapshot parsing, validation, reference checks, lifecycle checks, registration, and index generation only.

