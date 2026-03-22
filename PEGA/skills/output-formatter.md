# Skill: Output Formatter

> **Referenced by**: All agents
> **Purpose**: Ensures consistent file naming, structure, and cross-referencing

---

## FILE NAMING CONVENTION

```
workspace/findings/
├── 00-inventory.md                        ← Phase 1 inventory
├── flows/
│   ├── FL-001-loan-origination.md         ← [ID]-[kebab-case-name].md
│   ├── FL-002-credit-check-approval.md
│   └── FL-003-document-upload.md
├── decisions/
│   ├── DT-001-eligibility-check.md
│   ├── DT-002-rate-calculation.md
│   └── WH-001-status-change.md
├── integrations/
│   ├── INT-001-credit-bureau-api.md
│   ├── INT-002-document-ocr.md
│   └── INT-003-core-banking.md
├── ui/
│   ├── UI-001-applicant-info.md
│   ├── UI-002-loan-details.md
│   └── UI-003-credit-review.md
├── deep/
│   ├── DEEP-001-risk-assessment.md
│   └── DEEP-002-kyc-verification.md
├── diagrams/
│   ├── DIAG-001-loan-origination.md
│   └── DIAG-002-risk-assessment.md
└── FRD-COMPLETE.md
```

## ID ASSIGNMENT

```
Flows:         FL-001, FL-002, FL-003, ...
Decisions:     DT-001, DT-002, ... (tables/trees)  |  WH-001, WH-002, ... (when rules)
Integrations:  INT-001, INT-002, INT-003, ...
UI Screens:    UI-001, UI-002, UI-003, ...
Deep Analysis: DEEP-001, DEEP-002, ...
Diagrams:      DIAG-001, DIAG-002, ...

IDs are assigned in order of discovery. Once assigned, they don't change.
```

## CROSS-REFERENCE FORMAT

When referencing another finding from within a document:

```markdown
See [FL-001](../flows/FL-001-loan-origination.md) for the parent flow.
Uses decision rule [DT-001](../decisions/DT-001-eligibility-check.md).
Calls [INT-001](../integrations/INT-001-credit-bureau-api.md) for credit data.
Displayed on [UI-001](../ui/UI-001-applicant-info.md).
```

## STANDARD HEADER

Every output file starts with:

```markdown
# [Type] Analysis: [Name]

> **ID**: [XX-NNN]
> **Layer**: [application layer]
> **Analyzed**: [date]
> **Agent**: [which agent produced this]
> **Status**: [Complete / Partial — needs X]

---
```

## TASK LIST UPDATE FORMAT

After each agent run, append to workspace/MASTER-TASK-LIST.md:

```markdown
- [x] [task description] — completed [date] by Agent [N]
- [ ] [NEW] [discovered task] — added by Agent [N] on [date]
```
