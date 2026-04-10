# Functional Specification Document — Output Template

Use this template as the exact structure for every generated spec. Adapt section depth to the size of the codebase, but never remove a section — write "Not applicable" if a section has no content.

---

## Title Page

- **Document Title:** Functional Specification — [System Name]
- **Version:** 1.0
- **Date:** [Today's date]
- **Prepared by:** Claude (AI-assisted specification generation)
- **Reviewed by:** [Leave blank for the user to fill]

---

## Document Control

| Version | Date | Author | Change Description |
|---------|------|--------|--------------------|
| 1.0 | [Date] | Claude | Initial specification generated from codebase analysis |

---

## 1. Introduction & Purpose

Write 2-3 paragraphs covering:
- What the system is (one sentence)
- What business problem it solves (one paragraph)
- Who it serves (one sentence listing primary user groups)
- The value it provides (one paragraph, in business terms)

**Tone:** Write as if explaining to a new product owner on their first day. No acronyms without definition.

---

## 2. Project Scope

### 2.1 In Scope

Bullet list of all capabilities found in the code, grouped by module. Each bullet is one sentence.

Example:
- **User Management:** Registration, login, profile editing, password reset, and role-based access control
- **Order Processing:** Creation, editing, submission, approval workflow, and order history

### 2.2 Out of Scope

Explicitly state what the system does NOT do. Infer this from what is absent. This is critical for preventing scope creep.

Example:
- The system does not handle payment processing directly (orders are marked as "paid" manually)
- There is no built-in reporting or analytics dashboard
- Mobile-specific layouts are not provided; the interface is desktop-oriented

---

## 3. User Roles & Personas

| Role Name | Description | Access Level | Key Permissions |
|-----------|-------------|--------------|-----------------|
| [Role] | [One-sentence description] | [Full / Limited / Read-only] | [What they can do, comma-separated] |

For each role, add a short persona paragraph (2-3 sentences) describing a typical person in that role, their goals, and how they use the system. This helps stakeholders empathise with users.

---

## 4. System Overview

One paragraph describing the system at the highest level — what it is, how many major modules it has, and how a user typically flows through it.

Then a bullet list of modules with one-sentence descriptions:

- **[Module Name]:** [What it does from the user's perspective]
- **[Module Name]:** [What it does from the user's perspective]

---

## 5. Functional Requirements by Module

Repeat this structure for each module:

### 5.N [Module Name]

#### Overview
One paragraph explaining what this module does and why it exists, in business terms.

#### User Stories

- As a [role], I can [action] so that [benefit].
- As a [role], I can [action] so that [benefit].

#### Screen & Page Descriptions

For each screen/page in the module:

**[Screen Name]**
- **Purpose:** What the user accomplishes here
- **Access:** Which roles can see this screen
- **Key Elements:**
  - [Describe what the user sees: forms, tables, buttons, filters, etc.]
  - [Describe the primary action the user takes]
- **Navigation:** How the user gets here and where they go next

#### Business Rules

Number each rule for traceability:

| Rule ID | Rule Description | Trigger Condition |
|---------|-----------------|-------------------|
| BR-[Module]-001 | [Testable statement of the rule] | [When does this rule apply] |
| BR-[Module]-002 | [Testable statement of the rule] | [When does this rule apply] |

#### Data Requirements

| Field Name | Required | Format / Constraints | Allowed Values | Notes |
|------------|----------|---------------------|----------------|-------|
| [Plain English name] | Yes/No | [e.g. "Max 100 characters", "Email format", "Positive number"] | [e.g. "Active, Inactive, Suspended" or "Any"] | [Any additional context] |

#### Error Handling

| Error Scenario | User-Visible Message | User Resolution |
|---------------|---------------------|-----------------|
| [What goes wrong from user's perspective] | [Exact or paraphrased message] | [What the user should do] |

---

## 6. Cross-Cutting Concerns

### 6.1 Authentication & Access
- How users log in (username/password, SSO, etc.)
- Session behaviour (timeout, remember me)
- What happens when an unauthorised user tries to access a restricted page

### 6.2 Navigation Structure
- Main menu items and their hierarchy
- How navigation changes based on user role
- Breadcrumb or back-navigation patterns

### 6.3 Notifications & Communications
- What emails or notifications the system sends
- When they are triggered
- Who receives them

### 6.4 Search & Filtering
- What can be searched
- What filters are available
- How results are displayed

### 6.5 Export & Download
- What data can be exported
- Available formats (PDF, CSV, Excel)
- Any limitations

### 6.6 Audit & History
- What actions are tracked
- Whether users can view history/audit logs

---

## 7. Business Rules Summary

Consolidate all business rules from Section 5 into a single reference table:

| Rule ID | Module | Rule Description |
|---------|--------|-----------------|
| BR-[Module]-001 | [Module] | [Rule] |

---

## 8. Assumptions & Constraints

### Assumptions
Things inferred from the code that have not been explicitly confirmed by a stakeholder. Each assumption should be flagged for validation.

| ID | Assumption | Confidence | Needs Validation |
|----|-----------|------------|-----------------|
| A-001 | [What was assumed] | High / Medium / Low | Yes / No |

### Constraints
Limitations discovered in the code that affect the user experience.

Example:
- The system supports English language only (no multi-language support detected)
- File uploads are limited to [X] MB (if discoverable from config)
- The system requires an active internet connection (no offline capability detected)

---

## 9. Glossary

| Term | Definition |
|------|-----------|
| [Business term found in code] | [Plain English definition] |

Include terms that might be unfamiliar to a new team member. Source these from entity names, enum values, and field labels.

---

## 10. Appendix: Feature-to-Screen Map

Quick-reference for navigating the system:

| Feature | Screen / Page | Module | Roles |
|---------|--------------|--------|-------|
| [What the user does] | [Screen name] | [Module] | [Who can do it] |

---

## Writing Style Rules for This Template

1. **Active voice, present tense.** "The user submits the form" not "The form is submitted by the user"
2. **Specific, not vague.** "Maximum 50 characters" not "limited length"
3. **Business language.** "Customer record" not "customer_record entity" 
4. **User as subject.** Start sentences with "The user...", "The administrator...", "The system displays..."
5. **Testable statements.** Every requirement should be verifiable. If you cannot imagine a test for it, rewrite it.
6. **No internal references.** Never mention file names, class names, method names, database tables, or API paths.
