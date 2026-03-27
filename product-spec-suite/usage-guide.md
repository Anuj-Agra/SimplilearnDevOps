# Product Specification Suite — Usage Guide

## What This Is

Four skills that work together to manage functional specifications across your product lifecycle:

| Skill | What It Does | When to Use |
|-------|-------------|-------------|
| **Orchestrator** | Detects what you need and routes to the right skill | Always — start here |
| **Spec Generator** | Analyses codebase → layered `.md` spec files | Building spec from scratch |
| **Spec Updater** | New requirements + existing spec → change proposals + JIRAs | Keeping the spec current |
| **JIRA Generator** | Requirements → formatted JIRA tickets with acceptance criteria | Creating development work items |

---

## Quick Start Prompts

### Generate a Functional Spec from Code

```
My mono-repo is at [PATH]. Please analyse the codebase and generate
a layered functional specification as separate .md files.
```

Works **without** any prior documentation. If READMEs or Swagger files
happen to exist, they'll be used as enrichment automatically.

### Generate a Spec for a Single Module

```
My mono-repo is at [PATH]. Please analyse only the [MODULE_NAME]
module and generate its functional specification layers.

Backend code: [PATH_TO_SERVICE]
Frontend code: [PATH_TO_FRONTEND_MODULE]
```

### Scan First, Then Choose (Recommended for Large Repos)

```
My mono-repo is at [PATH]. Please scan the repository, identify all
modules, and show me the module map before generating anything.
```

Then follow up:

```
Generate specs for these modules: [MODULE_1], [MODULE_2], [MODULE_3]
```

---

### Update an Existing Spec with New Requirements

```
I have these new requirements:

1. Users should be able to bulk export customer records as CSV
2. The approval threshold for orders should change from £10,000 to £25,000
3. Add a dashboard showing monthly sales trends

My existing functional spec is at [PATH_TO_functional-specs/]

Please analyse the impact and show me what needs to change in the spec.
```

### Update Spec + Create JIRA Tickets (Combo)

```
I have these new requirements:

1. [Requirement 1]
2. [Requirement 2]

My existing spec is at [PATH].

Please update the spec AND create JIRA tickets for each requirement.
```

---

### Create JIRA Tickets from Requirements (With Spec)

```
I need JIRA tickets for these requirements:

1. [Requirement 1]
2. [Requirement 2]

My functional spec is at [PATH_TO_functional-specs/].

Each ticket should have Description, Functional Details, and
Acceptance Criteria in Given/When/Then format.
```

### Create JIRA Tickets (Without Spec — Standalone)

```
I need JIRA tickets for these requirements:

1. [Requirement 1]
2. [Requirement 2]

Each ticket should include Description, Functional Details,
and Acceptance Criteria.
```

### Create JIRA Tickets (From Code, No Spec)

```
My codebase is at [PATH]. I need JIRA tickets for these changes:

1. [Requirement 1]
2. [Requirement 2]

Please check the current code behaviour and then create properly
formatted JIRA tickets with acceptance criteria.
```

---

## What Each Skill Produces

### Spec Generator Output

A directory tree of `.md` files:
```
functional-specs/
├── README.md                     ← Start here
├── system/ (5 files)
├── modules/
│   └── <module>/ (6 files each)
│       └── sub-modules/ (optional)
└── reference/ (4 files)
```

### Spec Updater Output

```
spec-updates/
├── 00-impact-analysis.md        ← Read first: what changes where
└── 01-REQ-001-[name]/
    ├── change-summary.md
    ├── [affected-file-diffs].md  ← Exact changes per file
    └── jira-tickets.md           ← Dev tickets for this requirement
```

### JIRA Generator Output

```
jira-tickets/
├── 00-ticket-index.md            ← Summary of all tickets
├── EPIC-001-[name].md            ← Epic with child stories
└── STORY-001-[name].md           ← Standalone stories
```

---

## Tips

### For best spec generation
- Provide the mono-repo root, not individual file paths
- Mention known user roles if you have them
- For 20+ services, work in batches of 5-6 modules per session

### For best spec updates
- Be specific about requirements: "Add CSV export to customer list" is much better than "Add reporting"
- Point to the exact spec directory so the updater can cross-reference

### For best JIRA tickets
- One requirement per bullet point
- Include the business reason ("so that...") when possible
- Mention which user roles are involved
- Mention if you want Epic → Story breakdown or flat stories

### Iterating on output

After any skill produces output:
```
The JIRA for REQ-002 needs more acceptance criteria around edge cases.
Can you add ACs for: empty state, maximum records, and timeout?
```

```
The impact analysis for REQ-001 missed the Notifications module —
this change should trigger a new email to the finance team.
```

```
Split the Order Management module into two sub-modules:
Order Placement and Returns & Refunds.
```
