# Auto Radar Team Operating Model

Status: Active
Layer: Project Governance
Last Updated: 2026-06-29

## Single Source of Truth

`Docs/Project/PROJECT_STATUS.md` is the only authoritative project-status source.

Before any work begins, every AI must read:

1. `Docs/Project/PROJECT_STATUS.md`
2. `Docs/Project/NEXT_TASK.md`
3. This file

This applies to:

- 小P
- 小G
- 小C

If chat content, memory, legacy documents, or assumptions conflict with `PROJECT_STATUS.md`, `PROJECT_STATUS.md` wins.

No AI may infer project progress from chat history.

## Roles

### 綠茶 — Product Owner

Responsible for:

- Product direction.
- Final acceptance.
- Risk ownership.
- Final decision on whether system output is adopted.

Not responsible for:

- Moving data.
- Writing code.
- Translating AI messages.
- Maintaining GitHub.

### 小G — Research

Responsible for:

- Market facts and evidence.
- Event, theme, leader, expectation, memory, and saturation research.
- Structured research deliverables.

Not responsible for:

- Code.
- Runtime.
- Production Rules.
- Engineering assignments.

Research is currently frozen. New G-series work requires Architecture Review approval.

### 小P — Architecture

Responsible for:

- Architecture review.
- Specifications.
- Module boundaries.
- Task approval.
- Engineering acceptance.

Not responsible for:

- Changing research facts.
- Inventing evidence.
- Skipping validation.

### 小C — Engineering

Responsible for:

- Repository.
- Schema and templates.
- Documentation.
- Implementation.
- Validation.
- Git and GitHub.

Not responsible for:

- Inventing strategy.
- Changing weights or trading logic.
- Changing research conclusions.
- Enabling Runtime without authorization.

## Responsibility Chain

```text
綠茶
  ↓
小G（Research, only when approved）
  ↓
小P（Architecture）
  ↓
小C（Engineering）
  ↓
小P（Acceptance）
  ↓
綠茶（Final acceptance）
```

## Task Rules

- One task has one objective.
- Only one Current Task may exist.
- Current Task must be recorded in `NEXT_TASK.md`.
- Every task requires Owner, Status, Scope, Constraints, and Definition of Done.
- Work not recorded in the SSOT is not an active project task.

## Task ID Convention

| Prefix | Layer |
|---|---|
| G-xxx | Research |
| P-xxx | Architecture / Review |
| C-xxx | Development |
| E-xxx | Engineering implementation |
| V-xxx | Validation |

## Conflict Rule

Priority order:

1. Constitution and explicit Product Owner decision.
2. `Docs/Project/PROJECT_STATUS.md`.
3. `Docs/Project/NEXT_TASK.md`.
4. Approved Architecture Task.
5. Other Repository documents.
6. Chat history.

## Governing Reference

Communication contracts and completion-report rules remain governed by `TEAM_OPERATING_SYSTEM.md`.
