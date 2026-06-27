# Runtime Authority Matrix v1.0

Document ID: AR-RUNTIME-AUTHORITY-v1
Owner: 小P / Chief Architect
Status: architecture_frozen
Layer: Runtime Governance
Model Impact: authority_definition_only_not_production_change

---

## Default Policy

Runtime authority is deny-by-default.

This matrix defines maximum candidate authority. It does not activate any integration, Engine, score, weight, Pipeline, Strategy, or Production Rule.

| Entity | Runtime Permission | Allowed Output | Forbidden Output |
|---|---|---|---|
| Evidence | No Runtime Access | Research and validation input | Buy / Watch / Wait / Avoid, score changes, weights |
| Case | No Runtime Access | Decision Lab validation record | Trading decision, score changes, Production Rule |
| Pattern | No Runtime Access | Pattern candidate for validation | Runtime signal, weight, direct decision |
| Experience | Multiplier / Kill Switch Candidate only | Shadow candidate after separate approval | Active multiplier, active kill switch, direct decision |
| Playbook | Constraint / Multiplier / Context only | Candidate contextual guidance after validation | Direct Buy, autonomous strategy, unapproved weight |
| Prediction | Decision Snapshot only | Frozen pre-outcome expectation and risk | Order execution, score mutation, retrospective rewrite |
| Outcome | Review input only | Observed result record | Prediction rewrite, score change, trading decision |
| Outcome Evaluation | Review input only | Match, drift, timing, risk, and luck assessment | Production scoring, direct promotion |
| Review | Learning input only | Error classification and learning target | Runtime command, scoring change, Production Rule |
| Learning | Candidate output only | Lesson, hypothesis, playbook, or engineering candidate | Automatic Core promotion, direct Runtime change |
| Knowledge Update | No automatic Runtime access | Approved repository update | Silent Runtime activation or permission escalation |

## Mandatory Statements

* Case: No Runtime Access.
* Pattern: No Runtime Access.
* Experience: Multiplier / Kill Switch Candidate only.
* Playbook: Constraint / Multiplier / Context only.
* Prediction: Decision Snapshot only.
* Outcome: Review input only.
* Review: Learning input only.

## Permission Gate

Any future Runtime permission requires:

1. validated multi-case evidence;
2. 小P Architecture Review;
3. 綠茶 acceptance;
4. explicit Production impact;
5. tests, monitoring, and rollback plan;
6. a separately assigned Engineering Task;
7. an update to this matrix and the Architecture Decision Log.

## Prohibited Interpretation

The word `Candidate` never means enabled. Nothing in this document changes the current Runtime.

References:

* `Docs/ARCHITECTURE_CONSTITUTION.md`
* `Docs/ARCHITECTURE_FREEZE_POLICY.md`
* `Docs/ENTITY_MAP.md`

