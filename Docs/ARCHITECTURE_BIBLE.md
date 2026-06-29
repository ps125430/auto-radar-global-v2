# Auto Radar 架構聖經 v1.0

文件代號：AR-ARCHITECTURE-BIBLE-v1
版本：1.0
狀態：有效
負責人：小P／首席架構師
維護人：小C／工程
最後更新：2026-06-29
影響範圍：文件與知識整合，不影響正式執行與交易規則

## 文件定位

本文件是 Auto Radar 唯一完整架構說明，供新小P、新小G、新小C、新工程師與未來 AI 在單一文件中理解專案使命、歷史、治理、研究、架構、知識庫、儀表板、工程與路線圖。

本文件整合既有正式文件，但不取代下列權限：

- 專案最高治理以 [`Project/PROJECT_CONSTITUTION.md`](Project/PROJECT_CONSTITUTION.md) 為準。
- 當前專案狀態以 [`Project/PROJECT_STATUS.md`](Project/PROJECT_STATUS.md) 為唯一真相來源。
- 唯一目前任務以 [`Project/NEXT_TASK.md`](Project/NEXT_TASK.md) 為準。
- 正式執行權限以 [`RUNTIME_AUTHORITY_MATRIX.md`](RUNTIME_AUTHORITY_MATRIX.md) 為準。

若本文件與上述即時權限文件衝突，必須停止推測、查明最新狀態並修正本文件。

---

## 第一章　專案願景

### 目的

說明 Auto Radar 是什麼、不是什麼，以及產品最終要解決的問題。

### 目前狀態

Auto Radar 是一套可適應、可追溯、可驗證的市場決策智慧系統。它將證據、研究、案例、型態、經驗、劇本、預測、結果、檢討與學習串成持續演化的知識生命週期。

Auto Radar 不是：

- 股票資訊網站。
- 券商應用程式。
- 自動下單工具。
- 保證預測正確的黑箱。
- 看到單一新聞就產生買進訊號的系統。

產品目標是讓綠茶每天打開系統三十秒，就能理解：

- 今天怎麼做。
- 今天關注什麼。
- 今天不要做什麼。
- 為什麼。

### 已完成

- 建立固定產品使命。
- 建立證據到學習的可追溯架構。
- 建立唯讀繁體中文 North Star 儀表板第一版。
- 建立專案治理中心與唯一狀態來源。
- 建立研究封版、知識庫驗證與工程邊界。

### 下一步

- 以正式核准的每日資料取代等待資料狀態。
- 保持儀表板唯讀，先完成資料品質與驗證閉環。
- 在進入影子執行前完成獨立架構、監控與回復方案。

目前沒有已指派的下一個產品任務；不得自行從路線圖挑選工作。

### 架構註記

核心承諾：

```text
每一次決策留下證據
  ↓
每一次結果接受驗證
  ↓
每一次失敗找出原因
  ↓
每一次修正累積知識
  ↓
下一次決策更成熟
```

最終決策與風險仍由綠茶承擔。系統只執行已確認規則，不取代產品負責人的判斷。

### 驗證

- 產品使命來源：[`Project/VISION.md`](Project/VISION.md)。
- 權責來源：[`Project/AI_ROLE_SPECIFICATION.md`](Project/AI_ROLE_SPECIFICATION.md)。
- 交易與正式執行邊界來源：[`RUNTIME_AUTHORITY_MATRIX.md`](RUNTIME_AUTHORITY_MATRIX.md)。
- 本章不得被解讀為買賣建議或正式交易規則。

---

## 第二章　專案時間軸

### 目的

說明專案從研究、知識庫、儀表板到工程階段的演化順序，避免新接手者把不同時期的文件混為目前狀態。

### 目前狀態

專案位於「工程階段：North Star Shadow Dashboard Binding」。研究階段、知識庫第一階段與 North Star 儀表板第一版已完成。A-116 至 A-120 已獲 Architecture Review PASS，Runtime Gate 已開啟；E-121 至 E-125 Shadow infrastructure 與 E-126 至 E-130 Shadow integration 已完成並推送 GitHub，E-131 至 E-135 Dashboard Shadow binding 已完成並等待小P驗收，正式 Production Runtime 仍未獲授權。

### 已完成

| 日期 | 里程碑 | 結果 |
|---|---|---|
| 2026-06-25 | 專案基礎 | 建立專案管理核心、知識核心、決策實驗室與研究框架 |
| 2026-06-26 | 治理與知識生命週期 | 建立團隊作業系統、工作契約、證據、案例、學習與結果資料骨架 |
| 2026-06-27 | 研究階段完成 | 完成架構封箱與工程就緒審查，研究第一版正式封版 |
| 2026-06-27 至 2026-06-28 | 知識庫階段完成 | 建立主要實體知識庫、索引、驗證器與全域驗證 |
| 2026-06-28 至 2026-06-29 | 沙盒知識生命週期 | 完成證據匯入、案例候選、人工審查與型態候選流程 |
| 2026-06-29 | 儀表板第一版 | 建立唯讀介面並完成全站繁體中文化 |
| 2026-06-29 | 專案治理中心 | 建立唯一狀態來源、專案憲章、角色規格與正式交接 |
| 2026-06-29 | 架構聖經第一版 | 將全專案架構整合為單一交接文件 |
| 2026-06-29 | North Star 儀表板第一版 | 完成四屏任務中心、統一卡片、洋流圖、Top3、學習與演化介面 |

### 下一步

依正式路線圖依序前進：

```text
研究（完成／封版）
  ↓
知識庫（完成）
  ↓
North Star 儀表板第一版（工程完成／等待驗收）
  ↓
引擎（規劃中，正式行為受阻）
  ↓
自動化
  ↓
測試版
  ↓
正式第一版
```

### 架構註記

- 時間軸只記重大里程碑，不取代版本控制紀錄。
- 「完成知識庫」表示結構、索引與驗證能力存在，不代表取得正式執行權限。
- 「工程就緒」不等於「正式環境就緒」。
- 階段不可跳過，路線圖項目也不等於已核准任務。

### 驗證

- 重大時間軸來源：[`Project/PROJECT_HISTORY.md`](Project/PROJECT_HISTORY.md)。
- 當前階段來源：[`Project/PROJECT_STATUS.md`](Project/PROJECT_STATUS.md)。
- 路線圖來源：[`Project/ROADMAP.md`](Project/ROADMAP.md)。
- 工程就緒定義來源：[`ENGINEERING_READINESS_REVIEW.md`](ENGINEERING_READINESS_REVIEW.md)。

---

## 第三章　團隊模型

### 目的

定義綠茶、小P、小G、小C的責任、權限與禁止事項，防止角色越權。

### 目前狀態

團隊採「產品決策、研究、架構、工程、驗收」分離。每張任務只有一個目標與一位下一責任人。

### 已完成

| 角色 | 核心責任 | 權限 | 邊界 |
|---|---|---|---|
| 綠茶／產品負責人 | 產品方向、真實需求、風險與最終驗收 | 最終產品決策與風險接受 | 不搬資料、不寫程式、不代替研究或架構 |
| 小P／首席架構師 | 架構、規格、邊界、派工與驗收 | 接受或拒絕架構，阻擋違憲變更 | 不捏造證據、不改寫研究結論、不跳過驗證 |
| 小G／研究長 | 市場事實、證據、因果、預期與假設 | 提出研究結論、證據品質與不確定性 | 不寫程式、不改正式執行、不自行派工程 |
| 小C／工程 | 知識庫、文件、結構描述、程式、版本控制與驗證 | 在核准範圍內選擇實作並因驗證失敗阻擋提交 | 不發明策略、不改權重、不改研究、不放寬正式執行權限 |

責任鏈：

```text
綠茶提出需求
  ↓
小G研究（研究封版期間須先獲准）
  ↓
小P轉為架構與規格
  ↓
小C實作與驗證
  ↓
小P架構驗收
  ↓
綠茶最終驗收
```

### 下一步

- 每個新對話先確認自身角色。
- 每張派工使用固定輸入、輸出與完成定義。
- 發生權限重疊時停止實作，由小P釐清；涉及產品風險時由綠茶決定。

### 架構註記

四大鐵律：

- 小G不碰程式。
- 小P不改研究結論。
- 綠茶不搬資料。
- 小C不自行發明策略。

角色名稱描述責任，不授予超出專案憲章的權限。

### 驗證

- 角色完整規格：[`Project/AI_ROLE_SPECIFICATION.md`](Project/AI_ROLE_SPECIFICATION.md)。
- 團隊作業模型：[`Project/TEAM_OPERATING_MODEL.md`](Project/TEAM_OPERATING_MODEL.md)。
- 工作契約：[`../TEAM_OPERATING_SYSTEM.md`](../TEAM_OPERATING_SYSTEM.md)。
- 架構原則：[`Project/ARCHITECT_PRINCIPLES.md`](Project/ARCHITECT_PRINCIPLES.md)。

---

## 第四章　專案治理

### 目的

確保任何 AI 或協作者都從正式知識庫取得相同狀態，不依賴聊天記憶。

### 目前狀態

專案治理第二版已建立。GitHub 是正式知識庫，`Project/PROJECT_STATUS.md` 是唯一專案狀態來源。

### 已完成

核心治理規則：

1. **知識庫優先**：聊天寫入正式知識庫後才成為專案紀錄。
2. **單一真相來源**：階段、衝刺、目前任務與進度只由專案狀態文件宣告。
3. **單一目前任務**：任一時間只能有一個目前任務。
4. **零猜測**：資訊不足就提問，不自行補功能或策略。
5. **先架構後工程**：新引擎、正式行為與外部整合先經架構審查。
6. **強制同步**：完成任務時同步狀態、任務、工程或研究狀態、變更、交接與必要決策。

AI 啟動流程：

```text
專案憲章
  ↓
專案狀態
  ↓
目前與下一任務
  ↓
AI 角色規格
  ↓
團隊作業模型
  ↓
交接快照
  ↓
確認分支、工作目錄、遠端、範圍與完成定義
  ↓
開始工作
```

### 下一步

- 每次任務完成後執行完整專案同步。
- 新 AI 必須先完成啟動流程，不要求使用者重新解釋專案。
- 舊狀態文件只保留歷史用途，不得重新取得權限。

### 架構註記

治理權限由高至低：

```text
專案憲章與綠茶明確決策
  ↓
專案狀態
  ↓
唯一目前任務
  ↓
已核准架構規格
  ↓
其他正式知識庫文件
  ↓
聊天與個別 AI 記憶
```

架構聖經是完整說明文件，不是新的即時狀態來源。

### 驗證

- 最高治理：[`Project/PROJECT_CONSTITUTION.md`](Project/PROJECT_CONSTITUTION.md)。
- 唯一狀態：[`Project/PROJECT_STATUS.md`](Project/PROJECT_STATUS.md)。
- 唯一任務：[`Project/NEXT_TASK.md`](Project/NEXT_TASK.md)。
- 正式交接：[`Project/HANDOVER.md`](Project/HANDOVER.md)。
- 重大決策：[`Project/DECISION_LOG.md`](Project/DECISION_LOG.md)。

---

## 第五章　研究層

### 目的

說明研究層完成了什麼、研究如何進入架構，以及封版後可做與不可做的事。

### 目前狀態

研究階段第一版已完成並封版。G-030、G-031、G-033、G-034 是正式封版序列，不得在未經架構審查下新增 G 系列研究。

### 已完成

| 封版任務 | 架構意義 |
|---|---|
| G-030 | 收斂研究模組與主要市場認知資產 |
| G-031 | 整理研究間的依賴、邊界與交接條件 |
| G-033 | 完成研究封箱所需的架構一致性 |
| G-034 | 宣告研究第一版完成並轉入受限工程階段 |

研究資產涵蓋：

- 市場演化：市場記憶、預期差、型態飽和、敘事強度、AI 影響與資訊擴散。
- 敘事智慧：敘事生命週期、主題輪動、再生條件與敘事資料庫。
- 現實框架：區分事實、敘事、預期與市場反應。
- 市場流：市場角色、資訊流向、吸收記憶與資訊信心。
- 證據與案例驗證：預測封存、結果視窗、根因稽核與候選改善。
- 市場心智與決策日誌：記錄市場狀態、缺失資訊、可避免性與學習目標。
- 學習分類：成功、失敗、未知與改善候選。

### 下一步

封版期間只允許：

- 修正明確事實錯誤。
- 修復壞連結、編碼與結構問題。
- 加入已核准的證據、案例、結果、評估與檢討。
- 依驗證結果維護候選知識。

若確實需要新研究，必須先提出封版基線不足的原因，再由小P核准單一研究目標。

### 架構註記

- 研究只產生事實、假設、候選調節因子與驗證需求。
- 研究不得直接修改主題分數、階段分數、決策分數、權重或正式交易邏輯。
- 單一案例不能升級為核心規則。
- 研究結論必須保留反例、不確定性與失效條件。

### 驗證

- 研究狀態：[`Project/RESEARCH_STATUS.md`](Project/RESEARCH_STATUS.md)。
- 研究封版宣告：[`RESEARCH_PHASE_V1_COMPLETE.md`](RESEARCH_PHASE_V1_COMPLETE.md)。
- 封版政策：[`ARCHITECTURE_FREEZE_POLICY.md`](ARCHITECTURE_FREEZE_POLICY.md)。
- 研究框架位於 `Docs/`，資料候選位於 `Data/`，皆不自動取得正式執行權限。

---

## 第六章　系統架構

### 目的

整理主要架構決策、知識庫設計、儀表板設計，以及決策、檢討與驗證流程。

### 目前狀態

系統採分層架構：

```text
治理層
  ↓
研究層
  ↓
知識庫與結構描述層
  ↓
驗證與沙盒層
  ↓
展示層
  ↓
影子執行（尚未核准）
  ↓
正式執行（禁止）
```

### 已完成

重大架構決策：

| 決策代號 | 決策 |
|---|---|
| DEC-001 | 研究階段第一版封版 |
| DEC-002 | GitHub 是正式專案知識庫 |
| DEC-003 | `Project/PROJECT_STATUS.md` 是唯一專案狀態來源 |
| DEC-004 | 儀表板維持唯讀並只讀取知識庫 |
| DEC-005 | 儀表板以繁體中文為主要介面 |
| DEC-006 | 首頁以每日作戰、前三機會、風險、有效天數與可解釋性為核心 |
| DEC-007 | 缺少正式機會分數時必須誠實顯示等待資料 |
| DEC-008 | 專案憲章第二版管理 AI 啟動、權限、強制更新與衝突處理 |
| DEC-009 | 架構聖經是唯一完整架構交接文件 |
| DEC-010 | 儀表板採 North Star 四屏 Mission Control |
| DEC-011 | Runtime BLOCK 成立，N-001 至 N-010 暫停 |
| DEC-012 | Runtime Governance v1 PASS，Gate OPEN，授權 E-121 至 E-125 Shadow infrastructure |

決策資料流：

```text
證據
  ↓
案例
  ↓
型態
  ↓
經驗
  ↓
劇本
  ↓
預測快照
  ↓
結果
  ↓
結果評估
  ↓
檢討
  ↓
學習候選
  ↓
經核准的知識更新
```

檢討流程：

```text
預測
  ↓
結果
  ↓
評估
  ↓
檢討預測錯誤、行為錯誤、執行錯誤與缺失資訊
  ↓
判斷是否可避免
  ↓
建立學習目標與改善候選
```

驗證流程：

```text
結構描述驗證
  ↓
必要欄位驗證
  ↓
識別碼與生命週期驗證
  ↓
跨實體引用驗證
  ↓
索引與登錄驗證
  ↓
快速失敗
  ↓
產生驗證報告
```

### 下一步

- 修正已知資料損壞與路徑大小寫風險。
- 取得正式每日證據與核准資料。
- 小P驗收 E-121 至 E-125 Runtime infrastructure。
- 未經另案授權，不得進入 N-series 或 Production Runtime。
- 正式執行必須在影子驗證後另行核准。

### 架構註記

- 正式執行權限預設拒絕。
- 案例與型態沒有正式執行權限。
- 經驗只能是倍數或停止條件候選。
- 劇本只能提供條件、倍數或情境候選。
- 預測只能封存事件前狀態，不得事後改寫。
- 結果與檢討只供評估與學習，不得直接改分數。
- 候選、影子、已驗證、核心都不等於正式環境。
- Runtime Engine 最多只能成為 Read／Suggest Candidate，沒有 Repository Write 權限。
- Learning 僅允許 Suggest，不得直接更新 Knowledge。
- Runtime Gate 已對 E-121 至 E-125 Shadow infrastructure 開啟；Production Runtime 維持 CLOSED。

### 驗證

- 架構索引：[`ARCHITECTURE_INDEX.md`](ARCHITECTURE_INDEX.md)。
- 架構憲章：[`ARCHITECTURE_CONSTITUTION.md`](ARCHITECTURE_CONSTITUTION.md)。
- 實體圖：[`ENTITY_MAP.md`](ENTITY_MAP.md)。
- 正式執行權限：[`RUNTIME_AUTHORITY_MATRIX.md`](RUNTIME_AUTHORITY_MATRIX.md)。
- Runtime Governance candidate：[`Project/RUNTIME_GOVERNANCE.md`](Project/RUNTIME_GOVERNANCE.md)。
- 重大決策：[`Project/DECISION_LOG.md`](Project/DECISION_LOG.md)。

---

## 第七章　知識庫

### 目的

完整說明所有主要知識實體、沙盒、關係、資料流與驗證責任。

### 目前狀態

知識庫第一階段已完成，具備主要實體目錄、結構描述、索引與全域驗證能力。部分舊目錄仍有命名重疊或資料品質問題，不能將「結構存在」誤認為「內容已可正式使用」。

### 已完成

| 實體 | 用途 | 主要位置 | 正式執行權限 |
|---|---|---|---|
| 證據 | 保存來源、時間、摘要、重要度與可靠性 | `Knowledge/Evidence/`、`Schemas/Evidence/` | 無 |
| 案例 | 封存情境、預測、證據、結果與檢討 | `Knowledge/CaseLibrary/`、`Schemas/CaseLibrary/` | 無 |
| 型態 | 表示由多個案例支持的重複關係候選 | `Knowledge/Pattern/`、`Schemas/Pattern/` | 無 |
| 經驗 | 聚合型態與案例，追蹤健康度與衝突 | `Knowledge/Experience/`、`Schemas/Experience/` | 倍數或停止條件候選 |
| 知識圖譜 | 描述實體間靜態關係與依賴 | `Knowledge/Graph/`、`Schemas/Graph/` | 無推論權限 |
| 劇本 | 保存條件式回應知識與情境限制 | `Knowledge/Playbook/`、`Schemas/Playbook/` | 條件、倍數或情境候選 |
| 預測 | 封存事件前的預期、風險、失效條件與引用 | `Knowledge/Prediction/`、`Schemas/Prediction/` | 僅決策快照 |
| 結果 | 保存十分鐘、二十四小時與五個交易日結果 | `Knowledge/Outcome/`、`Schemas/Outcome/` | 僅供檢討 |
| 結果評估 | 比較預測與結果的敘事、龍頭、主題、流向、時間與風險 | `Knowledge/OutcomeEvaluation/`、`Schemas/OutcomeEvaluation/` | 僅供檢討 |
| 每日檢討 | 分類預測、行為、執行錯誤與缺失資訊 | `Knowledge/DailyReview/`、`Schemas/DailyDecision/` | 僅供學習 |
| 學習 | 將成功、失敗與未知轉為改善候選 | `Data/Learning/`、`Knowledge/Lessons/` | 僅候選輸出 |

沙盒生命週期：

```text
手動原始資料
  ↓
證據匯入沙盒
  ↓
證據
  ↓
案例候選沙盒
  ↓
人工審查
  ↓
已驗證案例
  ↓
型態探索沙盒
  ↓
型態候選
```

主要沙盒：

- `Sandbox/Ingestion/`：支援手動匯入 Markdown、JSON、YAML。
- `Sandbox/CaseCandidate/`：規則式將證據轉成案例候選。
- `Sandbox/Review/`：人工核准或拒絕案例候選。
- `Sandbox/PatternDiscovery/`：規則式將已驗證案例轉成型態候選。

全域驗證涵蓋：

- 重複識別碼。
- 遺漏必要欄位。
- 非法生命週期狀態。
- 遺漏結構描述或索引。
- 型態指向不存在案例。
- 經驗指向不存在型態或案例。
- 圖譜指向不存在實體。
- 劇本指向不存在圖譜。
- 評估指向不存在結果。
- 檢討指向不存在評估。

### 下一步

- 修復舊資料編碼與損壞 JSON。
- 解決 `Data/` 與 `data/` 並存的跨平台風險。
- 合併或明確封存 `Playbook/` 與 `Playbooks/` 等舊路徑差異。
- 加入正式來源的證據與多案例驗證。
- 在任何自動提升前建立人工審查與回復機制。

### 架構註記

- 每個實體必須有穩定識別碼、版本、狀態、擁有者與可追溯來源。
- 資料夾生命週期不自動授權內容升級。
- 圖譜只描述靜態關係，不執行推論。
- 沙盒資料不得被展示成正式市場事實。
- 驗證器採快速失敗；缺少引用時不得靜默補造。

### 驗證

- 實體與權限：[`ENTITY_MAP.md`](ENTITY_MAP.md)。
- 知識庫治理：[`REPOSITORY_GOVERNANCE.md`](REPOSITORY_GOVERNANCE.md)。
- 目錄標準：[`REPOSITORY_STRUCTURE_STANDARD.md`](REPOSITORY_STRUCTURE_STANDARD.md)。
- 全域驗證入口：`Runtime/Repository/global_validator.py`。
- 驗證報告：`Runtime/Repository/index/validation_report.json`。
- 已知問題：[`Project/KNOWN_ISSUES.md`](Project/KNOWN_ISSUES.md)。

---

## 第八章　儀表板

### 目的

說明儀表板首頁理念、資訊階層、每日決策中心、前三機會、今日發動原因、資金流與證據呈現。

### 目前狀態

North Star 儀表板第一版已完成 E-111 至 E-120 工程實作。它是唯讀展示層，只顯示知識庫現有內容，不計算策略、信心度、機會分數、資金流或交易行動。

### 已完成

首頁理念：

- 第一眼回答今日策略、風險、有效天數與市場狀態。
- 固定呈現前三大機會位置，但無核准分數時誠實顯示等待資料。
- 每個候選可展開查看原因、證據、資金、歷史與風險。
- 不以工程展示取代每日使用需求。

四屏資訊階層：

```text
北極星、今日航向、Top3、禁航區
  ↓
全球洋流、潮汐、市場環境、資料健康
  ↓
聰明資金、籌碼擁擠、市場能量、資金速度
  ↓
知識庫、每日學習、知識演化、決策檢討
```

主要模組：

- **今日北極星**：今日策略、信心度、預估有效天數、今日發動原因。
- **我的船**：目的地、航行時間、風浪、趨勢、原因與證據。
- **前三機會與禁航區**：機會候選、分數、資金、風險與避免布局邊界。
- **全球洋流圖**：呈現已驗證節點；缺少資料時顯示明確的未驗證概念航線。
- **市場與資金卡片**：洋流、潮汐、市場環境、資料健康、聰明資金、密度、能量與速度。
- **市場故事**：只顯示已有市場認知或策略原因，不自行生成市場結論。
- **學習與演化**：知識庫數量、每日學習摘要、生命週期與檢討狀態。
- **證據與可解釋性**：展開來源、引用實體、風險與缺失資料。

### 下一步

- 接入經核准的每日策略紀錄。
- 接入經核准的市場狀態資料。
- 接入正式機會分數與已驗證資金流圖譜。
- 修復外部圖示來源的可用性風險。

以上都需要獨立核准任務；儀表板不得自行推導缺失內容。

### 架構註記

- 顯示層不改寫知識庫。
- 缺少資料時使用明確等待狀態，不以相似度冒充機會分數。
- 概念航線必須標示尚未驗證，不得冒充正式資金流。
- 所有資訊卡使用標題、分數、趨勢、觀察窗、原因與證據骨架。
- 不得出現買進、賣出或其他未核准交易行動。
- 繁體中文是主要使用介面；股票代號、ETF 代號、API 名稱、除錯與紀錄可保留原文。
- 儀表板程式位於 `Dashboard/`，資料投影由核准腳本建立。

### 驗證

- 儀表板說明：[`../Dashboard/README.md`](../Dashboard/README.md)。
- 介面入口：`Dashboard/index.html`。
- 展示邏輯：`Dashboard/app.js`。
- 資料投影：`Dashboard/dashboard-data.js`。
- 產品決策：[`Project/DECISION_LOG.md`](Project/DECISION_LOG.md) 中 DEC-004 至 DEC-007、DEC-010。

---

## 第九章　工程

### 目的

整理已完成工程、目前衝刺、下一步與仍未完成的能力，防止把知識庫程式誤認為交易引擎。

### 目前狀態

目前為「North Star Shadow Dashboard Binding」階段。A-116 至 A-120 已獲小P架構驗收 PASS；E-121 至 E-125 與 E-126 至 E-130 已完成工程實作並推送 GitHub；E-131 至 E-135 已完成工程實作並等待驗收。N-001 至 N-010 與 Production Runtime 維持 BLOCKED。

### 已完成

| 任務 | 完成內容 |
|---|---|
| E-001 | 案例知識庫引擎 |
| E-002 | 型態知識庫引擎 |
| E-003 | 經驗知識庫引擎 |
| E-004 | 知識圖譜知識庫 |
| E-005 | 劇本知識庫 |
| E-006 | 結果、評估與檢討知識庫 |
| E-007 | 全域知識庫驗證器 |
| E-008 | 預測快照資料層 |
| E-009 | 每日報告產生器第一版 |
| E-010 | 晨間報告第一版 |
| E-011 | 證據知識庫基礎 |
| E-012 | 證據匯入沙盒 |
| E-013 | 證據轉案例候選沙盒 |
| E-014 | 人工審查與已驗證案例沙盒 |
| E-015 | 型態探索沙盒 |
| E-100 | Auto Radar 儀表板第一版 |
| E-101 Rev.1 | 儀表板全面繁體中文化 |
| C-035 | 專案治理中心與唯一狀態來源 |
| C-036 | 專案憲章與 AI 作業系統 |
| C-037 | 架構聖經第一版 |
| E-111 至 E-120 | North Star 儀表板框架、卡片、洋流、Hero、Captain、Top3、市場故事、學習、演化與整合 |
| A-116 至 A-120 | Runtime Authority、Decision Schema、IO Contract、Write Policy、Validation 與 Rollback Governance |
| E-121 至 E-125 | Runtime Framework、Decision Schema packaging、Explain Chain、Learning Suggestions 與 Patch Queue |
| E-126 至 E-130 | Shadow Orchestrator、Daily Shadow Run、Review Pipeline、Patch Suggestion Flow 與 Shadow Daily Brief |
| E-131 至 E-135 | Dashboard Shadow Data Binding、Live Context、Timeline、Explain Binding 與 Shadow Mode |

目前工程基線：

- E-120 完成後已有 144 項自動測試通過。
- 全域知識庫驗證通過且錯誤數為零。
- 正式分支為 `main`。
- E-111 至 E-120 未修改 Runtime、Pipeline、Scoring 或 Strategy。
- A-116 至 A-120 已 PASS，Runtime Gate 僅對核准的 Shadow infrastructure 開啟。

### 下一步

E-131 至 E-135 已完成，下一工程任務尚未指派。正式流程為：

1. 小P驗收 E-131 至 E-135。
2. 記錄 PASS 或修正要求。
3. 未經另案授權，不得開始 N-series 或 Production Runtime。

### 架構註記

已完成的是知識庫、驗證、沙盒、報告、展示與治理能力，不包含：

- 正式決策引擎啟用。
- 自動交易。
- 部位大小。
- 資金配置。
- 外部市場 API 整合。
- 正式評分或權重最佳化。
- 經驗倍數或停止條件的正式啟用。

工程不得因已有 `Runtime/Repository/` 目錄，就宣稱正式交易執行已存在；該目錄目前承載的是知識庫層工具。

### 驗證

- 目前工程狀態：[`Project/ENGINEERING_STATUS.md`](Project/ENGINEERING_STATUS.md)。
- 唯一目前任務：[`Project/NEXT_TASK.md`](Project/NEXT_TASK.md)。
- 工程就緒審查：[`ENGINEERING_READINESS_REVIEW.md`](ENGINEERING_READINESS_REVIEW.md)。
- 正式分支與 Commit 必須以 Git 實際結果確認，不依本文件快照推測。

---

## 第十章　未來路線圖

### 目的

說明目前位置、下一階段、測試版、正式第一版與長期方向，同時維持進入門檻。

### 目前狀態

七個產品階段中，研究、知識庫與儀表板第一版已完成，里程碑進度為 43%。Runtime Governance 已 PASS，Shadow Runtime infrastructure、Shadow integration 與 Dashboard Shadow binding 已完成並等待驗收；Production Engine、自動化、測試版與正式第一版尚未啟用。

### 已完成

- 研究：完成並封版。
- 知識庫：第一階段完成。
- 儀表板：第一版完成。
- 治理：專案治理第二版與架構聖經完成。
- Runtime Governance：A-116 至 A-120 PASS，Gate OPEN。
- Runtime Infrastructure：E-121 至 E-125 完成工程實作。
- Shadow Integration：E-126 至 E-130 完成工程實作。
- Dashboard Shadow Binding：E-131 至 E-135 完成工程實作。

### 下一步

#### 近期

- 由小P驗收 E-131 至 E-135。
- N-001 至 N-010 與 Production Runtime 維持 BLOCKED。
- 優先解決正式資料、編碼損壞、路徑重疊與驗證缺口。
- 維持唯讀產品使用，收集真實操作回饋。

#### 引擎階段

進入門檻：

- 明確架構規格。
- 資料契約與權限。
- 多案例驗證。
- 監控、失敗處理與回復方案。
- 小P審核與綠茶核准。

#### 自動化階段

候選範圍：

- 排程產生日常資料投影。
- 協助檢討佇列。
- 核准後的通知。

外部 API、自動寫入與認證資訊必須另案核准。

#### 測試版

定義：

- 使用正式核准資料進行每日唯讀操作。
- 資料更新穩定。
- 問題與使用者回饋可追蹤。
- 只有明確核准部分可以進入影子行為。

#### 正式第一版

完成條件：

- 每日流程可靠。
- 證據、預測、結果、檢討與學習完整可追溯。
- 安全、監控、回復與責任人明確。
- 影子驗證達標。
- 綠茶接受正式上線風險。

#### 長期

- 建立會學習、會修正、會累積市場知識的決策智慧系統。
- 持續改善資料品質、可解釋性與決策成熟度。
- 不追求每次猜中，而追求每次決策都能被驗證與學習。

### 架構註記

- 路線圖不是派工單。
- 階段不可跳過。
- 研究完成不代表策略有效。
- 知識庫完成不代表資料足夠。
- 工程完成不代表正式環境就緒。
- 影子驗證完成仍需獨立正式上線核准。

### 驗證

- 正式路線圖：[`Project/ROADMAP.md`](Project/ROADMAP.md)。
- 當前進度：[`Project/PROJECT_STATUS.md`](Project/PROJECT_STATUS.md)。
- 已知阻礙：[`Project/KNOWN_ISSUES.md`](Project/KNOWN_ISSUES.md)。
- 正式執行門檻：[`RUNTIME_AUTHORITY_MATRIX.md`](RUNTIME_AUTHORITY_MATRIX.md)。
- Runtime Gate：[`Project/RUNTIME_GOVERNANCE.md`](Project/RUNTIME_GOVERNANCE.md)。

---

## 完整引用索引

### 專案治理

- [`Project/PROJECT_CONSTITUTION.md`](Project/PROJECT_CONSTITUTION.md)
- [`Project/PROJECT_STATUS.md`](Project/PROJECT_STATUS.md)
- [`Project/NEXT_TASK.md`](Project/NEXT_TASK.md)
- [`Project/AI_ROLE_SPECIFICATION.md`](Project/AI_ROLE_SPECIFICATION.md)
- [`Project/TEAM_OPERATING_MODEL.md`](Project/TEAM_OPERATING_MODEL.md)
- [`Project/HANDOVER.md`](Project/HANDOVER.md)
- [`Project/PROJECT_HISTORY.md`](Project/PROJECT_HISTORY.md)
- [`Project/DECISION_LOG.md`](Project/DECISION_LOG.md)
- [`Project/ROADMAP.md`](Project/ROADMAP.md)
- [`Project/KNOWN_ISSUES.md`](Project/KNOWN_ISSUES.md)
- [`Project/VISION.md`](Project/VISION.md)
- [`Project/RUNTIME_AUTHORITY_MATRIX.md`](Project/RUNTIME_AUTHORITY_MATRIX.md)
- [`Project/DECISION_RUNTIME_SPECIFICATION.md`](Project/DECISION_RUNTIME_SPECIFICATION.md)
- [`Project/RUNTIME_IO_CONTRACT.md`](Project/RUNTIME_IO_CONTRACT.md)
- [`Project/REPOSITORY_WRITE_AUTHORITY.md`](Project/REPOSITORY_WRITE_AUTHORITY.md)
- [`Project/RUNTIME_GOVERNANCE.md`](Project/RUNTIME_GOVERNANCE.md)

### 架構治理

- [`ARCHITECTURE_CONSTITUTION.md`](ARCHITECTURE_CONSTITUTION.md)
- [`ARCHITECTURE_INDEX.md`](ARCHITECTURE_INDEX.md)
- [`ENTITY_MAP.md`](ENTITY_MAP.md)
- [`RUNTIME_AUTHORITY_MATRIX.md`](RUNTIME_AUTHORITY_MATRIX.md)
- [`REPOSITORY_GOVERNANCE.md`](REPOSITORY_GOVERNANCE.md)
- [`REPOSITORY_STRUCTURE_STANDARD.md`](REPOSITORY_STRUCTURE_STANDARD.md)
- [`ARCHITECTURE_FREEZE_POLICY.md`](ARCHITECTURE_FREEZE_POLICY.md)
- [`ENGINEERING_READINESS_REVIEW.md`](ENGINEERING_READINESS_REVIEW.md)
- [`RESEARCH_PHASE_V1_COMPLETE.md`](RESEARCH_PHASE_V1_COMPLETE.md)

## 文件邊界

本文件只整合既有正式內容：

- 不修改正式執行。
- 不修改資料管線。
- 不修改儀表板。
- 不新增策略。
- 不新增正式交易規則。
- 不授權任何候選進入正式環境。
