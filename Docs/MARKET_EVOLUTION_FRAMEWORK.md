# Market Evolution Framework v1.0

Document ID: AR-FRAMEWORK-2026-06-25
Owner: 小G / Research Chief
Reviewed by: 小P / Chief Architect
Status: Hypothesis Ready
Model Impact: Research only, not production scoring yet

---

## 1. Definition

Market Evolution Framework describes how market reactions change after investors, institutions, media, and AI systems repeatedly observe similar events and themes.

The framework is designed to help Auto Radar study whether a market pattern is still early, already familiar, crowded, saturated, or structurally faster than before.

This document belongs to the Hypothesis Layer. It is a research framework only and must not be treated as production scoring logic until validation is complete.

---

## 2. Core Hypothesis

Markets do not react to the same event pattern with the same speed, intensity, or direction forever.

When a theme or event pattern repeats, the market may evolve through several cognitive states:

* investors recognize the pattern earlier;
* expectations are priced in before the event;
* narrative strength accelerates capital flow;
* repeated playbooks become crowded;
* AI and information diffusion compress reaction time;
* good news may stop producing upside if the pattern is already saturated;
* bad news may stop producing downside if expectations were already too low.

Core hypothesis:

Market behavior is shaped not only by the event itself, but also by what the market already remembers, expected, priced in, and learned from previous similar events.

---

## 3. Six Market Evolution Indicators

These indicators are modifier candidates.
They should not directly change Theme Score, Stage Score, or Decision Score until validated.

The six indicators below are used to structure research observations. They are not production model weights.

### 3.1 Market Memory

Market Memory measures whether the market has already seen and learned a similar setup.

Research questions:

* Has this event or theme pattern appeared before?
* Did the market previously reward or punish the same setup?
* Are investors likely to recognize the playbook quickly?
* Is the market reacting from fresh discovery or from remembered pattern behavior?

Possible observations:

* low memory: the setup is new, underrecognized, or misunderstood;
* medium memory: the setup is known but not fully priced;
* high memory: the setup is familiar and may be front-run.

Research use:

Market Memory helps 小G evaluate whether the market is reacting to new information or replaying an old script.

### 3.2 Expectation Gap

Expectation Gap measures the difference between what the market expected and what actually happened.

Research questions:

* What did the market expect before the event?
* Was the result above, in line with, or below expectations?
* Was the positive or negative surprise already priced in?
* Did price action confirm or reject the surprise?

Possible observations:

* positive gap: actual result exceeds expectation;
* neutral gap: actual result matches expectation;
* negative gap: actual result misses expectation;
* inverted gap: result is good but price falls, or result is bad but price rises.

Research use:

Expectation Gap helps explain why good news may fail to rise and bad news may fail to fall.

### 3.3 Pattern Saturation

Pattern Saturation measures whether a known market playbook has become too crowded or too obvious.

Research questions:

* Is this theme already widely discussed?
* Are leaders already extended?
* Are late followers moving more than core leaders?
* Is price no longer responding to fresh positive news?
* Are traders using the same catalyst as an exit event?

Possible observations:

* low saturation: early pattern recognition;
* medium saturation: active momentum, still tradable with risk control;
* high saturation: crowded trade, higher reversal risk;
* extreme saturation: news becomes an exit trigger.

Research use:

Pattern Saturation supports stage review and risk discussion, but does not directly alter Stage Score until validated.

### 3.4 Narrative Strength

Narrative Strength measures whether a theme has a clear, repeatable, and emotionally compelling market story.

Research questions:

* Can the market explain the theme in one simple story?
* Does the story connect event, theme, leader, and future earnings potential?
* Is the narrative supported by data, orders, policy, or capital expenditure?
* Is the narrative spreading across sectors or only within one stock?

Possible observations:

* weak narrative: fragmented story, unclear beneficiary chain;
* moderate narrative: understandable story with partial evidence;
* strong narrative: clear story, strong leaders, broad market attention;
* overheated narrative: story is obvious, repeated, and vulnerable to disappointment.

Research use:

Narrative Strength helps 小G explain theme awareness and capital flow behavior.

### 3.5 AI Influence

AI Influence measures whether AI tools, algorithmic summarization, automated news feeds, or model-driven research are accelerating market interpretation.

Research questions:

* Did market reaction speed appear faster than historical cases?
* Did news, earnings, or policy language become widely summarized quickly?
* Are similar AI-generated narratives appearing across market commentary?
* Did reaction happen before traditional analyst reports arrived?

Possible observations:

* low AI influence: reaction follows traditional information flow;
* medium AI influence: summaries and narratives spread quickly;
* high AI influence: market interpretation compresses into a very short window.

Research use:

AI Influence helps study whether reaction windows are becoming shorter and whether Auto Radar needs faster evidence collection in future versions.

### 3.6 Information Diffusion

Information Diffusion measures how quickly and widely market information spreads.

Research questions:

* Was the catalyst known only to specialists or broadly visible?
* Did the information spread from one market to another?
* Did media, social platforms, analysts, and trading desks converge on the same message?
* Did the price move before most participants could manually process the event?

Possible observations:

* slow diffusion: information remains niche;
* normal diffusion: information spreads through expected channels;
* fast diffusion: market response appears compressed;
* saturated diffusion: everyone knows the catalyst, reducing surprise value.

Research use:

Information Diffusion helps distinguish early discovery from late consensus.

---

## 4. Market Evolution Report Format

Each major event or theme review should produce a structured Market Evolution section.

Suggested format:

```md
## Market Evolution Review

Event:
Theme:
Core Leaders:
Review Date:
Research Owner:

### Market Memory
Observation:
Evidence:
Hypothesis Impact:

### Expectation Gap
Observation:
Evidence:
Hypothesis Impact:

### Pattern Saturation
Observation:
Evidence:
Hypothesis Impact:

### Narrative Strength
Observation:
Evidence:
Hypothesis Impact:

### AI Influence
Observation:
Evidence:
Hypothesis Impact:

### Information Diffusion
Observation:
Evidence:
Hypothesis Impact:

### Summary
What changed in market behavior:
What Auto Radar should monitor next:
Whether this remains research-only:
```

Report output should be used by 小P for architecture review and by 小C only after implementation requirements are explicitly approved.

---

## 5. Integration With Auto Radar Scores

This framework may later support Market Cognition and Decision Score adjustment, but it is not connected to production scoring yet.

Current allowed use:

* research notes;
* Market Learning reports;
* hypothesis tagging;
* post-decision review;
* Root Cause Analysis;
* future score modifier design.

Current prohibited use:

* directly changing Theme Score;
* directly changing Stage Score;
* directly changing Decision Score;
* changing trading recommendations;
* changing position sizing;
* bypassing Constitution rules;
* converting a hypothesis into a production rule without validation.

Integration rule:

Any future model integration must go through 小P review, include validation evidence, and be implemented by 小C only after the specification is approved.

---

## 6. Validation Requirement

Each indicator must be validated before production use.

Required checks:

* historical case comparison
* forward tracking
* false positive review
* false negative review
* root cause tagging
* impact on decision quality

Validation notes:

* Historical case comparison must compare similar event-theme-leader chains across different market cycles.
* Forward tracking must record whether the indicator predicted useful behavior before the outcome was obvious.
* False positive review must identify cases where the indicator warned incorrectly.
* False negative review must identify cases where the indicator missed an important market evolution signal.
* Root cause tagging must explain whether failure came from data, interpretation, timing, saturation, or model design.
* Impact on decision quality must be judged by whether decisions became more evidence-based, timely, and risk-aware.

No indicator can become a production modifier until validation results are documented and approved.

---

## 7. Next Step

Next research step:

小G should apply this framework to selected historical and forward-looking cases and produce Market Evolution Reviews.

Next architecture step:

小P should define how validated indicators may later enter a controlled Modifier Candidate registry.

Next engineering step:

小C should not implement scoring changes yet. Engineering work is limited to storing this document and later implementing approved schemas or pipelines.
