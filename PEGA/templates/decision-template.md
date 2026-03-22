# Decision Analysis: [RULE NAME]

> **ID**: DT-XXX / WH-XXX
> **Layer**: [layer]
> **Analyzed**: [date]
> **Agent**: 02-Decision Mapper
> **Status**: [Complete / Partial]

---

## Metadata

| Field | Value |
|-------|-------|
| Rule Name | [name] |
| Type | [Decision Table / Decision Tree / When Rule / Map Value] |
| Layer | [layer] |
| Evaluation Mode | [First Match / All Matches / Weighted] |
| Total Conditions | [count] |
| Total Outcomes | [count] |

## Business Description

[2-3 sentences: What business question does this rule answer?]

## Condition Matrix

### Decision Table Format:
| # | [Condition 1 Name] | [Condition 2 Name] | ... | Result/Action |
|---|-------------------|-------------------|-----|---------------|
| 1 | [operator] [value] | [operator] [value] | | [outcome] |
| 2 | | | | |
| Otherwise | — | — | | [default outcome] |

### Decision Tree Format:
```
ROOT: [starting property or question]
├── IF [condition A]
│   ├── IF [condition A1] → RESULT: [action]
│   └── IF [condition A2] → RESULT: [action]
├── IF [condition B] → RESULT: [action]
└── OTHERWISE → RESULT: [default action]
```

### When Rule Format:
```
WHEN: [condition expression in plain English]
TRUE:  [what happens]
FALSE: [what happens]
```

## Plain English Rules

1. **Rule 1**: "If [business scenario], then [outcome]"
2. **Rule 2**: "If [business scenario], then [outcome]"
...

## Test Scenarios

| Scenario | Inputs | Expected Outcome | Explanation |
|----------|--------|-------------------|-------------|
| Happy path | [values] | [result] | [why] |
| Edge case | [values] | [result] | [why] |
| Default | [values] | [result] | [why] |

## Properties Used

| Property Path | Inferred Type | Description |
|---------------|---------------|-------------|
| .Property.Name | [type] | [what it represents] |

## Cross-References

| Used By | Where | How |
|---------|-------|-----|
| [FL-XXX: Flow Name] | Step [N] | [condition check / routing] |

## Open Questions

- [anything unclear]
