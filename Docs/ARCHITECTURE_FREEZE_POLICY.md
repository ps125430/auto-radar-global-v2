# Architecture Freeze Policy v1.0

Document ID: AR-GOV-FREEZE-2026-06-27
Version: 1.0
Owner: 小P / Chief Architect
Status: governance_active
Model Impact: repository_governance_only

---

## Governance Source

Architecture freeze governance follows `TEAM_OPERATING_SYSTEM.md`.

This document is governance-only. It must not directly modify Runtime, Pipeline, Scoring, Dashboard, Strategy, or Production Rules.

---

## Freeze Status

Current Architecture Freeze Status:

```text
candidate_freeze
```

Meaning:

* repository governance may be added;
* schema candidates may be added;
* production logic must not change;
* runtime behavior must not change without explicit approval.

---

## Allowed Changes

Allowed during freeze:

* Docs updates;
* README updates;
* schema candidates;
* templates;
* repository folder structure;
* registry tracking;
* review-only validation artifacts;
* archive and deprecation metadata.

---

## Forbidden Changes

Forbidden during freeze unless separately approved:

* Runtime change;
* Pipeline change;
* Scoring change;
* Dashboard behavior change;
* Strategy change;
* Production Rule change;
* direct Decision Engine modification;
* automatic promotion from candidate to production.

---

## Draft / Candidate / Shadow Policy

| Status | Meaning | Production Impact |
|---|---|---|
| draft | Early working artifact | None |
| schema_candidate | Candidate structure | None |
| research_candidate | Research-only candidate | None |
| shadow | Observed without influencing decisions | None |
| verified | Reviewed but not production | None unless separately approved |

Shadow artifacts may be tracked but must not influence final decisions.

---

## Constitution Change Rule

Constitution changes require:

* explicit task;
* 小P architecture review;
* 綠茶 acceptance;
* clear diff;
* no hidden production behavior change.

---

## Production Change Rule

Production changes require:

* architecture approval;
* validation evidence;
* rollback plan;
* explicit production impact statement;
* separate implementation task.

Repository governance tasks do not authorize production changes.

---

## Emergency Exception Rule

Emergency exceptions are allowed only for:

* broken repository integrity;
* invalid critical schema;
* security or credential risk;
* blocking GitHub synchronization.

Emergency work must be documented after resolution.

---

## Next Review Trigger

Review this freeze policy when:

* a production change is proposed;
* schema candidates need promotion;
* duplicate governance documents appear;
* cross-reference validator is implemented;
* Architecture Debt P0 item is opened.
