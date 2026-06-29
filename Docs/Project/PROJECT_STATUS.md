# Auto Radar Project Status

Document ID: AR-PROJECT-SSOT-v2
Status: Active
Authority: Single Source of Truth
Owner: 綠茶 / Product Owner
Maintainer: 小C / Engineering
Last Updated: 2026-06-30

---

## SSOT Rule

本文件是 Auto Radar 唯一專案狀態來源。

所有 AI（小P、小G、小C）開始工作前，必須先閱讀本文件。

若聊天內容、舊狀態文件或個別 AI 記憶與本文件衝突，以本文件為準。

## Current Phase

Engineering Phase — North Star Shadow Dashboard Binding

Research Phase v1.0 已完成並封版。Repository Layer 與 North Star Dashboard v1 已完成第一階段建置。A-116 至 A-120 已獲 Architecture Review PASS，Runtime Gate 已開啟。E-121 至 E-125 Shadow Runtime infrastructure 已完成並推送 GitHub。E-126 至 E-130 Shadow Runtime Integration 已完成並推送 GitHub。E-131 至 E-135 Dashboard Shadow Binding 已完成工程實作並等待小P驗收；Production Runtime 仍未獲授權。

## Current Sprint

Engineering Sprint 4 — Shadow Dashboard Binding

Sprint focus:

- 將 Shadow Runtime projection 綁定 Dashboard。
- 建立 Dashboard Live Context 與統一等待訊息。
- 建立 North Star Timeline。
- 建立 Today's Direction Runtime Explain Chain。
- 建立 Shadow Dashboard Mode 狀態卡。

## Current Task

| Field | Value |
|---|---|
| Task ID | E-135 |
| Task | Shadow Dashboard Mode |
| Owner | 小C / Engineering |
| Status | E-131 through E-135 implemented; awaiting 小P architecture review |
| Priority | P0 |

E-131 至 E-135 已完成工程實作；Architecture Review 前不得擴充為 N-series 或 Production Runtime。

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
- Runtime Governance v1 Architecture Review: PASS; Runtime Gate: OPEN.
- E-121 Runtime Framework, Loader, Context, Session, and Dispatcher implemented.
- E-122 Decision Runtime implemented as schema packaging without Decision Logic.
- E-123 Explain Runtime implemented as a traceable reference chain.
- E-124 Learning Runtime implemented as Lesson and Patch suggestions only.
- E-125 Repository Patch Queue implemented with Repository Manager approval.
- E-126 Shadow Runtime Orchestrator implemented.
- E-127 Daily Shadow Decision Run implemented.
- E-128 Shadow Review Pipeline implemented with Lesson Draft only.
- E-129 Patch Suggestion Flow implemented; Merge requires manual review.
- E-130 North Star Shadow Daily Brief implemented as Shadow output only.
- E-131 North Star Data Binding implemented for Dashboard Shadow fields.
- E-132 Dashboard Live Context implemented with one waiting message.
- E-133 North Star Timeline implemented.
- E-134 Explain Data Binding implemented for Today's Direction.
- E-135 Shadow Dashboard Mode implemented.
- 166 automated tests passing after E-131 through E-135.
- 162 automated tests passing after E-126 through E-130.
- 157 automated tests passing after E-121 through E-125.
- 144 automated tests passing after E-120.
- 143 automated tests passing at the start of C-035.
- GitHub `main` synchronized through the E-120 baseline commit `de7c69d`.

## In Progress

- E-131 through E-135 architecture review by 小P.

No Pipeline, Scoring, Strategy, trading, or Production work is in progress.

## Next Task

Not assigned. E-131 through E-135 must pass Architecture Review before any additional Runtime or Dashboard task.

## Overall Progress

Milestone method: 3 of 7 product stages are complete.

| Product Stage | Status |
|---|---|
| Research | Complete / Frozen |
| Repository | Complete |
| Dashboard | North Star v1 with Shadow Runtime binding implemented; awaiting acceptance |
| Engine | Shadow Runtime infrastructure, integration, and dashboard projection implemented; Gate OPEN; Production blocked |
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
- N-001 through N-010 and Production Runtime remain blocked.

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
