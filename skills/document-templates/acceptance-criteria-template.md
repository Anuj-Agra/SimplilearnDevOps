# Skill: Acceptance Criteria Template Reference

> Inject into Agent 05 (Acceptance Criteria).

## Gherkin structure

```
Given [system state / precondition]
  And [additional context if needed]
When [single triggering action]
Then [primary observable outcome]
  And [secondary verification]
  And [audit log expectation]
```

## Mandatory scenario types for KYC

| Type | Required? |
|------|----------|
| Happy path — standard success | Always |
| Validation error — missing/invalid input | Always |
| Edge case — boundary values (e.g. score = 39, 40, 70) | Always |
| Integration failure — timeout, 5xx, unavailable | Always |
| SLA — before/at goal/at deadline/after breach | For assignment steps |
| Regulatory compliance — verifies a regulatory obligation | Always |
| Security — unauthorised access attempt | Always |
| Maker-checker — same person cannot be maker and checker | For dual-approval flows |

## Then clause completeness

Each Then block must cover (where applicable):
- Case status transition
- Message shown to user
- Data written to case
- Audit log entry (what fields are recorded)
- Notification sent (to whom)
- Routing / assignment (workbasket or operator)
- Negative verification (what did NOT happen)
