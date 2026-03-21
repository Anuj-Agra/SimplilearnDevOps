# Schema: Rule-Obj-Activity

> Inject when analysing a PEGA Activity rule. Activities are procedural step sequences — the "imperative" layer of PEGA logic, used for complex automation in Classic PEGA.

---

## Role in the rule graph

```
Rule-Obj-Activity
    │
    ├── pySteps[].pyStepMethod = "CallActivity"
    │       └── pyStepPage + pyStepMethodParam "ActivityName" → Rule-Obj-Activity (recurse)
    │
    ├── pySteps[].pyStepMethod = "Property-Set"     (no external reference)
    ├── pySteps[].pyStepMethod = "Property-Map"     → references Data Transform
    ├── pySteps[].pyStepMethod = "Connect-*"        → references Connector rule
    ├── pySteps[].pyStepMethod = "Obj-Open"         → references a class/case
    ├── pySteps[].pyStepMethod = "Obj-Save"         → persists a page
    ├── pySteps[].pyStepMethod = "Declare-Run"      → runs Declare Expressions
    └── pySteps[].pyWhenName                        → Rule-Obj-When (condition on step)
```

---

## JSON field reference

```json
{
  "pyRuleName":   "KYC_CalculateRiskScore",
  "pyClassName":  "KYC-Work-CDD",
  "pxObjClass":   "Rule-Obj-Activity",
  "pyDescription":"Calculates the composite KYC risk score",

  "pyParameters": [
    { "pyName": "CustomerClass",  "pyType": "String",  "pyDirection": "In" },
    { "pyName": "RiskScore",      "pyType": "Decimal", "pyDirection": "Out" }
  ],

  "pySteps": [
    {
      "pyStepIndex":    1,
      "pyStepLabel":    "Get country risk score",
      "pyStepMethod":   "Property-Set",
      "pyStepPage":     "",
      "pyStepParam_propertyName":  ".CountryRiskScore",
      "pyStepParam_value":         "@(DecisionTable 'KYC_CountryRiskTable', .CustomerNationality)",
      "pyWhenName":     "",
      "pyWhenCondition":"",
      "pyOnError":      "Continue"
    },
    {
      "pyStepIndex":    2,
      "pyStepLabel":    "Call PEP check activity",
      "pyStepMethod":   "CallActivity",
      "pyStepPage":     "",
      "pyStepParam_ActivityName": "KYC_CheckPEPStatus",
      "pyWhenName":     "KYC_IsIndividualCustomer",
      "pyOnError":      "Break"
    },
    {
      "pyStepIndex":    3,
      "pyStepLabel":    "Set overall risk score",
      "pyStepMethod":   "Property-Set",
      "pyStepParam_propertyName": ".OverallRiskScore",
      "pyStepParam_value": "(.CountryRiskScore * 0.4) + (.CustomerTypeScore * 0.3) + (.PEPScore * 0.3)"
    },
    {
      "pyStepIndex":    4,
      "pyStepLabel":    "Save case",
      "pyStepMethod":   "Obj-Save",
      "pyStepPage":     "pyWorkPage"
    }
  ]
}
```

---

## Step methods to follow recursively

| pyStepMethod | Recurse? | What to follow |
|-------------|---------|---------------|
| `CallActivity` | Yes | `pyStepParam_ActivityName` → Rule-Obj-Activity |
| `Connect-REST` | Yes | Connector rule referenced in params |
| `Property-Map` | Yes | Data Transform referenced |
| `Obj-Open` | No | Documents data access |
| `Obj-Save` | No | Documents persistence |
| `Property-Set` | No | Documents property assignment |
| `Declare-Run` | No | Documents forward chaining trigger |
| any step | Check | `pyWhenName` → Rule-Obj-When |

---

## What to extract

- **Input / output parameters** — what data this activity expects and returns
- **Called activities** — recursive activity chain
- **External calls** — any Connect-* steps
- **Condition checks** — all `pyWhenName` references
- **Error handling** — `pyOnError` = Break (halts on fail) vs Continue (ignores error)
- **Side effects** — Obj-Save, Obj-Delete, correspondence steps

---

## Common issues to flag

- `pyOnError = Continue` on a critical step (e.g. Connect-REST) — silent failure risk
- Deep activity chains (> 5 levels) — performance and debugging risk
- Activities calling themselves (infinite recursion) — should be flagged
- No parameters defined but uses `.property` notation — relies on clipboard context

---
---

# Schema: Rule-Obj-Flowsection

> Inject when analysing a PEGA Flow Action rule (Rule-Obj-Flowsection). This defines the screen and processing associated with a human Assignment step in a flow.

---

## Role in the rule graph

```
Rule-Obj-Flowsection        ← Referenced by Flow step pyFlowActionName
    │
    ├── pyScreenName            → Rule-HTML-Section  (the UI screen shown)
    ├── pyPreActivity           → Rule-Obj-Activity  (runs before screen renders)
    ├── pyPostActivity          → Rule-Obj-Activity  (runs after user submits)
    ├── pyValidateActivity      → Rule-Obj-Activity  (validates input)
    ├── pyDataTransform         → Rule-Obj-DataTransform
    └── pyWhenConditions[]      → Rule-Obj-When      (visibility / availability)
```

---

## JSON field reference

```json
{
  "pyRuleName":          "KYC_CollectCDDDetails",
  "pyClassName":         "KYC-Work-CDD",
  "pxObjClass":          "Rule-Obj-Flowsection",
  "pyLabel":             "Collect CDD Details",
  "pyDescription":       "Screen for KYC Operator to enter customer identity details",

  "pyScreenName":        "CDDInitiation",
  "pyScreenClass":       "KYC-Work-CDD",

  "pyPreActivity":       "KYC_PreLoadCDDScreen",
  "pyPreActivityClass":  "KYC-Work-CDD",

  "pyPostActivity":      "KYC_PostSubmitCDD",
  "pyPostActivityClass": "KYC-Work-CDD",

  "pyValidateActivity":  "KYC_ValidateCDDInput",

  "pyActionButtons": [
    {
      "pyButtonLabel": "Submit",
      "pyButtonAction": "finishAssignment",
      "pyConnectName":  "ToSanctionsCheck"
    },
    {
      "pyButtonLabel": "Save Draft",
      "pyButtonAction": "saveWork"
    },
    {
      "pyButtonLabel": "Cancel",
      "pyButtonAction": "cancelAssignment"
    }
  ],

  "pyWhenConditions": [
    {
      "pyWhenName":    "KYC_IsReopenedCase",
      "pyEffect":      "ReadOnly",
      "pyTarget":      "CustomerName"
    }
  ]
}
```

---

## What to extract

- **Screen rendered**: `pyScreenName` → Rule-HTML-Section (always follow)
- **Pre-processing**: `pyPreActivity` → Rule-Obj-Activity (runs before display)
- **Post-processing**: `pyPostActivity` → Rule-Obj-Activity (runs on submit)
- **Validation**: `pyValidateActivity` → Rule-Obj-Activity
- **Action buttons**: what flow connectors each button triggers
- **Conditional behaviour**: which When rules affect field visibility or editability

---
---

# Schema: Rule-HTML-Section

> Inject when analysing a PEGA Section rule (Rule-HTML-Section). Sections define the UI — fields, layouts, embedded sections, and conditional display logic.

---

## Role in the rule graph

```
Rule-HTML-Section           ← Referenced by Flowsection pyScreenName or embedded in Harness
    │
    ├── pyFields[]
    │       └── pyWhen              → Rule-Obj-When (field-level visibility condition)
    │       └── pyValidate          → Validate rule (field validation)
    │       └── pyDataPageName      → Data Page (dropdown source)
    │
    ├── pyEmbeddedSections[]
    │       └── pySectionName       → Rule-HTML-Section (recurse into embedded section)
    │
    ├── pyRepeatingLayout
    │       └── pyPageListProperty  → property that drives the repeating grid
    │       └── pySectionName       → Rule-HTML-Section (row template — recurse)
    │
    └── pyWhenVisible               → Rule-Obj-When (section-level visibility)
```

---

## JSON field reference

```json
{
  "pyRuleName":      "CDDInitiation",
  "pyClassName":     "KYC-Work-CDD",
  "pxObjClass":      "Rule-HTML-Section",
  "pyLabel":         "CDD Initiation",
  "pyDescription":   "Customer details entry screen for CDD",

  "pyWhenVisible":   "KYC_IsCDDStage",

  "pyFields": [
    {
      "pyFieldType":          "Text",
      "pyPropertyReference":  ".CustomerFullName",
      "pyLabel":              "Customer full name",
      "pyRequired":           true,
      "pyReadOnly":           false,
      "pyMaxLength":          200,
      "pyWhen":               "",
      "pyValidate":           "KYC_ValidateCustomerName"
    },
    {
      "pyFieldType":          "Date",
      "pyPropertyReference":  ".CustomerDOB",
      "pyLabel":              "Date of birth",
      "pyRequired":           true,
      "pyWhen":               ""
    },
    {
      "pyFieldType":          "DropDown",
      "pyPropertyReference":  ".CustomerNationality",
      "pyLabel":              "Nationality",
      "pyRequired":           true,
      "pyDataPageName":       "D_CountryList",
      "pyDataPageClass":      "KYCOnboarding",
      "pyValueProperty":      "pyISOCode",
      "pyLabelProperty":      "pyLabel",
      "pyWhen":               ""
    },
    {
      "pyFieldType":          "Text",
      "pyPropertyReference":  ".TaxIdentificationNumber",
      "pyLabel":              "Tax ID / National ID",
      "pyRequired":           false,
      "pyWhen":               "KYC_IsTaxIDRequired"
    }
  ],

  "pyEmbeddedSections": [
    {
      "pySectionName":   "CDDAddressSection",
      "pySectionClass":  "KYC-Work-CDD",
      "pyWhen":          ""
    },
    {
      "pySectionName":   "CDDDocumentUploadSection",
      "pySectionClass":  "KYC-Work-CDD",
      "pyWhen":          "KYC_IsDocumentRequired"
    }
  ],

  "pyRepeatingLayout": {
    "pyPageListProperty": ".UBOList",
    "pySectionName":      "UBORowSection",
    "pyAddButtonLabel":   "Add UBO",
    "pyMaxRows":          10
  }
}
```

---

## What to extract

- **Field inventory**: every field with label, property, type, required flag, and any When condition
- **Embedded sections**: recurse into each `pySectionName` → Rule-HTML-Section
- **Repeating grids**: the Page List property driving the repeat, and the row template section
- **Data Page dropdowns**: source data pages for dropdown fields
- **Section-level visibility**: `pyWhenVisible` → Rule-Obj-When
- **Field-level conditions**: each `pyWhen` → Rule-Obj-When

---
---

# Schema: Rule-Obj-When

> Inject when analysing a PEGA When condition rule. When rules are named Boolean expressions used throughout PEGA to control branching, field visibility, and step execution.

---

## Role in the rule graph

```
Rule-Obj-When               ← Terminal node — does not reference other rules
    │
    └── pyExpression            ← Boolean expression using PEGA property references
                                   and @functions
```

When rules are **leaf nodes** — they do not reference other rules. They are the end of a recursive traversal branch.

---

## JSON field reference

```json
{
  "pyRuleName":    "KYC_IsHighRisk",
  "pyClassName":   "KYC-Work-CDD",
  "pxObjClass":    "Rule-Obj-When",
  "pyDescription": "True when the customer's risk rating is HIGH",

  "pyExpression":  ".RiskRating == \"HIGH\"",

  "pyExpressionType": "Simple",

  "pyConditions": [
    {
      "pyPropertyName":   ".RiskRating",
      "pyOperator":       "==",
      "pyValue":          "HIGH",
      "pyConnector":      ""
    }
  ]
}
```

---

## Expression types

| pyExpressionType | Meaning | Example |
|-----------------|---------|---------|
| `Simple` | Single property comparison | `.RiskRating == "HIGH"` |
| `Compound` | Multiple conditions with AND/OR | `.PEPFlag == true AND .RiskRating != "LOW"` |
| `Function` | Uses @function | `@Contains(.SanctionsHits, "OFAC")` |
| `Advanced` | Complex Java-like expression | Multi-line expressions |

---

## What to extract

- **Expression**: the full Boolean expression as a string
- **Properties referenced**: list every `.PropertyName` in the expression
- **Business meaning**: translate the expression to plain English
- **Used in**: catalogue where this When rule is referenced (flow connectors, field visibility, activity steps)

---

## Common When patterns in KYC

| When name pattern | Typical expression | Business meaning |
|------------------|-------------------|-----------------|
| `KYC_IsHighRisk` | `.RiskRating == "HIGH"` | Customer scored HIGH risk |
| `KYC_IsPEP` | `.PEPFlag == true` | Customer is a PEP |
| `KYC_IsEDDRequired` | `.EDDRequired == true` | EDD has been flagged |
| `KYC_IsSanctionsHit` | `.SanctionsHitFlag == true` | Confirmed sanctions hit |
| `KYC_IsAutoApprovable` | `.RiskRating == "LOW" AND .PEPFlag == false AND .SanctionsHitFlag == false` | All conditions for auto-approve met |
| `KYC_IsCorporateCustomer` | `.CustomerType == "Corporate"` | Legal entity (not individual) |
| `KYC_IsTaxIDRequired` | `@Contains("US,UK,DE", .CustomerNationality)` | Tax ID required for this country |
