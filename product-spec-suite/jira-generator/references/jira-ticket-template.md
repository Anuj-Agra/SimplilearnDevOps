# JIRA Ticket Template

The exact format for every generated ticket, with two complete worked examples.

---

## Full Ticket Structure

```markdown
---

## [EPIC/STORY]: [Action Verb] + [Specific Feature/Function] + [Target Area]

**Type:** Epic / Story
**Priority:** Critical / High / Medium / Low
**Module(s):** [Module name(s)]
**Labels:** [If user specified any]

---

### 📋 What Currently Exists

[Describe the current state of the system in the area this ticket affects.
This section provides essential context and prevents misunderstandings.

If spec is available:
"The [module] currently supports [existing capabilities]. Users can [existing actions].
The current business rules are: [reference BR-IDs]. The [screen name] screen
currently displays [existing fields/elements]. (See: modules/[mod]/02-screen-descriptions.md)"

If code was analysed:
"The system currently [observed behaviour in user language].
The [screen/area] currently [what it shows/does]."

If neither:
"Based on the requirement context: [what we understand about current state].
Note: Current state should be verified by the development team before implementation."]

---

### 🧑 1. User Story

As a **[type of user]**,
I want **[some goal/action]**,
So that **[reason/benefit — must be a real business outcome, not a restatement of the action]**.

---

### 📈 2. Business Impact & Motivation

**Problem Statement:**
[What pain point or gap does this solve? Reference "What Currently Exists" to
explain what's missing or broken. Be specific — "Currently, managers must manually
approve every order above £10,000, creating a 2-day delay for routine purchases."]

**Value:**
[Why is this worthwhile now? Quantify where possible.
e.g., "Reduces approval bottleneck by ~60%, freeing manager time for strategic reviews."
e.g., "Enables self-service for 80% of customer queries currently handled by support."
If no data available, state the qualitative benefit and flag: "(Estimate — to be validated)"]

**Measurable Signal:**
[How will we know this was successful? Define a concrete metric.
e.g., "90% of orders under £25,000 are processed within 1 hour of submission."
e.g., "Support tickets for password reset drop by 50% within 30 days of launch."
e.g., "Export feature used by at least 20 unique users per week within first month."]

---

### ✅ 3. Acceptance Criteria

**Scenario 1: [Happy Path — Title]**
- **Given** [pre-condition — user role, system state, data state]
- **When** [user action — what they click, enter, submit]
- **Then** [expected outcome — what the system does, what the user sees]
- **And** [additional expected behaviour if needed]

**Scenario 2: [Alternate Happy Path — Title]** (if applicable)
- **Given** [different pre-condition]
- **When** [action]
- **Then** [expected outcome]

**Scenario 3: [Negative / Edge Case — Title]**
- **Given** [invalid state, boundary condition, or error-producing condition]
- **When** [action]
- **Then** [error handling behaviour — what message appears, what does NOT happen]

**Scenario 4: [Permission Check — Title]** (if role-based)
- **Given** I am logged in as a **[role that should NOT have access]**
- **When** I attempt to [action]
- **Then** the system displays "[permission denied message]"
- **And** the [action] is not performed

**Scenario 5: [Boundary Condition — Title]** (if applicable)
- **Given** [exact boundary value — e.g. "the order total is exactly £25,000"]
- **When** [action]
- **Then** [expected behaviour at the boundary]

**Non-Functional Criteria:** (include when relevant)
- Performance: [e.g., "The export completes within 5 seconds for up to 1,000 records"]
- Security: [e.g., "Exported CSV does not include sensitive fields (SSN, payment details)"]
- Accessibility: [e.g., "All new form fields have associated labels for screen readers"]

---

### 🎨 4. Design & Interaction

**Design Link:** [Figma/Design Link: To be added]

**User Flow:**
1. User navigates to [starting screen] via [navigation path]
2. User [action on screen — what they see, what they click]
3. System [response — what appears, what changes]
4. User [next action]
5. System [final outcome — confirmation, redirect, download, etc.]

**Key UI Elements:**
- [New button/field/section and its location on the screen]
- [Changes to existing UI elements]
- [Modal/dialog/toast behaviour]

---

### 🛠 5. Functional & Developer Notes

**Validations:**
| Field | Rule | Error Message |
|-------|------|---------------|
| [Field name] | [e.g., Required, Max 100 chars, Email format, Must be future date] | "[Message shown to user]" |

**Data Requirements:**
| Field | New/Modified | Required | Format / Constraints | Allowed Values |
|-------|-------------|----------|---------------------|----------------|
| [Name] | New / Modified | Yes / No | [e.g., "Max 255 chars", "Decimal, 2 places"] | [e.g., "Active, Inactive" or "Any"] |

**Business Rule Changes:**
| Rule | Current | Proposed |
|------|---------|----------|
| [BR-ID or description] | [What it is today] | [What it becomes] |

**Blockers / Dependencies:**
- Depends on: [Linked ticket key or external system]
- Blocked by: [Anything that must happen first]
- Related: [Tickets covering adjacent areas]

**Affected Spec Sections:** (only if spec exists)
| File | Change |
|------|--------|
| `modules/[mod]/01-user-stories.md` | Add: US-[MOD]-NNN |
| `modules/[mod]/03-business-rules.md` | Modify: BR-[MOD]-NNN |

---

### 🚫 6. Out of Scope

- [What this ticket will NOT include — be explicit]
- [Adjacent feature that belongs in a separate ticket]
- [Edge case intentionally deferred]
- [Platform/device not covered]

---
```

---

## Example 1: Spec-Enriched Ticket (Existing Spec Available)

```markdown
---

## STORY: Raise Approval Threshold for High-Value Purchase Orders

**Type:** Story
**Priority:** High
**Module(s):** Order Management
**Labels:** order-workflow

---

### 📋 What Currently Exists

The Order Management module currently routes all orders exceeding £10,000 to the
Manager's approval queue. The approval workflow has three states: Submitted →
Pending Approval → Approved/Rejected (see BR-ORD-003 in modules/order-management/
03-business-rules.md). The Pending Approvals screen shows a queue of orders
awaiting manager review, with order details, submitter name, and total amount.
Managers can approve or reject with a comment. Sales Representatives must wait
for approval before the order progresses to fulfilment. On average, 45 orders
per week enter the approval queue. (See: modules/order-management/02-screen-
descriptions.md, Pending Approvals section.)

---

### 🧑 1. User Story

As a **Sales Representative**,
I want **orders under £25,000 to be processed without manager approval**,
So that **routine purchase orders are fulfilled faster, reducing the average
processing time from 2 days to same-day for mid-range orders**.

---

### 📈 2. Business Impact & Motivation

**Problem Statement:**
Currently, all 45 weekly orders above £10,000 require manual manager approval,
creating a 1-2 day bottleneck. Analysis shows that 72% of these orders (those
between £10,000 and £25,000) are routine and have never been rejected.

**Value:**
Eliminates the approval bottleneck for ~32 orders per week, reducing average
processing time from 2 days to under 1 hour for orders in the £10,000-£25,000
range. Frees approximately 3 hours/week of manager time currently spent on
routine approvals.

**Measurable Signal:**
- Orders between £10,000 and £25,000 processed within 1 hour of submission
  (target: 90% within first month)
- Manager approval queue volume drops by ~70%
- No increase in order rejection rate for orders above £25,000

---

### ✅ 3. Acceptance Criteria

**Scenario 1: Mid-range order proceeds without approval**
- **Given** I am logged in as a Sales Representative
- **When** I submit an order with a total of £15,000
- **Then** the order proceeds directly to "Confirmed" status
- **And** no approval request is created in the Manager's queue
- **And** I see a confirmation message: "Order confirmed and sent to fulfilment"

**Scenario 2: High-value order still requires approval**
- **Given** I am logged in as a Sales Representative
- **When** I submit an order with a total of £30,000
- **Then** the order status changes to "Pending Approval"
- **And** the order appears in the Manager's Pending Approvals screen
- **And** I see the message: "Order submitted for manager approval"

**Scenario 3: Boundary — exact threshold value**
- **Given** I am logged in as a Sales Representative
- **When** I submit an order with a total of exactly £25,000.00
- **Then** the order proceeds directly to "Confirmed" status without approval

**Scenario 4: Boundary — one penny above threshold**
- **Given** I am logged in as a Sales Representative
- **When** I submit an order with a total of £25,000.01
- **Then** the order status changes to "Pending Approval"

**Scenario 5: Orders below original threshold unaffected**
- **Given** I am logged in as a Sales Representative
- **When** I submit an order with a total of £5,000
- **Then** the order proceeds directly to "Confirmed" status
- (This behaviour should remain unchanged from current)

**Non-Functional:**
- No perceptible delay in order submission time after threshold change

---

### 🎨 4. Design & Interaction

**Design Link:** [Figma/Design Link: To be added]

**User Flow:**
1. Sales Representative creates an order on the Order Entry screen
2. Clicks "Submit Order"
3. System evaluates order total against the £25,000 threshold
4. If under £25,000: order moves to "Confirmed" → user sees confirmation
5. If £25,000 or above: order moves to "Pending Approval" → user sees
   approval notice
6. (Manager flow for high-value orders remains unchanged)

**Key UI Elements:**
- No visible UI changes — this is a threshold change in business logic
- Confirmation and approval messages remain in existing toast notification format

---

### 🛠 5. Functional & Developer Notes

**Validations:**
- No new validation rules — existing order total validation applies

**Data Requirements:**
- No new fields — existing order total field is used for threshold evaluation

**Business Rule Changes:**
| Rule | Current | Proposed |
|------|---------|----------|
| BR-ORD-003 | Orders exceeding £10,000 require manager approval | Orders exceeding £25,000 require manager approval |

**Blockers / Dependencies:**
- None identified
- Related: Finance team should be notified of policy change (outside this ticket)

**Affected Spec Sections:**
| File | Change |
|------|--------|
| `modules/order-management/03-business-rules.md` | Modify BR-ORD-003: threshold £10,000 → £25,000 |
| `reference/business-rules-master.md` | Sync BR-ORD-003 |

---

### 🚫 6. Out of Scope

- Changing the approval workflow itself (approve/reject flow remains the same)
- Adding a new approval tier (e.g., director approval for orders above £50,000)
- Modifying approval notification emails
- Backdating the threshold change to existing pending orders
- Audit logging of the threshold change itself

---
```

---

## Example 2: Standalone Ticket (No Spec, No Code)

```markdown
---

## STORY: Implement Bulk CSV Export for Customer Records List

**Type:** Story
**Priority:** Medium
**Module(s):** Customer Management

---

### 📋 What Currently Exists

Based on the requirement description: The Customer List screen currently displays
a paginated table of customer records. Individual records can be viewed in detail.
A single-record PDF export exists for individual customer profiles. There is no
capability to select multiple records or export them in bulk.

Note: Current state based on requirement context. The development team should
verify actual current behaviour before implementation.

---

### 🧑 1. User Story

As an **Administrator**,
I want **to select multiple customer records and export them as a CSV file**,
So that **I can perform offline analysis, create mail-merge lists, and share
customer data with external partners without manually copying records one by one**.

---

### 📈 2. Business Impact & Motivation

**Problem Statement:**
Administrators currently have no way to extract customer data in bulk. When they
need a list (e.g., for a marketing campaign or compliance audit), they must
manually open each record and copy information, which takes approximately 2 hours
for 100 records.

**Value:**
Reduces bulk data extraction from 2 hours to under 30 seconds for typical
exports. Enables new workflows: marketing campaigns, partner data sharing,
compliance reporting — all currently blocked by lack of export capability.

**Measurable Signal:**
- Bulk export feature used by at least 15 unique administrators per month
  within 60 days of launch
- Support tickets requesting "customer data extracts" drop by 80%

---

### ✅ 3. Acceptance Criteria

**Scenario 1: Successful bulk export of selected records**
- **Given** I am logged in as an Administrator on the Customer List screen
- **And** I have selected 5 customer records using the row checkboxes
- **When** I click the "Export Selected" button
- **Then** a CSV file downloads to my device
- **And** the file contains exactly 5 rows (plus header)
- **And** columns include: Customer Name, Email, Phone, Status, Created Date

**Scenario 2: Select All and export**
- **Given** I am on the Customer List screen displaying 25 records
- **When** I click the "Select All" checkbox in the table header
- **Then** all 25 visible records are selected (checkboxes ticked)
- **When** I click "Export Selected"
- **Then** a CSV file downloads containing all 25 records

**Scenario 3: No records selected (error)**
- **Given** I am on the Customer List screen
- **And** no records are selected
- **When** I click "Export Selected"
- **Then** the system displays a warning: "Please select at least one record to export"
- **And** no file is downloaded

**Scenario 4: Permission check — non-admin cannot export**
- **Given** I am logged in as a **Regular User**
- **When** I view the Customer List screen
- **Then** the row checkboxes are not visible
- **And** the "Export Selected" button is not visible

**Scenario 5: Deselect All**
- **Given** I have used "Select All" to select all records
- **When** I click the "Select All" checkbox again
- **Then** all records are deselected

**Scenario 6: Large export**
- **Given** I have selected 500 customer records (across multiple pages if paginated)
- **When** I click "Export Selected"
- **Then** the export completes and a CSV file downloads
- **And** the file contains exactly 500 data rows

**Non-Functional:**
- Performance: Export completes within 5 seconds for up to 1,000 records
- Performance: Export completes within 15 seconds for up to 10,000 records
- Security: Exported CSV must NOT include sensitive fields (payment details,
  SSN, internal notes) even if they appear on the detail screen
- Accessibility: Checkbox and "Export Selected" button are keyboard-navigable

---

### 🎨 4. Design & Interaction

**Design Link:** [Figma/Design Link: To be added]

**User Flow:**
1. Administrator navigates to Customer Management → Customer List
2. A new checkbox column appears as the first column of the table
3. A "Select All" checkbox appears in the table header row
4. User ticks individual rows or uses "Select All"
5. A counter appears above the table: "[N] records selected"
6. User clicks "Export Selected" button (located above the table, right-aligned)
7. Browser downloads a CSV file named `customers-export-[date].csv`
8. Selection remains after export (user can re-export or deselect)

**Key UI Elements:**
- Checkbox column: first column, before Customer Name
- "Select All" checkbox: in the header row of the checkbox column
- Selection counter: e.g., "12 records selected" — appears between the table
  header and the "Export Selected" button
- "Export Selected" button: right-aligned above the table, disabled state when
  nothing is selected

---

### 🛠 5. Functional & Developer Notes

**Validations:**
| Field/Action | Rule | Error Message |
|-------------|------|---------------|
| Export action | At least 1 record must be selected | "Please select at least one record to export" |
| CSV content | Sensitive fields excluded from export | N/A (no user message — fields simply omitted) |

**Data Requirements:**
| Field | In Export | Format |
|-------|----------|--------|
| Customer Name | Yes | Plain text |
| Email | Yes | Email format |
| Phone | Yes | Plain text |
| Status | Yes | "Active" / "Inactive" / "Suspended" |
| Created Date | Yes | DD/MM/YYYY |
| Payment Details | NO — excluded | N/A |
| Internal Notes | NO — excluded | N/A |

**Blockers / Dependencies:**
- None identified
- Related: If paginated selection across pages is needed (selecting records
  from page 1, then going to page 2 and selecting more), confirm whether
  selections persist across pages

---

### 🚫 6. Out of Scope

- Exporting in formats other than CSV (Excel, PDF) — separate ticket if needed
- Scheduled/recurring automated exports
- Custom column selection (user choosing which columns to include)
- Filtered export (exporting based on search/filter criteria without selection)
- Export of individual record detail view (already exists as single-record PDF)
- Mobile-optimised export experience

---
```

---

## Epic Format

```markdown
# EPIC: [Action Verb] + [Feature Area] + [Target Area]

**Type:** Epic
**Priority:** [Priority]
**Module(s):** [Modules]

---

## Epic Overview

### 📋 What Currently Exists
[Current state for the entire feature area]

### 📈 Business Impact
[Epic-level problem statement, value, and success signal]

### Stories in this Epic

| # | Summary | Priority |
|---|---------|----------|
| S1 | [Action Verb + Feature + Area] | High |
| S2 | [Action Verb + Feature + Area] | Medium |
| S3 | [Action Verb + Feature + Area] | Medium |

### 🚫 Epic-Level Out of Scope
[Boundaries for the entire epic — individual stories inherit these plus add their own]

---

## STORY S1: [Summary]

[Full 6-section ticket as above]

---

## STORY S2: [Summary]

[Full 6-section ticket as above]
```
