---
name: frd-deep-dive
description: "Generate a detailed, low-level Functional Requirements Document (FRD) for a single module by exhaustively analysing every file in the module's code. Produces granular 'the system shall...' statements, detailed data processing rules, complete workflow diagrams, input/output specifications, external interface requirements, and non-functional requirements. Goes far deeper than the spec-generator which produces high-level specs across many modules. Use this skill whenever the user asks for a 'detailed FRD', 'deep dive into a module', 'low-level functional requirements', 'exhaustive module analysis', 'granular requirements document', 'detailed system behaviour', or wants every function, field, validation, and workflow in a single module documented. Requires a specific module target — does not work for entire codebases."
---

# FRD Deep-Dive — Detailed Functional Requirements Document

Exhaustively analyse a **single module** and produce a granular Functional Requirements Document covering every function, field, rule, workflow, interface, and error state.

**Difference from spec-generator:** The spec-generator scans broadly and documents high-level user stories, screen summaries, and key business rules across many modules. This skill reads **every file** in one module and documents **every observable behaviour** at the lowest functional level — producing "the system shall..." statements that a QA team can directly convert into test cases.

---

## ZERO HALLUCINATION — Applies with Maximum Force

This skill produces granular, testable requirements. Fabricating even one "the system shall..." statement that doesn't exist in the code creates a false requirement that could waste development and QA effort.

> **Every "the system shall..." statement must trace to a specific code observation. Every field, validation rule, workflow step, and error message must have been directly read from the code. If you cannot find it in the code, do not write it. Ask the user.**

When the code is ambiguous about intent, write what the code does factually and tag it: `[Observed behaviour — business intent to be confirmed with stakeholder]`

---

## Step 0 — Scope the Module

### Auto-detect codebase root

```bash
CODEBASE_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
```

### Identify the target module

Ask the user which module to deep-dive. Then identify ALL code that belongs to this module:

```bash
# Find backend code for this module
find "$CODEBASE_ROOT" -type d -name "<module>" -not -path "*/node_modules/*" -not -path "*/test/*"

# Find frontend code for this module
find "$CODEBASE_ROOT" -type d -name "<module>" -path "*/app/*" -not -path "*/node_modules/*"
```

Confirm with the user: "I've identified these paths as belonging to the [Module Name] module: [list paths]. Is this correct, or are there other directories I should include?"

### Check for existing functional spec

```bash
ls "$CODEBASE_ROOT/functional-specs/modules/<module-name>/README.md" 2>/dev/null
```

If a high-level spec exists from the spec-generator, read it — it provides context and IDs to continue from. If not, this skill works standalone.

---

## Step 1 — Exhaustive Code Reading

Unlike the spec-generator which samples key files, this skill reads **every relevant file** in the module. This is a single module, so the file count is manageable.

### 1a. Build the complete file inventory

```bash
# All Java files in the module (excluding tests)
find <module-backend-path>/src/main -name "*.java" | sort

# All Angular files in the module (excluding tests/specs)
find <module-frontend-path>/src -name "*.ts" -o -name "*.html" -o -name "*.scss" -o -name "*.css" | grep -v ".spec.ts" | sort

# Config files
find <module-path> -name "*.yml" -o -name "*.yaml" -o -name "*.properties" -o -name "*.json" | grep -v node_modules | sort
```

### 1b. Read EVERY file in this order

**Backend — read ALL of these fully:**

1. **Every controller class** — Read line by line. Document every endpoint, every parameter, every return type, every annotation.
2. **Every service class** — Read line by line. Document every public method, every conditional branch, every calculation, every state change.
3. **Every entity/model class** — Read every field, every annotation, every relationship, every constraint.
4. **Every DTO/request/response class** — Read every field. These define the input/output contracts.
5. **Every enum** — Read every value. These define business states, types, categories.
6. **Every validator class** — Read every validation rule, custom validator, and error message.
7. **Every exception class and handler** — Read every exception type, message, and HTTP response mapping.
8. **Every repository/DAO** — Read custom query methods (named queries, @Query annotations) — these reveal data access patterns visible to users (search, filter, sort).
9. **Every config class in the module** — Read for timeouts, limits, feature flags, scheduled jobs.
10. **Every mapper/converter** — Read for data transformations that affect what users see.

**Frontend — read ALL of these fully:**

1. **Every component template (.html)** — Read every element, every binding, every *ngIf, every *ngFor, every (click), every form field.
2. **Every component class (.ts)** — Read every method, every property, every form definition, every service call.
3. **Every service (.service.ts)** — Read every HTTP call, every method, every data transformation.
4. **Every model/interface (.model.ts)** — Read every field definition.
5. **Every routing config** — Read every route, every guard, every resolver.
6. **Every guard** — Read access control logic.
7. **Every interceptor relevant to this module** — Read error handling, auth token injection.
8. **Every dialog/modal component** — Read confirmation flows, input forms.
9. **Every pipe/directive** — Read data display transformations (date formats, currency, etc.).
10. **i18n/translation entries for this module** — Read every label, message, error text.

### 1c. Read shared/common code used by this module

```bash
# Find imports from shared libraries
grep -rn "import.*shared\|import.*common\|import.*core" <module-path>/src --include="*.java" --include="*.ts" | grep -v test | sort -u
```

Read the specific shared classes that this module imports — they contribute validations, DTOs, and business rules.

---

## Step 2 — Generate the FRD

Output a single comprehensive document to `./functional-specs/modules/<module-name>/FRD-<module-name>.md`.

The document follows this exact structure. Read `references/frd-template.md` for the complete template.

### FRD Structure:

**1. Introduction**
- 1.1 Purpose — Why this document exists
- 1.2 Scope — What this module covers and does NOT cover
- 1.3 Definitions & Acronyms — Every business term found in this module
- 1.4 References — Links to related spec files if they exist

**2. System Overview**
- 2.1 Module Purpose — What this module does in business terms (1-2 paragraphs)
- 2.2 Context Diagram — Mermaid diagram showing how this module relates to other modules, external systems, and user roles
- 2.3 User Roles & Permissions — Every role with access, every permission, every restriction

**3. Functional Requirements**

This is the core section. For **every feature** in the module, generate:

- **FR-[MOD]-NNN: The system shall [specific behaviour].**
- Requirement ID, priority, source (which code file this was observed in — internal ref only)
- Input specification: what data enters this function
- Processing rules: what happens step by step
- Output specification: what the user sees or what data is produced
- Business rules that govern this function
- Error conditions and messages

Group requirements by feature area (e.g., "3.1 Order Creation", "3.2 Order Editing", "3.3 Order Approval").

**4. External Interface Requirements**
- 4.1 User Interfaces — Every screen described in full detail: layout, every field, every button, every table column, every filter, every sort option, every pagination control
- 4.2 Software Interfaces — Every API this module consumes (other modules, external services). Described as: what data goes out, what comes back, what the user sees as a result
- 4.3 Hardware Interfaces — Only if applicable (e.g., barcode scanner, printer)

**5. Data Requirements**
- 5.1 Logical Data Model — Every entity, every field, every relationship (described in business terms — "A Customer has many Orders", not "customer_id FK")
- 5.2 Data Dictionary — Every field: name, description, type (in plain English like "Text", "Number", "Date"), required/optional, format, allowed values, default, validation rules
- 5.3 Data Processing Rules — Every calculation, transformation, aggregation, and derivation the system performs. Written as numbered rules: "DPR-[MOD]-001: The system shall calculate the order total as the sum of (line item quantity × unit price) for all line items."

**6. Workflow Diagrams**
- Every user workflow as a Mermaid flowchart (read `references/mermaid-conventions.md` from spec-generator if available)
- Every entity state lifecycle as a Mermaid state diagram
- Every screen navigation flow as a Mermaid flowchart
- Every multi-role process showing handoffs between roles
- Decision trees for complex business rules

**7. Non-Functional Requirements** (only those observable from code)
- 7.1 Performance — Timeouts, pagination limits, batch sizes found in config
- 7.2 Security — Role-based access observed, field-level security, data masking
- 7.3 Audit & Logging — What actions create audit records (only if observed in code)
- 7.4 Data Retention — Soft delete vs hard delete patterns observed
- 7.5 Constraints — File upload limits, character limits, concurrent user limits (only from config)

Tag every NFR with `[Observed in config/code]` or `[To be confirmed — no evidence in code]`.

**8. Assumptions & Dependencies**
- 8.1 Assumptions — Everything inferred, with confidence level
- 8.2 Dependencies — External modules, services, or systems this module depends on
- 8.3 Open Questions — Everything ambiguous collected for the user

**Appendices**
- A. Complete Field Inventory — Every field across all screens and entities in one table
- B. Complete Error Message Inventory — Every error message the user can encounter
- C. Complete Business Rule Inventory — Every rule numbered and cross-referenced
- D. Requirement Traceability Matrix — FR-ID → Screen → Business Rule → AC mapping

---

## Step 3 — Requirement Writing Standards

### "The system shall..." format

Every functional requirement follows this structure:

```
**FR-[MOD]-NNN: The system shall [verb] [object] [condition/qualifier].**

- **Priority:** Must / Should / May
- **Input:** [What enters — fields, triggers, data]
- **Processing:** [Step-by-step what happens]
- **Output:** [What the user sees or what is produced]
- **Business Rules:** [BR-IDs that apply]
- **Error Conditions:** [What can go wrong and what happens]
- **Testable:** [Yes — describe how to verify]
```

### Requirement granularity

Each FR covers **one atomic behaviour**. Break complex features into multiple FRs:

Bad (too broad):
> FR-ORD-001: The system shall allow users to create orders.

Good (atomic):
> FR-ORD-001: The system shall display the Order Entry form when a Sales Representative clicks "New Order" on the Order List screen.
>
> FR-ORD-002: The system shall require the following fields on the Order Entry form: Customer Name (required, text, max 200 characters), Order Date (required, auto-populated with today's date, editable), Delivery Address (required, text, max 500 characters).
>
> FR-ORD-003: The system shall allow the user to add line items to the order, each consisting of: Product (required, dropdown from product catalogue), Quantity (required, positive integer, minimum 1), Unit Price (auto-populated from product catalogue, editable by Manager role only).
>
> FR-ORD-004: The system shall calculate and display the Order Total as the sum of (Quantity × Unit Price) for all line items, updated in real-time as items are added or modified.

### Data processing rules format

```
**DPR-[MOD]-NNN: The system shall [calculate/derive/transform] [what] as [formula/logic].**

Example:
DPR-ORD-001: The system shall calculate the line item subtotal as Quantity × Unit Price.
DPR-ORD-002: The system shall calculate the order total as the sum of all line item subtotals.
DPR-ORD-003: The system shall apply a 10% discount to the order total when the total exceeds £75 and the customer's loyalty tier is Gold or above.
```

---

## Step 4 — Generate Workflow Diagrams

For this deep-dive, generate **every workflow**, not just major ones.

### What to diagram:

1. **Every CRUD operation** as a workflow (Create, Read/Search, Update, Delete for each entity)
2. **Every state lifecycle** for every entity with states
3. **Every approval/review flow**
4. **Every search/filter flow** showing available filters, sort options, and result display
5. **Every import/export flow**
6. **Every notification trigger flow**
7. **Every error recovery flow** (what happens after an error — retry, redirect, etc.)
8. **The complete screen navigation map** for the module

### Diagram ID format:

```
WF-[MOD]-NNN    User workflow
SLC-[MOD]-NNN   State lifecycle
NAV-[MOD]-NNN   Navigation flow
DT-[MOD]-NNN    Decision tree (for complex business rules)
```

---

## Step 5 — Build Appendices

### A. Complete Field Inventory

Read every entity, every DTO, every form, and compile into one master table:

| Field ID | Field Name | Entity/Screen | Type | Required | Format | Validation | Default | Notes |
|----------|-----------|--------------|------|----------|--------|-----------|---------|-------|
| FLD-[MOD]-001 | Customer Name | Order Entry Form / Order Entity | Text | Yes | Max 200 chars | Not blank | — | Also displayed on Order List |

### B. Complete Error Message Inventory

| Error ID | Trigger | Message | Severity | Screen | Resolution |
|----------|---------|---------|----------|--------|-----------|
| ERR-[MOD]-001 | Order total is zero | "Order must contain at least one item" | Blocking | Order Entry | Add a line item |

### C. Complete Business Rule Inventory

| Rule ID | Rule | Trigger | Affected Screens | Affected FRs |
|---------|------|---------|-----------------|-------------|
| BR-[MOD]-001 | [Statement] | [When] | [Where] | FR-[MOD]-003, FR-[MOD]-007 |

### D. Requirement Traceability Matrix

| FR ID | Screen | Business Rules | Data Rules | Error Conditions | Testable |
|-------|--------|---------------|-----------|-----------------|---------|
| FR-[MOD]-001 | Order Entry | BR-[MOD]-001 | DPR-[MOD]-001 | ERR-[MOD]-003 | Yes |

---

## Step 6 — Write Output

Write the FRD to:
```
./functional-specs/modules/<module-name>/FRD-<module-name>.md
```

Also copy to `/mnt/user-data/outputs/` for download.

If the file would exceed ~3000 lines (very large module), split into multiple files:
```
./functional-specs/modules/<module-name>/
├── FRD-00-introduction.md
├── FRD-01-functional-requirements.md
├── FRD-02-interfaces.md
├── FRD-03-data-requirements.md
├── FRD-04-workflows.md
├── FRD-05-non-functional.md
├── FRD-06-appendices.md
└── FRD-index.md
```

---

## Asking Questions — Batch and Progress

For a deep-dive, you will encounter many ambiguities. Handle them efficiently:

1. **Read all code first** before asking any questions
2. **Collect ALL questions** across all sections
3. **Present them in one batch**, grouped by topic:

"I've completed the exhaustive code analysis for the [Module] module. Before I generate the FRD, I have [N] questions grouped by area:

**Business Rules (5 questions):**
1. [Question about observed logic]
2. ...

**Data Requirements (3 questions):**
1. [Question about field purpose]
2. ...

**Workflow (2 questions):**
1. [Question about incomplete flow]
2. ...

Please answer what you can, and mark anything you're unsure about as 'skip — flag as assumption'."

After receiving answers, generate the complete FRD.

---

## Quality Checklist

- [ ] Every FR is atomic — one behaviour per requirement
- [ ] Every FR is testable — QA can write a test case from it
- [ ] Every FR uses "The system shall..." language
- [ ] Every field in the data dictionary has: name, type, required, format, validation, allowed values
- [ ] Every workflow has a Mermaid diagram
- [ ] Every entity with states has a lifecycle diagram
- [ ] Every error message is documented with trigger and resolution
- [ ] Every business rule is numbered and cross-referenced to affected FRs
- [ ] The traceability matrix connects FRs → Screens → Rules → Errors
- [ ] No technical jargon in any requirement (except section 5 Dev Notes if applicable)
- [ ] All ambiguities flagged in Assumptions section
- [ ] Zero fabricated requirements — every statement traces to code
