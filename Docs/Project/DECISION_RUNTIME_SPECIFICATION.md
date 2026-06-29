# North Star Decision Runtime Specification

文件代號：AR-NORTH-STAR-DECISION-SPEC-v1
任務代號：A-117
版本：1.0
狀態：Accepted
層級：Runtime Contract
負責人：小P／首席架構師
模型影響：Schema only，不定義演算法、策略或正式評分
最後更新：2026-06-29

## 目的

定義 `NorthStarDecision`、`NorthStarReason` 與 `NorthStarConfidence` 的資料結構，使未來 Runtime 有一致、可驗證、可追溯的輸出契約。

本規格只定義欄位與驗證要求，不定義如何選擇方向、計算信心度或產生 Recommendation。

## NorthStarDecision

```json
{
  "schema_version": "1.0",
  "decision_id": "string",
  "generated_at": "date-time",
  "as_of": "date-time",
  "runtime_mode": "shadow_candidate",
  "decision_state": "insufficient_data | candidate | validated | rejected | archived",
  "direction_candidate": null,
  "recommendation_candidate": {
    "type": null,
    "text": null,
    "owner": "綠茶",
    "production_authorized": false
  },
  "window": {
    "start_at": null,
    "end_at": null,
    "label": null
  },
  "reasons": [],
  "confidence": {},
  "risk_factors": [],
  "invalidators": [],
  "input_refs": {
    "market_regime_ref": null,
    "capital_flow_ref": null,
    "repository_snapshot_ref": null,
    "strategy_candidate_ref": null,
    "validation_report_ref": null
  },
  "validation": {
    "status": "pending",
    "errors": [],
    "warnings": [],
    "validated_at": null,
    "validator_version": null
  },
  "model_impact": "shadow_candidate_not_production"
}
```

## 必要欄位

- `schema_version`
- `decision_id`
- `generated_at`
- `as_of`
- `runtime_mode`
- `decision_state`
- `recommendation_candidate`
- `reasons`
- `confidence`
- `risk_factors`
- `invalidators`
- `input_refs`
- `validation`
- `model_impact`

## Decision State

| 狀態 | 定義 |
|---|---|
| `insufficient_data` | 必要輸入不足，不得補造方向或 Recommendation |
| `candidate` | Engine 已產生候選，尚未通過 Runtime Validator |
| `validated` | 結構與引用驗證通過，仍非 Production |
| `rejected` | 驗證失敗或被 Architecture／Product Owner 拒絕 |
| `archived` | 已封存且不可修改 |

`validated` 只代表契約與引用有效，不代表市場判斷正確，也不代表正式交易授權。

## Recommendation Candidate

- `type`：可空字串。允許值需由未來獨立 Architecture Decision 定義。
- `text`：可空字串。不得由工程層硬編碼市場建議。
- `owner`：固定為綠茶，代表最終決策權。
- `production_authorized`：Phase 1 必須固定為 `false`。

當資料不足、方法未核准或引用失效時，`type` 與 `text` 必須為 `null`。

## NorthStarReason

```json
{
  "reason_id": "string",
  "claim": "string",
  "source_layer": "market_regime | capital_flow | repository | strategy | validation",
  "source_refs": ["string"],
  "evidence_refs": ["string"],
  "counter_evidence_refs": ["string"],
  "limitations": ["string"],
  "status": "candidate | validated | rejected"
}
```

規則：

- 每個 Reason 必須至少有一個 `source_ref`。
- 市場事實 Claim 必須有 `evidence_refs`。
- 缺少 Evidence 時只能描述資料狀態，不得描述市場因果。
- `counter_evidence_refs` 與 `limitations` 不得被省略；沒有內容時使用空陣列。
- Reason 不得直接修改 Decision。

## NorthStarConfidence

```json
{
  "value": null,
  "status": "unavailable | candidate | validated",
  "scale": "0_100",
  "methodology_ref": null,
  "coverage": null,
  "freshness": null,
  "consistency": null,
  "uncertainty": [],
  "production_authorized": false
}
```

規則：

- `value` 可為 `null` 或 0 至 100 的數字。
- `methodology_ref` 為空時，`value` 必須為 `null`。
- 本文件不提供 Confidence Formula、Weight 或 Threshold。
- `coverage`、`freshness`、`consistency` 只接受未來核准 Schema 定義的值。
- `production_authorized` 在 Phase 1 必須為 `false`。

## Input Reference Rule

- 所有非空引用必須指向已存在且通過 Schema Validation 的 Repository 實體。
- Snapshot 必須不可變。
- 不得引用聊天訊息、未追蹤檔案或 Sandbox 未驗證資料。
- 任一必要引用失效時，`decision_state` 必須為 `insufficient_data` 或 `rejected`。

## Validation Requirement

- JSON Schema 驗證。
- 必要欄位驗證。
- Enum 與數值範圍驗證。
- 引用完整性驗證。
- Timestamp 順序驗證。
- `production_authorized` 固定值驗證。
- 不得包含交易執行、部位或資金配置欄位。
- 相同輸入與版本的重跑必須可比較。

## 明確不包含

- Decision Algorithm。
- Confidence Formula。
- Strategy Selection。
- Opportunity Score。
- Trading Action。
- Position Sizing。
- Capital Allocation。
- Repository Write。
