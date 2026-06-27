# Repository Structure Standard v1.0

Document ID: AR-REPOSITORY-STRUCTURE-v1
Owner: 小P / Chief Architect
Status: architecture_frozen
Layer: Repository Governance
Model Impact: repository_structure_only_not_production

---

## Canonical Top-Level Structure

Some directories below are reserved architecture locations and may not exist until an approved task creates them.

| Directory | Purpose | Allowed Content | Forbidden Content | Owner |
|---|---|---|---|---|
| `Docs/` | Governance, architecture, frameworks, protocols, status, and roadmap | Markdown documentation and indexes | Runtime code, secrets, market records presented as live data | 小P |
| `Knowledge/` | Traceable cases, predictions, outcomes, reviews, lessons, journals, and experience | Templates and governed knowledge records | Executable production logic, credentials, unreviewed Production Rules | 小P |
| `Schemas/` | Machine-readable structure and validation contracts | JSON Schema and schema documentation | Live decisions, Runtime side effects, embedded strategy execution | 小P / 小C |
| `Runtime/` | Reserved location for explicitly approved execution components | Approved production or shadow execution code | Research drafts, undocumented rules, candidate logic presented as active | 小C under 小P approval |
| `Dashboard/` | Reserved location for approved user interface components | Display and interaction code | Hidden score mutations, strategy invention, governance source files | 小C under 小P approval |
| `Scripts/` | Reserved location for bounded repository and validation utilities | Validators, migration tools, maintenance scripts | Autonomous trading, undocumented destructive operations, embedded credentials | 小C |
| `Sandbox/` | Reserved location for isolated experiments | Non-production prototypes with clear status | Production dependencies, official records without promotion, live authority | 小P / 小C |
| `Archive/` | Reserved location for deprecated or retired artifacts | Immutable historical records and replacement references | Active canonical files, deletion of traceability | 小P |
| `Tests/` | Reserved location for automated verification | Unit, schema, integration, and governance tests | Production secrets, market conclusions, untracked fixtures | 小C |

## Existing Supporting Directories

| Directory | Purpose | Owner |
|---|---|---|
| `Data/` | Structured research libraries and candidate data | 小G / 小P |
| `Templates/` | Reusable task and completion contracts | 小P / 小C |

## Folder Rules

* Use `Docs/`, not `docs/`.
* Do not create a second directory with equivalent meaning.
* New top-level directories require Architecture Review.
* Reserved directories are not created merely to appear complete.
* Every active knowledge area should contain a README or canonical template.
* Archive rather than delete when traceability matters.
* Directory location does not grant Runtime authority.

## Naming Rules

* Governance documents: uppercase descriptive names with `.md`.
* JSON Schemas: lowercase snake case with `.schema.json`.
* Entity records: stable ID plus descriptive name where applicable.
* Task commits: `G-###`, `P-###`, `C-###`, or `V-###`.

## References

* `Docs/REPOSITORY_GOVERNANCE.md`
* `Docs/REGISTRY.md`
* `Docs/CHANGE_CLASSIFICATION.md`
* `Docs/ARCHITECTURE_CONSTITUTION.md`

