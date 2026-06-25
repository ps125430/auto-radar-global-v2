# Decision Lab Case Template

Document ID: AR-DL-CASE-TEMPLATE
Template Version: 2.0
Status: required_template
Model Impact: review_only_not_production_scoring

---

## Template Rule

All Case Library cases must use this updated template.

This template is required for every future backtest, validation case, event review, and Decision Lab case.

The template does not directly change Theme Score, Stage Score, Decision Score, Dashboard behavior, or production trading logic.

---

## 1. Case Metadata

Case ID:
Review Date:
Market Date Range:
Research Owner:
Architecture Reviewer:
Engineering Owner:
Related Decision Log:
Related Event:
Related Theme:
Related Narrative:
Related Knowledge Graph Node:
Related Case Validation ID:

---

## 2. Original Context

Market Mode:
Main Theme:
Next Theme:
Avoid Themes:
Core Leaders:
Risk Events:

Original Auto Radar Output:

```text
Buy / Watch / Wait / Avoid:
Attack Index:
Suggested Exposure:
Confidence Score:
Entry Condition:
Stop Loss Condition:
Take Profit Condition:
```

Final Decision by 綠茶:

---

## 3. Evidence at Decision Time

Known Facts:

* 

Market Expectations:

* 

Price / Volume Evidence:

* 

Narrative Evidence:

* 

Reality Check Notes:

* 

Unknowns / Assumptions:

* 

---

## 4. Outcome

Actual Market Outcome:

Price Reaction:
Theme Reaction:
Leader Reaction:
Time to Confirmation:
Time to Failure:
Maximum Favorable Move:
Maximum Adverse Move:

Outcome Classification:

```text
success / partial_success / false_positive / false_negative / avoided_loss / unclear
```

---

## 5. Review Questions

1. Did Auto Radar correctly identify the main theme?
2. Did Auto Radar correctly identify the stage and risk level?
3. Did the evidence support the decision at the time?
4. Was the market reaction already priced in?
5. Did narrative strength help or mislead the decision?
6. Did Reality Framework reveal missing facts or assumptions?
7. Did Market Evolution signals change the interpretation?
8. Did the outcome expose a model, data, timing, or execution issue?

---

## 6. Lesson Candidate

Lesson Summary:

What should be remembered:

What should not be overfitted:

Should this become:

```text
Lesson / Hypothesis / Playbook Candidate / No Change
```

---

## 7. Follow-Up

Required Follow-Up:

* 

Owner:
Due Date:
Review Status:

---

## 8. Validation Windows

T+10 minutes:

* AI Influence / high-frequency reaction:
* Immediate leader reaction:
* Initial narrative interpretation:

T+24 hours:

* Reality vs Narrative interpretation:
* Market expectation adjustment:
* Leader and theme confirmation:

T+5 trading days:

* Knowledge Graph propagation:
* Rotation target reaction:
* Sustained or failed narrative:

---

## 9. Root Cause Category

Select all that apply:

```text
[ ] expectation_blindness
[ ] memory_depletion
[ ] saturation_explosion
[ ] graph_disconnection
[ ] ai_resonance_overload
[ ] data_issue
[ ] timing_issue
[ ] other
```

Root Cause Notes:

* 

---

## 10. Weight Update Candidate

Is there any possible weight or rule adjustment candidate?

```text
yes / no / needs_more_cases
```

Candidate Description:

Evidence Required Before Any Model Change:

Important:

Weight updates are candidates only. They must not directly change production scoring without 小P review and a separate 小C implementation task.

---

## 11. Decision Confidence

Decision Confidence records how confident Auto Radar and the review team were at the time of the decision.

Pre-Event Confidence:

```text
low / medium / high
```

Confidence Score at Decision Time:

Key Confidence Drivers:

* 

Key Confidence Reducers:

* 

Was confidence justified by evidence?

```text
yes / no / partial / unclear
```

Confidence Calibration Notes:

* 

Required conclusion:

Did the case show overconfidence, underconfidence, or appropriate confidence?

```text
overconfidence / underconfidence / appropriate / unclear
```

---

## 12. Evidence Quality

Evidence Quality evaluates whether the decision was supported by reliable, timely, and relevant evidence.

Evidence Quality Rating:

```text
low / medium / high
```

Evidence Completeness:

```text
incomplete / sufficient / strong / excessive_noise
```

Source Quality:

```text
weak / mixed / reliable / verified
```

Evidence Categories Reviewed:

```text
[ ] event facts
[ ] market expectation
[ ] price action
[ ] volume action
[ ] leader confirmation
[ ] theme breadth
[ ] narrative strength
[ ] reality check
[ ] knowledge graph signal
[ ] contrary evidence
```

Missing Evidence:

* 

Contradicting Evidence:

* 

Evidence Quality Conclusion:

* 

---

## 13. Counterfactual Analysis

Counterfactual Analysis records what might have happened under different assumptions or decisions.

Counterfactual Question 1:

What if Auto Radar had ignored the main narrative?

Answer:

Counterfactual Question 2:

What if Auto Radar had waited for more confirmation?

Answer:

Counterfactual Question 3:

What if the opposite decision had been made?

Answer:

Alternative Decision Paths:

```text
[ ] Buy instead of Watch / Wait
[ ] Watch instead of Buy
[ ] Wait instead of Watch
[ ] Avoid instead of participate
[ ] Smaller exposure
[ ] Larger exposure
[ ] No action
```

Best Counterfactual Lesson:

* 

Counterfactual Risk:

* 

Final Counterfactual Conclusion:

```text
original_decision_best / alternative_decision_better / inconclusive / needs_more_cases
```
