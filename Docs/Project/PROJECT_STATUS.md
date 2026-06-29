# Auto Radar Project Status

Document ID: AR-PROJECT-SSOT-v2
Status: Active
Authority: Single Source of Truth
Owner: 綠茶 / Product Owner
Maintainer: 小C / Engineering
Last Updated: 2026-06-29

---

## SSOT Rule

本文件是 Auto Radar 唯一專案狀態來源。

所有 AI（小P、小G、小C）開始工作前，必須先閱讀本文件。

若聊天內容、舊狀態文件或個別 AI 記憶與本文件衝突，以本文件為準。

## Current Phase

Engineering Phase — Runtime Governance Gate

Research Phase v1.0 已完成並封版。Repository Layer 與 North Star Dashboard v1 已完成第一階段建置。A-116 至 A-120 Runtime Governance 文件已完成並等待架構驗收；Shadow Runtime 與 Production Runtime 仍未獲授權。

## Current Sprint

Architecture Sprint 3 — Runtime Governance

Sprint focus:

- 建立 Runtime Authority Matrix。
- 建立 North Star Decision Schema 與 Runtime IO Contract。
- 建立 Repository Write Authority。
- 建立 Validation、Rollback 與 E-121 Entry Gate。

## Current Task

| Field | Value |
|---|---|
| Task ID | A-120 |
| Task | Runtime Governance v1 |
| Owner | 小C / Documentation |
| Status | Implemented; awaiting 小P architecture acceptance |
| Priority | P0 |

在 A-120 完成架構驗收前，不得自行切換 Current Task 或開始 E-121。

## Completed

- Research Phase v1.0 architecture package frozen.
- Project governance, Constitution, Registry, Freeze Policy, and Architecture Index established.
- Repository engines completed for Case, Pattern, Experience, Graph, Playbook, Prediction, Evidence, Outcome, Evaluation, and Review.
- Global Repository Validator completed.
- Daily and Morning Markdown reports completed.
- Evidence ingestion, Case Candidate, Review, and Pattern Discovery Sandbox lifecycle completed.
- Dashboard v1 completed under E-100.
- Dashboard Traditional Chinese localization completed under E-101 Rev.1.
- Project Governance Center and SSOT completed under C-035.
- Governance v2.0 Constitution, AI Role Specification, Architect Principles, History, and Handover completed under C-036.
- Architecture Bible v1.0 completed under C-037 as the consolidated architecture handover.
- C-037 architecture acceptance: PASS.
- North Star Dashboard engineering sequence E-111 through E-120 completed.
- North Star card system, Hero, Captain, Top3, Ocean Map, Market Story, Learning, Evolution, and Mission Control integration completed.
- Architecture Decision confirmed the Runtime BLOCK and paused N-001 through N-010.
- Runtime Governance documentation A-116 through A-120 implemented for review.
- 144 automated tests passing after E-120.
- 143 automated tests passing at the start of C-035.
- GitHub `main` synchronized through the E-120 baseline commit `de7c69d`.

## In Progress

- A-120 architecture acceptance by 小P.
- Runtime Authority, IO, Validation, Rollback, and Repository Write review.

No Runtime implementation, Pipeline, Scoring, Strategy, or Production work is in progress.

## Next Task

E-121 — North Star Runtime.

Status: BLOCKED until A-116 through A-120 receive Architecture Review PASS and the active Runtime Authority Matrix is formally updated.

## Overall Progress

Milestone method: 3 of 7 product stages are complete.

| Product Stage | Status |
|---|---|
| Research | Complete / Frozen |
| Repository | Complete |
| Dashboard | North Star v1 implemented; awaiting acceptance |
| Engine | Runtime Governance implemented for review; Gate CLOSED |
| Automation | Planned |
| Beta | Planned |
| v1.0 | Planned |

Overall milestone progress: **43%**

This percentage measures completed product stages, not code volume or prediction quality.

## Active Boundaries

- Dashboard is read-only.
- Pattern, Case, Experience, and Playbook records do not authorize trading.
- Production Runtime, Decision Engine activation, position sizing, capital allocation, and real trading remain blocked.
- No unvalidated hypothesis may become a Production Rule.
- Research is frozen unless Architecture Review explicitly authorizes an exception.
- N-001 through N-010 and E-121 remain blocked.

## Canonical References

- `Docs/ARCHITECTURE_BIBLE.md`
- `Docs/Project/PROJECT_CONSTITUTION.md`
- `Docs/Project/NEXT_TASK.md`
- `Docs/Project/AI_ROLE_SPECIFICATION.md`
- `Docs/Project/ARCHITECT_PRINCIPLES.md`
- `Docs/Project/RUNTIME_AUTHORITY_MATRIX.md`
- `Docs/Project/DECISION_RUNTIME_SPECIFICATION.md`
- `Docs/Project/RUNTIME_IO_CONTRACT.md`
- `Docs/Project/REPOSITORY_WRITE_AUTHORITY.md`
- `Docs/Project/RUNTIME_GOVERNANCE.md`
- `Docs/Project/ROADMAP.md`
- `Docs/Project/TEAM_OPERATING_MODEL.md`
- `Docs/Project/HANDOVER.md`
- `Docs/Project/PROJECT_HISTORY.md`
- `Docs/Project/ENGINEERING_STATUS.md`
- `Docs/Project/RESEARCH_STATUS.md`
- `Docs/Project/DECISION_LOG.md`
- `Docs/Project/KNOWN_ISSUES.md`
- `Docs/Project/VISION.md`
- `TEAM_OPERATING_SYSTEM.md`
- `Docs/ARCHITECTURE_CONSTITUTION.md`

## Legacy Status Notice

Files such as `Docs/PROJECT_STATUS.md`, `Docs/PROJECT_STATE.md`, `Docs/ROADMAP.md`, and `Docs/HANDOVER_STATE.md` are historical references only.

They must not override this file.
