# Flow Analysis: [FLOW NAME]

> **ID**: FL-XXX
> **Layer**: [layer]
> **Analyzed**: [date]
> **Agent**: 01-Flow Analyzer
> **Status**: [Complete / Partial — needs X]

---

## Metadata

| Field | Value |
|-------|-------|
| Flow Name | [name] |
| Flow Type | [Screen Flow / Approval Flow / Decision Flow] |
| Application Layer | [COB / CRDFWApp / MSFWApp / PegaRules] |
| Class | [pyClassName] |
| Complexity | [Low / Medium / High / Critical] |
| Total Steps | [count] |
| Assignments (Human Tasks) | [count] |
| Decisions (Branch Points) | [count] |
| Sub-Flows Called | [count] |
| External Calls | [count] |

## Business Description

[Write 2-3 paragraphs in plain English describing what this flow does, who uses it, and why it exists. No PEGA jargon.]

## Actors

| Actor | Role in This Flow |
|-------|-------------------|
| [Role name] | [what they do] |

## Step-by-Step Process

1. **[Step label]** — [description in business terms]
2. **[Step label]** — [description]
3. **DECISION: [condition]** — IF [true path] / ELSE [false path]
4. **[Step label]** — [description]
...

## Shape Inventory

| Shape ID | Type | Label | Work Object | Harness/Section | Notes |
|----------|------|-------|-------------|-----------------|-------|
| | | | | | |

## Connector Map

| From | To | Condition | Type | When Rule |
|------|----|-----------|------|-----------|
| | | | | |

## Sub-Flow References

| Sub-Flow Name | Called From Step | Layer | Status |
|---------------|-----------------|-------|--------|
| | | | [needs analysis] |

## External Integration References

| Service | Called From Step | Type | Status |
|---------|-----------------|------|--------|
| | | | [needs analysis] |

## Decision Rule References

| Decision Rule | Used At Step | Type | Status |
|---------------|-------------|------|--------|
| | | | [needs analysis] |

## New Tasks Generated

- [ ] [task description]
- [ ] [task description]

## Open Questions

- [anything unclear or needing screenshot]
