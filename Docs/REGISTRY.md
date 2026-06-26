# Global Entity Registry

Document ID: AR-GOV-REGISTRY-2026-06-27
Version: 1.0
Owner: 小P / Chief Architect
Status: governance_active
Model Impact: repository_governance_only

---

## Governance Source

Repository administrative governance follows `TEAM_OPERATING_SYSTEM.md`.

This registry is a tracking document only. It must not directly modify Runtime, Pipeline, Scoring, Dashboard, Strategy, or Production Rules.

---

## Registry Update Rule

Every official repository entity must have:

* Entity Type
* ID Prefix
* Owner
* Related Directory
* Active Count
* Deprecated Count
* Archived Count

Registry counts must be reviewed when:

* a new entity is created;
* an entity is deprecated;
* an entity is archived;
* a directory structure changes;
* a cross-reference validator reports mismatch.

Updates require the responsible owner and must follow the Zero Guess Policy in `TEAM_OPERATING_SYSTEM.md`.

---

## Entity Registry

| Entity Type | ID Prefix | Active Count | Deprecated Count | Archived Count | Owner | Related Directory |
|---|---:|---:|---:|---:|---|---|
| Evidence | EV- | 0 | 0 | 0 | 小G / 小P | `Data/Evidence/` |
| Case | CASE- | 1 | 0 | 0 | 小P | `Knowledge/CaseLibrary/` |
| Pattern | PAT- | 0 | 0 | 0 | 小P | `Knowledge/Experience/Patterns/` |
| Experience | EXP- | 0 | 0 | 0 | 小P | `Knowledge/Experience/` |
| Playbook | PB- | 0 | 0 | 0 | 小P | `Knowledge/Playbooks/` |
| Journal | DJ- | 1 | 0 | 0 | 小P | `Knowledge/DecisionJournal/` |
| Confidence | CONF- | 0 | 0 | 0 | 小P | `Knowledge/OutcomeEvaluation/` |
| Outcome | OUT- | 0 | 0 | 0 | 小P | `Knowledge/Outcome/` |
| Review | REV- | 0 | 0 | 0 | 小P | `Knowledge/ReviewQueue/` |
| MarketMind | MM- | 1 | 0 | 0 | 小G / 小P | `Knowledge/MarketMind/` |

---

## Count Policy

Counts are repository tracking values, not production metrics.

* Active Count: records currently available for review or use in Decision Lab.
* Deprecated Count: records no longer recommended but retained for traceability.
* Archived Count: records moved out of active workflow.

---

## Cross Reference Rule

Every entity reference must use a stable ID. Free-text references should be upgraded to stable IDs during review.

Broken references must be recorded in `Docs/ARCHITECTURE_DEBT.md` or a future cross-reference report.
