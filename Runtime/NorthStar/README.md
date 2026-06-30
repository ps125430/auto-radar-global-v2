# North Star Runtime Infrastructure

Status: Shadow infrastructure and integration candidate
Production authorization: False

This package implements E-121 through E-130 as bounded Runtime infrastructure
and Shadow integration.
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
- `shadow.py`: orchestrates Shadow Run, Review, Patch Suggestion Flow, and
  Shadow Daily Brief in memory.
- `shadow_quality.py`: validates authored Shadow inputs and blocks incomplete
  Dashboard output before projection.

## Shadow Data Quality

E-136 至 E-140 新增：

- `Schemas/Runtime/shadow_input.schema.json`：Shadow 輸入契約。
- `ShadowInputValidator`：檢查必要欄位、分數範圍、觀察窗、Why Now 與 Evidence reference。
- `ShadowOutputQualityGate`：在 Dashboard projection 前檢查北極星、航向、Top3、禁航區、風險、Why Now 與 Explain Chain。
- `Data/ShadowInput/sample_real_input_v1.json`：半真實測試輸入，不是正式市場判斷。

Quality Gate 只驗證資料完整性，不計算分數、不建立策略，也不授權 Production。

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
