# ChatGPT Onboarding

Document ID: AR-CHATGPT-ONBOARDING-2026-06-25
Status: Active
Owner: 綠茶 / CEO
Maintained by: 小C / Repository Engineer

---

## Purpose

This document is the required onboarding path for any new ChatGPT session working on Auto Radar.

Do not ask the user to explain the whole project again.

Read the official repository documents first.

---

## Project Mission

Auto Radar Global v2 is an Adaptive Decision Intelligence System.

Its mission is to preserve evidence, validate decisions, learn from outcomes, and improve market decision quality over time.

It is not a one-shot prediction tool.

---

## Official Knowledge Rule

GitHub is the only official knowledge base.

Chat history is not an official record.

Important decisions must be written into GitHub.

---

## Highest Priority File

`Docs/Project/PROJECT_STATUS.md` is the Single Source of Truth.

Read it before working.

If chat, memory, or legacy project files conflict with it, the SSOT wins.

---

## Required Reading Order

Before starting work, read:

1. `Docs/Project/PROJECT_STATUS.md`
2. `Docs/Project/NEXT_TASK.md`
3. `Docs/Project/TEAM_OPERATING_MODEL.md`
4. `Docs/Project/ENGINEERING_STATUS.md` or `Docs/Project/RESEARCH_STATUS.md`
5. `Docs/Project/KNOWN_ISSUES.md`
6. `TEAM_OPERATING_SYSTEM.md`

Then read any task-specific files.

Legacy files under `Docs/` remain historical references and are not project-status authority.

---

## Work Rules

* Do not require the user to re-explain the project.
* Do not treat chat as official memory.
* Do not invent strategies.
* Do not change weights or trading logic without 小P approval.
* Do not change research conclusions.
* Do not create frameworks without approved direction.
* Preserve Research → Architecture → Development → Validation.

---

## Repository Work

When changing the project:

* inspect current repo state
* edit only requested files
* commit with the correct G / P / C / V prefix when applicable
* push to GitHub
* report commit hash and changed files

---

## If Context Is Missing

Read repository files before asking the user.

Ask only when the answer is not available in GitHub or when proceeding would create risk.
