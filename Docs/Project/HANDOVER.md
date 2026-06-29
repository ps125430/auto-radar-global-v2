# Auto Radar Handover

Document ID: AR-PROJECT-HANDOVER-v2
Status: Active
Authority: Current Handover Snapshot
Last Updated: 2026-06-29

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

Engineering Phase — Runtime Governance Gate

- Research: Complete / Frozen
- Repository: Complete
- Dashboard: North Star v1 implemented
- Engine: Runtime Governance implemented for review; Gate CLOSED
- Automation, Beta, v1.0: Planned

## Current Task

- Task ID: A-120
- Task: Runtime Governance v1
- Owner: 小C / Documentation
- Status: Implemented; awaiting 小P architecture acceptance
- Impact: Documentation / Runtime Governance only

## Completed in A-116 through A-120

- Runtime Authority Matrix。
- North Star Decision、Reason、Confidence Schema。
- Runtime IO Contract 與 Layer boundary。
- Repository Write Authority。
- Validation、Rollback 與 E-121 Entry Gate。

## Active Boundaries

- 不修改 Runtime。
- 不修改 Pipeline。
- 不修改 Dashboard。
- 不修改 Strategy、Scoring 或 Production Rule。
- Research Freeze 持續有效。
- Dashboard 仍為唯讀。
- Engine 與真實交易尚未獲授權。

## Validation Baseline

- C-035 commit 已同步至 GitHub `main`。
- 所有 Engine 目前仍為 Deny。
- Engine 最多只能成為 Read／Suggest Candidate。
- Learning 僅允許 Suggest，不得寫入 Repository。
- E-121、N-001 至 N-010、Production Runtime 全部 BLOCKED。
- 未修改任何 Runtime code、Pipeline、Scoring、Strategy 或 Production Rule。

## Immediate Next Step

1. 小P驗收 A-116 至 A-120。
2. 若 PASS，正式更新 active Runtime Authority Matrix。
3. 開啟 Runtime Governance Gate。
4. 由 Architecture 派發 E-121。

不得自行從 Roadmap 選擇工作開工。
