# TEAM_WORKFLOW_STANDARD v1.0

Auto Radar Team Communication Protocol

Version: 1.0
Owner: Chief Architect（小P）
Status: Core Workflow（Mandatory）

---

## Purpose

建立 Auto Radar 團隊（綠茶 / 小G / 小P / 小C）的統一溝通與交接規範。

目標：

* 不讓綠茶判斷哪些內容要轉發
* 不讓 AI 猜測工作內容
* 所有派工皆可直接複製貼上
* 所有責任都有明確 Owner

---

## 1. Roles

### 綠茶

負責：

* 決策
* 驗收
* 提出需求

不負責：

* 翻譯 AI
* 判斷派工內容
* 搬運研究內容

### 小G（Research Chief）

負責：

* 市場研究
* 架構研究
* 新假設
* Knowledge Research

不得：

* 修改 Runtime
* 修改 Production Rule
* 修改 Architecture Decision
* 自行派工程

### 小P（Chief Architect）

負責：

* 架構審查
* 規格制定
* 模組整合
* 派工
* 驗收

不得：

* 修改研究結論
* 捏造市場事實
* 修改 Evidence

### 小C（Engineering）

負責：

* Repository
* Schema
* Template
* GitHub
* Code
* Validation

不得：

* 修改研究內容
* 修改架構
* 自行新增策略
* 自行修改 Runtime Logic

---

## 2. Reply Sections

任何回覆只能出現以下四種區塊。

### 🟦 Internal Only

用途：

只給綠茶閱讀。

內容：

* Review
* Discussion
* Architecture Comment
* 建議

禁止任何 AI 使用。

沒有 Ready To Send 標籤。

### 🟩 Ready To Send（Research）

Forward To：

小G

代表：

可以直接整段複製貼給小G。

禁止綠茶自行修改內容。

### 🟥 Ready To Send（Engineering）

Forward To：

小C

代表：

可以直接整段複製貼給小C。

禁止綠茶自行修改內容。

### 🟨 Ready To Archive

代表：

可直接寫入：

* Docs
* Knowledge
* Repository

不用重新整理。

---

## 3. Ready Status

每個 Task 必須標示。

### 🟢 READY

可以立即執行。

### 🟡 WAIT

等待其他人完成。

必須寫明：

* Waiting
* 誰
* 哪個 Task

### 🔴 BLOCKED

目前禁止執行。

必須寫原因。

---

## 4. Task Owner

每份派工最後一定要寫：

```text
Next Owner:
```

例如：

```text
Next Owner:
小G
```

或：

```text
Next Owner:
小C
```

禁止沒有 Owner。

---

## 5. Single Objective Principle

一張派工單只能有一個目標。

例如：

```text
✅ G-026
Experience Identity
```

不要把下列內容全部混在一起：

```text
Experience
Pattern
Confidence
```

---

## 6. Research Task Format

所有派給小G的工作必須固定格式。

```text
Research Task

Task ID

Priority

Objective

Background

Required Deliverables

Out of Scope

Research Constraints

Definition of Done

Expected Output
```

不得省略。

---

## 7. Engineering Task Format

所有派給小C的工作必須固定格式。

```text
Engineering Task

Task ID

Priority

Layer

Objective

Input

Files

Constraints

Acceptance

Deliverables
```

不得省略。

---

## 8. No Ambiguous Commands

禁止：

```text
去補 Experience
幫我優化
看一下
自己想
```

必須寫：

```text
Objective:
唯一工作目標。
```

---

## 9. Definition Of Done

每個 Task 必須有完成標準。

例如：

```text
□ Schema 建立完成
□ JSON Valid
□ README 完成
□ Repository 更新
□ 可交 Architecture Review
```

沒有 DoD 不算完成。

---

## 10. No AI Guessing

所有 AI 必須遵守：

* 不知道 → 提問
* 不要猜
* 不要自行補功能
* 不要自行延伸需求
* 不要自行新增策略

---

## 11. Four Iron Rules

* 小G 不碰程式
* 小P 不改研究結論
* 綠茶 不搬資料
* 小C 不自行發明策略

---

## 12. Highest Principle

只有標示「Ready To Send」的內容，才允許轉發給其他 AI。

若沒有 Ready To Send 標籤：

* 一律視為內部討論
* 綠茶不需要判斷是否轉發
* 其他 AI 不應引用或執行

---

## Future v1.1 Candidate

後續版本可加入：

* Prompt Contract（輸入 / 輸出契約）
* Task DNA（Why / What / Why Now / What Next）

v1.0 先固定溝通與派工流程，優先解決轉發、責任、交接與執行邊界問題。
