# Prompt Contract

Version: 1.0
Owner: Chief Architect（小P）
Status: Core Workflow Candidate
Model Impact: workflow_only_not_production

---

## Research Contract（小G）

### Fixed Input

```text
Research Task
Task ID:
Priority:
Objective:
Background:
Required Deliverables:
Out of Scope:
Research Constraints:
Definition of Done:
Expected Output:
Next Owner:
```

### Fixed Output

```text
Task ID:
Status:
Research Summary:
Key Findings:
Evidence:
Market Implication:
Uncertainty:
Out of Scope Confirmation:
Suggested Next Step:
Next Owner:
```

### Boundary

小G 不修改 Runtime、Production Rule、Architecture Decision、GitHub 程式碼。

---

## Architecture Contract（小P）

### Fixed Input

```text
Architecture Review
Task ID:
Priority:
Objective:
Research Input:
System Context:
Constraints:
Decision Required:
Definition of Done:
Expected Output:
Next Owner:
```

### Fixed Output

```text
Task ID:
Status:
Architecture Decision:
Accepted Scope:
Rejected Scope:
Schema / Template Impact:
Repository Impact:
Validation Requirement:
Engineering Task Candidate:
Next Owner:
```

### Boundary

小P 不修改研究結論、不捏造市場事實、不修改 Evidence。

---

## Engineering Contract（小C）

### Fixed Input

```text
Engineering Task
Task ID:
Priority:
Layer:
Objective:
Input:
Files:
Constraints:
Acceptance:
Deliverables:
Next Owner:
```

### Fixed Output

```text
Task ID:
Status:
Commit Hash:
Git Status:
Files Changed:
Test Result:
Constraints Confirmation:
Next Owner:
```

### Boundary

小C 不修改研究內容、不修改架構、不自行新增策略、不自行修改 Runtime Logic。
