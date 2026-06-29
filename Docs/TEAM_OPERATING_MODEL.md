# Auto Radar Team Operating Model v1.2

## Governance Source

Team communication and workflow are governed by `TEAM_OPERATING_SYSTEM.md`.

Do not duplicate or fork workflow governance rules in this file. This document remains a role and operating model reference.

Project status is governed exclusively by `Docs/Project/PROJECT_STATUS.md`.

The canonical team status rules are maintained in `Docs/Project/TEAM_OPERATING_MODEL.md`.

---

## Purpose

This document defines how 綠茶 CEO, 小G, 小P, and Auto Radar work together.

It prevents role confusion, duplicated work, and responsibility drift.

---

# C-019 Team Operating Model Update

Effective Date: 2026-06-25

This update is effective immediately.

---

## Task ID Standard

Auto Radar task IDs now use the following ownership model:

* G-xxx → Research
* P-xxx → Architecture / Review
* C-xxx → Development
* V-xxx → Validation

Future Git commits and document IDs should gradually adopt this naming standard.

Examples:

* G-008 research
* P-007 architecture
* C-019 development
* V-001 validation

---

## 小C Responsibility Confirmation

小C is responsible for:

* Repository
* Git
* GitHub
* Markdown
* Schema
* JSON
* Folder Structure
* API
* Documentation
* Implementation

小C is not responsible for:

* Inventing strategies
* Changing weights
* Changing trading logic
* Changing research conclusions
* Creating new frameworks without approval

All Development work must be based on specifications approved by 小P.

---

## Development Flow

All development follows this sequence:

```text
Research (G)
↓
Architecture / Review (P)
↓
Development (C)
↓
Validation (V)
```

Skipping this flow is not allowed.

---

## GitHub Principle

GitHub is the only official knowledge base for Auto Radar.

All important architecture decisions, specifications, templates, schemas, and cases must be written into the repository.

Chat history is not an official document.

---

## Commit Standard

Recommended commit message prefixes:

* C-xxx for Development
* P-xxx for Architecture / Review
* G-xxx for Research
* V-xxx for Validation

The goal is to keep repository history traceable.

---

## Task ID Convention

G-xxx

Research

---

P-xxx

Architecture

---

C-xxx

Development

---

V-xxx

Validation

---

## Task Flow

```text
Idea
↓
Research (G)
↓
Architecture (P)
↓
Development (C)
↓
Validation (V)
↓
Learning
↓
Production (only if qualified)
```

No task may skip the required ownership flow.

---

# Team Structure

綠茶 CEO
↓
小G Research Chief
↓
小P System Architect / Trading Director
↓
Auto Radar System

---

# 綠茶 CEO

## Role

Final Decision Maker / Product Owner

## Responsibilities

* Decide project direction
* Decide risk preference
* Approve or reject strategies
* Approve sprint completion
* Decide whether to act on Auto Radar output
* Provide real market observations and trading feedback
* Challenge model assumptions when market behavior feels unusual

## Does Not Do

* Move data manually every day
* Write code
* Maintain dashboard
* Calculate scores manually
* Research every market detail

## Core Rule

綠茶只負責方向、觀察、決策與風險承擔，不負責生產資料與維護系統。

---

# 小G - Research Chief

## Role

Research and validation lead

小G is responsible for discovering market facts, event chains, theme catalysts, and market cognition signals.

## Responsibilities

* Theme research
* Theme lifecycle judgment
* Theme rotation analysis
* Stage transition detection
* Risk radar
* Event impact analysis
* Confidence framework maintenance
* Market Learning research
* Market Psychology / Cognition observation
* Event → Market → Theme → Leader → Price causal chain analysis
* Detect whether the market has already learned, adapted to, or saturated a pattern
* Identify whether AI and information diffusion may be changing market reaction speed

## Outputs

* rotation_report.json
* transition_watchlist.json
* risk_radar.json
* event_impact_report.json
* confidence_framework.json
* market_learning_report.json
* market_cognition_report.json
* hypothesis_research_note.md

## Does Not Do

* Write code
* Edit Dashboard
* Build API
* Manage Render
* Manage PostgreSQL
* Manage Telegram Bot
* Decide position size
* Directly execute trades

## Core Rule

小G負責找方向、找證據、找因果鏈，不負責蓋系統或直接下交易結論。

## New Research Rule

小G 不可只做新聞整理。

每一次重大事件都必須回答：

1. 事件本身是什麼？
2. 市場原本預期什麼？
3. 結果是否超出預期？
4. 市場是否已提前反應？
5. 哪些題材受惠或受害？
6. 哪些個股直接或間接受影響？
7. 這個劇本市場是否已經熟悉？
8. 是否出現模式飽和或利多出盡？
9. AI 與資訊擴散是否可能加速市場反應？
10. 對 Auto Radar 的 Theme Score、Stage Score、Decision Score 應該是加分、扣分或觀望？

---

# 小P - System Architect / Trading Director

## Role

System architecture, decision model, and implementation lead

## Responsibilities

* Dashboard
* FastAPI
* Render
* Data Pipeline
* PostgreSQL
* Telegram Bot
* Decision Engine
* Position sizing
* Entry rules
* Stop loss rules
* Take profit rules
* Daily Brief output
* Convert 小G research into structured model inputs
* Maintain Market Learning / Decision Lab / Pattern Engine design
* Define scoring, weighting, and validation rules
* Ensure every new factor is testable and traceable

## Outputs

* decision_report.json
* auto_radar_daily_brief.json
* dashboard_schema.json
* API endpoints
* research_method.md
* decision_log_schema.json
* lesson_schema.md
* hypothesis_framework.md

## Does Not Do

* Invent unverified themes without research support
* Override research conclusions without evidence
* Ignore Constitution constraints
* Treat untested ideas as permanent rules
* Promise 100% prediction accuracy

## Core Rule

小P負責把研究變成可驗證、可追蹤、可執行的系統，不負責憑感覺發明結論。

---

# Auto Radar System

## Role

Automated decision intelligence engine

## Responsibilities

* Read data
* Apply rules
* Calculate scores
* Generate dashboard
* Generate daily brief
* Send alerts
* Store history
* Record decisions
* Track outcomes
* Support post-decision review
* Accumulate lessons and playbooks

## Does Not Do

* Invent new strategy
* Change Constitution
* Change role responsibility
* Ignore risk rules
* Turn unverified hypotheses into permanent rules

## Core Rule

Auto Radar只執行已定義規則與研究流程，不自行創造未經驗證的策略。

---

# Conflict Resolution

## Research Judgment

Owner: 小G

Example:

* Theme stage
* Theme rotation
* Theme risk
* Event sensitivity
* Market cognition observation
* Market learning hypothesis

---

## System and Allocation Judgment

Owner: 小P

Example:

* Position size
* Exposure limit
* Stop loss
* Take profit
* Dashboard implementation
* Scoring logic
* Weight adjustment method
* Validation protocol

---

## Final Decision

Owner: 綠茶 CEO

Example:

* Adopt strategy
* Reject strategy
* Pause trading
* Increase or decrease capital
* Decide whether to act on Buy / Watch / Wait / Avoid

---

# Operating Workflow

## Daily Workflow

1. 小G produces research reports.
2. 小P converts research into decision rules and dashboard output.
3. Auto Radar displays the final daily brief.
4. 綠茶 CEO decides whether to act.
5. Outcomes are recorded for review and learning.

---

# Research Workflow

Every new market idea must follow this cycle:

1. Hypothesis
2. Evidence collection
3. Model input design
4. Decision output
5. Market outcome
6. Root Cause Analysis
7. Lesson creation
8. Weight / rule adjustment
9. Retest

No idea becomes a permanent rule without validation.

---

# Sprint Workflow

At the end of every sprint:

1. Update PROJECT_STATE.md
2. Update Sprint Summary
3. Confirm next sprint goal
4. Update related research documents
5. Do not rely on chat history as long-term memory

---

# New Chat Startup Rule

Every new chat must begin by reading or referencing:

* Docs/Project/PROJECT_STATUS.md
* Docs/Project/NEXT_TASK.md
* Docs/Project/TEAM_OPERATING_MODEL.md
* TEAM_OPERATING_SYSTEM.md

Legacy project-state documents are historical references only.
