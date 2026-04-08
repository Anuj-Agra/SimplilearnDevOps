# Gap Analysis Report — Output Template

---

## Title Page

- **Document Title:** Gap Analysis Report — [System Name]
- **Version:** 1.0
- **Date:** [Today's date]
- **Prepared by:** Claude (AI-assisted gap analysis)
- **Baseline Spec:** [Reference to functional spec document, if used]
- **Scope:** [Full codebase / Module name / Workflow name]

---

## Document Control

| Version | Date | Author | Change Description |
|---------|------|--------|--------------------|
| 1.0 | [Date] | Claude | Initial gap analysis from codebase scan |

---

## 1. Executive Summary

Write 3-4 paragraphs covering:

- **Coverage snapshot:** "Of [N] functional requirements, [X] are fully implemented, [Y] are partially implemented, and [Z] are missing."
- **Top risks:** The 3-5 most severe findings, each in one sentence with the user impact.
- **Technical health:** One-sentence summary of code quality (e.g., "The codebase has strong validation patterns but weak error handling and no timeout configuration on external calls.")
- **Recommendation:** What to fix before the next release, in priority order.

### Severity Summary

| Severity | Functional Gaps | Technical Gaps | Total |
|----------|----------------|----------------|-------|
| 🔴 Critical | [count] | [count] | [count] |
| 🟠 High | [count] | [count] | [count] |
| 🟡 Medium | [count] | [count] | [count] |
| **Total** | **[count]** | **[count]** | **[count]** |

---

## 2. Functional Gap Analysis

### 2.1 Requirements Coverage by Module

| Module | Total Reqs | ✅ Implemented | ⚠️ Partial | ❌ Missing | 🔍 Ambiguous | Coverage % |
|--------|-----------|---------------|-----------|-----------|-------------|------------|
| [Module] | [N] | [n] | [n] | [n] | [n] | [X%] |

### 2.2 Gap Details by Module

Repeat for each module:

#### [Module Name]

| Req ID | Requirement | Status | Gap Description | User Impact | Severity | Recommended Fix | Effort |
|--------|-------------|--------|-----------------|-------------|----------|-----------------|--------|
| FR-XXX-001 | [From spec] | ⚠️/❌ | [What is missing or wrong] | [What user experiences] | 🔴/🟠/🟡 | [Specific action] | Low/Med/High |

---

## 3. Technical Gap Analysis

### 3.1 Summary by Category

| Category | Critical | High | Medium | Total |
|----------|----------|------|--------|-------|
| Exception Handling | [n] | [n] | [n] | [n] |
| Input Validation | [n] | [n] | [n] | [n] |
| Resource Management | [n] | [n] | [n] | [n] |
| Concurrency | [n] | [n] | [n] | [n] |
| Security | [n] | [n] | [n] | [n] |
| Configuration | [n] | [n] | [n] | [n] |
| Data Integrity | [n] | [n] | [n] | [n] |

### 3.2 Findings Detail

#### 🔴 Critical Findings

| ID | Category | Location | Description | Production Scenario | Recommended Fix | Effort |
|----|----------|----------|-------------|---------------------|-----------------|--------|
| TG-001 | [Category] | [File:Line] | [What's wrong] | [When user does X, Y happens because...] | [Specific code change] | [Est.] |

#### 🟠 High Findings

[Same table structure]

#### 🟡 Medium Findings

[Same table structure]

---

## 4. Workflow Integrity

### 4.1 Audited Workflows

| Workflow | Steps | Status | Gaps Found |
|----------|-------|--------|------------|
| [Workflow name] | [N] | Clean / Gaps Found | [count] |

### 4.2 Workflow Gap Details

For each workflow with gaps:

**[Workflow Name]:** [One-sentence description]

| Step | Expected Behaviour | Actual Behaviour | Gap | Severity |
|------|--------------------|------------------|-----|----------|
| [Step N] | [From spec/inferred] | [What code does] | [What's missing] | 🔴/🟠/🟡 |

**Edge cases checked:**
- ❌/✅ User abandons mid-workflow (orphaned records?)
- ❌/✅ User retries a step (duplicate records?)
- ❌/✅ Concurrent users on same entity (race condition?)
- ❌/✅ Timeout during external call mid-workflow (partial state?)

---

## 5. Risk Heatmap

Matrix showing gap density per module per category. Use this to prioritize which module to fix first.

| Module | Exception Handling | Validation | Security | Data Integrity | Concurrency | Overall Risk |
|--------|--------------------|------------|----------|----------------|-------------|-------------|
| [Module] | 🔴/🟠/🟡/🟢 | ... | ... | ... | ... | 🔴/🟠/🟡/🟢 |

Legend: 🔴 Critical gaps present | 🟠 High gaps present | 🟡 Medium gaps only | 🟢 No gaps found

---

## 6. Prioritized Fix Plan

### Immediate (Before Next Release)

| Priority | ID | Description | Module | Effort | Assigned To |
|----------|-----|-------------|--------|--------|-------------|
| 1 | TG-001 | [Fix description] | [Module] | [Est.] | [Leave blank] |

### Next Sprint

[Same table]

### Backlog

[Same table]

---

## 7. Assumptions & Limitations

| ID | Assumption/Limitation | Impact on Analysis |
|----|----------------------|-------------------|
| A-001 | [e.g., "Analysis based on code only; runtime configuration not inspected"] | [e.g., "Timeout settings in deployment configs may override code defaults"] |

---

## Writing Style Rules

1. **Gaps are user-facing.** "User sees a blank page" not "NullPointerException at line 42"
2. **Fixes are developer-actionable.** "Add @NotNull to customerId in OrderService.createOrder()" not "fix the bug"
3. **Severity is evidence-based.** Critical = data loss or outage under normal conditions. High = fails under load or edge input. Medium = cosmetic or rare edge case.
4. **File references are precise.** Always include file name and line number for technical gaps.
5. **No invented gaps.** If the code is ambiguous, classify as 🔍 Ambiguous, don't invent a gap.
