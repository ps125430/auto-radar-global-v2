# Knowledge Graph Schema v1.0

Document ID: AR-KG-SCHEMA-2026-06-25
Owner: 小G / Research Chief
Reviewed by: 小P / Chief Architect
Implemented by: 小C / Repository Engineer
Status: schema_ready
Model Impact: schema_only_not_production_scoring

---

## Purpose

This folder defines the skeleton for Auto Radar Knowledge Graph data.

Current scope:

* Define Node schema.
* Define Edge schema.
* Create empty data files.
* Preserve graph metadata.

This task does not add real graph data and does not connect the graph to runtime, Dashboard, pipeline, Theme Score, Stage Score, or Decision Score.

---

## Files

* `GRAPH_SCHEMA.md` - human-readable schema definition
* `NODES.json` - empty node database with node schema template
* `EDGES.json` - empty edge database with edge schema template
* `GRAPH_METADATA.json` - graph-level metadata and governance rules

---

## Node Schema

```json
{
  "id": "",
  "name": "",
  "category": "",
  "status": "",
  "strength": 0,
  "confidence": 0,
  "saturation": 0,
  "last_updated": ""
}
```

### Node Field Rules

* `id`: unique node identifier
* `name`: node display name
* `category`: node category, such as narrative, theme, event, leader, risk, playbook, or hypothesis
* `status`: lifecycle or research status
* `strength`: numeric value from 0 to 100
* `confidence`: numeric value from 0 to 100
* `saturation`: numeric value from 0 to 100
* `last_updated`: ISO date string, formatted as YYYY-MM-DD

---

## Edge Schema

```json
{
  "source": "",
  "target": "",
  "weight": 0.0,
  "lag_days": 0,
  "confidence": 0,
  "edge_type": "",
  "last_validated": ""
}
```

### Edge Field Rules

* `source`: source node id
* `target`: target node id
* `weight`: numeric relationship strength
* `lag_days`: expected or observed delay between source and target effect
* `confidence`: numeric value from 0 to 100
* `edge_type`: relationship type, such as drives, confirms, rotates_to, weakens, or risk_to
* `last_validated`: ISO date string, formatted as YYYY-MM-DD

---

## Governance

* This schema is a skeleton only.
* Empty `nodes` and `edges` arrays mean no real graph data has been approved yet.
* Production scoring must not read these files until a separate integration task is approved.
* 小P must review graph logic before 小C implements runtime usage.
