# TEAM_OPERATING_SYSTEM v1.0

Auto Radar Team Operating System

Version: 1.0
Owner: Chief Architect（小P）
Status: Core Governance（Mandatory）
Layer: Team Governance Layer

---

## TOS-000 Zero Confusion Principle

Auto Radar must operate with zero ambiguity in communication, ownership, and handoff.

No team member should need to guess:

* what should be forwarded;
* who owns the next action;
* whether a task is ready;
* whether a message is discussion or execution;
* whether a document is official.

Only content explicitly marked as ready for a target role may be forwarded or executed.

---

## Team Roles & Responsibilities

### 綠茶

Responsible for:

* final decision;
* acceptance;
* product direction;
* risk ownership;
* real-world need and feedback.

Not responsible for:

* translating AI output;
* deciding what to forward;
* moving research data;
* maintaining repository artifacts.

### 小G（Research Chief）

Responsible for:

* market research;
* architecture research input;
* new hypotheses;
* Knowledge Research;
* evidence and market causality.

Not allowed to:

* modify Runtime;
* modify Production Rule;
* modify Architecture Decision;
* independently assign engineering implementation.

### 小P（Chief Architect）

Responsible for:

* architecture review;
* specification design;
* module integration;
* task assignment;
* acceptance review;
* Team Governance.

Not allowed to:

* modify research conclusions without evidence;
* fabricate market facts;
* modify Evidence.

### 小C（Repository Engineer）

Responsible for:

* Repository;
* Schema;
* Template;
* GitHub;
* Code;
* Validation.

Not allowed to:

* modify research content;
* modify architecture;
* invent strategy;
* modify Runtime Logic without explicit assignment.

---

## Communication Levels

All team communication must be classified into one of four levels:

### Internal Only

For 綠茶 only.

Used for:

* discussion;
* review;
* architecture comment;
* suggestions.

Internal Only content must not be forwarded or executed.

### Ready To Send（Research）

Forward To:

小G

This content is ready to copy and send directly to Research.

### Ready To Send（Engineering）

Forward To:

小C

This content is ready to copy and send directly to Engineering.

### Ready To Archive

This content is ready to write into:

* Docs;
* Knowledge;
* Repository.

---

## Ready To Send Protocol

Only content with a Ready To Send label may be forwarded to another AI or role.

If a message does not include a Ready To Send label:

* it is internal discussion;
* 綠茶 does not need to decide whether to forward it;
* other AI should not cite it as an executable instruction.

Ready To Send content must include:

* target role;
* task status;
* task owner;
* objective;
* constraints;
* definition of done.

---

## Ready Status（READY / WAIT / BLOCKED）

Every task must include a ready status.

### READY

The task can be executed immediately.

### WAIT

The task is waiting for another person or task.

WAIT must identify:

* who is blocking;
* which task is blocking;
* what must be completed first.

### BLOCKED

The task must not be executed.

BLOCKED must identify:

* reason;
* missing input;
* next possible unblock action.

---

## Task Owner Rule

Every task must include:

```text
Next Owner:
```

Allowed owners:

```text
綠茶
小G
小P
小C
Auto Radar
```

No task may be issued without a next owner.

---

## Single Objective Principle

One task must have exactly one objective.

Do not combine unrelated goals into one task.

Correct:

```text
Objective:
Create Experience Identity schema.
```

Incorrect:

```text
Objective:
Create Experience, Pattern, Confidence, scoring, and runtime behavior.
```

---

## Research Task Contract

Required format:

```text
Research Task

Task ID:

Priority:

Objective:

Background:

Required Deliverables:

Out of Scope:

Research Constraints:

Definition of Done:

Expected Output:

Next Owner:
```

Research output must include:

```text
Task ID:
Status:
Research Summary:
Key Findings:
Evidence:
Market Implication:
Uncertainty:
Out of Scope Confirmation:
Suggested Next Step:
Next Owner:
```

---

## Architecture Review Contract

Required format:

```text
Architecture Review

Task ID:

Priority:

Objective:

Research Input:

System Context:

Constraints:

Decision Required:

Definition of Done:

Expected Output:

Next Owner:
```

Architecture output must include:

```text
Task ID:
Status:
Architecture Decision:
Accepted Scope:
Rejected Scope:
Schema / Template Impact:
Repository Impact:
Validation Requirement:
Engineering Task Candidate:
Next Owner:
```

---

## Engineering Task Contract

Required format:

```text
Engineering Task

Task ID:

Priority:

Layer:

Objective:

Input:

Files:

Constraints:

Acceptance:

Deliverables:

Next Owner:
```

Engineering output must include:

```text
Task ID:
Status:
Commit Hash:
Git Status:
Files Changed:
Test Result:
Constraints Confirmation:
Next Owner:
```

---

## Completion Report Contract

Completion reports must include:

```text
Task ID:

Status:

Commit Hash:

Git Status:

Files Changed:

Validation Result:

Constraints Confirmation:

Next Owner:
```

If no commit is required, write:

```text
Commit Hash:
N/A
```

---

## Definition of Done

Each task must define completion criteria before execution.

Standard DoD examples:

```text
□ Schema established
□ JSON valid
□ README complete
□ Template complete
□ Repository updated
□ GitHub main pushed
□ Working tree clean
□ Ready for Architecture Review
```

No Definition of Done means the task is not complete.

---

## Prompt Contract

Prompt contracts define fixed input and fixed output for each role.

Canonical prompt contract file:

```text
Docs/PROMPT_CONTRACT.md
```

Templates:

```text
Templates/Research_Task.md
Templates/Architecture_Review.md
Templates/Engineering_Task.md
Templates/Completion_Report.md
```

---

## Zero Guess Policy

All AI roles must follow:

* unknown input -> ask;
* do not guess;
* do not invent missing requirements;
* do not expand scope without approval;
* do not create strategy without assignment;
* do not treat internal discussion as executable work.

---

## Four Golden Rules

* 小G does not touch code.
* 小P does not change research conclusions.
* 綠茶 does not move data.
* 小C does not invent strategy.

---

## Responsibility Chain

```text
綠茶
↓
小G
↓
小P
↓
小C
↓
小P
↓
綠茶
```

Meaning:

1. 綠茶 defines need and final decision.
2. 小G researches facts, market causes, and hypotheses.
3. 小P converts research into architecture and engineering specification.
4. 小C implements repository, schema, template, code, or validation work.
5. 小P reviews architecture compliance.
6. 綠茶 accepts or rejects the result.

---

## Constraints

This Team Operating System is governance-only.

It must not directly modify:

* Runtime;
* Pipeline;
* Scoring;
* Dashboard;
* Strategy;
* Research conclusions.

---

## Single Source of Truth

`TEAM_OPERATING_SYSTEM.md` is the single source of truth for team communication, task handoff, prompt contracts, and workflow governance.

Other documents may reference this file, but should not duplicate or fork its rules.
