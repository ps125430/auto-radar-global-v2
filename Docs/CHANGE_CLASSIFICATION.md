# Change Classification

Document ID: AR-GOV-CHANGE-CLASSIFICATION-2026-06-27
Version: 1.0
Owner: 小P / Chief Architect
Status: governance_active
Model Impact: repository_governance_only

---

## Governance Source

Change classification follows `TEAM_OPERATING_SYSTEM.md`.

This document is governance-only. It must not directly modify Runtime, Pipeline, Scoring, Dashboard, Strategy, or Production Rules.

---

## MAJOR

Definition:

Breaking architecture, repository structure, or governance change.

Allowed Scope:

* architecture redesign;
* lifecycle change;
* folder migration;
* core governance update.

Required Approval:

小P review and 綠茶 acceptance.

Runtime Impact:

Not allowed unless separately approved as production work.

Example:

Moving Decision Lab lifecycle from one repository structure to another.

---

## MINOR

Definition:

Backward-compatible addition to repository structure, schema candidates, or governance docs.

Allowed Scope:

* new schema candidate;
* new template;
* new governance section;
* new repository area.

Required Approval:

小P approved specification.

Runtime Impact:

None.

Example:

Adding `Schemas/OutcomeEvaluation/outcome_evaluation.schema.json`.

---

## PATCH

Definition:

Small correction that does not change meaning, scope, or lifecycle.

Allowed Scope:

* typo correction;
* broken link repair;
* formatting correction;
* README clarification.

Required Approval:

Task owner approval or 小P review when governance meaning may be affected.

Runtime Impact:

None.

Example:

Fixing a Markdown heading or correcting a referenced file path.

---

## EMERGENCY

Definition:

Urgent change required to prevent repository integrity, security, or synchronization failure.

Allowed Scope:

* remove exposed secret reference;
* repair corrupted schema file;
* unblock GitHub sync;
* fix broken critical governance file.

Required Approval:

Immediate 小P or 綠茶 approval when available. Document after action if urgent.

Runtime Impact:

Only if separately authorized and documented.

Example:

Repairing invalid JSON in a schema used by multiple review workflows.

---

## HOTFIX

Definition:

Small targeted fix to an already accepted artifact.

Allowed Scope:

* fix incorrect enum;
* restore missing required field;
* correct wrong status or model impact;
* patch a broken template section.

Required Approval:

小P review or task-specific approval.

Runtime Impact:

None unless separately classified as production hotfix.

Example:

Adding a missing required field to a schema candidate.

---

## Classification Rule

When classification is unclear, use the stricter category and ask 小P before implementation.

Do not guess.
