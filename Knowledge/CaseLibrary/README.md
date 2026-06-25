# Case Library

Document ID: AR-CASE-LIBRARY-README
Status: active_index
Model Impact: research_and_validation_only_not_production_scoring

---

## Purpose

Case Library is the permanent storage area for Auto Radar validation cases.

A Case records a real market event, the system state before the event, the market outcome after the event, and the lessons learned from validation.

The Case Library exists so Auto Radar can:

* preserve decision evidence;
* compare predictions with outcomes;
* support Root Cause Analysis;
* build reusable lessons;
* identify playbook candidates;
* prevent repeated mistakes;
* avoid relying on chat history as long-term memory.

---

## Naming Rules

Each case must use the following ID format:

```text
CASE-001
CASE-002
CASE-003
```

Recommended folder or file naming pattern:

```text
CASE-001_<short_event_name>
```

Example:

```text
CASE-001_Micron_Earnings
```

Rules:

* Case IDs must be unique.
* Case IDs must not be reused after deletion or archival.
* Reserved cases should remain marked as reserved until opened.
* Case names should be short, event-based, and readable.

---

## Validation Flow

Every case should follow the Decision Lab validation flow:

1. Fact & Prediction Freeze
2. Outcome Tracking Window
3. Root Cause Audit
4. Lesson or Hypothesis Extraction
5. Knowledge Core Update Candidate
6. Weight Update Candidate only when justified

Required references:

* `Docs/CASE_VALIDATION_PROTOCOL.md`
* `Schemas/case_validation.schema.json`
* `Schemas/prediction_snapshot.schema.json`
* `Schemas/outcome_tracker.schema.json`
* `Schemas/root_cause_audit.schema.json`
* `Knowledge/DecisionLab/CASE_TEMPLATE.md`
* `Knowledge/DecisionLab/ROOT_CAUSE_TEMPLATE.md`
* `Knowledge/DecisionLab/VALIDATION_CHECKLIST.md`

---

## Relationship With Decision Lab

Case Library stores the cases.

Decision Lab defines how cases are reviewed.

Relationship:

* Case Library = long-term case storage and index
* Decision Lab = validation method, templates, and review workflow
* Knowledge Core = lessons, hypotheses, playbooks, and decision memory extracted from cases

A case may produce:

* Lesson
* Hypothesis
* Playbook Candidate
* Knowledge Graph update candidate
* Weight update candidate

Important rule:

Case Library does not directly change Theme Score, Stage Score, Decision Score, Dashboard behavior, or production trading logic.

Any model change requires 小P review and a separate 小C implementation task.
