# Root Cause Analysis Template

Document ID: AR-DL-RCA-TEMPLATE
Status: template
Model Impact: review_only_not_production_scoring

---

## 1. RCA Metadata

RCA ID:
Related Case ID:
Related Decision Log:
Review Date:
Owner:
Reviewer:
Outcome Classification:

---

## 2. Problem Statement

What happened?

What did Auto Radar expect?

What did the market actually do?

Why does this require review?

---

## 3. Root Cause Category

Select all that apply:

```text
[ ] Data issue
[ ] Event interpretation issue
[ ] Expectation gap issue
[ ] Narrative issue
[ ] Reality check issue
[ ] Market evolution issue
[ ] Timing issue
[ ] Stage classification issue
[ ] Risk detection issue
[ ] Confidence calibration issue
[ ] Execution / workflow issue
[ ] Unknown
```

---

## 4. Evidence Review

Evidence Auto Radar used:

* 

Evidence Auto Radar missed:

* 

Evidence that was misleading:

* 

Evidence that appeared only after the decision:

* 

---

## 5. Five Whys

1. Why did the outcome differ from expectation?

Answer:

2. Why did Auto Radar interpret the situation that way?

Answer:

3. Why was the key signal missed or overweighted?

Answer:

4. Why did the current process allow this failure?

Answer:

5. What is the deepest fixable cause?

Answer:

---

## 6. Lesson Extraction

Lesson:

Should this lesson update:

```text
[ ] Knowledge/Events
[ ] Knowledge/Lessons
[ ] Knowledge/Playbooks
[ ] Knowledge/Hypothesis
[ ] Knowledge/DecisionLogs
[ ] Docs framework
[ ] No update
```

---

## 7. Model Impact Decision

Model change needed?

```text
yes / no / not_yet / needs_more_cases
```

If yes, required approval:

* 小P architecture review
* separate 小C implementation task
* validation before production scoring

---

## 8. Follow-Up Actions

Action Items:

* 

Owner:
Due Date:
Status:
