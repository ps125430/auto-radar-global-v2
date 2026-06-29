# Runtime Governance v1

文件代號：AR-RUNTIME-GOVERNANCE-v1
任務代號：A-120
版本：1.0
狀態：Architecture Review Pending
層級：Runtime Governance Gate
負責人：小P／首席架構師
維護人：小C／文件工程
模型影響：治理候選，不啟用 Runtime、Strategy 或 Production Rule
最後更新：2026-06-29

## 目的

整合 A-116 至 A-119，建立 North Star Intelligence Phase 1 的 Runtime Boundary、Authority、IO Contract、Validation、Rollback 與 Repository Write Policy。

本文件是 E-121 的前置 Gate，不是 E-121 的實作授權。

## Governing Documents

| 任務 | 文件 | 功能 |
|---|---|---|
| A-116 | `RUNTIME_AUTHORITY_MATRIX.md` | Read／Suggest／Write 與 Engine 權限 |
| A-117 | `DECISION_RUNTIME_SPECIFICATION.md` | North Star Decision、Reason、Confidence Schema |
| A-118 | `RUNTIME_IO_CONTRACT.md` | Engine Input／Output 與 Layer boundary |
| A-119 | `REPOSITORY_WRITE_AUTHORITY.md` | Repository Write 與 Learning Suggest policy |
| A-120 | 本文件 | 統一 Runtime Gate、Validation 與 Rollback |

## Runtime Boundary

Phase 1 僅允許：

- Shadow candidate。
- 不可變 Repository snapshot input。
- 結構化 candidate output。
- Contract、Schema、reference 與 permission validation。
- 受控 Runtime artifact、audit 與 daily brief candidate。
- Repository-only fallback。

Phase 1 禁止：

- Production Runtime。
- 正式 Recommendation。
- Trading Execution。
- Position Sizing。
- Capital Allocation。
- Strategy creation。
- Confidence Formula creation。
- Weight 或 Score 變更。
- Learning 自動寫回 Knowledge。
- Engine 直接跨 Layer 呼叫。
- 外部 API、Crawler 或 News ingestion。

## Runtime Authority

權限原則：

1. deny-by-default。
2. Engine 最多 Read＋Suggest。
3. Engine 沒有 Write。
4. 受控 Writer 僅可寫入白名單的 Runtime output 區域。
5. 所有 Runtime Output 都是 Candidate。
6. 最終決策與風險仍屬綠茶。

在本文件通過前，所有候選權限仍為 Deny。

## Runtime Orchestration

```text
Validated Repository Snapshot
  ↓
Snapshot Adapter
  ↓
Runtime Orchestrator
  ↓
Contract Gateway
  ↓
Independent Engine
  ↓
Runtime Validator
  ↓
Candidate Output
  ↓
Artifact／Audit／Brief Writer（如獲授權）
  ↓
Dashboard Read-only Projection
```

Engine 之間不得直接呼叫。Orchestrator 只傳遞契約，不修改 Engine Output。

## Validation Layers

### 1. Contract Validation

- Contract version。
- 必要欄位。
- Timestamp。
- Request／Response identity。

### 2. Schema Validation

- Type。
- Enum。
- Range。
- Nullable rule。
- `production_authorized = false`。

### 3. Reference Validation

- Entity 存在。
- Status 可用。
- Snapshot 不可變。
- Evidence traceability。

### 4. Permission Validation

- Engine identity。
- Read／Suggest／Write scope。
- Target path whitelist。
- Layer boundary。

### 5. Behavioral Validation

- 相同輸入可比較。
- 資料不足不補造。
- Engine failure 不影響 Repository。
- Candidate 不被呈現為 Production。

### 6. Rollback Validation

- Engine 可停用。
- Writer 可停用。
- Dashboard 可回到 Repository-only。
- Artifact 與 Audit 可保留。
- 正式知識不需回復，因 Runtime 不得修改。

## Fail Fast

以下情況立即停止：

- Schema 不符。
- 引用不存在。
- Engine 越權。
- 跨 Layer 直接呼叫。
- 輸出包含 Production authorization。
- Learning 嘗試修改 Repository。
- Writer target 不在白名單。
- Input 使用未驗證 Sandbox 資料。
- Runtime output 無法追溯來源。

停止後只允許產生 Error Contract 與 Audit Candidate。

## Rollback Policy

### 觸發條件

- Validation failure。
- Permission breach。
- Non-deterministic output。
- Reference drift。
- Schema version mismatch。
- Dashboard 顯示 Candidate 為 Production。
- Runtime latency 或 failure 超過未來 E-121 核准門檻。

### 動作

1. 關閉受影響 Engine。
2. 關閉相關 Writer。
3. 停止產生新 Candidate。
4. Dashboard 回到 Repository-only。
5. 保存 Input、Output、Error 與 Audit。
6. 建立 Root Cause Review。
7. 小P決定修復、降級或撤回。

### 禁止

- 刪除 Audit。
- 覆寫原 Snapshot。
- 用人工值假裝 Runtime 正常。
- 自動重新啟用。

## Repository Write Policy

- Engine：Read／Suggest only。
- Learning：Suggest only。
- Artifact、Audit、Brief：只能由受控 Writer 寫入候選位置。
- Knowledge Update：必須另建人工審核與 Repository Task。
- Production knowledge write：Phase 1 禁止。

## E-121 Entry Gate

只有滿足以下條件才能建立 E-121：

- [ ] A-116 文件完成。
- [ ] A-117 文件完成。
- [ ] A-118 文件完成。
- [ ] A-119 文件完成。
- [ ] A-120 文件完成。
- [ ] 五份文件引用一致。
- [ ] 小P Architecture Review PASS。
- [ ] 綠茶接受 Shadow-only 邊界。
- [ ] 現行 `Docs/RUNTIME_AUTHORITY_MATRIX.md` 正式更新。
- [ ] `Docs/Project/PROJECT_STATUS.md` 宣告 Runtime Governance Gate OPEN。
- [ ] E-121 有單一 Objective、Files、Constraints、Acceptance 與 Rollback test。

## E-121 Allowed Scope Candidate

通過 Gate 後，E-121 最多可建立：

- North Star Runtime skeleton。
- Contract models。
- Input adapters。
- Orchestrator。
- Runtime Validator。
- Disabled-by-default Engine interfaces。
- Artifact／Audit test doubles。
- Shadow fixtures。
- Rollback tests。

不得直接建立真正 Recommendation、Confidence Formula、Strategy Logic 或 Production Runtime。

## Gate Decision

目前 Gate：**CLOSED**

目前結論：

```text
Runtime Governance Package: IMPLEMENTED FOR REVIEW
Architecture Review: PENDING
E-121: BLOCKED
N-001 through N-010: BLOCKED
Production Runtime: BLOCKED
```

Next Owner：小P／Architecture Review
