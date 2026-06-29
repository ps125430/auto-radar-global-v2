# Auto Radar Team Operating Model

Status: Active
Layer: Project Governance
Last Updated: 2026-06-29

## Governance Authority

本文件受 `PROJECT_CONSTITUTION.md` 管理，負責團隊日常分工與工作交接，不得修改 Project Constitution。

## Single Source of Truth

`Docs/Project/PROJECT_STATUS.md` is the only authoritative project-status source.

Before any work begins, every AI must read:

1. `Docs/Project/PROJECT_CONSTITUTION.md`
2. `Docs/Project/PROJECT_STATUS.md`
3. `Docs/Project/NEXT_TASK.md`
4. `Docs/Project/AI_ROLE_SPECIFICATION.md`
5. This file
6. `Docs/Project/HANDOVER.md`

This applies to:

- 小P
- 小G
- 小C

If chat content, memory, legacy documents, or assumptions conflict with `PROJECT_STATUS.md`, `PROJECT_STATUS.md` wins.

No AI may infer project progress from chat history.

完成 Startup Protocol 後，AI 還必須確認 Git branch、working tree、remote、Current Task、Owner、Scope、Constraints 與 Definition of Done，才可開始修改。

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

角色 Mission、Authority、Never Do、Deliverables 與 KPI 由 `AI_ROLE_SPECIFICATION.md` 定義。

Chief Architect 的設計鐵律由 `ARCHITECT_PRINCIPLES.md` 定義。

## Mandatory Project Sync

Task 完成時必須依 `PROJECT_CONSTITUTION.md` 的 Mandatory Update Rule，同步更新適用的 Status、Task、Changelog、Handover、Decision 與 History 文件。

未完成文件同步、Validation、Commit 與 Push，不算完成交接。
