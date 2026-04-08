# FRD Template

Exact structure for the Functional Requirements Document. Every section is mandatory — write "Not identified in code analysis. To be confirmed with stakeholder." for empty sections.

---

## Document Header

```markdown
# Functional Requirements Document — [Module Name]

> **Version:** 1.0
> **Date:** [Date]
> **Module:** [Module Name]
> **Prepared by:** Claude (AI-assisted FRD generation from code analysis)
> **Status:** Draft — requires stakeholder review

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | Claude | Initial FRD generated from exhaustive code analysis |
```

---

## 1. Introduction

```markdown
## 1. Introduction

### 1.1 Purpose

This document provides a detailed functional requirements specification for the
[Module Name] module. It describes every observable behaviour, data requirement,
business rule, workflow, and interface at a level of detail sufficient for:
- Development teams to understand exact expected behaviour
- QA teams to derive test cases directly from requirements
- Business stakeholders to verify that the system meets their needs

### 1.2 Scope

**In scope:**
- [Bullet list of every capability this module provides]

**Out of scope:**
- [Capabilities that belong to other modules]
- [Features that do not exist in the current codebase]

### 1.3 Definitions & Acronyms

| Term | Definition |
|------|-----------|
| [Term] | [Plain English definition as used in this module] |

### 1.4 References

| Document | Location | Relevance |
|----------|----------|-----------|
| High-level functional spec | `./functional-specs/modules/[mod]/README.md` | Overview context |
| Business rules master | `./functional-specs/reference/business-rules-master.md` | Cross-module rules |
```

---

## 2. System Overview

```markdown
## 2. System Overview

### 2.1 Module Purpose

[2-3 paragraphs describing what this module does, what business problem it
solves, and who uses it. Written for someone who has never seen the system.]

### 2.2 Context Diagram

` ` `mermaid
%% CTX-[MOD]-001: Module Context
flowchart LR
    subgraph "Users"
        U1([Role 1])
        U2([Role 2])
    end
    subgraph "[Module Name]"
        M[Module capabilities summary]
    end
    subgraph "Other Modules"
        OM1(Module A)
        OM2(Module B)
    end
    subgraph "External Systems"
        EX1(System X)
    end
    U1 --> M
    U2 --> M
    M --> OM1
    M --> OM2
    M --> EX1
` ` `

### 2.3 User Roles & Permissions

| Role | Description | Access Level | Permissions in This Module |
|------|-------------|-------------|---------------------------|
| [Role] | [Description] | [Full/Limited/Read-only] | [Specific actions: can create, can edit, can approve, can view, cannot delete, etc.] |

### 2.4 Feature Summary

| Feature Area | Description | Key FRs |
|-------------|-------------|---------|
| [e.g., Order Creation] | [One sentence] | FR-[MOD]-001 to FR-[MOD]-012 |
| [e.g., Order Approval] | [One sentence] | FR-[MOD]-013 to FR-[MOD]-020 |
```

---

## 3. Functional Requirements

```markdown
## 3. Functional Requirements

### 3.1 [Feature Area Name]

#### FR-[MOD]-001: [Short description]

**The system shall** [specific, atomic, testable behaviour].

| Attribute | Detail |
|-----------|--------|
| **Priority** | Must / Should / May |
| **User Role(s)** | [Who can trigger this] |
| **Trigger** | [What starts this — user action, system event, schedule] |
| **Pre-conditions** | [What must be true before this can happen] |

**Input:**
| Field | Required | Format | Validation | Source |
|-------|----------|--------|-----------|--------|
| [Field] | Yes/No | [Format] | [Rules] | [User input / System / Other module] |

**Processing:**
1. The system [step 1 — what happens first]
2. The system [step 2 — next action]
3. If [condition], the system [conditional step]
4. Otherwise, the system [alternative step]

**Output:**
| Output | Recipient | Format | Content |
|--------|-----------|--------|---------|
| [Screen update / Message / File / Notification] | [User / Other module / External system] | [Display / Email / CSV / etc.] | [What it contains] |

**Business Rules:**
- BR-[MOD]-NNN: [Rule that applies to this FR]

**Error Conditions:**
| Condition | Error Message | Severity | Recovery |
|-----------|--------------|----------|----------|
| [What goes wrong] | "[Exact message]" | Blocking/Warning | [What user can do] |

**Testable:** Yes — [Brief description of how QA would verify this]

---

#### FR-[MOD]-002: [Next requirement]

[Same structure repeats for every requirement]
```

---

## 4. External Interface Requirements

```markdown
## 4. External Interface Requirements

### 4.1 User Interfaces

#### Screen: [Screen Name]

**Purpose:** [What the user accomplishes on this screen]
**Access:** [Roles that can see this screen]
**URL/Route:** [Navigation path in user terms, e.g., "Main Menu → Orders → Order List"]

**Layout Description:**

[Top-to-bottom, left-to-right description of every element on the screen]

**Header Section:**
- [Element 1: what it is, what it shows, what it does]
- [Element 2]

**Filter/Search Section:**
| Filter | Type | Options | Default | Behaviour |
|--------|------|---------|---------|-----------|
| [Filter name] | Dropdown/Text/Date/Toggle | [Options or format] | [Default] | [What happens when applied] |

**Data Table/List:**
| Column | Data | Sortable | Default Sort | Click Action |
|--------|------|----------|-------------|-------------|
| [Column name] | [What it shows] | Yes/No | [Asc/Desc/None] | [What happens when clicked] |

**Action Buttons:**
| Button | Label | Position | Visible When | Click Behaviour | Confirmation Required |
|--------|-------|----------|-------------|----------------|---------------------|
| [ID] | "[Label text]" | [Location] | [Condition] | [What happens] | Yes/No |

**Form Fields:** (if the screen has a form)
| Field | Label | Type | Required | Default | Validation | Error Message |
|-------|-------|------|----------|---------|-----------|---------------|
| [ID] | "[Label]" | Text/Dropdown/Date/Checkbox/etc. | Yes/No | [Default] | [Rules] | "[Message]" |

**Pagination:**
- [Records per page, page controls, total count display]

---

### 4.2 Software Interfaces

#### Interface: [Module/System Name]

**Direction:** Inbound / Outbound / Bidirectional
**Trigger:** [What causes this interaction]
**Purpose:** [Why this module talks to the other system — in business terms]

**Data Sent:**
| Field | Format | Description |
|-------|--------|-------------|
| [Field] | [Format] | [What it represents] |

**Data Received:**
| Field | Format | Description |
|-------|--------|-------------|
| [Field] | [Format] | [What it represents] |

**User-Visible Effect:** [What the user sees as a result of this interaction]
**Error Handling:** [What happens if the other system is unavailable]
```

---

## 5. Data Requirements

```markdown
## 5. Data Requirements

### 5.1 Logical Data Model

[Describe entities and relationships in plain English]

**[Entity Name]**
- [Description of what this entity represents]
- Relationships: [A Customer has many Orders. An Order has many Line Items.]

` ` `mermaid
%% DM-[MOD]-001: Logical Data Model
erDiagram
    CUSTOMER ||--o{ ORDER : "places"
    ORDER ||--|{ LINE-ITEM : "contains"
    ORDER }|--|| STATUS : "has"
` ` `

### 5.2 Data Dictionary

#### [Entity Name] Fields

| FLD ID | Field Name | Description | Type | Required | Format | Validation | Allowed Values | Default | Editable By |
|--------|-----------|-------------|------|----------|--------|-----------|----------------|---------|-------------|
| FLD-[MOD]-001 | [Name] | [What it represents] | Text/Number/Date/Boolean/Selection | Yes/No | [Constraints] | [Rules] | [Values or "Any"] | [Default] | [Roles] |

### 5.3 Data Processing Rules

| DPR ID | Rule | Input Fields | Output | Trigger |
|--------|------|-------------|--------|---------|
| DPR-[MOD]-001 | The system shall calculate [what] as [formula] | [Fields used] | [Result field] | [When calculated] |
```

---

## 6. Workflow Diagrams

```markdown
## 6. Workflow Diagrams

### 6.1 User Workflows

#### WF-[MOD]-001: [Workflow Name]

**Actors:** [Roles involved]
**Trigger:** [What starts the workflow]
**End State:** [What the successful outcome looks like]

` ` `mermaid
flowchart TD
    A([Trigger]) --> B[Step 1]
    B --> C{Decision?}
    C -->|Yes| D[Path A]
    C -->|No| E[Path B]
    D --> F([End state])
` ` `

**Step Details:**
| Step | Actor | Action | System Response | Business Rules |
|------|-------|--------|----------------|---------------|
| 1 | [Role] | [What they do] | [What system does] | BR-[MOD]-NNN |

### 6.2 Entity State Lifecycles

#### SLC-[MOD]-001: [Entity] Lifecycle

` ` `mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2 : [trigger by role]
` ` `

| From | To | Trigger | Role | Conditions | Side Effects |
|------|-----|---------|------|-----------|-------------|
| [State] | [State] | [Action] | [Role] | [Rules] | [Notifications, updates, etc.] |

### 6.3 Decision Trees

#### DT-[MOD]-001: [Complex Rule Name]

` ` `mermaid
flowchart TD
    A{Condition 1?} -->|Yes| B{Condition 2?}
    A -->|No| C[Outcome A]
    B -->|Yes| D[Outcome B]
    B -->|No| E[Outcome C]
` ` `
```

---

## 7. Non-Functional Requirements

```markdown
## 7. Non-Functional Requirements

All items in this section are documented ONLY if evidence was found in code or
configuration. Each item is tagged with its source.

### 7.1 Performance
| NFR ID | Requirement | Source | Observed Value |
|--------|------------|--------|----------------|
| NFR-[MOD]-001 | [e.g., "Pagination defaults to 25 records per page"] | [Config file] | [Value] |

### 7.2 Security
| NFR ID | Requirement | Source |
|--------|------------|--------|
| NFR-[MOD]-002 | [e.g., "Only Admin role can delete records"] | [@PreAuthorize on controller] |

### 7.3 Audit & Logging
[What actions create audit entries — only if observed]

### 7.4 Data Retention
[Soft delete vs hard delete patterns — only if observed]

### 7.5 Constraints
[Upload limits, character limits, etc. — only from config]
```

---

## 8. Assumptions & Open Questions

```markdown
## 8. Assumptions & Dependencies

### 8.1 Assumptions

| ID | Assumption | Confidence | Code Evidence | Needs Confirmation |
|----|-----------|------------|---------------|-------------------|
| A-[MOD]-001 | [What was assumed] | High/Med/Low | [Where observed] | Yes/No |

### 8.2 Dependencies

| Dependency | Type | Impact if Unavailable |
|-----------|------|----------------------|
| [Module/System] | [Data/Auth/Notification] | [What breaks from user perspective] |

### 8.3 Open Questions

| # | Question | Area | Impact on FRD |
|---|---------|------|-------------|
| 1 | [Question] | [Section] | [Which FRs are affected] |
```

---

## Appendices

```markdown
## Appendix A: Complete Field Inventory

| FLD ID | Field Name | Entity/Screen | Type | Required | Format | Validation |
|--------|-----------|--------------|------|----------|--------|-----------|
[Every field from every entity and every form in one consolidated table]

## Appendix B: Complete Error Message Inventory

| ERR ID | Trigger | Message | Screen | Severity | Resolution |
|--------|---------|---------|--------|----------|-----------|
[Every error the user can encounter in this module]

## Appendix C: Complete Business Rule Inventory

| BR ID | Rule | Trigger | Affected Screens | Affected FRs |
|-------|------|---------|-----------------|-------------|
[Every business rule in this module]

## Appendix D: Requirement Traceability Matrix

| FR ID | Feature Area | Screen | Business Rules | Data Rules | Error Conditions |
|-------|-------------|--------|---------------|-----------|-----------------|
[Maps every FR to its related screens, rules, and error conditions]
```
