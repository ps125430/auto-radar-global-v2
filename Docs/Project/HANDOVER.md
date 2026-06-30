# Auto Radar Handover

Document ID: AR-PROJECT-HANDOVER-v2
Status: Active
Authority: Current Handover Snapshot
Last Updated: 2026-06-30

## Startup Instruction

新 AI 不得要求使用者重新解釋專案。

先依序閱讀：

1. `PROJECT_CONSTITUTION.md`
2. `PROJECT_STATUS.md`
3. `NEXT_TASK.md`
4. `AI_ROLE_SPECIFICATION.md`
5. `TEAM_OPERATING_MODEL.md`
6. 本文件

## Current Repository

- Repository: `ps125430/auto-radar-global-v2`
- Remote: `https://github.com/ps125430/auto-radar-global-v2.git`
- Branch: `main`
- Local path: `C:\Users\user\Documents\Codex\2026-06-25\auto-radar-team-v1-0-auto\auto-radar-global-v2`
- GitHub baseline before Runtime Governance: `de7c69d`

工作開始前仍須執行 Git 檢查，不得只依賴本快照。

## Current Phase

Engineering Phase — Real Data Foundation

- Research: Complete / Frozen
- Repository: Complete
- Dashboard: North Star v1 implemented with Shadow Runtime binding
- Engine: E-121 through E-150 implemented; E-151 through E-155 Real Data Foundation implemented for review; Gate OPEN
- Automation, Beta, v1.0: Planned

## Current Task

- Task ID: E-155
- Task: Shadow Data Replay
- Owner: 小C / Engineering
- Status: E-151 through E-155 implemented; awaiting 小P architecture review
- Impact: Provider and Shadow data infrastructure only

## Completed Runtime Milestone

- Runtime Authority Matrix。
- North Star Decision、Reason、Confidence Schema。
- Runtime IO Contract 與 Layer boundary。
- Repository Write Authority。
- Validation、Rollback 與 E-121 Entry Gate。
- E-121 Runtime Framework、Loader、Context、Session、Dispatcher。
- E-122 Decision Schema packaging，沒有 Decision Logic。
- E-123 Decision 至 Repository Explain Chain。
- E-124 Lesson 與 Repository Patch suggestions，不直接寫入。
- E-125 需要 Repository Manager 審核的 Patch Queue。
- E-126 Shadow Runtime Orchestrator。
- E-127 Daily Shadow Decision Run。
- E-128 Shadow Review Pipeline 與 Lesson Draft。
- E-129 Patch Suggestion Flow，不自動 Merge。
- E-130 North Star Shadow Daily Brief。
- E-131 North Star Data Binding。
- E-132 Dashboard Live Context。
- E-133 North Star Timeline。
- E-134 Explain Data Binding。
- E-135 Shadow Dashboard Mode。
- E-136 Shadow Input Schema。
- E-137 AI Infrastructure、HBM、散熱、電力與 CPO 半真實測試輸入包。
- E-138 Input Quality Validator。
- E-139 Dashboard projection 前的 Shadow Output Quality Gate。
- E-140 First Real Shadow Brief。
- E-146 Decision Snapshot 與 `Snapshots/2026-06-30.json`。
- E-147 Manual Outcome Collector。
- E-148 Review-only Decision Residual 與 Accuracy。
- E-149 Manual diagnostic Root Cause attribution。
- E-150 Suggest-only Daily Reflection。
- E-151 Taiwan、US、Macro、News、ETF 與 Mock Provider adapters。
- E-152 Market Snapshot Builder 與 Snapshot Reader gateway。
- E-153 Automatic Provider Evidence Collector。
- E-154 Missing、Duplicate、Invalid、Outlier 與 Timestamp Fail-fast。
- E-155 2026-07-02 source-hashed deterministic Replay。

## Active Boundaries

- 不擴充未授權 Runtime。
- 不修改 Pipeline。
- 不修改 Dashboard。
- 不修改 Strategy、Scoring 或 Production Rule。
- Research Freeze 持續有效。
- Dashboard 仍為唯讀。
- Production Engine 與真實交易尚未獲授權。

## Validation Baseline

- C-035 commit 已同步至 GitHub `main`。
- Runtime Governance v1 Architecture Review PASS，Gate OPEN。
- E-121 至 E-125 僅為 Shadow infrastructure。
- E-126 至 E-130 僅為 Shadow integration。
- E-131 至 E-135 僅為 Dashboard Shadow binding。
- E-136 至 E-140 僅為 Shadow data integration；測試輸入不是研究結論。
- E-146 至 E-150 僅為 Shadow review records；不得修改 Scoring、Strategy 或 Repository。
- E-151 至 E-155 僅為 Provider/Shadow data infrastructure；尚未串接外部 API。
- Learning 僅允許 Suggest，不得寫入 Repository。
- N-001 至 N-010、Production Runtime 全部 BLOCKED。
- 186 項自動測試通過。
- 未修改 Pipeline、Dashboard、Scoring、Strategy 或 Production Rule。

## Immediate Next Step

1. 小P驗收 E-151 至 E-155。
2. 記錄 PASS 或修正要求。
3. 未經另案授權，不得進入 N-series 或 Production Runtime。

不得自行從 Roadmap 選擇工作開工。
