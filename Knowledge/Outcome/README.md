# Outcome Repository

Status: repository_active
Model Impact: review_only_not_production

## Purpose

The Outcome Repository stores observed market results linked to a Prediction and Decision reference.

It is the first post-event input to the repository review chain.

## Lifecycle

```text
open -> tracking -> reviewed -> archived
```

Lifecycle state records review progress only and does not trigger any Engine.

## Folder Structure

| Path | Purpose |
|---|---|
| `Records/` | Outcome JSON records |
| `index.json` | Generated Outcome Registry |
| `TEMPLATE.md` | Human-readable record template |

Records validate against `Schemas/Outcome/outcome.schema.json`.

## Boundary

Outcome records cannot create or modify Predictions, Decisions, Learning, Runtime, Pipeline, Scoring, Dashboard behavior, Strategy, or Production Rules.

## Repository Only

This Repository supports static record scanning, validation, registration, and index generation only.
