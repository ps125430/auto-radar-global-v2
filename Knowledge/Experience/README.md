# Experience Repository

Status: repository_active
Model Impact: repository_only_not_production

## Purpose

The Experience Repository stores governed Experience entities derived from registered Patterns and Cases.

An Experience is a repository record for validation and traceability. It is not a trading rule and has no Runtime authority.

## Lifecycle

```text
Draft
  -> Candidate
  -> Verified
  -> Deprecated
  -> Archived
```

Promotion between lifecycle states requires a separate approved review. Folder location alone does not promote an Experience.

## Folder Structure

| Folder | Purpose |
|---|---|
| `Draft/` | Incomplete Experience records |
| `Candidate/` | Experiences ready for repository validation |
| `Verified/` | Experiences that passed the approved repository review |
| `Deprecated/` | Experiences retained but no longer recommended |
| `Archived/` | Inactive historical Experiences retained for traceability |
| `index.json` | Generated Experience Registry |

Experience records use JSON and must validate against `Schemas/Experience/experience.schema.json`.

The pre-E-003 `Candidates/`, `Shadow/`, `Core/`, and `Patterns/` directories are retained as legacy research skeletons. The E-003 Repository Engine does not scan them.

## Source Reference Rules

Every `source_patterns` entry must resolve to `Knowledge/Pattern/index.json`.

Every `source_cases` entry must resolve to `Runtime/Repository/index/case_index.json`.

Missing references, duplicate Experience IDs, invalid status values, invalid health values, invalid JSON, and schema failures stop index generation immediately.

## Repository Boundary

Experience entities have no permission to create or modify:

* decisions;
* predictions;
* playbook Runtime behavior;
* confidence logic;
* learning rules;
* strategies;
* Runtime, Pipeline, or Scoring behavior;
* Dashboard behavior;
* Production Rules.

## Repository Only

The Experience Repository supports scanning, validation, registration, and index generation only.
