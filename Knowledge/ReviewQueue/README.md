# Review Queue

status: schema_candidate
model_impact: review_only_not_production

Review Queue stores outcomes waiting for review and completed review references.

It connects Outcome records to the Daily Review Pipeline:

```text
Prediction -> Outcome -> Review -> Learning -> Decision Journal -> Candidate
```

## Folders

```text
pending_review/
completed_review/
```

## Boundary Rule

Review Queue is a workflow repository only. It must not directly change runtime, pipeline, scoring, Dashboard, Decision, or production trading logic.
