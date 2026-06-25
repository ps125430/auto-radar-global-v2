# Case Validation Protocol v1.0

Document ID: AR-PROTOCOL-2026-06-25-D008
Owner: 小G / Research Chief
Reviewed by: 小P / Chief Architect
Implemented by: 小C / Repository Engineer
Status: Decision Lab Protocol
Model Impact: Validation only, not production scoring

---

## 1. Definition

Case Validation Protocol defines how Auto Radar freezes predictions before major events, tracks outcomes after the event, audits root causes, and stores validation results for future learning.

This protocol belongs to Decision Lab. It is used for validation, not live scoring.

---

## 2. Trigger

A Case Validation should be opened when one of the following event types appears:

* 全球重大總經事件
* 政策落地
* 一線巨頭財報
* 重大地緣政治事件

The goal is to preserve the state of Auto Radar before the event and compare it with what the market actually does afterward.

---

## 3. Validation Flow

### 3.1 Fact & Prediction Freeze

Before the event result is known, freeze the current Auto Radar state.

Required snapshot areas:

* related themes
* Theme Score state
* Stage Score state
* Decision Score state
* Market Cognition state
* Narrative status
* Knowledge Graph signals
* decision before event
* assumptions and notes

This freeze prevents hindsight bias.

### 3.2 Outcome Tracking Window

After the event, track market reaction across three time windows.

Tracking should include:

* price reaction
* volume reaction
* leader reaction
* theme breadth reaction
* graph propagation result
* narrative change
* reality vs expectation gap

### 3.3 Root Cause Audit

After the tracking window, audit whether Auto Radar was correct, partially correct, wrong, or inconclusive.

The audit should identify whether the miss came from expectation, memory, saturation, graph connection, AI resonance, or another cause.

### 3.4 Knowledge Core & Weight Update Candidate

Validated findings may be written into Knowledge Core.

Possible outputs:

* Lesson
* Hypothesis
* Playbook candidate
* Knowledge Graph update candidate
* Weight update candidate

Important rule:

Weight updates are candidates only. They must not directly change production scoring without 小P review and a separate 小C implementation task.

---

## 4. Outcome Windows

### 4.1 T+10 minutes

Focus:

AI Influence / high-frequency reaction

Questions:

* Did the market react faster than a human research workflow could process?
* Did price move before full narrative interpretation spread?
* Did leaders confirm the first reaction?
* Was the move likely driven by AI summarization or high-frequency positioning?

### 4.2 T+24 hours

Focus:

Reality vs Narrative interpretation

Questions:

* Did the market narrative match the real event result?
* Did good news fail to rise or bad news fail to fall?
* Did the initial explanation survive one full trading day?
* Did the event change theme leadership?

### 4.3 T+5 trading days

Focus:

Knowledge Graph propagation

Questions:

* Did the event propagate from one theme to related themes?
* Did rotation targets begin reacting?
* Did lagged beneficiaries appear?
* Did the original narrative strengthen, mutate, or fade?

---

## 5. Root Cause Categories

### 5.1 expectation_blindness

Auto Radar failed to identify what the market had already expected or priced in.

### 5.2 memory_depletion

Auto Radar assumed a previous pattern still worked, but market memory had weakened or the setup no longer carried the same meaning.

### 5.3 saturation_explosion

The theme, narrative, or trade was too crowded; the event became an exit trigger instead of a continuation trigger.

### 5.4 graph_disconnection

Auto Radar failed to connect the event to the right themes, leaders, rotation targets, or lagged beneficiaries.

### 5.5 ai_resonance_overload

AI-driven summarization, algorithmic reaction, or rapid information diffusion caused market reaction to compress or overshoot.

---

## 6. Event Type Checklists

### 6.1 tech_earnings

Checklist:

* Freeze expectations before earnings release.
* Track headline result vs market expectation.
* Track guidance quality.
* Track core leader reaction.
* Track supplier and rotation target reaction.
* Review whether narrative strengthened, mutated, or saturated.

### 6.2 fomc

Checklist:

* Freeze rate expectation before the announcement.
* Track statement, dot plot, press conference, and market interpretation.
* Track rates, dollar, equities, gold, and high-beta assets.
* Review whether market treated policy as preventive easing, inflation risk, or recession risk.

### 6.3 cpi_pce

Checklist:

* Freeze inflation expectation before release.
* Track headline and core data.
* Track rate expectation repricing.
* Track sector rotation.
* Review whether inflation data changed liquidity narrative or only confirmed expectations.

### 6.4 tariff_trade_policy

Checklist:

* Freeze policy expectation before announcement.
* Track affected countries, sectors, and supply chains.
* Track immediate winners and losers.
* Track relocation, substitution, and cost pass-through narratives.
* Review whether the policy produced real order shifts or only short-term attention.

---

## 7. Strict Limits

This protocol must not directly change production scoring.

Strict rules:

* Do not directly change Theme Score.
* Do not directly change Stage Score.
* Do not directly change Decision Score.
* Do not change Dashboard behavior.
* Do not change pipeline behavior.
* Do not modify Constitution rules.
* All weight adjustments can only be marked as candidates.

Any production model change requires:

* evidence from completed validation cases;
* 小P architecture review;
* separate 小C implementation task;
* runtime tests before deployment.

---

## 8. Related Schemas

* `Schemas/prediction_snapshot.schema.json`
* `Schemas/outcome_tracker.schema.json`
* `Schemas/root_cause_audit.schema.json`
* `Schemas/case_validation.schema.json`

These schemas define the Decision Lab validation data structure and do not connect to runtime by themselves.
