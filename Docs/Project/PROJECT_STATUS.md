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

Engineering Phase — Presentation and Governance

Research Phase v1.0 已完成並封版。Repository Layer 已完成第一階段建置。目前重點為 Dashboard 與專案治理，不代表 Shadow Runtime 或 Production Runtime 已獲授權。

## Current Sprint

Engineering Sprint 1 — Dashboard and Governance

Sprint focus:

- 建立每日可使用的唯讀 Dashboard。
- 完成 Dashboard 繁體中文化。
- 建立 `Docs/Project/` 專案治理中心。
- 維持 Runtime 與 Production Rule 邊界。

## Current Task

| Field | Value |
|---|---|
| Task ID | C-036 |
| Task | Project Constitution & AI Operating System |
| Owner | 小C / Engineering Chief |
| Status | Implemented; awaiting 小P architecture acceptance |
| Priority | P0 |

在 C-036 完成架構驗收前，不得自行切換 Current Task。

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
- 143 automated tests passing at the start of C-035.
- GitHub `main` synchronized through the C-035 baseline commit `94a77fe`.

## In Progress

- C-036 documentation acceptance by 小P.
- Governance v2.0 activation and handover verification.

No Runtime, Pipeline, Scoring, Strategy, or Production work is in progress.

## Next Task

Not assigned.

The next task must be assigned after C-036 architecture acceptance and must be recorded in `NEXT_TASK.md` before work starts.

## Overall Progress

Milestone method: 3 of 7 product stages are complete.

| Product Stage | Status |
|---|---|
| Research | Complete / Frozen |
| Repository | Complete |
| Dashboard | Complete for v1 |
| Engine | Planned; Production behavior blocked |
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

## Canonical References

- `Docs/Project/PROJECT_CONSTITUTION.md`
- `Docs/Project/NEXT_TASK.md`
- `Docs/Project/AI_ROLE_SPECIFICATION.md`
- `Docs/Project/ARCHITECT_PRINCIPLES.md`
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
