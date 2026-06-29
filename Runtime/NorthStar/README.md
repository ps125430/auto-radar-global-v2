# North Star Runtime Infrastructure

Status: Shadow infrastructure candidate
Production authorization: False

This package implements E-121 through E-125 as bounded Runtime infrastructure.
It does not contain strategy, scoring, trading commands, confidence calculation,
or production decision logic.

## Modules

- `framework.py`: disabled-by-default Runtime composition root.
- `loader.py`: read-only JSON loader for approved Repository roots.
- `context.py`: immutable Runtime input context.
- `session.py`: in-memory session lifecycle and rollback state.
- `dispatcher.py`: fail-fast engine dispatch through registered handlers.
- `decision.py`: validates and packages approved inputs into the Decision Schema.
- `explain.py`: builds a traceable Decision-to-Repository reference chain.
- `learning.py`: converts Review input into Lesson and Patch suggestions only.
- `patch_queue.py`: in-memory review queue requiring Repository Manager approval.

## Boundaries

- Runtime mode is limited to `shadow_candidate`.
- The framework is disabled unless explicitly enabled by its caller.
- Repository inputs are loaded as immutable snapshots.
- Engines cannot write to Knowledge, Data, or Repository indexes.
- Learning output is a suggestion, never a direct Repository update.
- Patch approval produces merge authorization metadata only; this package has no
  merge or filesystem-write operation.
- Production Runtime, trading, strategy, scoring, and capital allocation remain
  blocked.

## Governance

The package is governed by:

- `Docs/Project/RUNTIME_AUTHORITY_MATRIX.md`
- `Docs/Project/DECISION_RUNTIME_SPECIFICATION.md`
- `Docs/Project/RUNTIME_IO_CONTRACT.md`
- `Docs/Project/REPOSITORY_WRITE_AUTHORITY.md`
- `Docs/Project/RUNTIME_GOVERNANCE.md`

