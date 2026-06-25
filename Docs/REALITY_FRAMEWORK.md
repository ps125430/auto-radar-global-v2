# Reality Framework v1.0

Document ID: AR-FRAMEWORK-2026-06-25-D005
Owner: 小G / Research Chief
Reviewed by: 小P / Chief Architect
Implemented by: 小C / Repository Engineer
Status: Framework Draft
Model Impact: Research and validation only, not production scoring yet

---

## 1. Definition

Reality Framework defines how Auto Radar separates market facts from market stories, assumptions, emotions, and model expectations.

Its purpose is to keep every decision grounded in observable reality:

* what actually happened;
* what the market expected;
* what price and volume actually did;
* what evidence supports the interpretation;
* what remains uncertain;
* what was later proven wrong.

This framework is not a trading strategy. It does not directly change Theme Score, Stage Score, Decision Score, position sizing, or production rules.

---

## 2. Core Principle

Auto Radar must distinguish:

* Fact - directly observable or verifiable information;
* Interpretation - the explanation currently assigned to the fact;
* Assumption - an unverified belief used to reason about the market;
* Hypothesis - a testable market idea;
* Decision - the action or recommendation produced after rules are applied;
* Outcome - what the market actually did afterward.

Core rule:

Reality comes before narrative, scoring, and confidence.

---

## 3. Reality Check Layers

### 3.1 Event Reality

Checks what actually happened.

Questions:

* What is the confirmed event?
* When did it happen?
* What source confirms it?
* Was the event final, preliminary, rumored, or revised?

### 3.2 Expectation Reality

Checks what the market expected before the event.

Questions:

* What was consensus expectation?
* Was the market positioned for the result?
* Was the event a surprise or already priced in?

### 3.3 Price Reality

Checks what price action actually showed.

Questions:

* Did leaders confirm the event?
* Did volume support the move?
* Did price react immediately or with delay?
* Was there a reversal after the first reaction?

### 3.4 Evidence Reality

Checks whether the explanation has evidence.

Questions:

* What evidence supports the current interpretation?
* What evidence contradicts it?
* Is the evidence direct or indirect?
* Is the evidence strong enough for decision support?

### 3.5 Model Reality

Checks whether Auto Radar's model matched the market outcome.

Questions:

* Did the score describe the market correctly?
* Did the recommendation match the actual risk?
* Did the model miss a key factor?
* Should the miss become a lesson, hypothesis, or architecture review item?

---

## 4. Reality Review Format

Suggested format:

```md
# Reality Review

Date:
Event:
Theme:
Core Leaders:
Research Owner:

## Event Reality
Confirmed facts:
Source notes:
Unconfirmed items:

## Expectation Reality
Original expectation:
Actual result:
Expectation gap:

## Price Reality
Leader reaction:
Theme reaction:
Volume / breadth notes:

## Evidence Reality
Supporting evidence:
Contradicting evidence:
Evidence quality:

## Model Reality
Auto Radar output:
Actual outcome:
Mismatch:
Root cause candidate:

## Conclusion
Fact:
Interpretation:
Assumption:
Hypothesis:
Next action:
```

---

## 5. Integration With Auto Radar

Allowed use:

* Market Learning reports;
* event reviews;
* hypothesis reviews;
* Decision Log review;
* Root Cause Analysis;
* Lesson creation;
* future validation design.

Prohibited use:

* directly changing Theme Score;
* directly changing Stage Score;
* directly changing Decision Score;
* directly changing position sizing;
* bypassing Constitution rules;
* converting unverified assumptions into production logic.

---

## 6. Validation Requirement

Reality Framework should be validated by comparing reviews against later outcomes.

Required checks:

* source quality review
* expectation accuracy review
* price confirmation review
* false interpretation review
* missed evidence review
* root cause tagging
* impact on decision quality

---

## 7. Next Step

小G should use this framework when reviewing major events and market reactions.

小P should decide whether Reality Review requires a formal schema in Knowledge Core.

小C should not implement code or scoring changes until a separate approved specification exists.
