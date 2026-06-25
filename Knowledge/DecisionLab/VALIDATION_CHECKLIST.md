# Decision Lab Validation Checklist

Document ID: AR-DL-VALIDATION-CHECKLIST
Status: template
Model Impact: validation_only_not_production_scoring

---

## Purpose

This checklist is used before a case, lesson, hypothesis, or playbook is promoted inside Auto Radar.

It prevents unverified ideas from becoming production scoring logic.

---

## 1. Case Completeness

```text
[ ] Case ID exists
[ ] Related date range is clear
[ ] Related event is identified
[ ] Related theme is identified
[ ] Original Auto Radar output is recorded
[ ] Final decision by 綠茶 is recorded
[ ] Outcome is recorded
[ ] Evidence at decision time is separated from evidence discovered later
```

---

## 2. Evidence Quality

```text
[ ] Facts are separated from interpretation
[ ] Market expectation is documented
[ ] Price / volume reaction is documented
[ ] Leader reaction is documented
[ ] Narrative evidence is documented
[ ] Contradicting evidence is documented
[ ] Unknowns and assumptions are listed
```

---

## 3. Outcome Review

```text
[ ] Outcome classification is selected
[ ] Maximum favorable move is recorded when available
[ ] Maximum adverse move is recorded when available
[ ] Timing of confirmation or failure is recorded
[ ] False positive / false negative status is reviewed
[ ] Avoided loss cases are not ignored
```

---

## 4. Root Cause Review

```text
[ ] Root cause category is selected
[ ] Five Whys are completed
[ ] Missed evidence is identified
[ ] Misleading evidence is identified
[ ] Timing issue is reviewed
[ ] Confidence calibration is reviewed
[ ] Stage classification is reviewed when relevant
```

---

## 5. Promotion Rules

A case may become a Lesson only if:

```text
[ ] The lesson is supported by evidence
[ ] The lesson is not only hindsight explanation
[ ] The lesson avoids overfitting one event
[ ] The lesson has clear future use
```

A hypothesis may become a Playbook Candidate only if:

```text
[ ] It appears in multiple cases or has strong forward evidence
[ ] It has clear trigger conditions
[ ] It has invalidation rules
[ ] It has risk controls
[ ] It does not violate Constitution
```

A playbook may affect production logic only if:

```text
[ ] 小P approves architecture impact
[ ] Validation results are documented
[ ] False positives and false negatives are reviewed
[ ] Separate 小C implementation task exists
[ ] Runtime tests are completed
```

---

## 6. Final Review

Reviewer:
Review Date:
Decision:

```text
approved_as_lesson / keep_as_hypothesis / promote_to_playbook_candidate / reject / needs_more_data
```

Notes:
