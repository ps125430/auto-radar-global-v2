# Narrative Intelligence Framework v1.0

Document ID: AR-FRAMEWORK-2026-06-25-D004
Owner: 小G / Research Chief
Reviewed by: 小P / Chief Architect
Implemented by: 小C / Repository Engineer
Status: Hypothesis Ready
Model Impact: Research only, not production scoring yet

---

## 1. Definition

Narrative Intelligence Framework defines how Auto Radar observes, records, and evaluates market narratives.

A market narrative is the story the market uses to explain why an event matters, which themes may benefit, which leaders matter, and why capital should move now.

This framework is research infrastructure. It does not directly change Theme Score, Stage Score, Decision Score, position sizing, or trading recommendations.

---

## 2. Purpose

The purpose of Narrative Intelligence is to help Auto Radar answer:

* What story is the market trading?
* Is the story new, strengthening, mature, or exhausted?
* Which event created or changed the story?
* Which themes and leaders are attached to the story?
* Is the narrative supported by evidence or only by attention?
* Has the market already priced in the story?

---

## 3. Core Hypothesis

Market price movement is often driven by a combination of evidence and narrative.

A strong narrative can accelerate capital flow when it connects:

* an event;
* a theme;
* a believable future outcome;
* clear leader stocks;
* market attention;
* repeatable confirmation evidence.

However, a strong narrative can also become dangerous when it becomes too obvious, crowded, or disconnected from evidence.

Core hypothesis:

Narrative quality affects market awareness, theme leadership, and reaction speed, but it must be validated before becoming any production score modifier.

---

## 4. Narrative Intelligence Dimensions

These dimensions are research candidates only.
They should not directly change Theme Score, Stage Score, or Decision Score until validated.

### 4.1 Narrative Clarity

Measures whether the market can explain the theme in a simple and repeatable way.

Research questions:

* Can the story be summarized clearly?
* Does the market understand why the event matters?
* Are the beneficiaries easy to identify?
* Is the story too vague to guide capital flow?

### 4.2 Evidence Support

Measures whether the narrative is supported by concrete evidence.

Research questions:

* Is the story supported by earnings, orders, policy, demand, pricing, or capex?
* Are there measurable signals behind the story?
* Is the narrative moving faster than the evidence?
* Is the evidence improving or weakening?

### 4.3 Leader Confirmation

Measures whether core leader stocks confirm the narrative.

Research questions:

* Are leaders outperforming followers?
* Are leaders reacting before the broad theme?
* Are leader moves supported by volume or only short-term attention?
* Are followers rising while leaders stall?

### 4.4 Attention Expansion

Measures whether the narrative is spreading across the market.

Research questions:

* Is the story spreading from specialists to mainstream investors?
* Are media, analysts, and social channels converging on the same explanation?
* Is capital rotating into related themes?
* Is awareness still early or already crowded?

### 4.5 Narrative Durability

Measures whether the narrative can survive beyond one news cycle.

Research questions:

* Does the story have multiple future catalysts?
* Can new evidence continue to support it?
* Is the theme connected to a structural trend?
* Does the narrative fade quickly after the first event?

### 4.6 Narrative Risk

Measures whether the narrative is becoming fragile.

Research questions:

* Is the story too consensus?
* Is valuation or price action already stretched?
* Is good news failing to create new upside?
* Is the narrative being used as an exit event?
* Is evidence lagging behind attention?

---

## 5. Narrative Intelligence Report Format

Suggested research format:

```md
# Narrative Intelligence Review

Narrative Name:
Related Event:
Related Theme:
Core Leaders:
Review Date:
Research Owner:

## Narrative Summary
What story is the market trading?

## Evidence Support
What evidence supports or weakens the story?

## Leader Confirmation
Which leaders confirm or reject the narrative?

## Attention Expansion
Is awareness early, expanding, crowded, or exhausted?

## Narrative Durability
Can the story survive beyond one catalyst?

## Narrative Risk
What could break or reverse the narrative?

## Research Conclusion
Should this remain research-only, enter hypothesis tracking, or be reviewed by 小P for future architecture design?
```

---

## 6. Integration With Auto Radar

Allowed use:

* market research notes;
* Market Learning reports;
* Knowledge Core entries;
* hypothesis tracking;
* event review;
* post-decision Root Cause Analysis;
* future modifier candidate design.

Prohibited use:

* directly changing Theme Score;
* directly changing Stage Score;
* directly changing Decision Score;
* directly changing position sizing;
* changing trading recommendations;
* bypassing Constitution rules;
* promoting unvalidated narratives into production logic.

Integration rule:

Narrative Intelligence can only enter production after validation, 小P approval, and a separate 小C implementation task.

---

## 7. Validation Requirement

Each narrative dimension must be validated before production use.

Required checks:

* historical case comparison
* forward tracking
* false positive review
* false negative review
* leader confirmation review
* attention saturation review
* root cause tagging
* impact on decision quality

Validation must prove that the narrative signal improves decision quality instead of only explaining price movement after the fact.

---

## 8. Next Step

小G should apply this framework to selected market themes and produce Narrative Intelligence Reviews.

小P should decide whether any narrative dimensions deserve a formal schema in Knowledge Core.

小C should not implement scoring changes from this framework until a separate approved specification exists.
