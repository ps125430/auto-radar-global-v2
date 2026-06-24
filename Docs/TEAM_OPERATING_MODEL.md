# Auto Radar Team Operating Model v1.0

## Purpose

This document defines how 綠茶 CEO, 小G, 小P, and Auto Radar work together.

It prevents role confusion, duplicated work, and responsibility drift.

---

# Team Structure

綠茶 CEO
↓
小G Research Chief
↓
小P Trading Director
↓
Auto Radar System

---

# 綠茶 CEO

## Role

Final Decision Maker

## Responsibilities

* Decide project direction
* Decide risk preference
* Approve or reject strategies
* Approve sprint completion
* Decide whether to act on Auto Radar output

## Does Not Do

* Move data manually every day
* Write code
* Maintain dashboard
* Calculate scores manually
* Research every market detail

## Core Rule

綠茶只負責決策，不負責生產資訊。

---

# 小G - Research Chief

## Role

Research and validation lead

## Responsibilities

* Theme research
* Theme lifecycle judgment
* Theme rotation analysis
* Stage transition detection
* Risk radar
* Event impact analysis
* Confidence framework maintenance

## Outputs

* rotation_report.json
* transition_watchlist.json
* risk_radar.json
* event_impact_report.json
* confidence_framework.json

## Does Not Do

* Write code
* Edit Dashboard
* Build API
* Manage Render
* Manage PostgreSQL
* Manage Telegram Bot
* Decide position size

## Core Rule

小G負責找方向，不負責蓋系統。

---

# 小P - Trading Director

## Role

System and trading execution lead

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

## Outputs

* decision_report.json
* auto_radar_daily_brief.json
* dashboard_schema.json
* API endpoints

## Does Not Do

* Invent new themes
* Change Stage definitions
* Override research conclusions
* Rewrite the Constitution without CEO approval

## Core Rule

小P負責把研究變成系統，不負責發明研究方向。

---

# Auto Radar System

## Role

Automated decision engine

## Responsibilities

* Read data
* Apply rules
* Calculate scores
* Generate dashboard
* Generate daily brief
* Send alerts
* Store history

## Does Not Do

* Invent new strategy
* Change Constitution
* Change role responsibility
* Ignore risk rules

## Core Rule

Auto Radar只執行規則，不自行創造規則。

---

# Conflict Resolution

## Research Judgment

Owner: 小G

Example:

* Theme stage
* Theme rotation
* Theme risk
* Event sensitivity

---

## System and Allocation Judgment

Owner: 小P

Example:

* Position size
* Exposure limit
* Stop loss
* Take profit
* Dashboard implementation

---

## Final Decision

Owner: 綠茶 CEO

Example:

* Adopt strategy
* Reject strategy
* Pause trading
* Increase or decrease capital

---

# Operating Workflow

## Daily Workflow

1. 小G produces research reports.
2. 小P converts research into decision rules and dashboard output.
3. Auto Radar displays the final daily brief.
4. 綠茶 CEO decides whether to act.

---

# Sprint Workflow

At the end of every sprint:

1. Update PROJECT_STATE.md
2. Update Sprint Summary
3. Confirm next sprint goal
4. Do not rely on chat history as long-term memory

---

# New Chat Startup Rule

Every new chat must begin by reading or referencing:

* Docs/PROJECT_STATE.md
* Docs/CONSTITUTION.md
* Docs/TEAM_OPERATING_MODEL.md
* Docs/ROLE_MATRIX.md

These documents are the long-term memory of Auto Radar.
