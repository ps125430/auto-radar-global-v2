# Evidence to Case Candidate Sandbox

## Purpose

This Sandbox performs the first rule-based mapping from validated Sandbox
Evidence to Case Candidates.

```text
Evidence
  |
  v
Case Candidate
```

It does not infer meaning, score confidence, assign a grade, or promote a
Candidate into the formal Case Library.

## Structure

```text
Sandbox/CaseCandidate/
|-- candidates/                 Generated Case Candidate JSON
|-- processed/                  Reserved for reviewed processing records
|-- failed/                     Reserved for rejected processing records
|-- case_candidate.py           Rule mapper and validator
|-- case_candidate.schema.json  Sandbox-only Candidate schema
`-- candidate_registry.json     Candidate lookup and Evidence traceability
```

## Rule Mapping

The mapper copies these fields without interpretation:

| Evidence | Case Candidate |
| --- | --- |
| `evidence_id` | `evidence_id` |
| numeric Evidence suffix | matching `CC-xxx` suffix |
| `title` | `title` |
| `symbols` | `symbols` |
| `tags` | `tags` |
| `source` | `source` |
| `collected_at` | `generated_at` |

The following values are fixed:

- `status`: `Candidate`
- `confidence`: `null`
- `grade`: `null`
- `review_required`: `true`
- `model_impact`: `repository_only`

## Commands

Generate Candidates from the five Sandbox Evidence records:

```powershell
python Sandbox/CaseCandidate/case_candidate.py generate
```

Validate existing Candidates and the Registry:

```powershell
python Sandbox/CaseCandidate/case_candidate.py validate
```

## Fail-fast Rules

Processing stops on the first:

- duplicate Candidate ID
- missing Evidence identifier
- Evidence reference that cannot be resolved
- missing required Candidate field
- invalid Candidate lifecycle
- Candidate or Registry mismatch

## Boundary

This is a manual Sandbox utility. It does not generate Patterns, Experiences,
Predictions, Decisions, Strategies, scores, or Production Rules. Every output
requires human review before any separate repository workflow may use it.
