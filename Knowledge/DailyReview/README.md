# Daily Review Repository

Status: repository_active
Model Impact: review_pipeline_only

## Purpose

The Daily Review Repository stores static review records linked to a Prediction reference, registered Outcome, and registered Evaluation.

It captures prediction, behavior, execution, and missing-information review fields without running Learning logic.

## Lifecycle

```text
draft -> reviewed -> archived
```

## Folder Structure

| Path | Purpose |
|---|---|
| `Records/` | Daily Review JSON records |
| `index.json` | Generated Review Registry |
| `TEMPLATE.md` | Human-readable review template |

Records validate against `Schemas/DailyDecision/review_record.schema.json`.

## Boundary

Review records cannot execute Predictions, Decisions, Learning, Runtime, Pipeline, Scoring, Dashboard behavior, Strategy, or Production Rules.

`learning_target` is a static review field only.

## Repository Only

This Repository supports static record scanning, validation, registration, and index generation only.
