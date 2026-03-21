# Skill: Jira Ticket Template Reference

> Inject into Agent 04 (Jira Breakdown).

## Hierarchy model

```
EPIC (E1, E2, E3...)
  STORY (E1.S1, E1.S2...)
    TASK (E1.S1.T1, E1.S1.T2...)
      SUB-TASK (E1.S1.T2.a, E1.S1.T2.b...)
```

## PEGA task name prefixes

| Prefix | Rule type |
|--------|-----------|
| FLOW: | Flow rule |
| DT: | Data Transform rule |
| SECT: | Section / Harness rule |
| DEC: | Decision Table / Tree |
| CONN: | Connector and Metadata rule |
| SLA: | SLA rule |
| ROUT: | Router rule |
| ACCESS: | Access Group / Privilege |
| DATA: | Data Page / Class / Property |
| RPT: | Report Definition |
| QA: | Test cases / UAT preparation |
| ARCH: | Architecture spike / design decision |

## Story point guide (Fibonacci)

| Points | PEGA work |
|--------|-----------|
| 1 | Minor text or config change |
| 2 | New field with validation on existing section |
| 3 | New section (5–10 fields) or minor flow step |
| 5 | New sub-flow, decision table, or connector |
| 8 | New case type or major flow restructure |
| 13 | Complete flow with sub-flows, integrations, UI, SLAs |
