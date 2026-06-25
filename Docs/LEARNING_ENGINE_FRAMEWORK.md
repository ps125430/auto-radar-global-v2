# Learning Engine Framework v1.0

Document ID: AR-LEARNING-ENGINE-FRAMEWORK-v1
Owner: 小G / Research Chief
Reviewed by: 小P / Chief Architect
Implemented by: 小C / Repository Engineer
Status: Hypothesis Ready
Layer: Review / Decision Lab
Model Impact: Review metric candidate only, not production scoring

---

## 1. Purpose

Learning Engine Framework defines how Auto Radar classifies success, failure, learning actions, confidence calibration issues, unknowns, and learning score candidates.

This framework is for Review / Decision Lab only.

It does not directly change Theme Score, Stage Score, Decision Score, position sizing, production trading logic, Dashboard behavior, or pipeline behavior.

---

## 2. Failure Taxonomy

Failure Taxonomy classifies why a decision, interpretation, or validation case failed.

The taxonomy is stored in:

```text
Data/Learning/FAILURE_TAXONOMY.json
```

Failure categories:

* Information Perception Failures
* Market Cognition Failures
* Temporal & Propagation Failures
* Boundary & Force Majeure Failures

Failure taxonomy is used for root cause review, not production scoring.

---

## 3. Success Taxonomy

Success Taxonomy classifies why a decision, interpretation, or validation case worked.

The taxonomy is stored in:

```text
Data/Learning/SUCCESS_TAXONOMY.json
```

Success categories:

* Information Perception Success
* Market Cognition Success
* Temporal & Propagation Success
* Boundary & Random Luck

Success taxonomy helps separate skill, structure, evidence, timing, and luck.

---

## 4. Learning Action Flow

Learning Action Flow defines what Auto Radar should do after a review.

The action list is stored in:

```text
Data/Learning/LEARNING_ACTIONS.json
```

Possible actions include:

* Need Nothing
* Need New Evidence
* Need Missing Data
* Need New Case Study
* Need Framework Update
* Need Hypothesis Update
* Need Engineering Fix
* Need Validation
* Need Confidence Recalibration

Learning actions are workflow outputs only. They do not change production scoring by themselves.

---

## 5. Confidence Calibration

Confidence Calibration reviews whether Auto Radar was too confident, not confident enough, or appropriately calibrated.

Questions:

* Was confidence supported by evidence quality?
* Did confidence ignore missing data?
* Did confidence overfit one narrative?
* Did confidence correctly account for uncertainty?
* Did confidence improve after review?

Confidence Calibration may create a learning action, but it must not directly change production scoring.

---

## 6. Unknown Tracker

Unknown Tracker records what the system did not know at decision time.

Unknowns may include:

* missing market expectation data
* incomplete leader reaction
* unvalidated Knowledge Graph propagation
* unknown information half-life
* unknown regime condition
* untested narrative lifecycle state

Unknowns must be preserved so the review process does not rewrite history after the outcome is known.

---

## 7. Learning Score Candidate

Learning Score Candidate is a review metric candidate.

The structure is stored in:

```text
Data/Learning/LEARNING_SCORE_CANDIDATE.json
```

Learning Score is not trading performance.

A profitable case can have low learning score.

A losing case can have high learning score.

Learning Score must not directly change Theme Score, Stage Score, Decision Score, or production trading logic.

Weights are candidate only and require case validation.

---

## 8. Boundary Rule

Learning Engine outputs are review artifacts only.

Strict limits:

* Do not modify production scoring.
* Do not modify Theme Score.
* Do not modify Stage Score.
* Do not modify Decision Score.
* Do not create production trading rules.
* Do not promote one case into a Core Rule.
* Do not treat luck as skill.
* Do not hide unknowns after outcomes are known.

Any production impact requires:

* multiple validated cases
* 小P architecture review
* explicit implementation task for 小C
* validation before deployment

---

Status: Hypothesis Ready

Layer: Review / Decision Lab

Model Impact: Review metric candidate only, not production scoring
