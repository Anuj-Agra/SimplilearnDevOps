---
name: spec-generator
description: "Analyse a codebase (mono-repo or single-project) and generate a layered Functional Specification as a tree of .md files. Works with Java, Angular, and mixed full-stack codebases. Produces one folder per business module with separate files for user stories, screen descriptions, business rules, data requirements, and error handling. Works entirely from code analysis — no technical specifications, architecture docs, or prior documentation required (though it will use them to enrich the output if they happen to exist). Triggers on: 'generate a functional spec', 'document my codebase', 'what does my system do', 'analyse this code', 'create spec from repo', 'reverse-engineer requirements', 'feature inventory from code', or any request to understand a system's capabilities from the user's perspective."
---

# Functional Specification Generator

Analyse a codebase and produce a layered functional specification as a directory tree of `.md` files — one per layer per module — ready to drop into the project.

**This skill works entirely from code.** No prior documentation, technical specs, or architecture docs are required. If they happen to exist in the repo, they are used as bonus enrichment — nothing more.

---

## Step 0 — Clarify Scope

Confirm with the user:

1. **Target** — Whole mono-repo? Specific module? Sub-module?
2. **Codebase root path** — The single root containing all services, libs, frontends.
3. **Known user roles** — Ask. If unknown, discover from code.

Do NOT ask about technical specs. Instead, silently check for them in Step 1.

---

## Step 1 — Reconnaissance

Goal: Build a mental map of the system without reading every file.

### 1a. Map the topology

```bash
# Top-level structure
ls -la <root>
find <root> -maxdepth 2 -name "pom.xml" -o -name "build.gradle" -o -name "package.json" -o -name "angular.json" 2>/dev/null | sort
```

Classify every top-level directory:
- **Service** — Deployable backend (build file + controllers + main class)
- **Frontend App** — Angular/React app (angular.json or equivalent)
- **Shared Library** — Used by services, no controllers, no main
- **Infrastructure** — CI/CD, Docker, deploy scripts → skip
- **Documentation** — docs/ folders → silent enrichment

### 1b. Silent documentation scan (enrichment only)

```bash
find <root> -maxdepth 5 \( -name "README.md" -o -name "ARCHITECTURE.md" -o -name "swagger.yaml" -o -name "openapi.json" -o -name "*.feature" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -30
```

If docs are found, read them and use the context to write richer descriptions. If none are found, proceed without them. This step never blocks progress.

### 1c. Scan each service and frontend

Read `references/scanning-guide.md` for the complete set of `grep` and `find` commands. Run them **per-service** and **per-frontend**.

Priority order for Java backends:
1. Controllers/endpoints (feature surface)
2. Security config (roles and permissions)
3. Entity/model classes (data managed)
4. Service classes (business rules)
5. Validation annotations (data constraints)
6. Exception handlers (error messages)
7. Enums (business states)
8. Scheduled jobs (background processes affecting users)
9. Email/notification templates (communications)

Priority order for Angular frontends:
1. Route definitions (page structure)
2. Route guards (role-based access)
3. Component templates (UI the user sees)
4. Form definitions (input fields and validation)
5. Service calls (actions users trigger)
6. Error/toast messages (user feedback)
7. i18n files (user-facing labels)

### 1d. Map cross-service relationships

```bash
grep -rn "@FeignClient\|RestTemplate\|WebClient" <root> --include="*.java" | grep -v test
grep -rn "@KafkaListener\|@RabbitListener\|@JmsListener\|@EventListener" <root> --include="*.java" | grep -v test
```

Translate into user language: "When a user places an order, the system automatically checks stock availability."

---

## Step 2 — Build the Module Map

Group services/frontends into business modules. A module is a **logical business grouping** — it may span multiple services or be a subset of one.

**Naming rules** (full details in `references/naming-conventions.md`):
- Folders: `kebab-case`, plain English, max 3 words
- Files: numbered prefix + layer name (e.g. `01-user-stories.md`)
- IDs: `US-ORD-001`, `BR-ORD-001`, `ERR-ORD-001`

Present the module map to the user and confirm before deep-diving.

---

## Step 3 — Deep-Dive & Write Layered Files

Work **one module at a time**. For each module, read the relevant code and generate 6 files (see `references/layer-templates.md` for exact templates):

| # | File | Contains |
|---|------|---------|
| 00 | `README.md` | Module overview — purpose, key users, capabilities |
| 01 | `01-user-stories.md` | All user stories with IDs |
| 02 | `02-screen-descriptions.md` | Screen-by-screen: what user sees, actions, navigation |
| 03 | `03-business-rules.md` | Numbered, testable business rules |
| 04 | `04-data-requirements.md` | Field-level spec: name, required, format, allowed values |
| 05 | `05-error-handling.md` | Error scenarios, messages, resolutions |

For sub-modules, nest the same structure under `sub-modules/<name>/`.

---

## Step 4 — System-Level Files

| File | Contains |
|------|---------|
| `system/01-introduction-and-purpose.md` | What the system is, problem it solves, who uses it |
| `system/02-project-scope.md` | In-scope and out-of-scope |
| `system/03-user-roles-and-personas.md` | All roles, descriptions, access levels, personas |
| `system/04-system-overview.md` | Module map with summaries and relationships |
| `system/05-cross-cutting-concerns.md` | Auth, navigation, notifications, search, export, audit |

---

## Step 5 — Reference Files

| File | Contains |
|------|---------|
| `reference/business-rules-master.md` | All rules from all modules |
| `reference/glossary.md` | Business terms defined |
| `reference/feature-screen-map.md` | Feature → Screen → Module → Role |
| `reference/assumptions-and-constraints.md` | Inferred facts needing validation |

---

## Step 6 — Index Files

| File | Contains |
|------|---------|
| `README.md` | Master index with links to every file |
| `tech-specs-index.md` | What docs were found (or "none found") and how they were used |

---

## Step 7 — Write Output

Create the full tree under `/mnt/user-data/outputs/functional-specs/`. Read `references/output-structure.md` for the exact layout.

```
functional-specs/
├── README.md
├── tech-specs-index.md
├── system/ (5 files)
├── modules/
│   └── <module-name>/ (6 files each + optional sub-modules/)
└── reference/ (4 files)
```

---

## Quality Checklist

- [ ] No technical jargon — zero framework, language, database, or code references
- [ ] No vague language — every statement specific and testable
- [ ] User perspective only — every feature is a user action or system response
- [ ] Roles named on every feature
- [ ] Business rules are testable
- [ ] Cross-links use relative paths
- [ ] Plain English throughout

## ZERO HALLUCINATION — The Cardinal Rule

> **Every statement in the spec must trace to a specific line, file, annotation, template, or configuration you directly read in the code. If you cannot point to the source, do not write the statement.**

### What this means in practice

**You CAN write** (because you saw it in code):
- "The system requires an email address during registration" → because you read `@NotNull @Email` on a field in the registration entity, or saw `<input type="email" required>` in a component template
- "Only Administrators can access the User Management screen" → because you read `@PreAuthorize("hasRole('ADMIN')")` on the controller or `canActivate: [AdminGuard]` on the route
- "Orders progress through three stages: Draft, Submitted, Approved" → because you read `enum OrderStatus { DRAFT, SUBMITTED, APPROVED }` in the code

**You CANNOT write** (because you are guessing):
- "The system sends an email confirmation after registration" → unless you found an email template or a `sendEmail()` call in the registration flow
- "Users can search by date range" → unless you found a date-range filter in the component template or a date parameter in the controller
- "The report is generated daily" → unless you found a `@Scheduled` annotation or cron configuration

### When you encounter ambiguity — ASK, don't guess

If the code is ambiguous, collect your specific questions and present them to the user before writing that section of the spec:

"I found the following areas where I need your input before I can document them accurately:

1. **Order service** — There's logic that checks whether the customer has a loyalty tier, but I cannot determine from the code alone what discount percentages apply to each tier. What are the tier-based discount rules?
2. **Report module** — I see a report generation function but cannot determine who has access to view the reports. Which roles should see which reports?
3. **Notifications** — I see an email service is configured, but I cannot find specific templates for order-related emails. Does the system send order confirmation emails?"

### Never fill gaps with assumptions

- Do NOT assume a feature exists because it "typically would" in this type of system
- Do NOT infer business rules that aren't expressed in code (no "it probably requires...")
- Do NOT generate screen descriptions for screens you haven't seen in the templates
- Do NOT add fields to data requirements that aren't in the entity or form definitions
- Do NOT create user stories for capabilities that aren't evidenced in controllers or routes

### Confidence marking

When documenting something where the code is clear about the WHAT but ambiguous about the WHY or the exact business intent:

- Write what you can confirm from code
- Append: `[Source: observed in code — business intent to be confirmed]`
- Add to `reference/assumptions-and-constraints.md` with confidence level

### The assumptions file is your safety net

Anything you are less than 100% certain about goes into `reference/assumptions-and-constraints.md` with:
- The assumption stated clearly
- Where in the code you observed the behaviour
- Confidence level (High / Medium / Low)
- What specifically needs to be confirmed by the user or team

## Anti-Patterns

| Do NOT write | Write instead |
|---|---|
| "The REST endpoint accepts a POST request" | "The user submits the registration form" |
| "Data is persisted to the orders table" | "The system saves the order details" |
| "The microservice publishes a Kafka event" | "After approval, the Inventory module is automatically notified" |
| "The Angular component uses reactive forms" | "The form requires the following fields: ..." |
| "The JWT token expires after 30 minutes" | "Users are automatically signed out after 30 minutes of inactivity" |
| "The system probably sends a welcome email" (guessing) | Ask the user: "Does the system send a welcome email after registration? I didn't find evidence of this in the code." |
| "Users can filter by date range" (assuming) | Only document filters you found in the template code |
