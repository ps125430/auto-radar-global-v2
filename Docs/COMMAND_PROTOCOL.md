# User Command Protocol

Document ID: AR-COMMAND-PROTOCOL-2026-06-25
Status: Active
Owner: 綠茶 / CEO
Maintained by: 小C / Repository Engineer

---

## Purpose

This document defines how user commands map to Auto Radar project actions.

Commands must be recorded here when they become stable workflow controls.

---

## 紀錄

Meaning:

Update the entire Project Sync set.

Required actions:

* update `Docs/PROJECT_MEMORY.md`
* update `Docs/PROJECT_STATUS.md`
* update `Docs/HANDOVER_STATE.md`
* update `Docs/ARCHITECTURE_DECISION_LOG.md` when architecture decisions changed
* commit changes to GitHub

---

## 派工

Meaning:

Output tasks using the G / P / C / V convention.

Task families:

* G-xxx Research
* P-xxx Architecture / Review
* C-xxx Development
* V-xxx Validation

---

## 交接

Meaning:

Create a Handover Snapshot.

Required actions:

* update `Docs/HANDOVER_STATE.md`
* summarize current sprint
* summarize current architecture
* summarize current repository and latest commit
* identify immediate next step

---

## 討論

Meaning:

Discuss only.

Rules:

* do not modify GitHub
* do not edit files
* do not create commits
* use discussion to clarify direction, architecture, or research

---

## 封版

Meaning:

Sprint End.

Required actions:

* update project status
* update sprint summary
* update changelog
* confirm completed and pending items
* write final sprint memory into GitHub

---

## 開始新 Sprint

Meaning:

Create new Sprint state.

Required actions:

* update `Docs/PROJECT_STATUS.md`
* update `Docs/PROJECT_MEMORY.md`
* update `Docs/HANDOVER_STATE.md`
* define sprint focus
* identify P0 / P1 / P2 priorities

---

## Protocol Rule

When new commands become stable, this file must be updated.

Chat history is not the official protocol.
