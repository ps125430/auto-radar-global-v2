# Repository Governance

Document ID: AR-GOV-REPOSITORY-2026-06-27
Version: 1.0
Owner: 小P / Chief Architect
Status: governance_active
Model Impact: repository_governance_only

---

## Governance Source

Team communication and workflow are governed by `TEAM_OPERATING_SYSTEM.md`.

This document governs repository administration only. It must not directly modify Runtime, Pipeline, Scoring, Dashboard, Strategy, or Production Rules.

---

## Repository Lifecycle

Repository artifacts move through:

```text
draft -> candidate -> review -> verified -> core -> deprecated -> archived
```

Lifecycle changes must preserve traceability and owner responsibility.

---

## Folder Governance

Canonical top-level folders:

| Folder | Purpose |
|---|---|
| `Docs/` | Governance, framework, protocol, roadmap, and architecture documents |
| `Knowledge/` | Cases, reviews, lessons, market memory, journals, and experience records |
| `Schemas/` | JSON schema candidates and schema skeletons |
| `Data/` | Structured data libraries and graph data |
| `Templates/` | Reusable task and report templates |

Use `Docs/`, not `docs/`.

---

## Naming Convention

* Documents use uppercase descriptive names: `REPOSITORY_GOVERNANCE.md`.
* Schemas use lowercase snake case: `outcome.schema.json`.
* Task commits use task ID prefixes: `C-###`, `P-###`, `G-###`, `V-###`.
* Entity IDs use registry prefixes from `Docs/REGISTRY.md`.

---

## Version Policy

Use semantic-style document versioning:

* `v1.0`: first accepted governance version.
* `v1.1`: compatible additions.
* `v2.0`: breaking governance or structure change.

Schema candidates must clearly mark:

```text
status = schema_candidate
model_impact = research_only_not_production
```

or the task-specific approved model impact.

---

## Archive Policy

Do not delete official records unless explicitly approved.

Deprecated or inactive records should be:

* marked deprecated;
* linked to replacement if available;
* retained for audit;
* excluded from active workflow by status.

---

## Cross Reference Policy

Cross references must use stable IDs where possible.

Required cross-reference examples:

* Prediction -> Outcome
* Outcome -> Review
* Review -> Learning
* Review -> Decision Journal
* Case -> Evidence
* Experience -> Pattern
* Pattern -> Case

Broken references must be recorded in `Docs/ARCHITECTURE_DEBT.md`.

---

## Contribution Policy

All repository changes require:

* clear task ID;
* single objective;
* owner;
* constraints;
* acceptance criteria;
* completion report.

Engineering work must follow the Engineering Contract in `TEAM_OPERATING_SYSTEM.md`.

---

## RACI Matrix

| Area | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Research content | 小G | 小P | 綠茶 | 小C |
| Architecture | 小P | 綠茶 | 小G | 小C |
| Repository implementation | 小C | 小P | 小G | 綠茶 |
| Validation | 小P | 綠茶 | 小G / 小C | Auto Radar |
| Final decision | 綠茶 | 綠茶 | 小G / 小P | 小C |

---

## Repository Health Score

Repository Health Score is a governance review metric only.

Suggested candidate dimensions:

* registry completeness;
* broken cross references;
* stale candidates;
* deprecated item hygiene;
* schema validity;
* README coverage;
* duplicate document risk.

This score must not affect production trading logic.

---

## Cross Reference Validator

Cross Reference Validator is a future governance utility candidate.

Candidate checks:

* missing referenced IDs;
* duplicate entity IDs;
* invalid status values;
* orphaned outcome or review records;
* stale candidate records.

No validator may modify data automatically without separate architecture approval.

---

## Zero Guess Policy Reference

All unclear repository changes must follow Zero Guess Policy in `TEAM_OPERATING_SYSTEM.md`.

If required input is missing:

```text
Ask before implementation.
```
