# Market Flow Framework v1.0

Document ID: AR-FRAMEWORK-2026-06-25-D017
Owner: 小G / Research Chief
Reviewed by: 小P / Chief Architect
Implemented by: 小C / Repository Engineer
Status: Framework Only
Layer: Research Layer
Model Impact: Research only, not production scoring

---

## 1. Definition

Market Flow Framework defines how Auto Radar studies information movement across markets, sectors, themes, leaders, and macro assets.

The framework focuses on how one market reaction may become a signal for another market reaction.

It is designed for research, validation, and Decision Lab review only.

It does not directly change Theme Score, Stage Score, Decision Score, position sizing, Dashboard behavior, pipeline behavior, or production trading logic.

---

## 2. Core Hypothesis

Markets do not react in isolation.

Information may travel through a chain:

```text
Event -> Price Discovery Market -> Validation Market -> Liquidity Trigger -> Confirmation Market -> Theme / Leader Reaction
```

Core hypothesis:

When a market consistently leads, validates, absorbs, or confirms information, Auto Radar can track that relationship as a research signal.

This signal remains a hypothesis until repeated cases validate it.

---

## 3. Market Role

Market Role defines what function each market plays in global information flow.

Each market can have one or more roles depending on event type, liquidity regime, time zone, and market structure.

Supported role candidates:

* Price Discovery
* Validation
* Liquidity Trigger
* Confirmation
* Risk Transmission
* Sentiment Amplifier
* Rotation Signal
* Absorption Zone

### 3.1 Price Discovery

The market that reacts first and reveals the initial direction of interpretation.

Example research question:

* Which market first repriced the event?
* Was that move confirmed later by larger or more liquid markets?

### 3.2 Validation

The market that confirms whether the initial reaction was credible.

Example research question:

* Did the second market validate or reject the first move?
* Was the validation broad or concentrated in one asset?

### 3.3 Liquidity Trigger

The market that triggers broader risk-on or risk-off capital movement.

Example research question:

* Did FX, rates, credit, or futures cause cross-asset repricing?
* Did liquidity movement amplify the original signal?

### 3.4 Confirmation

The market that confirms whether the signal reached themes, leaders, or real trading opportunities.

Example research question:

* Did core leaders confirm the macro or sector signal?
* Did theme breadth expand after confirmation?

---

## 4. Information Flow Direction

Each information flow chain must support direction tagging.

Supported direction values:

```text
Forward
Backward
Bidirectional
```

### 4.1 Forward

Forward flow means information travels from the original event or leading market toward downstream markets.

Example:

```text
US AI earnings -> AI semiconductor leaders -> Taiwan supply chain
```

### 4.2 Backward

Backward flow means downstream market reaction reveals information about the original market or event.

Example:

```text
Supplier reaction -> implied demand signal -> original AI leader interpretation
```

### 4.3 Bidirectional

Bidirectional flow means two markets continuously validate, reject, or reinforce each other.

Example:

```text
US AI leaders <-> Taiwan semiconductor supply chain
```

Direction tags are research metadata only. They must not become production scoring rules without validation.

---

## 5. Absorption Memory

Absorption Memory describes how markets become less sensitive or more sensitive to repeated information.

Status:

```text
Hypothesis
```

Absorption Memory asks whether a market has already digested a repeated event pattern.

Possible states:

* Fresh Sensitivity
* Partial Absorption
* Full Absorption
* Desensitization
* Resensitization

### 5.1 Desensitization

The market reacts less to repeated information because the pattern is already known or priced in.

Research questions:

* Did the same event type produce a weaker reaction than before?
* Did good news fail to create upside?
* Did the market treat the event as already expected?

### 5.2 Resensitization

The market reacts more strongly to repeated information because conditions changed.

Research questions:

* Did a known pattern regain strength because liquidity, positioning, or expectations changed?
* Did a previously ignored catalyst become important again?
* Did leaders confirm renewed sensitivity?

Absorption Memory is a hypothesis layer concept. It must not directly change production scoring.

---

## 6. Information Confidence

Each Information Flow must support confidence metadata.

Required fields:

```text
Confidence
Validation Status
Decay
```

### 6.1 Confidence

Confidence measures how reliable the flow relationship appears based on evidence.

Suggested research values:

```text
low / medium / high
```

### 6.2 Validation Status

Validation Status records whether the flow has been tested.

Suggested research values:

```text
unvalidated / tracking / validated_candidate / rejected / needs_more_cases
```

### 6.3 Decay

Decay records whether the signal weakens over time.

Suggested research values:

```text
none / slow / medium / fast / unknown
```

Decay is important because a leading market signal may be useful only during a short reaction window.

---

## 7. Market Flow Record Format

Suggested research format:

```md
# Market Flow Review

Flow ID:
Review Date:
Event:
Primary Market:
Secondary Market:
Related Theme:
Related Leaders:

## Market Role
Primary Market Role:
Secondary Market Role:

## Information Flow Direction
Direction: Forward / Backward / Bidirectional

## Absorption Memory
State:
Hypothesis Notes:

## Information Confidence
Confidence:
Validation Status:
Decay:

## Evidence
Supporting Evidence:
Contradicting Evidence:

## Conclusion
Research Conclusion:
Candidate Status:
Next Validation Required:
```

---

## 8. Integration With Auto Radar

Allowed use:

* Market Learning reports
* Decision Lab case review
* Prediction Snapshot review
* Knowledge Graph candidate design
* Evidence review
* Root Cause Analysis

Prohibited use:

* Direct Theme Score changes
* Direct Stage Score changes
* Direct Decision Score changes
* Direct position sizing changes
* Dashboard behavior changes
* Pipeline behavior changes
* Production trading rules

All Market Flow findings remain research candidates until validated through multiple cases and reviewed by 小P.

---

## 9. Validation Requirement

Each Market Flow relationship must be validated before production use.

Required checks:

* historical case comparison
* forward tracking
* false positive review
* false negative review
* direction accuracy review
* absorption memory review
* information confidence decay review
* impact on decision quality

No Market Flow signal may become a production rule from one case.

---

Status: Framework Only

Layer: Research Layer

Hypothesis Ready

No Production Rule
