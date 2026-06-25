# Decision Lab

## Purpose

Decision Lab is the learning core of Auto Radar.

Its purpose is to record every decision, track its outcome, analyze success or failure, and convert the result into reusable market knowledge.

Auto Radar does not only make decisions.

It learns from decisions.

---

## Decision Types

Auto Radar decisions must be explicit:

* Buy
* Watch
* Wait
* Avoid

Each decision must include evidence and invalidation conditions.

---

## Decision Log Schema

Each decision should eventually be stored as structured data.

Required fields:

```json
{
  "decision_id": "2026-06-26-MEMORY-001",
  "date": "2026-06-26",
  "theme": "Memory / HBM / NAND",
  "decision": "Buy",
  "decision_score": 86,
  "confidence": 82,
  "risk_level": "medium",
  "suggested_exposure": "10-20%",
  "time_horizon": "1-5 trading days",
  "evidence": {
    "event": 95,
    "expectation": 70,
    "market": 88,
    "capital": 60,
    "theme": 90,
    "leader": 84,
    "technical": 80,
    "history": 72,
    "market_cognition": 55
  },
  "invalid_conditions": [
    "SOX reverses sharply",
    "leader stocks open high and close low",
    "foreign capital sells aggressively"
  ],
  "notes": "Decision based on event plus market confirmation. Capital confirmation still incomplete."
}
```

---

## Outcome Tracking

Every decision should be reviewed at:

* 1 day
* 3 days
* 5 days
* 10 days
* 20 days

Outcome fields:

* return_pct
* max_drawdown
* max_favorable_move
* thesis_validated
* timing_validated
* stop_loss_triggered
* take_profit_triggered

---

## Review Questions

Every weak or failed decision must answer:

1. What happened?
2. What did we miss?
3. What did we overestimate?
4. What did we underestimate?
5. Which evidence layer failed?
6. Was the event already priced in?
7. Did market cognition change?
8. Did capital disagree?
9. Did leader stocks fail to confirm?
10. Did AI / information diffusion accelerate the reaction?
11. Did Pattern Saturation cause a reversal?
12. What lesson should be added?

---

## Root Cause Categories

Root causes should be tagged:

* EVENT_OVERWEIGHT
* CAPITAL_MISSING
* EXPECTATION_ALREADY_PRICED
* LEADER_DIVERGENCE
* TECHNICAL_FALSE_BREAKOUT
* PATTERN_SATURATION
* MARKET_MEMORY_CHANGED
* AI_DIFFUSION_SPEED_UP
* MACRO_SHOCK
* RISK_CONTROL_FAILURE
* POSITION_SIZE_TOO_HIGH
* TIMING_TOO_EARLY
* TIMING_TOO_LATE

---

## Lesson Output

Each review should create a Lesson when useful.

Example:

```markdown
# Lesson 0001

## Context
Micron earnings beat expectations, but Memory stocks opened high and faded.

## Root Cause
The event was already highly expected and partially priced in.

## Lesson
Strong earnings alone are not enough. If Awareness and Pattern Saturation are high, Auto Radar must wait for capital and leader confirmation.

## Model Change Candidate
Reduce Event Overlay impact when Awareness Score > 80 and first-day price action is open-high-close-low.
```

---

## Success Definition

A decision is not judged only by profit or loss.

A decision should be evaluated by:

* Was the reasoning correct?
* Was timing correct?
* Was risk controlled?
* Was the position size appropriate?
* Did the market confirm the thesis?
* Did the review produce new knowledge?

---

## Final Principle

A failed decision is useful if it improves the next decision.

A winning decision is dangerous if it reinforces wrong reasoning.
