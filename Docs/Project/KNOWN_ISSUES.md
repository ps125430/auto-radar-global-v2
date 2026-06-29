# Known Issues

Status: Active
Last Updated: 2026-06-29

## UI

| ID | Issue | Severity | Status |
|---|---|---|---|
| UI-001 | Dashboard icons depend on an external Lucide CDN; text and layout remain usable if icons fail | Low | Open |
| UI-002 | Top3 has no approved Opportunity Score and therefore displays an unavailable state | Expected limitation | Open |
| UI-003 | Daily strategy, confidence, window, and market regimes are not populated by approved records | Expected limitation | Open |

## Data

| ID | Issue | Severity | Status |
|---|---|---|---|
| DATA-001 | Knowledge Graph contains no validated capital-flow nodes or edges | Medium | Open |
| DATA-002 | Daily Prediction and MarketMind records are drafts with empty decision fields | Medium | Open |
| DATA-003 | Legacy Narrative Library and daily brief files contain encoding or JSON corruption | High | Open |
| DATA-004 | Current Sandbox Evidence records are fictional validation samples, not live market evidence | Medium | Open |

## Architecture

| ID | Issue | Severity | Status |
|---|---|---|---|
| ARCH-001 | Shadow Runtime has no approved architecture package | Blocking | Open |
| ARCH-002 | Production Runtime and Decision Engine activation remain prohibited | Blocking | Open |
| ARCH-003 | Automation provider, credentials, monitoring, failure handling, and rollback are not approved | High | Open |

## Repository

| ID | Issue | Severity | Status |
|---|---|---|---|
| REPO-001 | Legacy project-status documents are stale and must not override the SSOT | Medium | Mitigated by C-035 |
| REPO-002 | Several legacy documents contain mojibake or damaged Chinese text | High | Open |
| REPO-003 | Both `Data/` and `data/` paths exist, creating case-sensitivity risk across platforms | Medium | Open |

## Performance

| ID | Issue | Severity | Status |
|---|---|---|---|
| PERF-001 | No material Dashboard performance issue is currently known | Informational | Monitoring |

## Issue Rules

- Do not hide an issue by replacing it with inferred data.
- Close an issue only with validation evidence.
- Any issue that changes architecture or Runtime requires a separate approved task.
