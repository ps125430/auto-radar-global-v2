# Experience Engine

status: schema_candidate
model_impact: research_only_not_production

Experience Engine stores reusable market experience candidates derived from validated patterns and cases.

This repository area is for research and validation only. Experience records must not directly change Decision, Theme Score, Stage Score, Decision Score, runtime, pipeline, scoring, Dashboard, or production trading logic.

## Structure

```text
Knowledge/Experience/
├── Patterns/
├── Candidates/
├── Shadow/
├── Verified/
├── Core/
└── Deprecated/
```

## Status Flow

Pattern status:

```text
pattern_candidate
pattern_validation
pattern_verified
pattern_deprecated
```

Experience status:

```text
experience_candidate
shadow_experience
verified_experience
core_experience
deprecated_experience
```

## Boundary Rule

No Experience record is a Production Rule. Promotion requires separate architecture review, validation, and implementation approval.
