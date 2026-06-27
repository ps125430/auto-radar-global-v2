# Entity Map v1.0

Document ID: AR-ENTITY-MAP-v1
Owner: 小P / Chief Architect
Status: architecture_frozen
Layer: Knowledge Architecture
Model Impact: research_and_review_only_not_production

---

## Canonical Entity Flow

```text
Evidence
  -> Case
  -> Pattern
  -> Experience
  -> Playbook
  -> Prediction
  -> Outcome
  -> Outcome Evaluation
  -> Review
  -> Learning
  -> Knowledge Update
```

The flow defines traceability, not automatic promotion. Every transition requires its approved validation gate.

## Entity Definitions

| Entity | Purpose | Owner | Runtime Permission | Repository Location | Related Schema |
|---|---|---|---|---|---|
| Evidence | Preserve sourced observations and evidence quality | 小G | No Runtime Access | `Data/Evidence/` | `Data/Evidence/EVIDENCE_SCHEMA.json` |
| Case | Freeze context, prediction, evidence, outcome, and analysis for validation | 小P | No Runtime Access | `Knowledge/CaseLibrary/` | `Schemas/CaseLibrary/case_quality.schema.json`, `Schemas/case_validation.schema.json` |
| Pattern | Represent a recurring candidate relationship derived from Cases | 小P | No Runtime Access | `Knowledge/Experience/Patterns/` | `Schemas/Experience/pattern.schema.json` |
| Experience | Aggregate validated Pattern candidates with confidence and health | 小P | Multiplier / Kill Switch Candidate only | `Knowledge/Experience/` | `Schemas/Experience/experience.schema.json` |
| Playbook | Preserve conditional response knowledge and constraints | 小P | Constraint / Multiplier / Context only | `Knowledge/Playbooks/` | Not established; architecture approval required |
| Prediction | Freeze expected scenario, leader, theme, risk, invalidator, and window | 小P | Decision Snapshot only | `Knowledge/PredictionSnapshots/`, `Knowledge/Daily/` | `Schemas/DailyDecision/prediction_snapshot_v2.schema.json` |
| Outcome | Record observed market results across approved windows | 小C / Review process | Review input only | `Knowledge/Outcome/`, `Knowledge/Daily/` | `Schemas/Outcome/outcome.schema.json` |
| Outcome Evaluation | Compare Prediction and Outcome without changing Production logic | 小P | Review input only | `Knowledge/OutcomeEvaluation/` | `Schemas/OutcomeEvaluation/outcome_evaluation.schema.json` |
| Review | Identify prediction, behavior, execution, and information errors | 小P | Learning input only | `Knowledge/DailyReview/`, `Knowledge/ReviewQueue/` | `Schemas/DailyDecision/review_record.schema.json` |
| Learning | Classify success/failure and create improvement candidates | 小P | Candidate output only | `Data/Learning/`, `Knowledge/Lessons/` | `Data/Learning/LEARNING_SCORE_CANDIDATE.json` |
| Knowledge Update | Apply an approved update to a governed knowledge asset | 小P | No automatic Runtime access | `Knowledge/` | Depends on target entity; separate approval required |

## Promotion Boundary

```text
Research
  -> Candidate
  -> Validation
  -> Shadow
  -> Verified
  -> Core
  -> Production only by separate approval
```

No entity receives Runtime authority through status promotion alone.

## Identity and Cross References

* Entity IDs follow `Docs/REGISTRY.md`.
* Cross references follow `Docs/REPOSITORY_GOVERNANCE.md`.
* Broken or ambiguous references are recorded in `Docs/ARCHITECTURE_DEBT.md`.
* Runtime permissions are governed by `Docs/RUNTIME_AUTHORITY_MATRIX.md`.

