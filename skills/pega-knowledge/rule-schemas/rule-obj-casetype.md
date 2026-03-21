# Schema: Rule-Obj-CaseType

> Inject when analysing a PEGA Case Type rule. This is the root of a KYC workflow — it defines the case lifecycle, stages, processes, and entry flows.

---

## Role in the rule graph

```
Rule-Obj-CaseType          ← ROOT of every KYC workflow
    │
    ├── pyStages[]          → each stage contains pyProcesses[]
    │       └── pyProcesses[]   → each process references a Rule-Obj-Flow
    │               └── pyFlowName  → Rule-Obj-Flow (follow this reference)
    │
    ├── pyStartingFlow      → Rule-Obj-Flow  (entry flow — always follow)
    ├── pyCreateFlow        → Rule-Obj-Flow  (case creation flow)
    └── pyActionFlows[]     → Rule-Obj-Flow  (case-wide action flows)
```

---

## JSON field reference

```json
{
  "pyRuleName":        "KYC-Work-CDD",
  "pyClassName":       "KYC-Work-CDD",
  "pxObjClass":        "Rule-Obj-CaseType",
  "pyLabel":           "Customer Due Diligence",
  "pyDescription":     "Standard KYC CDD case type for individual customers",
  "pyWorkIDPrefix":    "KYC-",
  "pyStartingFlow":    "pyStartCase",
  "pyCreateFlow":      "KYC_CDDCreate",
  "pyDefaultUrgency":  "10",
  "pyCaseLocking":     "Optimistic",

  "pyStages": [
    {
      "pyStageName":   "Initiation",
      "pyStageLabel":  "Initiation",
      "pyStageID":     "S-1",
      "pyProcesses": [
        {
          "pyProcessName":  "Collect Details",
          "pyFlowName":     "KYC_CollectCDDDetails",
          "pyFlowClass":    "KYC-Work-CDD"
        }
      ],
      "pyEntryCondition": "",
      "pyExitCondition":  "DocumentsVerified == true"
    },
    {
      "pyStageName":   "Screening",
      "pyStageID":     "S-2",
      "pyProcesses": [
        {
          "pyProcessName": "Sanctions & PEP Check",
          "pyFlowName":    "KYC_SanctionsScreening",
          "pyFlowClass":   "KYC-Work-CDD"
        },
        {
          "pyProcessName": "Risk Scoring",
          "pyFlowName":    "KYC_RiskScoring",
          "pyFlowClass":   "KYC-Work-CDD"
        }
      ]
    },
    {
      "pyStageName":   "Approval",
      "pyStageID":     "S-3",
      "pyProcesses": [
        {
          "pyProcessName": "Approval",
          "pyFlowName":    "KYC_CDDApproval",
          "pyFlowClass":   "KYC-Work-CDD"
        }
      ]
    },
    {
      "pyStageName":   "Complete",
      "pyStageID":     "S-4",
      "pyIsFinal":     true
    }
  ],

  "pyActionFlows": [
    {
      "pyActionName":  "Reopen",
      "pyFlowName":    "pyReOpen",
      "pyPrivilege":   "ReopenCase"
    }
  ],

  "pyCaseRelationships": [
    {
      "pyRelationshipType": "Child",
      "pyChildClass":       "KYC-Work-EDD",
      "pyRelationshipName": "EDD Sub-case"
    }
  ],

  "pyStatusWorkList": [
    "Open-Initiation",
    "Open-Screening",
    "Open-Approval",
    "Open-SanctionsReview",
    "Open-EDDRequired",
    "Resolved-Approved",
    "Resolved-Rejected",
    "Resolved-Withdrawn"
  ]
}
```

---

## What to extract during recursive analysis

| Field | Recurse into? | Rule type discovered |
|-------|--------------|---------------------|
| `pyStartingFlow` | Yes | Rule-Obj-Flow |
| `pyCreateFlow` | Yes | Rule-Obj-Flow |
| `pyStages[].pyProcesses[].pyFlowName` | Yes | Rule-Obj-Flow |
| `pyActionFlows[].pyFlowName` | Yes | Rule-Obj-Flow |
| `pyCaseRelationships[].pyChildClass` | Yes (load its CaseType) | Rule-Obj-CaseType |

---

## Analysis output for CaseType

When narrating a CaseType, produce:

1. **Case lifecycle overview** — stages in order with entry/exit conditions
2. **Process inventory** — all flows per stage, with their purpose
3. **Status transition map** — all valid statuses and what triggers each
4. **Child case relationships** — linked sub-cases and their trigger conditions
5. **Access control summary** — which access groups can perform which actions

---

## Common issues to flag

- Missing exit conditions on stages → case may get stuck in stage
- No action flow for Reopen → cannot recover from incorrect resolution
- Child case class not found in hierarchy → broken relationship
- Stage with no processes → effectively a skip-through stage (confirm intentional)
