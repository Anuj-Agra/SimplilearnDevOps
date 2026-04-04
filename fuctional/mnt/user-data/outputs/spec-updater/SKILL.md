---
name: spec-updater
description: "Take new requirements and an existing functional specification, perform impact analysis, and produce spec change proposals showing exactly which files need to change and how. Use this skill whenever a user has new requirements, feature requests, or change requests and wants to know how they affect the existing functional specification. Produces a set of change proposal .md files that show what to add, modify, or remove in the spec, plus a summary JIRA ticket for each change. Triggers on: 'update the spec', 'new requirements against the spec', 'what changes in the spec', 'impact analysis', 'spec changes needed', 'keep the spec up to date', 'how does this affect the spec', 'suggest changes to the functional specification', or any request to evolve an existing spec with new work."
---

# Functional Specification Updater

Takes new requirements and an existing functional spec, performs impact analysis, and produces change proposals showing exactly which `.md` files change and how.

---

## Step 0 — Gather Inputs

### New requirements

Accept requirements in any form:
- User describes them in conversation
- User uploads a document (PRD, email, meeting notes, feature brief)
- User provides a bullet list
- User provides JIRA epics or feature requests

**Normalise** each requirement into a structured block:

```
REQ-NNN: [One-sentence summary]
Detail: [Full description — 2-3 sentences]
Affected roles: [Which user roles are involved, or "To be determined"]
Type: New Feature / Feature Change / Feature Removal / Rule Change / Data Change / UI Change
```

If any requirement is vague, push back and ask for clarity:
- "Add reporting" → What reports? What data? Who sees them? What format?
- "Improve the workflow" → Which workflow? What specifically changes?
- "Make it better" → What specific behaviour should change?

### Existing functional spec

Auto-detect the codebase root and look for the spec:

```bash
CODEBASE_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
```

Then check if `./functional-specs/` exists relative to root:

```bash
ls "$CODEBASE_ROOT/functional-specs/README.md" 2>/dev/null
```

- If found → use it automatically. Tell the user: "I found your functional spec at `./functional-specs/`."
- If not found → ask: "I don't see a `functional-specs/` directory in your project root. Can you point me to your existing spec, or would you like me to generate one first?"
- If the user pastes spec content directly in the conversation → that works too.

If no existing spec exists, tell the user:
"I don't see an existing functional specification. I can:
1. **Generate one first** from your codebase (using the spec-generator skill), then process these requirements against it
2. **Create JIRA tickets** directly from these requirements without a spec (using the jira-generator skill)

Which would you prefer?"

---

## Step 1 — Read the Existing Spec (Efficiently)

Do NOT read every file. Read strategically:

**Always read first:**
1. `README.md` — module map and system shape
2. `system/04-system-overview.md` — module relationships
3. `system/03-user-roles-and-personas.md` — current roles
4. `reference/business-rules-master.md` — scan for affected rules

**Then read only the modules likely affected** by the requirements:
- Requirement mentions a feature area → read that module's README + all layers
- Requirement adds a new role → read roles file + all modules referencing access
- Requirement changes data → read relevant `04-data-requirements.md`
- Requirement changes rules → read relevant `03-business-rules.md`
- Requirement adds screens → read relevant `02-screen-descriptions.md`
- Requirement changes a workflow, adds steps, or modifies state transitions → read relevant `06-flow-diagrams.md`
- Requirement affects cross-module flows → read `system/06-system-flow-diagrams.md`

---

## Step 2 — Impact Analysis

For each normalised requirement, produce an impact analysis. This is the core value — telling the product owner exactly what changes, where, and why.

### Generate `./spec-updates/00-impact-analysis.md` (relative to `CODEBASE_ROOT`):

```markdown
# Impact Analysis — [Date]

## Requirements Analysed

| ID | Summary | Type | Complexity |
|----|---------|------|-----------|
| REQ-001 | [Summary] | [Type] | Low / Medium / High |

---

## REQ-001: [Summary]

### Classification
- **Type:** New Feature / Feature Change / Rule Change / Data Change / UI Change
- **Scope:** [N] modules affected, [N] files to change
- **Complexity:** Low (1-2 files) / Medium (3-5) / High (6+)

### Modules Affected

| Module | Impact | Files to Change |
|--------|--------|----------------|
| [Module Name] | [What changes] | [File list] |

### Spec Files Requiring Changes

| File Path | Change Type | Summary |
|-----------|------------|---------|
| `modules/[mod]/01-user-stories.md` | Add | New stories: US-[MOD]-NNN |
| `modules/[mod]/03-business-rules.md` | Modify | BR-[MOD]-005 threshold changes |
| `modules/[mod]/06-flow-diagrams.md` | Modify | Update [workflow name] flow — add new step |
| `system/02-project-scope.md` | Modify | Add [feature] to in-scope |
| `system/06-system-flow-diagrams.md` | Modify | Update [journey name] — add new module interaction |
| `reference/business-rules-master.md` | Modify | Sync with module rule changes |

### New Files Needed
- `modules/[new-module]/` — [If a new module is needed, list all 7 files including 06-flow-diagrams.md]

### Cross-Module Impacts
- [Dependencies between modules that this requirement triggers]

### Risks & Questions
- [Anything ambiguous needing stakeholder clarification]
- [Potential conflicts with existing business rules]
```

---

## Step 3 — Generate Change Proposals

For each affected file, generate a **change proposal** showing exactly what to add, modify, or remove.

### Output structure (relative to `CODEBASE_ROOT`):

```
./spec-updates/
├── 00-impact-analysis.md                    # Overall impact summary
├── 01-REQ-001-[short-name]/                 # One folder per requirement
│   ├── change-summary.md                    # What changes and why
│   ├── modules-[mod]-01-user-stories.md     # Updated file content (or diff)
│   ├── modules-[mod]-03-business-rules.md   # Updated file content (or diff)
│   ├── modules-[mod]-06-flow-diagrams.md    # Updated Mermaid diagrams
│   ├── system-02-project-scope.md           # Updated file content (or diff)
│   ├── system-06-system-flow-diagrams.md    # Updated system diagrams (if cross-module impact)
│   └── reference-business-rules-master.md   # Updated file content (or diff)
└── 02-REQ-002-[short-name]/
    └── ...
```

### Change proposal file format:

Use a clear **CURRENT → PROPOSED** diff format so the user can see exactly what changes:

```markdown
# Change Proposal: [File Path]

**Requirement:** REQ-001 — [Summary]
**Change Type:** Add / Modify / Remove
**Original File:** `functional-specs/modules/order-management/03-business-rules.md`

---

## Changes

### Addition: New rule after BR-ORD-005

Add the following row to the Business Rules table:

| Rule ID | Rule | Trigger Condition | Affects |
|---------|------|-------------------|---------|
| BR-ORD-006 | Orders exceeding £25,000 require director-level approval in addition to manager approval | When order total exceeds £25,000 | Order submission screen, approval workflow |

### Modification: BR-ORD-003

**Current:**
| BR-ORD-003 | A discount of 10% is applied when the basket total exceeds £50 | Checkout | Checkout screen |

**Proposed:**
| BR-ORD-003 | A discount of 10% is applied when the basket total exceeds £75 | Checkout | Checkout screen |

**Reason:** REQ-001 raises the discount threshold from £50 to £75.

### Addition: New State Transition

Add to the State Transitions section:

| From State | To State | Trigger | Who Can Trigger | Conditions |
|-----------|----------|---------|----------------|-----------|
| Pending Manager Approval | Pending Director Approval | Manager approves | Manager | Order total > £25,000 |
```

### Diagram change proposals

When a requirement affects flows, state lifecycles, or navigation, generate diagram change proposals in the same CURRENT → PROPOSED format:

```markdown
# Change Proposal: modules/order-management/06-flow-diagrams.md

**Requirement:** REQ-001 — Add director approval for high-value orders
**Change Type:** Modify
**Diagram affected:** FLOW-ORD-001: Order Submission

---

## Current Diagram

` ` `mermaid
%% FLOW-ORD-001: Order Submission (CURRENT)
flowchart TD
    D --> E{Order total exceeds £10,000?}
    E -->|No| F{{System confirms order}}
    E -->|Yes| G{{Routes to Manager approval}}
    G --> H([Pending Approval])
` ` `

## Proposed Diagram

` ` `mermaid
%% FLOW-ORD-001: Order Submission (PROPOSED)
%% CHANGED: Threshold raised to £25,000, added Director approval tier
flowchart TD
    D --> E{Order total exceeds £25,000?}
    E -->|No| F{{System confirms order}}
    E -->|Yes| G{{Routes to Manager approval}}
    G --> G2{Manager approves?}
    G2 -->|Yes, total > £50,000| G3{{Routes to Director approval}}
    G2 -->|Yes, total ≤ £50,000| H([Order Confirmed])
    G2 -->|No| I([Order Rejected])
    G3 --> H
` ` `

**Changes made:**
- Threshold raised from £10,000 to £25,000
- Added Director approval step for orders exceeding £50,000
- Added rejection path
```

(Remove spaces from triple backtick fences when generating actual output.)

---

## Step 4 — Generate Change-Related JIRA Tickets

For each requirement, also generate JIRA tickets for the development work needed to implement the spec changes. Read `references/jira-format.md` for the exact template.

Write these to the same output folder as the change proposals:

```
./spec-updates/
├── 00-impact-analysis.md
├── 01-REQ-001-[short-name]/
│   ├── change-summary.md
│   ├── ... (change proposals)
│   └── jira-tickets.md              # JIRA tickets for this requirement
└── ...
```

After all files are written, also copy to `/mnt/user-data/outputs/spec-updates/` for download.

---

## Step 5 — Present to User

After generating all files, present the impact analysis first (so the user sees the big picture), then the change proposals. Summarise:

"I've analysed [N] requirements against your functional spec. Here's what I found:

- **REQ-001:** [Summary] — affects [N] modules, [N] files to change
- **REQ-002:** [Summary] — affects [N] modules, [N] files to change

The change proposals show exactly what to add, modify, or remove in each file. I've also generated JIRA tickets for each requirement.

Would you like me to:
1. Apply these changes directly to the spec files?
2. Adjust any of the proposals first?
3. Generate additional JIRA breakdown?"

---

## ZERO HALLUCINATION — The Cardinal Rule

> **Every change proposal and every JIRA ticket must trace directly to: (a) an explicit statement in the user's requirements, (b) content in the existing spec, or (c) a confirmed answer from the user. If you cannot point to the source, do not write it. Ask instead.**

### What this means in practice

**You CAN write:**
- A change to BR-ORD-003 → because the user's requirement explicitly says "change the threshold to £25,000" AND the existing spec has BR-ORD-003 with the current threshold
- A new user story US-ORD-016 → because the requirement describes a new capability that doesn't exist in the current spec
- An impact on the Notifications module → because the existing spec documents a notification triggered by the area being changed

**You CANNOT write:**
- "This change may also require updates to the reporting module" → unless the requirement mentions reporting OR the spec shows a direct dependency
- "The new screen should include a date picker" → unless the requirement says so or the user confirmed it
- "Performance should be under 2 seconds" → unless the requirement specifies a performance target or the existing spec has one for similar features

### When requirements are incomplete — ASK, don't fill in gaps

Before generating change proposals, review each requirement and collect gaps:

"Before I can generate accurate change proposals, I need clarification on these points:

1. **REQ-001 (Bulk Export)** — You mentioned CSV export, but which fields should be included? All visible columns, or a specific subset?
2. **REQ-002 (New Approval Tier)** — Should the director receive an email notification when an order enters their queue, or only see it on the dashboard?
3. **REQ-003 (Dashboard)** — Which metrics should appear? I cannot determine this from the existing spec alone."

**Present ALL questions for ALL requirements at once** — do not drip-feed questions one at a time.

### Never invent adjacent changes

When analysing impact, only document changes that are **directly caused** by the requirement:
- DO flag a change to `reference/business-rules-master.md` if a module rule changes (this is a direct sync dependency)
- DO NOT add "while we're at it, we should also update the glossary with..." unless the requirement introduces a new term
- DO NOT suggest "this might be a good time to also refactor the..." — that is scope creep, not impact analysis

### Confidence marking in change proposals

If a change is logically implied but not explicitly stated:
- Write the change proposal
- Mark it: `[Implied by REQ-NNN — confirm with stakeholder]`
- Add to the Risks & Questions section of the impact analysis

---

## Quality Rules

- Change proposals must use the **same format, IDs, and conventions** as the existing spec
- New IDs continue the existing numbering sequence (if spec has US-ORD-001 through 015, new stories start at US-ORD-016)
- Cross-references must be updated (business-rules-master, feature-screen-map, glossary)
- No technical jargon in any change proposal
- Every new business rule must be testable
- Every new user story must name the role
