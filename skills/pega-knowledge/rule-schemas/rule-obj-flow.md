# Schema: Rule-Obj-Flow

> Inject when analysing a PEGA Flow rule. Flows are the process backbone — they sequence steps, decisions, assignments, sub-flows, and external service calls.

---

## Role in the rule graph

```
Rule-Obj-Flow
    │
    ├── pyFlowSteps[].pyStepType = "Assignment"
    │       └── pyFlowActionName    → Rule-Obj-Flowsection (screen shown to user)
    │       └── pySLAName           → Rule-Obj-SLA
    │       └── pyRouterName        → Rule-Obj-Router
    │
    ├── pyFlowSteps[].pyStepType = "Utility"
    │       └── pyActivityName      → Rule-Obj-Activity  (follow this reference)
    │       └── pyConnectorName     → Rule-Connect-REST/SOAP
    │       └── pyDataTransformName → Rule-Obj-DataTransform
    │
    ├── pyFlowSteps[].pyStepType = "SubFlow"
    │       └── pySubFlowName       → Rule-Obj-Flow      (recurse into sub-flow)
    │       └── pySubFlowClass      → class of sub-flow
    │
    ├── pyFlowSteps[].pyStepType = "Decision"
    │       └── pyWhenName          → Rule-Obj-When      (follow this reference)
    │       └── pyDecisionName      → Rule-Obj-DecisionTable
    │
    ├── pyFlowSteps[].pyStepType = "Spinoff"
    │       └── pySubFlowName       → Rule-Obj-Flow      (async branch)
    │
    └── pyConnectors[].pyWhenName   → Rule-Obj-When      (branch condition)
```

---

## JSON field reference

```json
{
  "pyRuleName":    "KYC_CDDOnboarding",
  "pyClassName":   "KYC-Work-CDD",
  "pxObjClass":    "Rule-Obj-Flow",
  "pyFlowType":    "work",
  "pyDescription": "Main CDD onboarding process flow",

  "pyFlowSteps": [
    {
      "pyStepName":         "CollectCustomerDetails",
      "pyStepLabel":        "Collect Customer Details",
      "pyStepType":         "Assignment",
      "pyFlowActionName":   "KYC_CollectCDDDetails",
      "pyFlowActionClass":  "KYC-Work-CDD",
      "pySLAName":          "KYC-SLA-CDDInitiation",
      "pyRouterName":       "KYC_RouterToKYCOps",
      "pySkillName":        "",
      "pyWorkBasketName":   "KYC-Initiation-WB"
    },
    {
      "pyStepName":         "RunSanctionsCheck",
      "pyStepLabel":        "Run Sanctions Screening",
      "pyStepType":         "Utility",
      "pyActivityName":     "",
      "pyConnectorName":    "KYC-Conn-SanctionsAPI",
      "pyDataTransformName":"KYC_BuildSanctionsRequest"
    },
    {
      "pyStepName":         "EvaluateRisk",
      "pyStepLabel":        "Evaluate Risk",
      "pyStepType":         "Utility",
      "pyActivityName":     "KYC_CalculateRiskScore"
    },
    {
      "pyStepName":         "RiskDecision",
      "pyStepLabel":        "Risk Decision",
      "pyStepType":         "Decision",
      "pyWhenName":         "KYC_IsHighRisk",
      "pyDecisionName":     ""
    },
    {
      "pyStepName":         "RunEDDSubFlow",
      "pyStepLabel":        "Spawn EDD",
      "pyStepType":         "SubFlow",
      "pySubFlowName":      "KYC_EDDProcess",
      "pySubFlowClass":     "KYC-Work-EDD"
    },
    {
      "pyStepName":         "BackgroundCheck",
      "pyStepLabel":        "Background Check",
      "pyStepType":         "Spinoff",
      "pySubFlowName":      "KYC_BackgroundScreening",
      "pySubFlowClass":     "KYC-Work-CDD"
    },
    {
      "pyStepName":         "Split-ForAll",
      "pyStepType":         "Split-ForAll",
      "pySubFlowName":      "KYC_VerifyDocument",
      "pyForAllPageList":   "DocumentList"
    },
    {
      "pyStepName":         "EndApproved",
      "pyStepType":         "End",
      "pyStatusWork":       "Resolved-Approved"
    }
  ],

  "pyConnectors": [
    {
      "pyConnectName":  "ToSanctions",
      "pyStepFrom":     "CollectCustomerDetails",
      "pyStepTo":       "RunSanctionsCheck",
      "pyCondition":    "",
      "pyWhenName":     "",
      "pyLabel":        ""
    },
    {
      "pyConnectName":  "HighRiskPath",
      "pyStepFrom":     "RiskDecision",
      "pyStepTo":       "RunEDDSubFlow",
      "pyCondition":    "RiskRating == \"HIGH\"",
      "pyWhenName":     "KYC_IsHighRisk"
    },
    {
      "pyConnectName":  "LowRiskPath",
      "pyStepFrom":     "RiskDecision",
      "pyStepTo":       "EndApproved",
      "pyCondition":    "RiskRating == \"LOW\"",
      "pyWhenName":     "KYC_IsLowRisk"
    }
  ]
}
```

---

## Step type reference

| pyStepType | Meaning | References to follow |
|-----------|---------|---------------------|
| `Assignment` | Human task — creates an assignment in a workbasket | `pyFlowActionName` → Rule-Obj-Flowsection; `pySLAName`; `pyRouterName` |
| `Utility` | Automated step — calls an activity, connector, or data transform | `pyActivityName` → Rule-Obj-Activity; `pyConnectorName`; `pyDataTransformName` |
| `SubFlow` | Calls another flow synchronously — waits for it to complete | `pySubFlowName` → Rule-Obj-Flow (recurse) |
| `Spinoff` | Calls another flow asynchronously — does not wait | `pySubFlowName` → Rule-Obj-Flow (recurse, lower priority) |
| `Decision` | Branches based on a condition | `pyWhenName` → Rule-Obj-When; `pyDecisionName` → Decision Table |
| `Split` | Fork — start parallel paths | Follow each branch flow |
| `Split-ForAll` | Iterate a Page List — spawn sub-flow per item | `pySubFlowName` → Rule-Obj-Flow; `pyForAllPageList` |
| `Split-Join` | Wait for parallel paths to converge | Reference to matching Split step |
| `End` | Flow terminal — sets final status | `pyStatusWork` → case status value |

---

## Recursive traversal rules for flows

1. Follow ALL `SubFlow` references — these are synchronous and in-scope
2. Follow ALL `Spinoff` references — but flag as async (lower analysis priority)
3. Follow ALL `Decision` step `pyWhenName` references
4. Follow ALL connector `pyWhenName` references (branch conditions)
5. Follow `Assignment` step `pyFlowActionName` → Rule-Obj-Flowsection
6. Follow `Utility` step `pyActivityName` → Rule-Obj-Activity
7. Do NOT follow the same flow twice — track visited set to prevent infinite loops
8. Do NOT follow flows in a different class unless explicitly in scope

---

## What to extract during analysis

- **Entry point**: what step starts the flow (first step with no incoming connector)
- **Terminal points**: all `End` steps with their `pyStatusWork` values
- **Decision inventory**: all branches with conditions and destinations
- **Assignment inventory**: all human tasks with SLA, workbasket, and screen
- **External calls**: all Connector steps
- **Sub-flows**: all SubFlow and Spinoff references
- **When conditions used**: all referenced Rule-Obj-When names
