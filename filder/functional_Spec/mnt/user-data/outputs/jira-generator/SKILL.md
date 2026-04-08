---
name: jira-generator
description: "Generate properly formatted JIRA tickets from new requirements, with a structured 6-section anatomy: User Story, Business Impact, Acceptance Criteria, Design & Interaction, Functional & Developer Notes, and Out of Scope. Optionally enriched by an existing functional specification or codebase analysis to describe 'what already exists' before describing what changes. Works three ways: (1) requirements + existing functional spec = richly cross-referenced tickets, (2) requirements alone = standalone tickets, (3) requirements + codebase = analyses code first then generates tickets. Triggers on: 'create JIRA tickets', 'write acceptance criteria', 'format as JIRA', 'break into stories', 'JIRA stories for this feature', 'create epics and stories', 'acceptance criteria for this requirement', 'ticket breakdown', or any request to produce development work items from requirements."
---

# JIRA Ticket Generator

Generate JIRA tickets with a structured 6-section anatomy from new requirements. Every ticket clearly describes **what already exists** before describing what changes.

Works in three modes depending on what the user provides:

| User provides | Mode | How "What Exists" is populated |
|---|---|---|
| Requirements + existing functional spec | **Spec-Enriched** | Current state pulled from spec files, with section references and existing IDs |
| Requirements only (no spec, no code) | **Standalone** | Current state described from the requirement context; ask user to fill gaps |
| Requirements + codebase path | **Code-Aware** | Current state discovered by reading relevant code, translated to user language |

---

## The Ticket Anatomy — 6 Mandatory Sections

Every ticket follows this exact structure. Read `references/jira-ticket-template.md` for the full template with worked examples.

**Summary line:** `[Action Verb] + [Specific Feature/Function] + [Target Area]`

| # | Section | Purpose |
|---|---------|---------|
| 1 | 🧑 User Story | Who wants what and why |
| 2 | 📈 Business Impact & Motivation | Problem, value, measurable success signal |
| 3 | ✅ Acceptance Criteria | Scenario-based Given/When/Then including edge cases and non-functional |
| 4 | 🎨 Design & Interaction | Design link placeholder + user flow description |
| 5 | 🛠 Functional & Developer Notes | Validations, data requirements, blockers/dependencies, spec references |
| 6 | 🚫 Out of Scope | What this ticket will NOT do |

---

## Step 0 — Gather Inputs

### Requirements (always required)

Accept in any form: conversation, document upload, bullet list, existing JIRA epic for breakdown.

**Normalise** each requirement:

```
REQ-NNN: [One-sentence summary]
Detail: [Full description]
Affected roles: [Roles involved, or "To be determined"]
Type: New Feature / Feature Change / Feature Removal / Rule Change / Data Change / UI Change
```

Push back on vague requirements:
- "Add reporting" → What reports? What data? Who sees them? What format?
- "Improve the workflow" → Which workflow? What specifically changes?
- "Make it faster" → What operation? What is the expected speed?

### Existing functional spec (optional — enriches output)

Auto-detect the codebase root:

```bash
CODEBASE_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
```

Then check for `./functional-specs/` relative to root. If found, read:
1. `README.md` to get the module map
2. `system/03-user-roles-and-personas.md` for current roles
3. `reference/business-rules-master.md` for current rules
4. Affected module files: `01-user-stories.md`, `02-screen-descriptions.md`, `03-business-rules.md`, `04-data-requirements.md`, `05-error-handling.md`

If not found and user hasn't pointed to a spec, proceed without it — generate standalone tickets.

Use this to populate the **"What Currently Exists"** block, reference existing spec IDs, and continue numbering.

### Codebase path (optional — enables current-state discovery)

If the user provides a codebase path but no spec:
1. Run targeted scans for affected areas (controllers, services, templates, validators)
2. Discover current behaviour and translate to user language
3. Populate "What Currently Exists" from code observations
4. Never output technical details — only user-visible behaviour

### JIRA preferences (ask if not specified)

Read `references/jira-preferences.md`. Defaults: Epic → Stories, no story points, no labels, no sprint.

---

## Step 1 — Establish "What Already Exists"

**This step is critical.** Before writing any ticket, build a clear picture of the current state. This prevents ambiguity, avoids duplicate work, and gives developers essential context.

### From spec

Extract per affected module:
- Current user stories (to reference or modify)
- Current screens and their elements (what's on the page today)
- Current business rules (what logic governs the area today)
- Current data fields and constraints (what's already captured)
- Current error handling (what edge cases are already covered)

### From codebase (no spec)

Scan affected areas and translate:
- Existing endpoints → "The system currently allows users to..."
- Existing form fields → "The [screen] currently captures: ..."
- Existing business logic → "Currently, [rule in plain English]"
- Existing error messages → "When [condition], the user sees..."

### From neither

State what you know from requirement context. Be explicit:
"Current state based on requirement description. Development team should verify before implementation."

---

## Step 2 — Analyse & Decompose

### Size each requirement

- **Small** (rule change, field addition, label change) → Single Story
- **Medium** (new screen, new workflow step, new report) → 2-4 Stories
- **Large** (new feature area, multiple screens, multiple roles) → Epic with 3+ Stories

### Decompose into Stories

Each distinct user action = one Story. Also decompose by role, screen, or workflow step.

---

## Step 3 — Generate Tickets

For each Story, generate the full 6-section ticket per `references/jira-ticket-template.md`.

### Section-by-section guidance:

**Summary:** Strong action verb + specific feature + area. Never vague.

**🧑 User Story:** "So that" must state a real business benefit, not restate the action. If the user's requirement already contains a "so that" or business reason, use it.

**📈 Business Impact:**
- Problem Statement: What is painful/missing today? Reference "What Currently Exists" to explain the gap.
- Value: Quantify where possible. If user provided business justification, use it. If not, infer and flag as assumption.
- Measurable Signal: Concrete success metric. If not obvious, suggest one.

**✅ Acceptance Criteria:** Must include at minimum:
- 1+ happy-path scenario
- 1+ negative/edge-case scenario
- Non-functional criteria when relevant (performance target, security, accessibility)
- Permission scenario if role-based access is involved
- Each scenario titled, with Given/When/Then

**🎨 Design & Interaction:**
- Always include design link placeholder: `[Figma/Design Link: To be added]`
- User Flow: Step-by-step navigation path. Reference spec screen descriptions if available.

**🛠 Functional & Developer Notes:**
- Validations: Field-level rules (required, format, min/max, regex patterns in plain language)
- Data Requirements: New or modified fields, formats, constraints
- Blockers/Dependencies: Other tickets, external systems, data migrations. If spec exists, list affected spec file paths here.
- "What Currently Exists" summary: Brief recap of current state relevant to implementation

**🚫 Out of Scope:** Never empty. At minimum one explicit boundary. Think about:
- Adjacent features that belong in separate tickets
- Performance/security optimisation (unless requested)
- Historical data migration (unless requested)
- Mobile-specific layouts (unless requested)
- Internationalisation (unless requested)

---

## Step 4 — Write Output

Write to `./jira-tickets/` relative to `CODEBASE_ROOT`. Also copy to `/mnt/user-data/outputs/jira-tickets/` for download.

```
./jira-tickets/
├── 00-ticket-index.md              # Summary with current-state context
├── EPIC-001-[short-name].md        # Epic + child stories (full 6-section each)
├── EPIC-002-[short-name].md
└── STORY-[standalone].md           # Standalone stories
```

### 00-ticket-index.md

```markdown
# JIRA Ticket Index — [Date]

## Current State Summary
[What currently exists in the affected areas — shared context for all tickets]

## Requirements → Tickets

| REQ | Summary | Tickets | Module |
|-----|---------|---------|--------|
| REQ-001 | [Summary] | EPIC-001 (4 Stories) | Order Management |

## All Tickets

| Ticket | Type | Summary | Priority |
|--------|------|---------|----------|
| EPIC-001 | Epic | [Action Verb + Feature + Area] | High |
| EPIC-001-S1 | Story | [Action Verb + Feature + Area] | High |

## Spec Files Affected
| File | Changed By |
|------|-----------|
| `modules/order-management/03-business-rules.md` | EPIC-001-S2 |
```

---

## Step 5 — Present to User

"I've generated [N] JIRA tickets from your [N] requirements. Each ticket includes:

1. User Story (who, what, why)
2. Business Impact with measurable success signal
3. Acceptance Criteria (Given/When/Then + edge cases)
4. Design & Interaction flow
5. Functional notes with validations and dependencies
6. Explicit Out of Scope boundaries

[If spec/code used: Every ticket describes what currently exists before stating what changes.]

Shall I adjust breakdown, add criteria, or change priorities?"

---

## ZERO HALLUCINATION — The Cardinal Rule

> **Every sentence in every ticket must trace to: (a) the user's requirements, (b) the existing functional spec, (c) code you directly read, or (d) a confirmed answer from the user. If you cannot point to the source, do not write it. Ask instead.**

### What this means in practice

**You CAN write in a ticket:**
- "The user can select multiple records" → because the requirement explicitly says "bulk selection"
- "Currently, orders above £10,000 require approval (BR-ORD-003)" → because you read this from the spec
- "The system validates email format" → because you saw the validation in the code or spec
- Acceptance criteria covering edge cases for features that are explicitly described in the requirement

**You CANNOT write:**
- "The export should include customer name, email, phone, and address" → unless the requirement or spec specifies these exact fields. If unspecified, ASK: "Which fields should be included in the export?"
- "The dashboard shows monthly sales trends and revenue by region" → unless the requirement lists these metrics. If it just says "add a dashboard", ASK: "What metrics should the dashboard display?"
- "Performance target: under 2 seconds" → unless the requirement or spec states this
- "The user receives an email notification" → unless the requirement explicitly mentions it

### When requirements lack detail — ASK before writing tickets

Before generating any ticket, review each requirement for completeness. If critical details are missing, collect ALL questions and present them together:

"I need the following details before I can write accurate JIRA tickets:

1. **Bulk Export** — Which fields should be included in the CSV?
2. **Bulk Export** — Is there a maximum number of records for a single export?
3. **New Dashboard** — Which metrics should appear? Over what time period?
4. **New Dashboard** — Which user roles should see the dashboard?

Once you answer these, I can generate precise tickets with accurate acceptance criteria."

**Do NOT generate placeholder tickets with invented details and a note saying "to be confirmed".** Get the answers first, then generate accurate tickets.

### Acceptance criteria must be grounded

- Happy-path ACs must test the behaviour described in the requirement
- Edge-case ACs must test boundaries that are evident from the requirement (e.g., if it mentions a threshold, test boundary values)
- Do NOT invent edge cases for features the requirement doesn't describe
- Non-functional criteria only if the requirement mentions them or the existing spec has benchmarks for similar features

### The "What Currently Exists" block must be factual

- If from spec: quote what the spec says, with file references
- If from code: describe only what you directly read, translated to user language
- If from neither: state clearly that current state needs verification
- NEVER write "The system currently [invented behaviour]"

---

## Quality Rules

- **Summary: action verb format** — `[Verb] + [Feature] + [Area]`, always
- **"What exists" always documented** — from spec, code, or context — never invented
- **User Story "So that" is a real benefit** — never restates the "I want"
- **Business Impact has measurable signal** — even if estimated (mark as estimate)
- **AC: at least 1 negative/edge scenario per ticket** — never only happy paths
- **Non-functional AC included** when performance or security matters
- **Design link placeholder always present** — even as "To be added"
- **Out of Scope never empty** — at least one explicit boundary
- **No technical jargon** in sections 1-4 and 6; permitted in section 5 (Developer Notes)
- **Spec references concentrated in section 5** — not scattered
- **IDs continue existing sequences** when spec is available
