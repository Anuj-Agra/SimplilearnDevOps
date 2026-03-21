# Skill: KYC Approval Flows

> Inject this file into agents that need to describe, document, or generate acceptance criteria for KYC approval hierarchies.

---

## KYC approval hierarchy

```
AUTO-APPROVE
    │── Condition: LOW risk + no hits + all docs verified + no PEP
    │── Actor: System (no human intervention)
    └── SLA: Immediate

RM REVIEW (Relationship Manager)
    │── Condition: MEDIUM risk
    │── Actor: Assigned Relationship Manager
    │── SLA: 48 business hours from assignment
    └── Escalation: → Compliance if SLA breached

COMPLIANCE REVIEW
    │── Condition: HIGH risk OR PEP OR EDD required
    │── Actor: Compliance Officer
    │── SLA: 5 business days from assignment
    └── Escalation: → Head of Compliance if SLA breached

DUAL APPROVAL (Maker-Checker)
    │── Condition: EDD cases, sanctions near-hits, HIGH risk corporate
    │── Actor 1 (Maker): Compliance Officer submits decision
    │── Actor 2 (Checker): Senior Compliance Officer independently verifies
    │── Constraint: Maker and Checker must be different individuals
    └── SLA: Each stage has its own SLA clock

SANCTIONS REVIEW
    │── Condition: Confirmed sanctions hit
    │── Actor: Dedicated Sanctions Review team (separate from KYC Ops)
    │── SLA: 24 business hours from hit confirmation
    │── Outcome options: Clear (false positive), Escalate to MLRO, Block
    └── SAR filing may be required

MLRO APPROVAL
    │── Condition: SAR filing required; confirmed sanctions hit not cleared
    │── Actor: Money Laundering Reporting Officer
    │── SLA: Defined by regulation (typically 5 days for SAR)
    └── Outcome: SAR filed / Account blocked / Relationship exited
```

---

## SLA reference table

| SLA name | Process | Goal | Deadline | Business hours? | Escalation |
|----------|---------|------|---------|----------------|-----------|
| KYC-SLA-CDDInitiation | CDD case creation | 1 hour | 4 hours | Yes | KYC Team Lead |
| KYC-SLA-DocumentVerification | Document review | 4 hours | 24 hours | Yes | KYC Team Lead |
| KYC-SLA-RMReview | RM review (MEDIUM risk) | 24 hours | 48 hours | Yes | Compliance team |
| KYC-SLA-ComplianceReview | Compliance review (HIGH risk) | 3 days | 5 days | Yes | Head of Compliance |
| KYC-SLA-EDDCompletion | Full EDD case | 5 days | 10 days | Yes | Head of Compliance |
| KYC-SLA-SanctionsReview | Sanctions hit review | 4 hours | 24 hours | Yes | MLRO |
| KYC-SLA-SARFiling | SAR preparation and filing | 3 days | 5 days | Yes | MLRO / Legal |
| KYC-SLA-PeriodicReview | Periodic KYC refresh | [N] days before due | Due date | Yes | KYC Team Lead |

---

## Workbasket reference

| Workbasket name | Owner | Receives |
|----------------|-------|---------|
| `KYC-Initiation-WB` | KYC Operations | New CDD cases awaiting initiation |
| `KYC-DocReview-WB` | KYC Document Team | Cases with uploaded documents awaiting review |
| `KYC-RMReview-WB` | Relationship Managers | MEDIUM risk cases |
| `KYC-Compliance-WB` | Compliance Officers | HIGH risk, PEP, EDD cases |
| `KYC-Sanctions-WB` | Sanctions Review Team | Sanctions hit cases |
| `KYC-MLRO-WB` | MLRO | SAR and escalated sanctions cases |
| `KYC-Manual-Screening-WB` | KYC Operations | Cases where automated screening failed |
| `KYC-PeriodicReview-WB` | KYC Operations | Cases due for periodic review |

---

## Decision outcomes and case status transitions

| Decision | Actor | Case status after decision |
|---------|-------|--------------------------|
| Auto-approved | System | `Resolved-Approved` |
| RM approved | Relationship Manager | `Resolved-Approved` (LOW/MEDIUM) or routed to Compliance (if concerns flagged) |
| RM rejected | Relationship Manager | `Resolved-Rejected` |
| RM escalated | Relationship Manager | `Open-ComplianceReview` |
| Compliance approved | Compliance Officer | `Resolved-Approved` (single approval) or → Checker (dual approval) |
| Compliance rejected | Compliance Officer | `Resolved-Rejected` |
| Compliance EDD required | Compliance Officer | `Open-EDDReview` (sub-flow spawned) |
| Checker approved | Senior Compliance Officer | `Resolved-Approved` |
| Checker rejected | Senior Compliance Officer | `Resolved-Rejected` |
| Checker sent back | Senior Compliance Officer | `Open-ComplianceReview` (returned to Maker) |
| Sanctions cleared | Sanctions Reviewer | Return to main flow |
| Sanctions escalated | Sanctions Reviewer | `Open-MLROReview` |
| MLRO SAR filed | MLRO | `Open-SARFiled` → `Resolved-SARSubmitted` |
| MLRO account blocked | MLRO | `Resolved-Blocked` |
| Document rejected | Document Reviewer | `Open-DocumentResubmission` (notification to customer) |
| SLA breached | System (automatic) | Status unchanged + SLA breach flag set + escalation assignment created |

---

## Maker-checker pattern (PEGA implementation)

```
Step 1: Maker Assignment (Compliance Officer)
    │── Actor: pyAssignedOperatorID = ComplianceOfficerA
    │── Screen: ComplianceReviewSection
    │── Action buttons: Submit Decision, Request More Info, Escalate
    └── On submit: captures pxSubmittedByName = ComplianceOfficerA

Step 2: Checker Assignment (Senior Compliance Officer)
    │── Actor: pyAssignedOperatorID ≠ pxSubmittedByName (enforced by Router)
    │── Screen: CheckerReviewSection (read-only view of Maker decision + full case)
    │── Action buttons: Approve, Reject, Send Back to Maker
    └── Constraint enforced by: Router rule checks pyCurrentOperatorID ≠ pxSubmittedByName
```

**Key constraint**: The Router rule for the Checker assignment must exclude the Maker. This is implemented in PEGA by:
- Router type: Skill-based or To-WorkBasket
- When condition on the router: `pyAssignedOperatorID != pxSubmittedByName`
- If the only available Checker is the Maker, escalate to senior or hold in queue

---

## Escalation chain pattern

```
Assignment created
    │
    ├── [SLA Goal reached — e.g. 24 hours]
    │       └── Urgency increases (visual indicator on case)
    │
    ├── [SLA Deadline reached — e.g. 48 hours]
    │       ├── pyStatusWork = existing status + "-SLABreached" flag set
    │       ├── New assignment created in escalation workbasket
    │       ├── Notification sent to escalation target
    │       └── Audit log: SLA breach recorded
    │
    └── [Second SLA Deadline — e.g. 72 hours]
            ├── Escalated further to Head of Compliance workbasket
            └── Dashboard flag: regulatory escalation risk
```
