# Evidence Repository

Status: repository_active
Model Impact: evidence_only_not_production

## Purpose

The Evidence Repository is the required entry point for sourced information entering Auto Radar.

News, regulatory disclosures, exchange announcements, economic-calendar events, company filings, and macro events must become Evidence before they may support a Case.

No Evidence record creates a Case automatically.

## Lifecycle

```text
Incoming -> Verified -> Rejected
                    -> Archived
```

Lifecycle transitions require an external review. Folder placement alone does not verify Evidence.

## Folder Structure

| Path | Status | Purpose |
|---|---|---|
| `incoming/` | Incoming | Newly collected records awaiting verification |
| `verified/` | Verified | Records accepted for repository use |
| `rejected/` | Rejected | Records rejected during verification |
| `archive/` | Archived | Historical records retained for traceability |
| `TEMPLATE.md` | N/A | Required Markdown and YAML structure |
| `Runtime/Repository/index/evidence_registry.json` | N/A | Generated Evidence Registry |

Records validate against `Schemas/Evidence/evidence.schema.json`.

The pre-E-011 `Data/Evidence/` files remain research references for tiers and penalties. They are not scanned as Evidence entities.

## Source Rule

Each Evidence record must preserve:

* an identifiable original source;
* publication and collection timestamps;
* a human-authored summary;
* lifecycle status;
* importance and reliability values for review.

## Boundary

This Repository does not connect to external feeds, crawl websites, summarize with AI, generate Cases, create decisions, or execute trading behavior.

Importance and reliability are repository review fields only. They do not alter Production scoring.

## Repository Only

This Repository supports parsing, validation, lifecycle checks, registration, and index generation only.

