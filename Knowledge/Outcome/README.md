# Outcome Repository

status: schema_candidate
model_impact: review_only_not_production

Outcome Repository stores observed market results after a prediction or decision.

It is the evidence bridge between Prediction, Review, Learning, Decision Journal, and Candidate records.

## Purpose

* preserve market outcomes;
* compare expected narrative with actual narrative;
* track leader, theme, and macro results;
* support Review Queue triage;
* support Decision Lab closed-loop validation.

## Boundary Rule

Outcome records are review artifacts only. They must not directly change runtime, pipeline, scoring, Dashboard, Decision, or production trading logic.
