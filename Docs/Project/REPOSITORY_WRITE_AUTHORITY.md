# Repository Write Authority

文件代號：AR-REPOSITORY-WRITE-AUTHORITY-v1
任務代號：A-119
版本：1.0
狀態：Accepted
層級：Runtime Governance
負責人：小P／首席架構師
模型影響：寫入政策候選，不授權自動知識更新
最後更新：2026-06-29

## 目的

定義 Runtime Engine 與平台服務對 Repository 的 Read、Suggest、Write 權限，防止 Learning 或 Decision Runtime 直接修改正式知識。

## 最高原則

- Runtime Engine 沒有 Repository Write 權限。
- `Suggest` 是輸出候選，不是寫入正式知識。
- Learning Engine 僅允許 Suggest。
- Learning Engine 僅允許 Suggest，不得直接修改 Repository。
- Knowledge Update 必須經人工或獨立核准流程。
- 未列入白名單的寫入一律 Deny。

## Engine 權限

| Engine | Read | Suggest | Write |
|---|---:|---:|---:|
| North Star Intelligence | Candidate | Candidate | No |
| Ocean Intelligence | Candidate | Candidate | No |
| Opportunity Lifecycle | Candidate | Candidate | No |
| Captain Decision | Candidate | Candidate | No |
| Daily Story | Candidate | Candidate | No |
| Learning Runtime | Candidate | Candidate | **No** |
| Evolution Runtime | Candidate | Candidate | No |
| Explainability Runtime | Candidate | Candidate | No |
| Ocean Replay | Candidate | Candidate | No |
| North Star Daily Brief | Candidate | Candidate | No |

以上權限在 A-120 PASS 前均為 Deny。

## 平台 Writer

只有以下受控平台服務可成為 Write Candidate：

| Writer | 允許用途 | 允許位置 | 條件 |
|---|---|---|---|
| Artifact Writer | 保存不可變 Shadow Output | `Runtime/Artifacts/` | Contract 與 Validation PASS |
| Audit Recorder | 保存 request、version、error、latency 與 permission audit | `Runtime/Audit/` | 不含 Secret，不改寫既有紀錄 |
| Daily Brief Writer | 產生每日唯讀報告 | `Reports/NorthStar/` | 所有引用可追溯，無 Production Command |

這些路徑與 Writer 尚不存在。只能由 E-121 在 A-120 PASS 後建立。

## 永久禁止的 Runtime 寫入

Runtime 不得直接寫入：

- `Knowledge/Evidence/`
- `Knowledge/CaseLibrary/`
- `Knowledge/Pattern/`
- `Knowledge/Experience/`
- `Knowledge/Playbook/`
- `Knowledge/Prediction/`
- `Knowledge/Outcome/`
- `Knowledge/OutcomeEvaluation/`
- `Knowledge/DailyReview/`
- `Data/Learning/`
- `Schemas/`
- `Docs/`
- `Dashboard/`

Runtime 也不得修改 Registry、Index、Constitution、Score、Weight 或 Research conclusion。

## Suggest Contract

Suggestion 必須包含：

```json
{
  "suggestion_id": "string",
  "suggestion_type": "lesson | lifecycle | playbook | evidence_request | engineering | other",
  "generated_at": "date-time",
  "source_refs": ["string"],
  "description": "string",
  "uncertainty": ["string"],
  "validation_required": true,
  "target_repository": null,
  "status": "candidate",
  "production_authorized": false
}
```

`target_repository` 在 Runtime 產生時必須為 `null`。目標位置只能由後續人工 Review 指定。

## Learning Promotion Flow

```text
Learning Runtime
  ↓
Suggestion Candidate
  ↓
Runtime Validator
  ↓
Review Queue（候選，由受控 Writer 或人工建立）
  ↓
小P Architecture Review
  ↓
綠茶核准（若涉及產品或風險）
  ↓
獨立 Repository Update Task
  ↓
小C 實作、驗證、Commit、Push
```

Learning Runtime 不得跳過任何一步。

## Write Validation

每次受控寫入必須驗證：

- Writer identity。
- Target path 白名單。
- Contract version。
- Schema。
- Source references。
- Duplicate ID。
- Immutable rule。
- Production boundary。
- Audit record。
- Rollback instruction。

任一失敗立即停止，不得產生部分寫入。

## Rollback

- Runtime Artifact 與 Report 只能新增版本，不覆寫正式知識。
- 錯誤 Artifact 標記 `rejected` 並保留 audit。
- 停止 Writer 後，Dashboard 回到 Repository-only 狀態。
- Rollback 不得刪除 Evidence、Decision、Outcome 或 Audit。

## Gate

目前 Write Authority：**NONE**

A-120 PASS 只允許 E-121 建立 Shadow Writer Candidate，不自動授予 Production Write。
