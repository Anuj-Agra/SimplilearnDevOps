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

## Step 2B — Extract Front-to-Back Flows (NEW — run after Feature Inventory)

Before writing any FRD section, trace the complete front-to-back flows for
every significant user journey. These become Sections 4A and 4B in the document.

A **flow** is the complete path a user action takes from the UI button click
through every layer to storage and back — not just the frontend or backend alone.

### Flow Discovery

```bash
# Step 1: Find Angular entry points (where user actions originate)
grep -rn "\(click\)=\|mat-button\|routerLink\|\[formGroup\]\|ngSubmit" \
  <angular_path> --include="*.html" | head -40

# Step 2: Find the Angular service calls those components make
grep -rn "this\.[a-zA-Z]*[Ss]ervice\.\|\.subscribe\|\.pipe(" \
  <angular_path> --include="*.ts" | grep -v "//\|spec\|test" | head -40

# Step 3: Find Angular HTTP calls (what URL does each service call?)
grep -rn "this\.http\.\(get\|post\|put\|delete\|patch\)\|httpClient\." \
  <angular_path> --include="*.ts" | grep -v "//\|spec\|test" | head -40

# Step 4: Match those URLs to Java controllers
grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@PatchMapping\|@RequestMapping" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -40

# Step 5: Trace each controller to its service call
grep -rn "@Service" <java_path> --include="*.java" -l | head -20

# Step 6: Find what the service reads/writes
grep -rn "repository\.\|\.save\|\.findBy\|\.delete\|\.update\|kafkaTemplate\.\|rabbitTemplate\.\|restTemplate\." \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -40

# Step 7: Find async / event flows (fire-and-forget steps)
grep -rn "@EventListener\|@KafkaListener\|@Async\|publishEvent\|kafkaTemplate\.send\|@Scheduled" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -20

# Step 8: Find external system calls
grep -rn "restTemplate\.\|webClient\.\|@FeignClient\|HttpClient" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -20
```

### For Each Flow, Record This Map

```
FLOW: [Plain English name, e.g. "Submit a Purchase Order"]

TRIGGER:     User clicks "[Button label]" on [Screen name]
             ↓ (Angular calls)
FRONTEND:    [ComponentName] → [ServiceName].method()
             ↓ (HTTP [METHOD] /api/[path])
API LAYER:   [ControllerName].[method]()
             ↓ (calls)
BUSINESS:    [ServiceName].[method]() — applies [business rules]
             ↓ (reads/writes)
DATA:        [Repository] → [Entity / table in business terms]
             ↓ (optionally)
ASYNC:       Publishes [EventName] → [Consumer] handles [async action]
             ↓ (optionally)
EXTERNAL:    Calls [External System] via [integration name]
             ↓ (response back up)
RESPONSE:    User sees [success screen / message / updated data]

ERROR PATHS:
  If [condition] → User sees [error message], stays on [screen]
  If [condition] → [Alternate outcome]
```

### Flow Complexity Classification

| Type | Characteristics | Diagram style |
|---|---|---|
| **Simple CRUD** | UI → API → DB → response | Linear flowchart |
| **Multi-step workflow** | Multiple services, status transitions | Swim-lane diagram |
| **Async / event-driven** | Fire and forget, background processing | Sequence + async arrow |
| **Integration flow** | Calls external system | Sequence with external actor |
| **Approval chain** | Human decision point mid-flow | Flowchart with decision diamond |

---

## Step 3 — Deep-Dive: Extract All 12 Sections

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

### 3H — System Flows (Sections 4A and 4B)

**Run Step 2B extraction first**, then for each flow found:

**Section 4A — High-Level Overview**
- Build the Flow Inventory table (F-001 through F-N)
- Classify each flow: Simple / Multi-step / Approval chain / Async / Integration
- Draw the master Mermaid `flowchart TD` covering all flows in one diagram

**Section 4B — Detailed Breakdowns**
For each flow F-[###]: swim-lane sequence diagram + written walkthrough + error flows table

### 3I — External System Interactions (Section 13 — NEW)

This is the most important section for understanding what the module depends on outside
itself. Extract every outbound call to a system outside the current module scope.

**Step 1 — Discover all external calls**
```bash
# All outbound HTTP calls (to external systems or other modules)
grep -rn "restTemplate\.\|webClient\.\|@FeignClient\|HttpClient\.\|OkHttpClient" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -40

# External base URLs (not localhost)
grep -rn "base-url\|baseUrl\|BASE_URL\|\.url\s*=\|endpoint\." \
  <java_path>/src/main/resources --include="*.yml" --include="*.properties" | \
  grep -v "localhost\|127\.0\.0\|actuator\|swagger\|#" | head -20

# Kafka / messaging to external topics
grep -rn "kafkaTemplate\.send\|rabbitTemplate\.send\|sqsClient\." \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -20

# Inbound webhooks (external systems calling us)
grep -rn "@PostMapping\|@PutMapping" <java_path> --include="*.java" | \
  grep -i "webhook\|callback\|notify\|event\|inbound" | head -10

# File transfers
grep -rn "sftp\|ftp\|scp\|Files\.write\|FileOutputStream\|S3Client\|BlobClient" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -10
```

**Step 2 — For each external call, extract the interaction contract**
Read the calling code to find:
- What data is sent (method parameters, request body fields)
- What responses are handled (switch/if on response, status codes checked)
- What the system does with each response (what gets saved, what gets triggered)
- What happens on timeout or error (catch blocks, fallback logic)
- What timeout/retry configuration is set

```bash
# Read each external client class in full
cat <ExternalClientClass>.java

# Find response handling logic
grep -rn "getBody\|getStatusCode\|\.getStatus\|switch.*status\|if.*status\|\
  ResponseEntity\|onSuccess\|onError\|onFailure\|\.block()" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -40

# Find timeout configuration
grep -rn "setReadTimeout\|connectTimeout\|responseTimeout\|timeoutDuration\|\
  @TimeLimiter\|TimeLimiterConfig\|readTimeout\|writeTimeout" \
  <java_path> --include="*.java" --include="*.yml" | head -20

# Find retry configuration
grep -rn "@Retry\|@Retryable\|RetryConfig\|maxAttempts\|waitDuration\|backoff" \
  <java_path> --include="*.java" --include="*.yml" | head -20

# Find fallback behaviour
grep -rn "fallback\|@CircuitBreaker\|onErrorReturn\|orElse\|defaultValue\|degraded" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -20
```

**Step 3 — Translate to business language for Section 13**
For each external interaction found, populate the Section 13 template:

```
EXT-[###]: [Business name of external system]
  
  Interaction [###].N — [What this system is asking for in plain English]
  
  Triggered when: [User action or system event — not a method call]
  
  What this system sends:
    [Field name] — [why the external system needs it] — [example value]
    [Field name] — [why the external system needs it] — [example value]
  
  What comes back:
    Success: [What information returns and what it means]
    Failure: [What information returns and what it means]
    Unavailable: [How system detects this — timeout after N seconds]
  
  What happens with each response:
    On success → [what gets saved, what gets triggered, what user sees]
    On failure → [what gets saved, what gets triggered, what user sees]
    On unavailable → [fallback: retry/queue/graceful error, what user sees]
  
  Timing: [User waits N seconds / async — user sees result later / batch overnight]
  
  Data shared: [List of any personal or sensitive data sent to this system]
```

**Step 4 — Build the failure impact summary (Section 13.3)**
For each external system, answer: what can users still do if this system is down?
This is the most important question for a product owner reviewing resilience.

**Step 5 — Build the data sharing table (Section 13.4)**
List every piece of information that leaves this system to an external system.
Flag any personal data (names, addresses, financial data) for GDPR review.

1. **Swim-lane sequence diagram** (Mermaid `sequenceDiagram`)
   - One column per layer: User → UI Component → API → Business Logic → Data Store → Notifications → External System
   - Label every arrow in plain English describing what data or action moves
   - Use `alt/else` for business branches (approval threshold, validation outcome)
   - Use `--)` dashed arrows for async steps that happen in the background
   - `note over` for steps the user does not directly experience

2. **Written walkthrough** — Step 1 through Step N in plain English
   - Each step = one layer transition in the diagram
   - Name the business rule that fires (reference BR-XXX)
   - Describe what the user sees at each stage
   - Describe async/background effects separately from the user-facing flow

3. **Error flows table** — for each flow, document what goes wrong at each step

4. **Flow metrics** — response time expectations, async step count, external call count

**Flow quality rules:**
- Every flow must trace end-to-end: user action → screen → API → business logic → data → response
- Async steps must be explicitly labelled so POs understand the user does NOT wait for them
- No flow may reference class names, method names, HTTP verbs, or database table names
- Every external system call must be labelled with the business name of that system
- Approval chains must show both the approve and reject paths

---

## Step 4 — Assemble Document

Read `references/frd-output-template.md` and follow its **15-section structure** exactly.

Section order in the document:
1. Introduction & Purpose
2. Project Scope
3. User Roles & Personas
4. User Stories & Use Cases
4A. System Flows — High-Level Overview
4B. System Flows — Detailed Breakdowns
5. Functional Requirements
6. UI/UX — Screens & Navigation
7. Data Requirements
8. Business Rules
9. Error Handling
10. Assumptions & Constraints
11. Glossary
12. Appendix: Feature-to-Screen Map
**13. External System Interactions** ← NEW

**When graph data is available**, additionally enrich:
- **Section 4A**: use graph edge types to classify flows (compile edge = sync, event = async)
- **Section 13**: use graph fan-out projection to confirm all external module calls are documented
- **Section 13.3**: cross-reference graph's entry-point nodes with external system calls
- **Section 10**: list dead modules from graph as "flagged for removal confirmation"

---

## Step 5 — Generate Word Document

Read `/mnt/skills/public/docx/SKILL.md` and produce `.docx`.

For the flow sections specifically:
- **Section 4A flowchart**: embed as a Mermaid diagram block — render to SVG/image if docx supports it, otherwise include as a code block with an instruction to view in the HTML version
- **Section 4B sequence diagrams**: one diagram per flow, each on its own page
- **Written walkthrough**: numbered steps below each sequence diagram using Heading 3

---

## Step 6 — Quality Gate

### Completeness
- [ ] All 15 sections present (including 4A, 4B, and 13)
- [ ] Section 4A flow inventory has one row per significant user journey
- [ ] Section 4B has one subsection (F-[###]) per flow in the 4A inventory
- [ ] Every F-[###] has: sequence diagram + written walkthrough + error flows table
- [ ] **Section 13.1** lists every external system the module calls or receives calls from
- [ ] **Section 13.2** has one EXT-[###] subsection per external system with full interaction spec
- [ ] **Every interaction** (EXT-[###].N) has: what is sent + what comes back + what happens next
- [ ] **Section 13.3** failure impact summary covers every external system
- [ ] **Section 13.4** data sharing table flags any personal/sensitive data leaving the system
- [ ] Every module in scope has Section 5 + 6 entries
- [ ] Every role in roles table + at least one user story
- [ ] Every screen has a description in Section 6
- [ ] Every mandatory field has a data requirement
- [ ] Every BR is numbered and has a test scenario
- [ ] Every error has a user-visible message
- [ ] Section 2 has ≥3 explicit out-of-scope items

### External System Section Quality (Section 13)
- [ ] Every external system has a business name — not a URL or class name
- [ ] "What is sent" describes information in business terms — no field names or JSON keys
- [ ] "What comes back" covers ALL response types (success, each failure type, unavailable)
- [ ] "What happens next" is written from the user's perspective — not from the code's perspective
- [ ] Timing states clearly whether the user waits synchronously or sees a result later
- [ ] Fallback behaviour is documented — what users see when the external system is down
- [ ] Data sharing table flags personal data (name, address, financial data) for GDPR review
- [ ] "Criticality" is set for every external system (Critical / Important / Optional)

### Flow Diagram Quality
- [ ] Master flowchart (4A) uses only plain English labels — no class/method names
- [ ] Every sequence diagram (4B) has actor names matching FRD Section 3 role names
- [ ] Async steps use dashed arrows (`--)`) — not solid arrows
- [ ] Approval chains show both approve AND reject paths
- [ ] External systems are shown as actors/participants with their business name
- [ ] No diagram has more than 8 participants (split into sub-flows if needed)

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
