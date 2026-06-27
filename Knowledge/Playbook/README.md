# Playbook Repository

Status: repository_active
Model Impact: repository_only_not_production

## Purpose

The Playbook Repository stores static, governed knowledge templates linked to validated Repository relationships.

A Playbook is not executable behavior, a trading strategy, or a Production Rule.

## Lifecycle

```text
Draft
  -> Candidate
  -> Shadow
  -> Verified
  -> Deprecated
  -> Archived
```

Promotion requires a separate approved review. Folder location does not grant Runtime authority.

## Folder Structure

| Folder | Purpose |
|---|---|
| `Draft/` | Incomplete Playbook templates |
| `Candidate/` | Templates ready for repository validation |
| `Shadow/` | Templates retained for non-executing observation |
| `Verified/` | Templates that passed the approved repository review |
| `Deprecated/` | Templates retained but no longer recommended |
| `Archived/` | Inactive historical templates retained for traceability |
| `index.json` | Generated Playbook Registry |

Playbook records use JSON and must validate against `Schemas/Playbook/playbook.schema.json`.

The pre-E-005 `Knowledge/Playbooks/` directory is retained as a legacy research area. The E-005 Repository does not scan it.

## Repository Boundary

Playbooks in this Repository cannot create or modify:

* decisions;
* predictions;
* confidence logic;
* learning logic;
* Runtime or Pipeline behavior;
* Scoring;
* Dashboard behavior;
* strategies;
* Production Rules.

Shadow is a Repository lifecycle state only. It does not activate shadow execution.

## Graph Dependency

Each Playbook contains one static `graph_reference`:

```json
{
  "node_id": "EXP-001",
  "relation": "DERIVED_FROM",
  "target": "PAT-001"
}
```

The tuple must exactly match an Edge in `Knowledge/Graph/index.json`.

Playbooks do not maintain direct Case, Pattern, or Experience dependency lists. Their declared dependency is resolved through the Graph Registry.

Missing Graph references stop Registry generation immediately.

## Repository Only

The Playbook Repository supports scanning, validation, registration, and index generation only.

