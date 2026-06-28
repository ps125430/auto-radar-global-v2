# Sandbox Review Pipeline

## Purpose

This Sandbox records human review of Case Candidates and materializes approved
records as Sandbox Verified Cases.

```text
Evidence
  |
  v
Case Candidate
  |
  v
Human Review
  |
  v
Sandbox Verified Case
```

No review decision is inferred or automated. A reviewer must create the Review
record before the verifier can produce a Verified Case.

## Structure

```text
Sandbox/Review/
|-- pending/                       Pending human Review records
|-- approved/                      Approved human Review records
|-- rejected/                      Rejected human Review records
|-- verified/                      Generated Sandbox Verified Cases
|-- review_pipeline.py             Validator and materializer
|-- review.schema.json             Sandbox Review schema
`-- verified_case_registry.json    Review and Verified Case traceability
```

## Lifecycle

- `Pending`: awaiting human review
- `Approved`: human approval recorded
- `Rejected`: human rejection recorded
- `Verified`: approved Candidate materialized as a Sandbox Verified Case

Only `Approved` Reviews with `decision: Approve` can produce a Verified Case.
Pending and Rejected Reviews never produce one.

## Commands

Materialize approved Reviews:

```powershell
python Sandbox/Review/review_pipeline.py verify
```

Validate Reviews, Verified Cases, references, and the Registry:

```powershell
python Sandbox/Review/review_pipeline.py validate
```

## Fail-fast Rules

Processing stops on the first:

- missing Candidate identifier
- Candidate reference not found
- duplicate Review ID
- more than one Review for a Candidate
- invalid lifecycle or decision pairing
- missing required Review field
- Verified Case or Registry mismatch

## Boundary

All outputs remain in this Sandbox. The pipeline does not write to the formal
Case Library and cannot create Patterns, Experiences, Playbooks, Predictions,
Decisions, Strategies, scores, trades, or Production Rules.
