# Knowledge Graph Repository

Status: repository_active
Model Impact: repository_only_not_production

## Purpose

The Knowledge Graph Repository stores static, traceable relationships between registered Repository Entities.

It connects Case, Pattern, and Experience records and reserves Node Types for future Playbook, Rule, and Evidence registries.

## Boundary

The Graph records declared relationships only. It does not perform:

* inference;
* reasoning;
* decisions;
* predictions;
* Runtime behavior;
* learning;
* playbook logic;
* confidence logic;
* Pipeline or Scoring behavior;
* Dashboard behavior.

The existing `Data/KnowledgeGraph/` and `Data/knowledge_graph/` assets remain separate research skeletons and are not scanned by this Repository.

## Graph Structure

Each JSON file in `Edges/` represents one directed static edge:

```text
node_id --relation--> target
```

Supported Node Types:

```text
Case
Pattern
Experience
Playbook
Rule
Evidence
```

Supported Relations:

```text
DERIVED_FROM
REFERENCES
GENERATES
USES
DEPENDS_ON
RELATED_TO
```

All edges must validate against `Schemas/Graph/graph.schema.json`.

The generated Registry is `Knowledge/Graph/index.json`.

Playbook, Rule, and Evidence are reserved Node Types. References to them fail validation until their entity registries exist.

## Fail-Fast Rules

Index generation stops when the Repository finds:

* an invalid or missing source Node;
* an invalid Relation;
* a missing target Entity;
* a duplicate `(node_id, relation, target)` edge;
* a self-reference where `node_id` equals `target`;
* invalid JSON or Schema fields.

## Repository Only

This Repository supports static edge scanning, validation, registration, and index generation only.

