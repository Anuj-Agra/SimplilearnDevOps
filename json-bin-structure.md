# Skill: PEGA JSON & BIN Structure

> Inject this file into agents that need to read or interpret raw PEGA rule exports.

---

## How PEGA exports rules

PEGA exports rules in two formats:
- **JSON** — human-readable; produced by PEGA's export utilities and some migration tools
- **BIN** — binary serialised format; produced by PEGA's native archive/zip export (`.zip` containing `.bin` files per rule)

BIN files cannot be read directly — they must be decoded by PEGA tooling or by searching for readable string content within them.

---

## Universal fields (present in every rule JSON)

| Field | Type | Description |
|-------|------|-------------|
| `pyRuleName` | String | The rule's name — unique within the class + rule type combination |
| `pyClassName` | String | The PEGA class this rule belongs to (e.g. `KYC-Work-CDD`) |
| `pxObjClass` | String | Internal class identifier — usually matches `pyClassName` |
| `pyRuleSet` | String | The RuleSet this rule lives in (e.g. `KYCOnboarding`) |
| `pyRuleSetVersion` | String | Version in Major.Minor.Patch format (e.g. `01-01-01`) |
| `pyAvailability` | String | `Available`, `Blocked`, `Withdrawn`, `Final` |
| `pxCreateDateTime` | DateTime | Rule creation timestamp |
| `pxUpdateDateTime` | DateTime | Last modification timestamp |
| `pxCommittedByName` | String | Operator who last saved the rule |
| `pyDescription` | String | Human-readable description of the rule's purpose |
| `pyLabel` | String | Display label (used in UI) |

---

## Flow rule JSON fields

```json
{
  "pyRuleName": "KYC_CDDOnboarding",
  "pyClassName": "KYC-Work-CDD",
  "pyFlowType": "work",
  "pyCaseName": "KYC-Work-CDD",
  "pyFlowSteps": [
    {
      "pyStepName": "CollectCustomerDetails",
      "pyStepType": "Assignment",
      "pyFlowActionName": "KYC_CollectCDDDetails",
      "pySLAName": "KYC-SLA-CDDInitiation",
      "pyRouterName": "KYC_RouterCDDInitiation",
      "pyFlowActionClass": "KYC-Work-CDD"
    },
    {
      "pyStepName": "SanctionsCheck",
      "pyStepType": "Utility",
      "pyActivityName": "",
      "pyConnectorName": "KYC-Conn-SanctionsAPI",
      "pyDataTransformName": "KYC_BuildSanctionsRequest"
    },
    {
      "pyStepName": "RiskScoring",
      "pyStepType": "Utility",
      "pyDataTransformName": "KYC_CalculateRiskScore"
    },
    {
      "pyStepName": "RouteByRisk",
      "pyStepType": "Decision",
      "pyDecisionName": "KYC_RiskRoutingDecision"
    }
  ],
  "pyConnectors": [
    {
      "pyConnectName": "ToSanctionsCheck",
      "pyStepFrom": "CollectCustomerDetails",
      "pyStepTo": "SanctionsCheck",
      "pyCondition": "",
      "pyWhenName": ""
    },
    {
      "pyConnectName": "ToEDDFlow",
      "pyStepFrom": "RouteByRisk",
      "pyStepTo": "End",
      "pyCondition": "RiskRating == \"HIGH\"",
      "pyWhenName": "KYC_IsHighRisk"
    }
  ]
}
```

### Key Flow fields to read

| Field | Meaning |
|-------|---------|
| `pyFlowSteps[].pyStepType` | `Assignment` = human task; `Utility` = automated step; `Decision` = branching; `SubFlow` = calls another flow; `Split` = parallel; `Connector` = external service call |
| `pyFlowSteps[].pyFlowActionName` | The Flow Action rule that defines the screen/button for an Assignment step |
| `pyFlowSteps[].pySLAName` | SLA applied to this Assignment step |
| `pyFlowSteps[].pyRouterName` | Router rule that determines who gets the assignment |
| `pyFlowSteps[].pyConnectorName` | Connector rule called in a Connector step |
| `pyFlowSteps[].pySubFlowName` | Name of sub-flow called in a SubFlow step |
| `pyConnectors[].pyCondition` | PEGA expression evaluated for branching (e.g. `RiskRating == "HIGH"`) |
| `pyConnectors[].pyWhenName` | Name of a When condition rule (alternative to inline condition) |

---

## Data Transform rule JSON fields

```json
{
  "pyRuleName": "KYC_CalculateRiskScore",
  "pyClassName": "KYC-Work-CDD",
  "pyDataTransformSteps": [
    {
      "pyMode": "Set",
      "pyTarget": ".CountryRiskScore",
      "pySource": "@(DecisionTable 'KYC_CountryRiskTable', .CustomerNationality)",
      "pyWhenName": ""
    },
    {
      "pyMode": "Set",
      "pyTarget": ".OverallRiskScore",
      "pySource": "(.CountryRiskScore * 0.4) + (.CustomerTypeScore * 0.3) + (.PEPScore * 0.3)",
      "pyWhenName": ""
    },
    {
      "pyMode": "Set",
      "pyTarget": ".RiskRating",
      "pySource": "@(DecisionTable 'KYC_RiskThresholdTable', .OverallRiskScore)",
      "pyWhenName": ""
    },
    {
      "pyMode": "Set",
      "pyTarget": ".EDDRequired",
      "pySource": "true",
      "pyWhenName": "KYC_IsPEP"
    }
  ]
}
```

### pyMode values

| pyMode | Meaning |
|--------|---------|
| `Set` | Assign a value to the target property |
| `Default` | Assign only if target is currently empty |
| `Append` | Add a new entry to a Page List |
| `Remove` | Delete an entry from a Page List |
| `Map` | Copy a page structure (with property mapping) |
| `Update Page` | Apply sub-transform to an embedded page |

---

## Connector rule JSON fields

```json
{
  "pyRuleName": "KYC-Conn-SanctionsAPI",
  "pyClassName": "KYC-Work-CDD",
  "pyServiceURL": "https://api.sanctions-provider.com/v2/screen/individual",
  "pyHTTPMethod": "POST",
  "pyTimeout": "5000",
  "pyAuthProfile": "SanctionsAPIAuth",
  "pySSLProfile": "KYCTLSProfile",
  "pyRequestDataTransform": "KYC_BuildSanctionsRequest",
  "pyResponseDataTransform": "KYC_ParseSanctionsResponse",
  "pyResponseClass": "KYC-Data-SanctionsResponse",
  "pyHeaders": [
    { "pyName": "Content-Type", "pyValue": "application/json" },
    { "pyName": "Accept", "pyValue": "application/json" }
  ],
  "pyQueryParameters": [],
  "pyErrorHandling": "pyServiceFailed"
}
```

---

## Decision Table rule JSON fields

```json
{
  "pyRuleName": "KYC_CountryRiskTable",
  "pyClassName": "KYC-Work-CDD",
  "pyResultProperty": "CountryRiskScore",
  "pyResultType": "Integer",
  "pyColumns": [
    { "pyColumnName": "CustomerNationality", "pyOperator": "=" }
  ],
  "pyRows": [
    { "pyConditions": [{ "pyValue": "US" }], "pyResult": "20" },
    { "pyConditions": [{ "pyValue": "GB" }], "pyResult": "20" },
    { "pyConditions": [{ "pyValue": "IR" }], "pyResult": "90" },
    { "pyConditions": [{ "pyValue": "KP" }], "pyResult": "100" }
  ],
  "pyDefaultResult": "50"
}
```

---

## SLA rule JSON fields

```json
{
  "pyRuleName": "KYC-SLA-CDDReview",
  "pyClassName": "KYC-Work-CDD",
  "pyGoalInterval": "PT8H",
  "pyDeadlineInterval": "PT72H",
  "pyBusinessCalendar": "KYCBusinessCalendar",
  "pyEscalationChain": [
    {
      "pyEscalationTime": "PT48H",
      "pyEscalationTarget": "KYC-TeamLead-WorkBasket",
      "pyEscalationType": "Workbasket"
    },
    {
      "pyEscalationTime": "PT72H",
      "pyEscalationTarget": "Compliance-WorkBasket",
      "pyEscalationType": "Workbasket"
    }
  ]
}
```

### Interval format (ISO 8601 Duration)
- `PT8H` = 8 hours
- `PT72H` = 72 hours (3 days)
- `P3D` = 3 calendar days
- `P10D` = 10 calendar days

---

## BIN file reading guidance

When given a BIN file:
1. BIN files are Java-serialised objects — they are not human-readable in raw form
2. Look for readable string fragments: rule names, class names, endpoint URLs, property names often survive as readable UTF-8 strings within the binary
3. The rule name is typically near the start of the file as a UTF-8 string
4. Property references (`.PropertyName`) appear as readable strings
5. URLs and expression strings survive readably
6. Request the developer to export the rule as JSON via PEGA's App Studio or Dev Studio rule export, or via the PEGA Migration Manager
7. Alternatively, extract readable strings using: `strings <filename>.bin | grep -E "(py[A-Z]|KYC|http)" `
