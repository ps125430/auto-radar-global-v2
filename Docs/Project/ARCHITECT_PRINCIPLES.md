# Auto Radar Architect Principles

Document ID: AR-ARCHITECT-PRINCIPLES-v1
Version: 1.0
Status: Active
Owner: 小P / Chief Architect
Governed By: `PROJECT_CONSTITUTION.md`
Last Updated: 2026-06-29

## 1. 先架構後工程

先確認 Objective、資料流、Authority、Boundary、Failure Mode 與 Definition of Done，再開始 Coding。

工程不得用實作結果反向取代缺少的 Architecture Decision。

## 2. Research 與 Engineering 分離

- Research 負責事實、Evidence、因果、Hypothesis 與不確定性。
- Architecture 負責把研究轉為規格與驗證邊界。
- Engineering 只實作核准規格。

研究文件不得直接成為 Runtime 行為，工程也不得重寫研究結論。

## 3. Explainability First

任何輸出都必須能追溯：

```text
Evidence -> Entity -> Rule or Candidate -> Output -> Outcome -> Review
```

無法說明來源、限制與失效條件的 Decision，不得進入 Production。

## 4. Product First

架構服務於真實產品目標：

- 使用者每天能在 30 秒內理解今天的狀態。
- 清楚知道可做、不可做與原因。
- 系統保留 Evidence 與 Review，不製造虛假的確定性。

不得為展示技術而增加與產品無關的複雜度。

## 5. Repository First

- 正式狀態、決策與規格只存在於 Repository。
- Git history 必須可追蹤。
- Chat、口頭共識與個別 AI 記憶不是 Architecture authority。
- 每個 Entity 必須有明確位置、Schema、Owner 與 lifecycle。

## 6. Long-term Maintainability

- 優先使用清楚、穩定且可測試的介面。
- 保持單一責任與單一真相來源。
- 避免重複文件、隱藏狀態與無 Owner 的資料。
- 變更必須考慮 migration、compatibility、monitoring 與 rollback。
- 技術債必須被記錄，不能靠記憶管理。

## 7. No Magic Decision

- 不允許無來源的分數、權重或結論。
- 不允許單一新聞直接產生交易決策。
- 不允許 AI 用黑箱推論補齊缺少資料。
- 不允許把相關性描述成因果。
- 不允許把 Candidate、Shadow 或 Verified 偷換為 Production。

任何 Decision 都必須有可檢查的 Input、Rule、Boundary、Invalidator 與 Review path。

## Architecture Review Checklist

Architecture Review 必須確認：

- Objective 是否唯一。
- Owner 與 Authority 是否清楚。
- Research 與 Engineering 是否分離。
- Schema、reference 與 lifecycle 是否定義。
- Runtime 與 Production impact 是否明確。
- Explainability、failure mode、validation 與 rollback 是否足夠。
- 是否符合 Product Mission。
- 是否更新 SSOT 與交接文件。
