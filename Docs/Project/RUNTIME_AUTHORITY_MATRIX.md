# Runtime Authority Matrix

文件代號：AR-RUNTIME-AUTHORITY-v2-CANDIDATE
任務代號：A-116
版本：1.0
狀態：Architecture Review Pending
層級：Runtime Governance
負責人：小P／首席架構師
維護人：小C／文件工程
模型影響：治理候選，不啟用 Runtime 或正式決策
最後更新：2026-06-29

## 目的

定義 North Star Intelligence Phase 1 的 Runtime 權限、讀取／建議／寫入等級、Engine 邊界與 Repository 權限。

本文件在 A-120 通過前不授予任何 Runtime 權限。現行有效權限仍以 `Docs/RUNTIME_AUTHORITY_MATRIX.md` 的 deny-by-default 規則為準。

## 權限等級

| 權限 | 定義 | 可做 | 不可做 |
|---|---|---|---|
| Deny | 無權限 | 回傳權限拒絕 | 讀取、建議、寫入 |
| Read | 唯讀 | 透過 Repository API 讀取已驗證快照 | 修改來源、繞過驗證、直接讀取未核准資料 |
| Suggest | 候選輸出 | 回傳具來源與限制的候選結果 | 自動執行、直接成為正式決策、寫回 Knowledge |
| Write | 受控寫入 | 經 Validator 後寫入指定 Runtime artifact 或 Report 區域 | 修改研究、Schema、治理文件或知識實體 |

權限由低至高不自動繼承。`Suggest` 不代表 `Write`，`Write` 也不代表 Production。

## Engine 權限矩陣

| Engine | Read | Suggest | Write | 邊界 |
|---|---:|---:|---:|---|
| N-001 North Star Intelligence | Candidate | Candidate | No | 可整合核准輸入並產生 North Star Decision Candidate |
| N-002 Ocean Intelligence | Candidate | Candidate | No | 可描述資金來源、目的地、速度與退潮候選 |
| N-003 Opportunity Lifecycle | Candidate | Candidate | No | 可輸出生命週期狀態候選，不得自動升降級 |
| N-004 Captain Decision | Candidate | Candidate | No | 可輸出建議文字候選，不得成為正式交易指令 |
| N-005 Daily Story | Candidate | Candidate | No | 可輸出來源可追溯的市場故事候選，不得捏造事實 |
| N-006 Learning Runtime | Candidate | Candidate | No | 僅能提出 Lesson 或 Knowledge Update Candidate |
| N-007 Evolution Runtime | Candidate | Candidate | No | 可比較時間快照並輸出演化候選 |
| N-008 Explainability Runtime | Candidate | Candidate | No | 可建立引用鏈，不得改寫 Decision 或 Evidence |
| N-009 Ocean Replay | Candidate | Candidate | No | 可重播不可變快照，不得重算歷史並覆寫原值 |
| N-010 North Star Daily Brief | Candidate | Candidate | No | 可聚合已驗證候選，不得新增 Recommendation |

`Candidate` 表示 A-120 通過後，可在 E-121 的 Shadow Scope 內被明確授權；目前仍為 Deny。

## 平台服務權限

| 服務 | Read | Suggest | Write | 允許位置 |
|---|---:|---:|---:|---|
| Runtime Orchestrator | Candidate | No | No | 僅傳遞不可變契約 |
| Runtime Validator | Candidate | No | No | 驗證輸入、輸出、引用與狀態 |
| Artifact Writer | Candidate | No | Candidate | `Runtime/Artifacts/`，需 E-121 建立與核准 |
| Audit Recorder | Candidate | No | Candidate | `Runtime/Audit/`，需 E-121 建立與核准 |
| Daily Brief Writer | Candidate | No | Candidate | `Reports/NorthStar/`，需 E-121 建立與核准 |
| Knowledge Promotion Writer | No | No | No | Phase 1 不存在 |

Engine 本身沒有寫入權。只有受控 Writer 服務可在輸出通過 Validator 後寫入明確白名單位置。

## Repository Authority

### 可讀候選

- `Knowledge/` 中狀態與 Schema 均有效的實體。
- `Data/` 中明確標示可供 Runtime candidate 使用的資料。
- `Runtime/Repository/index/` 中通過全域驗證的索引與報告。
- `Schemas/` 中核准版本。

### 禁止讀取

- 未驗證 Sandbox 資料。
- 損壞、缺少版本或缺少來源的紀錄。
- 聊天內容。
- 未納入 SSOT 的臨時檔案。
- 任何 Credential、Secret 或未核准外部來源。

### 禁止寫入

- `Knowledge/`
- `Data/`
- `Schemas/`
- `Docs/`
- `Dashboard/`
- `TEAM_OPERATING_SYSTEM.md`
- 任何現有 Evidence、Case、Pattern、Experience、Playbook、Prediction、Outcome、Review 或 Learning 紀錄

## Engine 邊界

- Engine 不得彼此直接呼叫。
- Engine 只接受 Runtime IO Contract 定義的不可變輸入。
- Engine 輸出必須是 Candidate，並包含來源、限制與 Validation。
- Engine 不得自行查網路、呼叫外部 API 或讀取聊天內容。
- Engine 不得自行建立 Strategy、Weight、Score Formula 或 Production Rule。
- Engine 不得執行交易、下單、部位配置或資金配置。

## 權限衝突規則

發生權限不明或文件衝突時：

1. 立即 Deny。
2. 保留輸入與錯誤紀錄。
3. 不產生替代值。
4. 回報 Runtime Governance Error。
5. 交由小P Architecture Review。

## Gate 狀態

目前狀態：**CLOSED**

開啟條件：

- A-116 至 A-120 全部完成。
- 小P Architecture Review PASS。
- 綠茶接受 Shadow Runtime 邊界。
- 現行 `Docs/RUNTIME_AUTHORITY_MATRIX.md` 完成正式修訂。
- E-121 建立獨立工程任務。
