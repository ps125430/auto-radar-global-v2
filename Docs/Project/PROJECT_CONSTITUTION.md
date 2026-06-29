# Auto Radar Project Constitution

Document ID: AR-PROJECT-CONSTITUTION-v2
Version: 2.0
Status: Active
Authority: Highest Project Governance
Owner: 綠茶 / Product Owner
Architecture Owner: 小P / Chief Architect
Maintainer: 小C / Engineering
Effective Date: 2026-06-29

## Purpose

本憲章是 Auto Radar 專案治理的最高規範。它定義專案如何保存真相、啟動工作、分配權責與控制變更。

本文件不建立交易策略、正式評分、Runtime 權限或 Production Rule。

## Authority Order

發生衝突時，依下列順序處理：

1. 本憲章與綠茶明確的產品決策。
2. `PROJECT_STATUS.md` 的當前專案狀態。
3. `NEXT_TASK.md` 的唯一 Current Task。
4. 已核准的 Architecture specification。
5. 其他 Repository 文件。
6. 聊天內容與個別 AI 記憶。

聊天不得覆蓋 Repository 中的正式紀錄。

## Repository First

- GitHub Repository 是 Auto Radar 唯一正式知識庫。
- 重大決策、規格、狀態、模板、Schema、Case 與驗證結果必須寫入 Repository。
- 聊天內容只有在寫入 Repository 後才成為正式專案紀錄。
- 不得以聊天記憶推測專案進度或補造缺少的規格。

## Single Source of Truth

`Docs/Project/PROJECT_STATUS.md` 是唯一專案狀態來源。

- 專案階段、Sprint、Current Task、進度與下一步只由該文件宣告。
- `Docs/Project/NEXT_TASK.md` 只管理唯一 Current Task 與候選 Next Task。
- 舊狀態文件只能作為歷史資料，不得覆蓋 SSOT。

## AI Startup Protocol

任何 AI 或協作者開始工作前，必須依序：

1. 閱讀 `PROJECT_CONSTITUTION.md`。
2. 閱讀 `PROJECT_STATUS.md`。
3. 閱讀 `NEXT_TASK.md`。
4. 閱讀 `AI_ROLE_SPECIFICATION.md`，確認自身權限。
5. 閱讀 `TEAM_OPERATING_MODEL.md`。
6. 閱讀 `HANDOVER.md`。
7. 確認 Current Task、Owner、Scope、Constraints 與 Definition of Done。
8. 檢查 Git branch、working tree 與 remote。
9. 只執行已授權工作；資訊不足時停止推測並提出問題。

完成以上步驟，才可修改 Repository。

## Mandatory Update Rule

每個完成的 Task 必須在同一次 Project Sync 中更新適用項目：

- `PROJECT_STATUS.md`
- `NEXT_TASK.md`
- `ENGINEERING_STATUS.md` 或 `RESEARCH_STATUS.md`
- `CHANGELOG.md`
- `HANDOVER.md`
- `DECISION_LOG.md`，若涉及重大產品或治理決策
- `PROJECT_HISTORY.md`，若形成重大里程碑

文件更新、Commit、Push 與 Validation 缺一不可。未推送至正式 GitHub `main` 的內容不視為完成交接。

## Architecture First

- 先定義目的、邊界、資料契約與驗證，再進行工程實作。
- 新 Engine、Runtime 行為、外部整合與 Production Rule 必須先通過 Architecture Review。
- Candidate、Shadow、Verified 與 Core 都不自動取得 Runtime 權限。
- Runtime 權限採 deny-by-default。

## Research Freeze

Research Phase v1.0 已封版。

- G-030、G-031、G-033、G-034 為封版序列。
- 禁止未經 Architecture Review 新增 G 系列研究。
- 研究修正不得直接改變 Strategy、Scoring 或 Runtime。
- 新研究例外必須記錄原因、Owner、範圍、驗證要求與模型影響。

## Team Responsibility

- 綠茶：產品方向、風險承擔、最終驗收與決策。
- 小G：市場研究、Evidence、因果與 Hypothesis。
- 小P：架構、規格、邊界、派工與驗收。
- 小C：Repository、文件、Schema、程式、Git 與驗證。
- Auto Radar：執行已確認規則，不自行發明策略。

詳細權限由 `AI_ROLE_SPECIFICATION.md` 定義。

## Governance Rule

- 一張 Task 只有一個 Objective。
- 任一時間只能有一個 Current Task。
- 不知道就提問，不得猜測或自行延伸需求。
- 重大決策必須可追溯到 Decision ID、Owner 與 Git commit。
- 所有 Production 變更必須具備審核、驗證、監控與回復方案。
- 不得用工程便利性改變研究結論或交易邏輯。

## Amendment Rule

修改本憲章必須：

1. 建立獨立治理 Task。
2. 由小P完成 Architecture Review。
3. 由綠茶核准。
4. 說明變更原因、影響範圍與相容性。
5. 更新版本、Decision Log、Project Status 與 History。
6. 完成 Git commit、push 與引用驗證。

任何下位文件不得默示修改本憲章。

## Governance Map

```text
PROJECT_CONSTITUTION
  -> PROJECT_STATUS
  -> NEXT_TASK
  -> AI_ROLE_SPECIFICATION
  -> TEAM_OPERATING_MODEL
  -> HANDOVER
  -> Task specifications and implementation records
```

此圖表示權限與啟動順序。下位文件不得覆蓋上位文件。
