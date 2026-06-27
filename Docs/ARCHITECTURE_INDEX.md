# Architecture Index

Document ID: AR-ARCH-INDEX-v1
Owner: 小P / Chief Architect
Status: architecture_portal
Layer: Architecture Governance
Model Impact: governance_only_not_production

---

## Architecture Portal

This is the canonical entry point for Auto Radar architecture and repository governance.

| Area | Canonical Document | Purpose |
|---|---|---|
| Architecture Constitution | `Docs/ARCHITECTURE_CONSTITUTION.md` | Highest architecture principles and boundaries |
| Team Operating System | `TEAM_OPERATING_SYSTEM.md` | Roles, task contracts, communication, and handoff |
| Repository Governance | `Docs/REPOSITORY_GOVERNANCE.md` | Repository lifecycle, naming, contribution, and references |
| Freeze Policy | `Docs/ARCHITECTURE_FREEZE_POLICY.md` | Allowed and forbidden changes during freeze |
| Change Classification | `Docs/CHANGE_CLASSIFICATION.md` | MAJOR, MINOR, PATCH, EMERGENCY, and HOTFIX |
| Global Registry | `Docs/REGISTRY.md` | Entity prefixes, counts, owners, and locations |
| Architecture Debt | `Docs/ARCHITECTURE_DEBT.md` | Known architecture debt and resolution tracking |
| Entity Map | `Docs/ENTITY_MAP.md` | Canonical entity flow, ownership, schemas, and permissions |
| Runtime Authority Matrix | `Docs/RUNTIME_AUTHORITY_MATRIX.md` | Deny-by-default Runtime permission whitelist |
| Repository Structure | `Docs/REPOSITORY_STRUCTURE_STANDARD.md` | Canonical directory responsibilities and boundaries |
| Project Blueprint | `Docs/PROJECT_BLUEPRINT.md` | Thirty-minute project and architecture overview |
| Research Phase Closure | `Docs/RESEARCH_PHASE_V1_COMPLETE.md` | Research Phase v1.0 completion and freeze declaration |

## Supporting Governance

* `Docs/ARCHITECTURE_DECISION_LOG.md`
* `Docs/PROJECT_MEMORY.md`
* `Docs/PROJECT_STATUS.md`
* `Docs/HANDOVER_STATE.md`
* `Docs/PROMPT_CONTRACT.md`
* `Docs/CONSTITUTION.md`

## Reading Order

1. `Docs/PROJECT_BLUEPRINT.md`
2. `Docs/ARCHITECTURE_CONSTITUTION.md`
3. `TEAM_OPERATING_SYSTEM.md`
4. `Docs/ENTITY_MAP.md`
5. `Docs/RUNTIME_AUTHORITY_MATRIX.md`
6. `Docs/REPOSITORY_STRUCTURE_STANDARD.md`
7. `Docs/ARCHITECTURE_FREEZE_POLICY.md`

## Boundary

This index documents architecture only. It does not authorize Runtime, Pipeline, Scoring, Dashboard, Strategy, or Production Rule changes.

