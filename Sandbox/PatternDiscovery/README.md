# Pattern Discovery Sandbox

## Purpose

This Sandbox groups Verified Cases into review-required Pattern Candidates
using explicit tag rules.

```text
Evidence
  |
  v
Verified Case
  |
  v
Pattern Candidate
```

No AI, semantic inference, embedding, clustering model, or trading logic is
used.

## Structure

```text
Sandbox/PatternDiscovery/
|-- candidates/                         Generated Pattern Candidate JSON
|-- processed/                          Reserved processing records
|-- failed/                             Reserved failed records
|-- pattern_discovery.py                Rule mapper and validator
|-- pattern_candidate.schema.json       Sandbox-only schema
`-- pattern_candidate_registry.json     Candidate and Case references
```

## Discovery Rules

| Pattern Candidate | Required Case tag | Pattern tag |
| --- | --- | --- |
| `PC-001` | `filing` or `exchange` | `corporate_disclosure` |
| `PC-002` | `macro` or `calendar` | `macro_calendar` |
| `PC-003` | `manual` | `manual_news` |

The shared `sample` tag is ignored. A Verified Case must match exactly one
rule. The `similarity_score` is `1.0` only because every included Case
satisfies its declared rule; it is not a confidence score or model output.

## Commands

Generate Pattern Candidates:

```powershell
python Sandbox/PatternDiscovery/pattern_discovery.py discover
```

Validate Candidates, Registry, and traceability:

```powershell
python Sandbox/PatternDiscovery/pattern_discovery.py validate
```

## Traceability

Validation resolves every chain:

```text
Pattern Candidate
  -> Verified Case
  -> Evidence
```

## Fail-fast Rules

Processing stops on the first:

- duplicate Pattern Candidate ID
- missing source Case
- Case or Evidence reference that cannot be resolved
- invalid Candidate status
- similarity outside `0.0` to `1.0`
- missing required field
- rule or Registry mismatch

## Boundary

All records remain in this Sandbox and require human review. The discovery
process cannot produce Experiences, Playbooks, Predictions, Decisions,
trading behavior, scores, Strategies, or Production Rules.
