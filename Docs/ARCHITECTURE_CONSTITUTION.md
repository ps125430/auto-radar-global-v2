# Auto Radar Architecture Constitution v1.0

Document ID: AR-ARCH-CONSTITUTION-v1
Owner: 小P / Chief Architect
Status: architecture_frozen
Layer: Architecture Governance
Model Impact: governance_only_not_production

---

## Purpose

This constitution defines the architecture boundaries of Auto Radar Global v2 after Research Phase v1.0.

It governs structure, authority, entity promotion, and Runtime access. It does not create a Production Rule, trading strategy, Engine, score, weight, or Runtime behavior.

`Docs/CONSTITUTION.md` remains the system's trading and decision constitution. This document governs architecture only.

## Core Principles

1. GitHub is the official repository of project knowledge.
2. Evidence must remain traceable through decision, outcome, review, and learning.
3. Research assets do not become production behavior without validation and explicit approval.
4. Each entity has one defined purpose, owner, repository location, and Runtime boundary.
5. Architecture must preserve the separation of Research, Architecture, Development, Validation, and final decision.
6. Candidate, Shadow, and Verified do not mean Production.
7. Runtime permissions are deny-by-default.

## Architecture Hierarchy

Architecture authority follows this order:

```text
Architecture Constitution
  -> Team Operating System
  -> Repository Governance
  -> Architecture Freeze Policy
  -> Change Classification
  -> Approved Architecture Decisions
  -> Frameworks and Protocols
  -> Schemas and Templates
  -> Knowledge and Data Records
```

Lower layers must not override higher layers.

## Entity Hierarchy

The canonical knowledge and learning flow is:

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

Entity definitions, ownership, locations, and permissions are maintained in `Docs/ENTITY_MAP.md`.

No entity may skip validation merely because a related upstream entity exists.

## Runtime Boundary

Runtime access is denied unless explicitly listed in `Docs/RUNTIME_AUTHORITY_MATRIX.md`.

The following rules apply:

* Research documents and Cases have no Runtime access.
* Patterns have no Runtime access.
* Experience is a Multiplier / Kill Switch Candidate only.
* Playbooks are Constraint / Multiplier / Context candidates only.
* Predictions are Decision Snapshots only.
* Outcomes, Evaluations, and Reviews feed review and learning only.
* Candidate assets must not directly alter Theme Score, Stage Score, Decision Score, weights, or trading logic.

## Authority / Role Boundary

| Role | Authority | Forbidden |
|---|---|---|
| 綠茶 / CEO | Product direction, acceptance, risk, final decision | Producing or maintaining system data |
| 小G / Research Chief | Evidence, market research, causality, hypotheses | Code, Runtime, Production Rules, architecture approval |
| 小P / Chief Architect | Architecture, specifications, integration, review | Fabricating evidence or rewriting research conclusions |
| 小C / Repository Engineer | Repository, Schema, Template, implementation, validation | Inventing strategy, weights, research conclusions, or architecture |
| Auto Radar | Execute explicitly confirmed rules | Inventing strategy or promoting candidates |

Detailed workflow authority is governed by `TEAM_OPERATING_SYSTEM.md`.

## Constitution Amendment Rule

An amendment requires:

1. a dedicated Task ID and single objective;
2. Architecture Review by 小P;
3. acceptance by 綠茶;
4. a documented change classification;
5. an explicit Runtime and Production impact statement;
6. validation and rollback requirements when behavior may change;
7. a traceable Git commit.

No lower-level document may amend this constitution implicitly.

## Global Golden Rules

* Research is not Production.
* Candidate is not Verified.
* Verified is not Core.
* Core is not automatically Runtime-authorized.
* No single news item creates a Buy decision.
* Stage 6 is not tradable.
* Stage 5 popularity must not be represented as low risk.
* No unvalidated hypothesis changes production scoring.
* No AI role may exceed its assigned authority.
* Unknown requirements must follow the Zero Guess Policy.

## Governance References

* `TEAM_OPERATING_SYSTEM.md`
* `Docs/REPOSITORY_GOVERNANCE.md`
* `Docs/ARCHITECTURE_FREEZE_POLICY.md`
* `Docs/CHANGE_CLASSIFICATION.md`
* `Docs/REGISTRY.md`
* `Docs/ARCHITECTURE_DEBT.md`
* `Docs/ARCHITECTURE_INDEX.md`

