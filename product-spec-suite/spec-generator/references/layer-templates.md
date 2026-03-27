# Layer Templates

Exact templates for each output file. Replace all `[bracketed]` placeholders.

---

## Master README.md

```markdown
# Functional Specification — [System Name]

> **Version:** 1.0  |  **Generated:** [Date]  |  **Prepared by:** Claude

## How to Read This Specification

- **New to the system?** Start with [Introduction](./system/01-introduction-and-purpose.md) and [System Overview](./system/04-system-overview.md)
- **Looking for a feature?** Check [Feature-to-Screen Map](./reference/feature-screen-map.md)
- **Need a business rule?** See [Business Rules Master](./reference/business-rules-master.md)
- **Reviewing accuracy?** Check [Assumptions](./reference/assumptions-and-constraints.md)

## System Documentation

| Document | Description |
|----------|-------------|
| [Introduction](./system/01-introduction-and-purpose.md) | What the system is and why it exists |
| [Project Scope](./system/02-project-scope.md) | In scope and out of scope |
| [User Roles](./system/03-user-roles-and-personas.md) | Who uses the system |
| [System Overview](./system/04-system-overview.md) | Module map |
| [Cross-Cutting Concerns](./system/05-cross-cutting-concerns.md) | Auth, navigation, notifications |

## Modules

| Module | Description | Link |
|--------|-------------|------|
| [Name] | [One sentence] | [View →](./modules/[name]/README.md) |

## Reference

| Document | Description |
|----------|-------------|
| [Business Rules Master](./reference/business-rules-master.md) | All rules in one place |
| [Glossary](./reference/glossary.md) | Terms defined |
| [Feature-Screen Map](./reference/feature-screen-map.md) | Feature → Screen → Module → Role |
| [Assumptions](./reference/assumptions-and-constraints.md) | Items needing validation |
```

---

## System Templates

### system/01-introduction-and-purpose.md

```markdown
# Introduction & Purpose

[← Back to Index](../README.md)

## What is [System Name]?
[One sentence: "[System Name] is a [type] that enables [users] to [activity]."]

## The Problem It Solves
[1-2 paragraphs, plain language]

## Who Uses It
- **[Role]** — [One sentence about their use]

## Document Scope
This specification covers the current behaviour as implemented in the codebase.
```

### system/02-project-scope.md

In Scope: bullet list by module. Out of Scope: what the system does NOT do (inferred from absence).

### system/03-user-roles-and-personas.md

Role summary table: Role | Description | Access Level | Key Permissions. Then a 2-3 sentence persona for each.

### system/04-system-overview.md

Module map table, inter-module relationships in user language, end-to-end user journeys as numbered steps.

### system/05-cross-cutting-concerns.md

Sections: Authentication & Access, Navigation Structure, Notifications & Communications, Search & Filtering, Export & Download, Audit & History.

---

## Module Templates

### Module README.md

```markdown
# [Module Name]

[← Back to Index](../../README.md)

## Purpose
[One paragraph: what this module does in business terms]

## Key Users
- **[Role]** — [How they use this module]

## Capabilities
- [Capability 1]
- [Capability 2]

## Specification Layers

| Layer | Document |
|-------|----------|
| User Stories | [View →](./01-user-stories.md) |
| Screens | [View →](./02-screen-descriptions.md) |
| Business Rules | [View →](./03-business-rules.md) |
| Data Requirements | [View →](./04-data-requirements.md) |
| Error Handling | [View →](./05-error-handling.md) |
```

### 01-user-stories.md

```markdown
# [Module] — User Stories

[← Back to Module](./README.md)

| ID | Story | Priority |
|----|-------|----------|
| US-[MOD]-001 | As a **[role]**, I can [action] so that [benefit]. | Core / Supporting |
```

### 02-screen-descriptions.md

For each screen:
- **Purpose:** what user accomplishes
- **Access:** which roles
- **Navigation:** how user gets here
- **What the User Sees:** layout description in plain English
- **Available Actions:** table of Action | Description | Conditions

### 03-business-rules.md

```markdown
# [Module] — Business Rules

[← Back to Module](./README.md)

| Rule ID | Rule | Trigger Condition | Affects |
|---------|------|-------------------|---------|
| BR-[MOD]-001 | [Testable statement] | [When applies] | [Screens/features] |
```

Include **State Transitions** section if entities have lifecycles (From → To → Trigger → Who → Conditions).

### 04-data-requirements.md

Per entity/form: Field | Required | Format/Constraints | Allowed Values | Notes

### 05-error-handling.md

Error Scenarios table: ID | Scenario | User Message | Severity | Resolution
Validation Messages table: Field | Validation | Message Shown

---

## Reference Templates

### business-rules-master.md
All rules from all modules: Rule ID | Module | Rule | Trigger

### glossary.md
Term | Definition | Used In

### feature-screen-map.md
Feature | Screen | Module | Roles

### assumptions-and-constraints.md
Assumptions table: ID | Assumption | Confidence | Source | Needs Validation
Constraints table: ID | Constraint | Impact | Source
Discrepancies table: Area | Documentation Says | Code Implements | This Spec Uses

---

## tech-specs-index.md

If docs were found: list each with path, type, and key insights extracted.
If no docs found: "No technical specifications were discovered in the codebase. This functional specification was generated entirely from code analysis."
