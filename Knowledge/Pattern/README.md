# Pattern Repository

Status: repository_active
Model Impact: repository_only_not_production

## Purpose

The Pattern Repository stores governed Pattern entities derived from one or more registered Cases.

A Pattern is a repository record for validation. It is not a trading rule and has no Runtime authority.

## Lifecycle

```text
Draft
  -> Candidate
  -> Verified
  -> Deprecated
  -> Archived
```

Promotion between lifecycle states requires a separate approved review. Folder location alone does not promote a Pattern.

## Folder Structure

| Folder | Purpose |
|---|---|
| `Draft/` | Incomplete Pattern records |
| `Candidate/` | Patterns ready for validation |
| `Verified/` | Patterns that passed the approved repository review |
| `Deprecated/` | Patterns retained but no longer recommended |
| `Archived/` | Inactive historical Patterns retained for traceability |
| `index.json` | Generated Pattern Registry |

Pattern records use JSON and must validate against `Schemas/Pattern/pattern.schema.json`.

## Source Case Rule

Every `source_cases` entry must resolve to a registered Case in `Runtime/Repository/index/case_index.json`.

Missing Case references, duplicate Pattern IDs, invalid status values, invalid JSON, and schema failures stop index generation immediately.

## Boundary

Pattern entities have no permission to create or modify:

* decisions;
* predictions;
* confidence;
* experience logic;
* playbooks;
* learning rules;
* strategies;
* Dashboard behavior;
* Pipeline, Scoring, or market Runtime behavior.

## Repository Only

The Pattern Repository supports scanning, validation, registration, and index generation only.

