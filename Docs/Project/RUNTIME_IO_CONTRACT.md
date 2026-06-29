# Runtime IO Contract

文件代號：AR-RUNTIME-IO-CONTRACT-v1
任務代號：A-118
版本：1.0
狀態：Accepted
層級：Runtime Contract
負責人：小P／首席架構師
模型影響：契約候選，不啟用 Engine
最後更新：2026-06-29

## 目的

建立 North Star Intelligence Phase 1 各 Engine 的 Input／Output Contract，禁止跨 Layer 直接呼叫、共享可變狀態或繞過驗證。

## Runtime Layer

```text
Repository API
  ↓
Snapshot Adapter
  ↓
Runtime Orchestrator
  ↓
Contract Gateway
  ↓
Engine
  ↓
Runtime Validator
  ↓
Candidate Output
  ↓
受控 Writer（如獲授權）
```

Engine 不得直接讀取檔案系統，也不得直接呼叫其他 Engine。

## 通用 Input Envelope

```json
{
  "contract_version": "1.0",
  "request_id": "string",
  "engine_id": "string",
  "requested_at": "date-time",
  "as_of": "date-time",
  "runtime_mode": "shadow_candidate",
  "snapshot_refs": ["string"],
  "payload": {},
  "validation": {
    "status": "validated",
    "validator_version": "string"
  }
}
```

Input 必須：

- 不可變。
- 已通過 Schema 與 Cross Reference Validation。
- 有明確 `as_of`。
- 有版本與來源。
- 不包含 Secret 或未核准外部資料。

## 通用 Output Envelope

```json
{
  "contract_version": "1.0",
  "request_id": "string",
  "engine_id": "string",
  "generated_at": "date-time",
  "output_state": "insufficient_data | candidate | validated | rejected",
  "payload": {},
  "source_refs": ["string"],
  "warnings": [],
  "errors": [],
  "model_impact": "shadow_candidate_not_production"
}
```

Output 必須：

- 對應唯一 `request_id`。
- 保留所有來源引用。
- 明確揭露資料不足、警告與錯誤。
- 不包含執行交易或修改 Repository 的命令。
- 在 Runtime Validator 通過前不得交給 Writer。

## Engine Contract Matrix

| Engine | Input | Output | 禁止 |
|---|---|---|---|
| N-001 North Star Intelligence | Market Regime、Capital Flow、Repository Snapshot、Strategy Candidate、Validation Report | `NorthStarDecision` Candidate | 自行取得資料、定義策略、呼叫 N-002 至 N-010 |
| N-002 Ocean Intelligence | Capital Flow Snapshot、Graph Snapshot、Outcome Window Snapshot | Ocean State Candidate | 推測缺失節點、修改 Knowledge Graph |
| N-003 Opportunity Lifecycle | Opportunity Snapshot Sequence、Validation Status | Lifecycle State Candidate | 自動升級、降級或淘汰 Entity |
| N-004 Captain Decision | Validated NorthStarDecision Candidate、Risk Snapshot | Captain Text Candidate | 產生正式交易指令或資金配置 |
| N-005 Daily Story | Validated Reason Candidates、Regime／Flow References | Story Candidate | 新增市場事實、引用新聞原文作為未驗證結論 |
| N-006 Learning Runtime | Decision、Outcome、Evaluation、Review Snapshots | Lesson／Improvement Candidate | 直接修改 Knowledge、Playbook、Weight 或 Strategy |
| N-007 Evolution Runtime | Yesterday／Today／Week Snapshots | Evolution Delta Candidate | 覆寫歷史、修改 Entity Status |
| N-008 Explainability Runtime | Decision、Reason、Strategy、Flow、Regime、Evidence References | Explainability Graph Candidate | 改寫來源或補造 Evidence |
| N-009 Ocean Replay | Immutable Ocean Snapshots、Timeline Range | Replay Frame Sequence | 事後重算並替換原 Snapshot |
| N-010 Daily Brief | Validated Candidate Outputs、Repository Health | North Star Daily Brief Candidate | 產生不存在的 Recommendation 或小P指令 |

## 禁止跨 Layer 直接呼叫

- Dashboard 不得呼叫 Engine；只能讀取經核准投影。
- Engine 不得直接呼叫 Repository filesystem。
- Engine 不得直接呼叫 Writer。
- Engine 不得直接呼叫另一個 Engine。
- Learning 不得直接呼叫 Knowledge Promotion。
- Daily Brief 不得回寫 Decision、Reason 或 Confidence。

所有調度由 Runtime Orchestrator 完成；所有邊界由 Contract Gateway 檢查。

## Error Contract

```json
{
  "error_code": "string",
  "category": "contract | schema | reference | permission | validation | runtime",
  "message": "string",
  "engine_id": "string",
  "request_id": "string",
  "source_refs": ["string"],
  "retryable": false,
  "fallback": "repository_only"
}
```

規則：

- 不得吞掉錯誤。
- 不得以預設市場值掩蓋缺失資料。
- 權限錯誤一律不可重試，需 Architecture Review。
- Runtime 錯誤必須回到 Repository-only fallback。

## Determinism 與 Idempotency

- 相同 Input Snapshot、Contract Version 與 Engine Version 必須可重現。
- 每個 request 必須具有唯一識別碼。
- 重複 request 不得產生不同持久化 Artifact。
- Replay 只能讀取既有 Snapshot，不得修改歷史。

## Version Rule

- 新增必要欄位或改變語意屬 MAJOR。
- 新增選填欄位屬 MINOR。
- 文件與驗證修正屬 PATCH。
- Engine 不得接受高於自身支援版本的 Contract。

## Gate

本 Contract 只有在 A-120 PASS 且 E-121 明確引用後才能進入 Shadow Runtime 工程。
