---
name: functional-spec-generator
description: >
  Reverse-engineer a comprehensive, non-technical Functional Requirements Document (FRD)
  from an existing Java backend and/or Angular frontend codebase — accelerated by
  repo-graph.json when available. Use this skill whenever a product owner, business
  analyst, or stakeholder wants to know what a system does from a user's perspective.
  Triggers: 'create FRD', 'write functional spec', 'document the system', 'what does
  this module do', 'generate requirements', 'user stories from code', 'extract business
  rules', 'document this module', 'feature list', 'scope document', 'product spec'.
  Works for whole codebases, specific modules, or sub-modules. Output is a professional
  Word .docx covering all 10 required sections. ALWAYS use repo-graph.json if it exists
  in the working directory — it eliminates the need to re-scan the codebase structure.
---

# Functional Specification Generator (FRD) — Graph-Accelerated

Produce a complete, professional **Functional Requirements Document** written entirely
in business language. No technical terms. No code references. Readable by a product
owner who has never seen the code.

---

## The Golden Rule

Every sentence must pass: *"Would a non-technical product owner understand this and
verify it by watching someone use the system?"* If no — rewrite or remove it.

---

## Step 0 — Graph Check FIRST

**Before scanning any code**, check if `repo-graph.json` exists:

```bash
ls -la repo-graph.json 2>/dev/null || echo "NO GRAPH"
```

### If repo-graph.json EXISTS → Graph-Accelerated Mode

Use the graph to skip directory scanning entirely. The graph already contains the
complete module structure, dependencies, and metrics.

```bash
# Load the module index (all module names — near zero tokens)
python3 scripts/project_graph.py --graph repo-graph.json --mode index

# Get the subtree for the target scope
python3 scripts/project_graph.py --graph repo-graph.json --mode subtree --node <scope>

# Get critical modules (high fan-in = widely used = important to document well)
python3 scripts/project_graph.py --graph repo-graph.json --mode critical --top 10

# Get dead modules (do NOT write FRD sections for dead code)
python3 scripts/project_graph.py --graph repo-graph.json --mode dead
```

From the graph projection, extract:
- **Module inventory** — all modules in scope, their LOC, file count
- **Integration map** — which modules talk to which (edges = integration points in FRD)
- **Dead modules** — skip these in the FRD (flag them in Section 10 Assumptions)
- **Critical modules** — prioritise these for deepest documentation
- **Module parent/child hierarchy** — maps to Section 2 (Scope) structure

Then go directly to **Step 3** (skip Step 1 directory survey — already done by graph).

### If NO repo-graph.json → Standard Mode

Proceed with Step 1 (full directory reconnaissance) below.

---

## Step 0b — Scope Clarification

Ask the user ONCE:
1. **Scope** — Whole system? A module? A sub-module?
2. **Code paths** — Java backend path, Angular frontend path
3. **Known roles** — User types they can name, or discover from code
4. **System name** — Business name of the product

---

## Step 1 — Reconnaissance (Standard Mode — skip if graph available)

### 1a. Directory Survey

```bash
find <codebase_path> -maxdepth 3 -type d | sort | head -80
find <codebase_path> -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
```

### 1b. Java Backend — High-Signal Scans

```bash
# Every feature the system exposes
grep -rn "@RestController\|@Controller\|@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@PatchMapping" \
  <java_path> --include="*.java" -l

# User roles and access rules
grep -rn "ROLE_\|hasRole\|@PreAuthorize\|@Secured\|@RolesAllowed\|GrantedAuthority" \
  <java_path> --include="*.java" | head -60

# Field validation rules
grep -rn "@NotNull\|@NotBlank\|@Size\|@Min\|@Max\|@Pattern\|@Email\|@Future\|@Past\|@Positive" \
  <java_path> --include="*.java" | head -100

# State / status enums
grep -rn "enum " <java_path> --include="*.java" -l | head -20

# Business rule violations
grep -rn "@ExceptionHandler\|@ControllerAdvice\|BusinessException\|ResponseStatus\|HttpStatus\." \
  <java_path> --include="*.java" | head -80

# Scheduled/background processes
grep -rn "@Scheduled\|cron\|fixedDelay" <java_path> --include="*.java" | head -20

# Email templates
find <java_path> -name "*.html" -o -name "*.ftl" | grep -i "mail\|notif\|template" | head -10
```

### 1c. Angular Frontend — High-Signal Scans

```bash
# All screens (the sitemap)
grep -rn "path:\|component:\|canActivate:\|children:" \
  <angular_path> --include="*.ts" | grep -i "rout" | head -100

# Access control per screen
grep -rn "canActivate\|AuthGuard\|RoleGuard\|*ngIf.*role\|hasPermission" \
  <angular_path> --include="*.ts" --include="*.html" | head -60

# Form fields and validation
grep -rn "FormGroup\|FormControl\|Validators\.\|required\|minLength\|maxLength" \
  <angular_path> --include="*.ts" | head -80

# User-visible messages
grep -rn "snackBar\|toast\|MatSnackBar\|errorMessage\|successMessage" \
  <angular_path> --include="*.ts" --include="*.html" | head -60

# i18n labels
find <angular_path> -name "en.json" -o -name "messages.json" | head -5
```

---

## Step 2 — Feature Inventory

Build this table from graph data (preferred) or from Step 1 scans:

| Module (business name) | Feature | Who | Screen | Key fields | Business rules | Success | Errors |
|---|---|---|---|---|---|---|---|

**Module naming — always translate to business English:**
- `com.app.auth` → "User Authentication"
- `com.app.order` → "Order Management"
- `com.app.product` → "Product Catalogue"
- `com.app.report` → "Reporting"
- `com.app.admin` → "Administration"

**When graph is available**, populate this table from the subtree projection's
node labels + path structure instead of directory scanning.

---

## Step 3 — Deep-Dive: Extract All 10 Sections

Work through each module. For each extract:

### 3A — User Stories & Use Cases (Section 4)
**User story format**: *"As a [role], I want to [action] so that [benefit]."*

**Full use case** for every multi-step workflow:
```
USE CASE: [Name]
Actor:         [Role]
Goal:          [What they're trying to achieve]
Preconditions: [What must be true first]

Main Flow:
  1. The [role] navigates to [screen name].
  2. The system displays [what they see].
  3. The [role] [fills in / selects / clicks].
  4. The system validates.
  5. The system [processes/saves/sends].
  6. The system confirms: "[success message]".

Alternate Flows:
  4a. Required field missing → field highlighted, "[error message]"
  4b. Business rule fires → "[specific error message]"
  2a. No permission → "You do not have permission to access this page."

Postcondition: [What is true after success]
```

### 3B — Functional Requirements (Section 5)
Format: **FR-[MOD]-[###]**: The system **shall** [observable action] [condition].
- "shall" only — never "should", "may", "might"
- Testable by QA without code access

### 3C — Screen Descriptions (Section 6)
```
SCREEN: [Business name]
Access:  [Roles]  |  Purpose: [One sentence]
Arrived from: [Previous screen]  |  Leads to: [Next screen]
What the user sees: [panels, form fields with labels, table columns, buttons]
Key interactions: [what happens when user clicks each main action]
Confirmation dialogs: [any "are you sure?" prompts]
```

### 3D — Data Requirements (Section 7)
Per entity: field name in plain English, required yes/no, format/length, allowed values, example.
Map: String→Text, Integer→Whole number, BigDecimal→Decimal, Boolean→Yes/No, LocalDate→Date, enum→"Selection: A, B, C"

### 3E — Business Rules (Section 8)
```
BR-[MOD]-[###]: [Rule in plain English]
Condition:    [When it fires]
Effect:       [What the user experiences]
Testable by:  [Specific test scenario]
```

### 3F — Error Handling (Section 9)
Categories: validation, permission, business rule violation, not found, duplicate, system unavailable, session expired.
For each: scenario | what user sees | message wording | resolution.

### 3G — Assumptions & Constraints (Section 10)
Dead modules from graph → "Module X appears unused — flagged for confirmation"
Missing features → out-of-scope items
Config limits → constraints

---

## Step 4 — Assemble Document

Read `references/frd-output-template.md` and follow its 12-section structure exactly.

**When graph data is available**, enrich the document with:
- **Section 2 (Scope)**: use graph's `totalModules`, `totalEdges` for the scope summary
- **Section 4 (Use Cases)**: cross-reference integration edges as integration steps in use case flows
- **Section 10 (Assumptions)**: list dead modules from graph as "flagged for removal confirmation"
- **Appendix**: add a module dependency summary from the graph's critical nodes

---

## Step 5 — Generate Word Document

Read `/mnt/skills/public/docx/SKILL.md` and produce `.docx`.

---

## Step 6 — Quality Gate

### Completeness
- [ ] All 10 sections present
- [ ] Every module in scope (from graph or scan) has Section 5 + 6 entries
- [ ] Every role in roles table + at least one user story
- [ ] Every screen has a description in Section 6
- [ ] Every mandatory field has a data requirement
- [ ] Every BR is numbered and has a test scenario
- [ ] Every error has a user-visible message
- [ ] Section 2 has ≥3 explicit out-of-scope items
- [ ] Dead modules (from graph) flagged in assumptions

### Anti-jargon (BANNED — rewrite immediately if found)
REST, API, HTTP, POST, GET, JSON, JWT, database, table, column, entity, repository,
service layer, Spring, Angular, Java, SQL, cron, batch, boolean, null, enum, String,
fast, robust, scalable, secure, user-friendly, large number, should be able to, may, might

---

## Large Codebase Strategy

1. Use graph index to get all modules (1 projection, ~2,000 tokens)
2. Present module list to user — ask which 3–5 to prioritise
3. Load subtree projection per selected module (3,000 tokens each)
4. Deep-dive one module at a time
5. After every 2 modules, pause and check detail level is right
