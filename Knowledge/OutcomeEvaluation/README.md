# Outcome Evaluation Repository

status: schema_candidate
model_impact: research_only_not_production

Outcome Evaluation stores the research-only evaluation layer between Outcome records and Review / Learning records.

It measures whether a prediction matched the market result across narrative, leader, theme, flow, timing, and risk dimensions.

## Purpose

* evaluate prediction quality after outcomes are recorded;
* calculate review-only PMS fields;
* identify narrative drift and leader drift;
* support Decision Lab review and learning;
* preserve evidence for future case quality review.

## Evaluation Status

```text
TRUE_ALPHA
PARTIAL_SUCCESS
TIMING_MISMATCH
NARRATIVE_DRIFT
LEADER_DRIFT
COMPLETE_MISS
BLACK_SWAN
```

## Boundary Rule

Outcome Evaluation is research-only. It must not directly change runtime, pipeline, scoring, Dashboard, Decision, or production trading logic.
