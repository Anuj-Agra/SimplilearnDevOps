---
name: product-spec-orchestrator
description: "Central router for the Product Specification Suite. Use this skill whenever a user wants to work with functional specifications in any way — generating specs from code, updating specs with new requirements, or creating JIRA tickets from requirements. This orchestrator detects intent and routes to the correct specialist skill. Triggers on any mention of: 'functional spec', 'spec from code', 'document the system', 'what does the system do', 'update the spec', 'new requirements', 'spec changes', 'create JIRA', 'JIRA tickets', 'acceptance criteria', 'user stories from code', 'business rules', 'feature inventory', 'impact analysis', 'requirement breakdown', or any product-owner workflow involving specifications and requirements management."
---

# Product Specification Suite — Orchestrator

This is the routing layer. It detects what the user needs and dispatches to the correct specialist skill.

## The Three Specialist Skills

| Skill | What It Does | Location |
|-------|-------------|----------|
| **spec-generator** | Analyses a codebase and produces a layered functional specification as a tree of `.md` files | `/mnt/skills/user/spec-generator/SKILL.md` |
| **spec-updater** | Takes new requirements + existing spec → produces spec change proposals with exact diffs | `/mnt/skills/user/spec-updater/SKILL.md` |
| **jira-generator** | Takes new requirements (optionally with existing spec) → produces JIRA-formatted tickets with Description, Functional Details, and Acceptance Criteria | `/mnt/skills/user/jira-generator/SKILL.md` |

## Routing Logic

Read the user's message and match to a workflow:

### Route → spec-generator

User wants to **create a functional specification from scratch** by analysing code.

Signal phrases:
- "Generate a functional spec"
- "Document my codebase / system / application"
- "What does my system do?"
- "Analyse this code and tell me what it does"
- "Create spec from this repo / mono-repo"
- "Reverse-engineer the requirements"
- "I need a functional specification"
- User provides a codebase path without an existing spec

**Action:** Read `/mnt/skills/user/spec-generator/SKILL.md` and follow its instructions.

### Route → spec-updater

User has **new requirements** and an **existing functional spec**, and wants to know **what changes** in the spec.

Signal phrases:
- "I have new requirements, update the spec"
- "What needs to change in the spec for this feature?"
- "Impact analysis for these requirements"
- "How does this requirement affect the current spec?"
- "Suggest changes to the functional spec"
- "Keep the spec up to date with these changes"
- User provides both new requirements AND a path to existing spec files

**Action:** Read `/mnt/skills/user/spec-updater/SKILL.md` and follow its instructions.

### Route → jira-generator

User wants **JIRA tickets** formatted with Description, Functional Details, and Acceptance Criteria.

Signal phrases:
- "Create JIRA tickets"
- "Write acceptance criteria for this"
- "Format this as JIRA stories"
- "Break this requirement into stories"
- "I need JIRAs for this feature"
- "Write tickets with acceptance criteria"
- User asks for "stories" or "tickets" or "epics"

**Action:** Read `/mnt/skills/user/jira-generator/SKILL.md` and follow its instructions.

### Route → spec-updater THEN jira-generator (Combo)

User wants **both** — spec changes AND JIRA tickets for the same requirements.

Signal phrases:
- "New requirements — update the spec and create JIRAs"
- "Here are the changes — I need spec updates and tickets"
- Any combination of update + JIRA language

**Action:** Run spec-updater first (produces change proposals), then run jira-generator using the same requirements plus the change proposals as additional context.

### When Uncertain

If you cannot determine the workflow from the user's message, ask:

"I can help you with functional specifications in three ways:

1. **Generate** — Analyse your codebase and create a functional spec from scratch
2. **Update Spec** — Take new requirements and show exactly what changes in your existing spec
3. **Create JIRA Tickets** — Turn requirements into formatted JIRA stories with acceptance criteria

Which would you like to do? (Or I can do a combination — for example, update the spec AND create JIRAs for the same requirements.)"

---

## Shared Principles — Govern All Three Skills

### Principle 1: Zero Hallucination — Evidence or Ask

This is the single most important rule across all three skills.

> **Every statement in every output must trace back to a concrete source: code you read, a spec file you read, or information the user explicitly provided. If you cannot point to the source, do not write the statement. Ask the user instead.**

This means:
- **spec-generator:** Only document features, rules, fields, and screens you directly observed in the code. If a service class has ambiguous logic, do not guess its business purpose — ask the user: "I see logic in the order service that checks [condition]. What is the business reason for this?"
- **spec-updater:** Only propose changes that are directly stated or logically implied by the requirements provided. If a requirement says "add bulk export" but does not say which fields to export, do not invent a field list — ask: "Which fields should be included in the export?"
- **jira-generator:** Only write acceptance criteria, business rules, and functional details that are grounded in the requirements, the spec, or the code. If the user says "add a dashboard" but provides no details about what metrics to show, do not invent metrics — ask.

**When in doubt, ask. Asking a clarifying question is always better than fabricating a plausible-sounding answer.**

### Principle 2: The "User's Eyes" Rule

> Every sentence in every output must pass: "Would a user or business stakeholder understand and care about this?"

No technical jargon. No code references. No database schemas. No framework names. The output describes **observable behaviour** — what users see, do, and experience.

---

## Notes for the Orchestrator

- If the user references paths that do not exist, tell them and ask for the correct paths.
- If the user asks to generate a spec but already has one, confirm: "I see you already have a functional spec at [path]. Would you like me to regenerate it from scratch, or update it with new changes?"
- If the user asks for JIRA tickets but has no spec AND no codebase, the jira-generator can still work — it generates tickets from the requirements alone, just without cross-referencing existing features.
- All three skills produce `.md` files as output. The user can copy these directly into their project or JIRA instance.
