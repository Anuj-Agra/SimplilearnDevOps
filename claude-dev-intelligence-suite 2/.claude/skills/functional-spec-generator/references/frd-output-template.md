# Functional Requirements Document — Output Template

Follow this structure exactly. Every section must appear. Write "Not applicable — [reason]"
only if a section genuinely has no content after thorough code analysis.

---

## COVER PAGE

```
FUNCTIONAL REQUIREMENTS DOCUMENT

System Name:   [Business name of the system]
Version:       1.0 — Draft
Date:          [Today's date]
Prepared by:   AI-assisted analysis — requires human review and sign-off
Reviewed by:   [Leave blank]
Approved by:   [Leave blank]
```

---

## DOCUMENT CONTROL

| Version | Date | Changed by | Change Description |
|---------|------|------------|--------------------|
| 1.0 | [Date] | AI-assisted | Initial FRD generated from codebase analysis |

---

## TABLE OF CONTENTS

(Auto-generated from headings)

---

# 1. Introduction & Purpose

## 1.1 What is this system?

Write 1 paragraph. One sentence on what the system is. One sentence on who it is for.
One sentence on the primary problem it solves.

**Tone**: "A new product owner walking in on their first day would read this and
immediately understand what this system is for."

Example paragraph:
> The [System Name] is a web-based platform used by [primary user group] to [primary
> function]. It enables [organisation name] to [key business capability] without
> [the problem it replaces or removes]. The system serves [X] distinct user types
> and covers [N] major functional areas.

## 1.2 Business Problem Solved

1–2 paragraphs. What was difficult or impossible before this system existed?
What manual process does it replace or support? What business outcome does it enable?

## 1.3 Who Uses This System?

One sentence listing each user type (not technical role names — business names).
Example: "The system is used by Customer Service Agents, Operations Managers,
Finance Approvers, and System Administrators."

---

# 2. Project Scope

## 2.1 In Scope

Everything the system currently does, grouped by functional area. One bullet per
capability group. Write these as plain English statements of capability.

- **[Functional Area]:** [List of capabilities as a comma-separated sentence]
- **[Functional Area]:** [List of capabilities]

Example:
- **Customer Management:** Creating new customer accounts, editing customer details,
  viewing account history, and suspending or reactivating accounts
- **Order Processing:** Creating, editing, submitting, and cancelling orders; tracking
  order status through its full lifecycle; viewing order history

## 2.2 Out of Scope

Explicitly state what the system does NOT do. This is as important as what it does do.
Infer from absence in code — if it isn't there, it's out of scope.

Write at minimum 3–5 items. Examples:
- The system does not process payments directly; payment status is updated manually
  or by an external system
- The system does not provide mobile-specific layouts; it is designed for desktop use
- There is no built-in reporting dashboard; data export is available for external analysis
- The system does not manage [X] — this is handled by [external system/process]

---

# 3. User Roles & Personas

## 3.1 Roles Summary

| Role Name | Description | Access Level | Key Permissions |
|-----------|-------------|--------------|-----------------|
| [Business role name] | [1-sentence description of who this person is] | Full / Limited / Read-only | [Comma-separated list of what they can do] |

**Note**: Use business role names, not technical names.
Map: `ROLE_ADMIN` → "System Administrator" | `ROLE_USER` → "Standard User" |
`ROLE_MANAGER` → "Manager" | `ROLE_READ_ONLY` → "Viewer"

## 3.2 Role Personas

For each role, write 2–3 sentences describing a typical person in that role.

**[Role Name]**
> [Name a typical person, e.g. "Sarah is a Customer Service Agent..."] She uses the
> system [how frequently] to [primary tasks]. Her most common actions are [top 3 things
> she does]. She needs to [key goal] without [key friction point she experiences].

---

# 4. User Stories & Use Cases

## 4.1 User Stories

Group by module/functional area. Write one per distinct user action.

**Format**: *As a [role], I want to [action] so that [benefit].*

### [Module Name]
- As a [role], I want to [action] so that [benefit].
- As a [role], I want to [action] so that [benefit].

*(Repeat for every module)*

## 4.2 Use Cases

Write a full use case for every significant multi-step workflow.
Minor CRUD operations (view a list, edit a single field) do not need full use cases.

### UC-[MOD]-[###]: [Use Case Name]

| Field | Detail |
|---|---|
| **Actor** | [Role name] |
| **Goal** | [One sentence — what they are trying to accomplish] |
| **Preconditions** | [What must be true before this starts] |
| **Trigger** | [What causes the user to start this] |

**Main Flow** (what happens when everything goes right):

1. The [role] navigates to [screen name — business name].
2. The system displays [what they see].
3. The [role] [action — fills in / selects / clicks].
4. The system [validates / checks / processes].
5. The system [result — saves / sends / displays].
6. The system displays [success confirmation message or next screen].

**Alternate Flows** (what can go wrong or differ):

- **4a** — If a required field is empty: The system highlights the field in red and
  displays "[exact or close wording of error message]." The user corrects the field
  and resubmits.
- **4b** — If [business rule fires]: The system displays "[message]." The user
  [resolution].
- **2a** — If the user does not have permission: The system redirects to the home page
  and displays "You do not have permission to access this page."

**Postcondition**: [What is now true after successful completion]

*(Repeat for every significant workflow)*

---

# 5. Functional Requirements

One FR statement per feature. Numbered for traceability.

**Format**: **FR-[MOD]-[###]**: The system **shall** [action] [condition/trigger].

Group by module:

## FR: [Module Name]

| Requirement ID | The system shall... |
|---|---|
| **FR-[MOD]-001** | [Observable action] [when/if condition]. |
| **FR-[MOD]-002** | [Observable action] [when/if condition]. |

**Writing rules**:
- "The system shall" starts every statement — never "The user shall"
- Describe the result the user experiences — not how the system achieves it
- Every statement must be independently testable by QA
- Use only "shall" / "must" — never "should", "may", "could"

**Examples of good FR statements**:
- The system **shall** display the order reference number on a confirmation screen
  immediately after an order is successfully submitted.
- The system **shall** prevent submission of a form if any field marked as mandatory
  is empty, and shall highlight each empty mandatory field in red.
- The system **shall** lock a user account after 5 consecutive failed login attempts
  and display a message directing the user to contact an administrator.
- The system **shall** automatically sign out users who have been inactive for
  30 consecutive minutes and shall display a session-expiry notification.

---

# 6. UI/UX — Screens & Navigation

## 6.1 Navigation Structure

Describe the main menu and navigation hierarchy as the user experiences it.

**Main navigation items** (as labelled in the application):
- [Menu item 1] → leads to [screen/section]
- [Menu item 2] → leads to [screen/section]

**Navigation varies by role**:
- [Role A] sees: [list of menu items]
- [Role B] sees: [list of menu items]

## 6.2 Screen Descriptions

One entry per screen/page in the application.

### [Screen Business Name]

| Field | Detail |
|---|---|
| **Access** | [Which roles can reach this screen] |
| **Purpose** | [One sentence — what the user accomplishes here] |
| **How to get here** | [Previous screen or menu item] |
| **Where to go next** | [After completing the primary action] |

**What the user sees**:
- [Describe the main sections or panels visible on the page]
- [List form fields with their labels exactly as shown to the user]
- [Describe tables with column headings as shown]
- [List buttons with their labels]
- [Note any read-only information panels]
- [Note any filters, search bars, or sorting options]

**Key interactions**:
- When the user clicks "[Button label]": [describe what happens]
- When the user types in the search bar: [describe result]
- When the user selects a row in the table: [describe what opens]
- Before [destructive action]: The system asks the user to confirm with the message
  "[confirmation message wording]"

*(Repeat for every screen in the application)*

---

# 7. Data Requirements

## 7.1 Data Entities

For each major piece of information the system manages, document what it captures.

### [Entity Plain English Name, e.g. "Customer Record"]

**Purpose**: [What this information is used for, in one sentence]

| Field Name | Required | Format | Allowed Values | Example |
|------------|----------|--------|----------------|---------|
| [Plain English name] | Yes / No | [Text max 100 chars / Date / Whole number / Decimal / Yes-No / Selection] | [Any / list of options] | [Example value] |

**Notes**: [Any important rules about this data as a whole, e.g. "Only one active
record per customer is permitted."]

*(Repeat for every entity)*

## 7.2 Data Display Rules

Where the system shows calculated or derived information to the user:

| Displayed Value | How It Appears | Notes |
|---|---|---|
| [What the user sees] | [How it is formatted/presented] | [Any conditions on display] |

---

# 8. Business Rules

## 8.1 Rules by Module

### [Module Name]

| Rule ID | Rule | Condition | What the User Experiences | How to Test |
|---------|------|-----------|---------------------------|-------------|
| **BR-[MOD]-001** | [Plain English statement] | [When does this apply?] | [What the user sees/can't do] | [Test scenario] |

**Examples of well-written business rules**:

| Rule ID | Rule | Condition | What the User Experiences | How to Test |
|---|---|---|---|---|
| BR-ORD-001 | An order cannot be submitted if its total value is zero | User clicks "Submit Order" | System displays: "Order must contain at least one item with a quantity greater than zero." | Create an order with no items and click Submit |
| BR-ORD-002 | Orders exceeding £10,000 require manager approval before processing | Order total exceeds £10,000 | Order status changes to "Pending Approval" and the manager receives an email notification | Submit an order for £10,001 |
| BR-USR-001 | A user cannot be assigned a role higher than the role of the user making the change | Admin attempts to assign a role | Roles higher than the current user's own level are shown as disabled | Log in as Supervisor and attempt to assign Administrator role |

## 8.2 Status Lifecycle Rules

For each entity that has a status or state:

### [Entity Name] Status Lifecycle

```
[Status A] → [Status B] → [Status C]
                ↓
           [Status D]
```

| From Status | To Status | Who Can Change It | Condition |
|---|---|---|---|
| [Status A] | [Status B] | [Role] | [When/why] |

---

# 9. Error Handling

## 9.1 Validation Errors (Missing or Invalid Input)

| Scenario | Field(s) Affected | Message Shown to User | Resolution |
|---|---|---|---|
| [Plain English description] | [Field name as shown in UI] | "[Exact or close wording]" | [What the user should do] |

## 9.2 Permission Errors

| Scenario | Message Shown to User | Resolution |
|---|---|---|
| User tries to access a page they cannot see | "You do not have permission to access this page." | Contact an administrator |
| User tries to perform an action they cannot do | "[Specific message if different]" | [Resolution] |

## 9.3 Business Rule Violations

| Scenario (business rule that fired) | Message Shown to User | Resolution |
|---|---|---|
| [Plain English of the rule that was violated] | "[Message]" | [What to do] |

## 9.4 System & Connectivity Errors

| Scenario | Message Shown to User | Resolution |
|---|---|---|
| The system cannot complete a request due to a temporary problem | "[Message wording]" | [e.g. "Wait and try again"] |
| The user's session has expired | "[Session expiry message]" | Log back in |
| A record the user is looking for does not exist | "[Not found message]" | [Resolution] |
| The user tries to create something that already exists | "[Duplicate message]" | [Resolution] |

---

# 10. Assumptions & Constraints

## 10.1 Assumptions

Things inferred from the code that must be confirmed by a stakeholder before the FRD
is treated as final.

| ID | Assumption | Confidence | Requires Validation |
|----|-----------|------------|---------------------|
| A-001 | [What was assumed] | High / Medium / Low | Yes / No |

## 10.2 Constraints

Limitations discovered in the code that affect what users can do.

| ID | Constraint | Impact on Users |
|----|-----------|-----------------|
| C-001 | The system supports the English language only | Users who require other languages are not served |
| C-002 | [File upload limit, if found in config] | Users cannot upload files larger than [X] MB |
| C-003 | [Session timeout, if found] | Users are automatically signed out after [N] minutes of inactivity |

## 10.3 External Dependencies

Systems or services the application relies on that are outside this system's scope:

| External System / Service | What This System Relies on It For |
|---|---|
| [Name] | [What it does for this system, in plain language] |

---

# 11. Glossary

Business and domain terms used in this document that a new team member may not know.

| Term | Definition |
|---|---|
| [Term as used in the system] | [Plain English definition] |

---

# 12. Appendix: Feature-to-Screen Map

Quick reference: what can I do, and where?

| What the user can do | Screen name | Section reference | Who can do it |
|---|---|---|---|
| [Feature description] | [Screen business name] | FR-[MOD]-[###] | [Role(s)] |

---

## WRITING STYLE RULES

Enforce these throughout every section of the document:

1. **Active voice, present tense.** "The system displays" not "is displayed by the system"
2. **User as actor.** "The user submits", "The manager approves", "The administrator resets"
3. **Specific, never vague.** "Maximum 100 characters" not "limited length"
4. **Business language.** "Customer record" not "customer_record entity"
5. **Testable statements.** Every FR shall can be verified by a QA tester
6. **No internal references.** No file names, class names, table names, API paths, HTTP methods
7. **No tech jargon.** If in doubt, remove it

**BANNED WORDS AND PHRASES** — if these appear, rewrite:
- Technical: REST, API, HTTP, POST, GET, JSON, XML, JWT, OAuth, cron, batch,
  entity, repository, service layer, Spring, Angular, Java, SQL, database, table,
  column, endpoint, boolean, null, enum, String
- Vague: fast, quickly, efficiently, robust, scalable, secure, reliable,
  intuitive, user-friendly, large number, many, several, various, etc.
- Weak modal verbs: should be able to, may, might, could (replace with "shall" or remove)
