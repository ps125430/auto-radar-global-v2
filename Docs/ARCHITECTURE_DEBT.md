# Architecture Debt Registry

Document ID: AR-GOV-ARCH-DEBT-2026-06-27
Version: 1.0
Owner: 小P / Chief Architect
Status: governance_active
Model Impact: repository_governance_only

---

## Governance Source

Architecture debt handling follows `TEAM_OPERATING_SYSTEM.md`.

This registry tracks architecture debt only. It must not directly modify Runtime, Pipeline, Scoring, Dashboard, Strategy, or Production Rules.

---

## Debt Registry Format

Each architecture debt item must include:

| Field | Rule |
|---|---|
| Debt ID | Stable ID using `DEBT-###` |
| Description | Clear statement of the debt |
| Owner | Responsible role |
| Priority | P0 / P1 / P2 / P3 |
| Due | Target date or review milestone |
| Status | open / reviewing / resolved / deferred / archived |
| Related Module | Repository area or framework |
| Resolution Rule | What must happen before closure |

---

## Architecture Debt Registry

| Debt ID | Description | Owner | Priority | Due | Status | Related Module | Resolution Rule |
|---|---|---|---|---|---|---|---|
| DEBT-001 | Cross-reference validator not yet implemented. | 小P / 小C | P1 | Next repository governance review | open | Repository Governance | Define validator scope before implementation. |
| DEBT-002 | Registry counts require periodic manual review until validator exists. | 小P | P2 | Next sprint review | open | Global Entity Registry | Review counts against repository directories. |

---

## Resolution Rule

Architecture debt can only be marked resolved when:

* the affected document or module is updated;
* validation evidence exists;
* owner confirms closure;
* no Runtime, Pipeline, Scoring, Dashboard, Strategy, or Production Rule change was introduced unless separately approved.

---

## Escalation Rule

P0 debt must be reviewed by 小P before any related engineering work continues.

Unclear debt must follow Zero Guess Policy and be clarified before implementation.
