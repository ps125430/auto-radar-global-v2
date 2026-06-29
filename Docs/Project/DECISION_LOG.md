# Product Decision Log

Status: Active
Last Updated: 2026-06-29

| Decision ID | Date | Decision | Reason | Owner | Status |
|---|---|---|---|---|---|
| DEC-001 | 2026-06-27 | Research Phase v1.0 is frozen | Prevent unvalidated expansion and protect the architecture baseline | 小P | Accepted |
| DEC-002 | 2026-06-27 | GitHub is the official project knowledge base | Chat history is incomplete and cannot provide durable traceability | 綠茶 / 小P | Accepted |
| DEC-003 | 2026-06-29 | `Docs/Project/PROJECT_STATUS.md` is the project SSOT | New AI sessions require one current, auditable status source | 綠茶 / 小P | Accepted |
| DEC-004 | 2026-06-29 | Dashboard remains read-only and Repository-backed | Presentation must not alter strategy, scoring, or Runtime | 小P | Accepted |
| DEC-005 | 2026-06-29 | Dashboard uses Traditional Chinese as the primary UI language | The product must serve daily user decisions, not engineering demonstration | 綠茶 | Accepted |
| DEC-006 | 2026-06-29 | Dashboard UX is organized around Daily Tactical, Top3, risk, window, and explainability | The first screen must support a 30-second daily review | 綠茶 / 小P | Accepted |
| DEC-007 | 2026-06-29 | Top3 displays honest unavailable states when Opportunity Score is absent | Similarity or candidate fields must not be mislabeled as approved scores | 小P / 小C | Accepted |
| DEC-008 | 2026-06-29 | Project Constitution v2.0 governs all AI startup, authority, mandatory updates, and conflict resolution | Future collaborators must operate from Repository truth instead of chat memory | 綠茶 / 小P | Accepted |
| DEC-009 | 2026-06-29 | `Docs/ARCHITECTURE_BIBLE.md` is the single complete architecture handover | New collaborators need one traceable overview without replacing the live project SSOT | 綠茶 / 小P | Accepted |
| DEC-010 | 2026-06-29 | Dashboard adopts the North Star four-screen Mission Control hierarchy | Daily use must prioritize direction, opportunities, risk, flow, energy, and learning without inventing missing data | 綠茶 / 小P | Accepted |

## Decision Rule

A decision belongs here when it changes:

- product mission;
- project phase;
- architecture authority;
- governance;
- user workflow;
- Production or Runtime boundary.

Implementation details belong in task specifications or Git history, not this log.
