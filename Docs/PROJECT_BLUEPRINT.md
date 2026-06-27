# Auto Radar Global v2 Project Blueprint

Document ID: AR-PROJECT-BLUEPRINT-v1
Owner: 小P / Chief Architect
Status: research_phase_v1_frozen
Layer: Project Architecture
Model Impact: overview_only_not_production

---

## System Overview

Auto Radar is an Adaptive Decision Intelligence System.

Its purpose is not to predict every market move. It preserves evidence, freezes expectations, observes outcomes, reviews errors, and converts validated learning into traceable knowledge candidates.

## Team Model

| Role | Primary Responsibility |
|---|---|
| 綠茶 / CEO | Direction, acceptance, risk, final decision |
| 小G / Research Chief | Market facts, evidence, causality, hypotheses |
| 小P / Chief Architect | Architecture, specifications, integration, review |
| 小C / Repository Engineer | Repository, schemas, templates, implementation, validation |
| Auto Radar | Execute only confirmed rules and record results |

The complete workflow contract is `TEAM_OPERATING_SYSTEM.md`.

## Data Flow

```text
Source
  -> Evidence
  -> Structured Data
  -> Case / Daily Record
  -> Validation
  -> Repository Knowledge
```

Data must remain attributable, time-aware, and distinguish observed fact from interpretation.

## Decision Flow

```text
Market Context
  -> Prediction Snapshot
  -> Buy / Watch / Wait / Avoid candidate language
  -> Human decision by 綠茶
  -> Outcome
```

No research document or single news item may directly produce a Production decision.

## Learning Flow

```text
Prediction
  -> Outcome
  -> Outcome Evaluation
  -> Review
  -> Root Cause
  -> Learning
  -> Improvement Candidate
```

Success and failure both produce learning. Learning quality is distinct from trading profit.

## Knowledge Flow

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

See `Docs/ENTITY_MAP.md` for entity ownership and schemas.

## Repository Map

| Area | Responsibility |
|---|---|
| `Docs/` | Governance and architecture |
| `Data/` | Structured research data |
| `Knowledge/` | Cases and accumulated project knowledge |
| `Schemas/` | Data contracts and validation candidates |
| `Templates/` | Repeatable task and report formats |
| Reserved engineering areas | `Runtime/`, `Dashboard/`, `Scripts/`, `Sandbox/`, `Archive/`, `Tests/` |

See `Docs/REPOSITORY_STRUCTURE_STANDARD.md`.

## Runtime Boundary

Runtime access is deny-by-default.

Research, Cases, and Patterns have no Runtime access. Experience and Playbook permissions remain candidates with no active production authority. Prediction is a snapshot; Outcome and Review are learning inputs.

See `Docs/RUNTIME_AUTHORITY_MATRIX.md`.

## Governance Map

```text
Architecture Constitution
  -> Team Operating System
  -> Repository Governance
  -> Freeze Policy
  -> Change Classification
  -> Registry and Architecture Debt
  -> Entity and Runtime Maps
```

The portal is `Docs/ARCHITECTURE_INDEX.md`.

## Current Phase

Research Phase v1.0:

```text
Complete and frozen
```

Next phase:

```text
Engineering Layer / Shadow Runtime
```

The next phase does not begin Production authorization. It requires separate architecture, implementation, and validation tasks.

## First 30 Minutes

Read in this order:

1. `Docs/PROJECT_MEMORY.md`
2. `Docs/PROJECT_STATUS.md`
3. `Docs/PROJECT_BLUEPRINT.md`
4. `Docs/ARCHITECTURE_INDEX.md`
5. `Docs/HANDOVER_STATE.md`
6. `TEAM_OPERATING_SYSTEM.md`

