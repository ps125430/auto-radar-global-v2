# Auto Radar Project Status

Document ID: AR-PROJECT-SSOT-v2
Status: Active
Authority: Single Source of Truth
Owner: 綠茶 / Product Owner
Maintainer: 小C / Engineering
Last Updated: 2026-07-01

---

## SSOT Rule

本文件是 Auto Radar 唯一專案狀態來源。

所有 AI（小P、小G、小C）開始工作前，必須先閱讀本文件。

若聊天內容、舊狀態文件或個別 AI 記憶與本文件衝突，以本文件為準。

## Current Phase

Engineering Phase — Sprint 10 Captain Intelligence

Research Phase v1.0 已完成並封版。Runtime Gate 已開啟。E-121 至 E-160 已完成 Shadow Runtime、Living Ocean 與官方資料基礎。E-161 至 E-165 已建立 Captain Profile、My Ship、Budget boundary、單一 Active Mission 與 Captain Brief，等待小P驗收；不包含選股、交易訊號、Strategy、Scoring 或訂單。

## Current Sprint

Engineering Sprint 10 — Captain OS v1

Sprint focus:

- 建立 Captain Profile 並強制 Decision Runtime 讀取。
- 建立可序列化 My Ship。
- 依 Profile 計算 Shadow Budget boundary。
- 每日只允許一個 Active Mission。
- 產生 Good Morning Captain Brief。

## Current Task

| Field | Value |
|---|---|
| Task ID | E-165 |
| Task | Captain Brief Generator |
| Owner | 小C / Engineering |
| Status | E-161 through E-165 implemented; awaiting 小P architecture review |
| Priority | P0 |

E-161 至 E-165 已完成工程實作；Budget Engine 僅計算資金邊界，Mission 與 Brief 均為 Shadow context。

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
- E-136 Shadow Input Schema implemented.
- E-137 Sample Real Input Pack implemented for AI Infrastructure, HBM, Cooling, Power, and CPO.
- E-138 Input Quality Validator implemented with fail-fast checks.
- E-139 Shadow Output Quality Gate implemented before Dashboard projection.
- E-140 First Real Shadow Brief generated.
- 171 automated tests passing after E-136 through E-140.
- E-146 Decision Snapshot implemented and saved for 2026-06-30.
- E-147 Manual Outcome Collector implemented.
- E-148 Decision Residual Engine implemented as Review-only comparison.
- E-149 Root Cause Analyzer implemented with manual diagnostic attribution.
- E-150 Daily Reflection implemented as draft suggestion only.
- 178 automated tests passing after E-146 through E-150.
- E-151 unified Market Provider Layer implemented with six no-network adapters.
- E-152 validated Market Snapshot Builder and Snapshot-only Runtime gateway implemented.
- E-153 automatic Provider Evidence Collector implemented without Repository writes.
- E-154 Data Quality Engine implemented with five fail-fast categories.
- E-155 deterministic 2026-07-02 Shadow Replay implemented with source hashes.
- 186 automated tests passing after E-151 through E-155.
- E-156 Official Provider Registry implemented for TWSE, TPEx, MOPS, US Market, Macro, ETF, and News.
- E-157 versioned Global Snapshot v2 implemented with AM/PM replay identity.
- E-158 unified Evidence Normalizer implemented for official-first source records.
- E-159 Ocean Health Engine implemented with data-confidence adjustment candidate only.
- E-160 Living Ocean Monitor implemented in the read-only Dashboard.
- 194 automated tests passing after E-156 through E-160.
- E-161 Captain Profile Engine implemented; Decision Runtime now requires a validated profile reference.
- E-162 serializable My Ship State Engine implemented.
- E-163 profile-driven Budget Allocation Engine implemented without stock selection or orders.
- E-164 Mission Engine implemented with one Active Mission invariant.
- E-165 Captain Brief Generator implemented with immutable Shadow artifacts.
- 203 automated tests passing after E-161 through E-165.
- 162 automated tests passing after E-126 through E-130.
- 157 automated tests passing after E-121 through E-125.
- 144 automated tests passing after E-120.
- 143 automated tests passing at the start of C-035.
- GitHub `main` synchronized through the E-120 baseline commit `de7c69d`.

## In Progress

- E-161 through E-165 architecture review by 小P.

No Pipeline, Scoring, Strategy, trading, or Production work is in progress.

## Next Task

Not assigned. E-161 through E-165 must pass Architecture Review before Dashboard binding or additional Captain Runtime work.

## Overall Progress

Milestone method: 3 of 7 product stages are complete.

| Product Stage | Status |
|---|---|
| Research | Complete / Frozen |
| Repository | Complete |
| Dashboard | North Star v1 driven by gated Shadow test input; awaiting acceptance |
| Engine | Shadow Runtime, Living Ocean, Captain Profile, Ship State, Budget boundary, Mission, and Captain Brief implemented; Production blocked |
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
