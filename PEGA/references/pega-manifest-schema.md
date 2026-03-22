# PEGA Manifest Schema — Parsing Guide

> **For agents**: Common JSON structures you'll encounter in PEGA exports.

## Manifest Wrapper

Most PEGA exports wrap rules in one of these structures:

### Format A: Array of Rules
```json
{
  "pxResultCount": 150,
  "pxResults": [
    { "pxObjClass": "Rule-Obj-Flow", "pyRuleName": "...", ... },
    { "pxObjClass": "Rule-Obj-When", "pyRuleName": "...", ... }
  ]
}
```

### Format B: Flat Array
```json
[
  { "pxObjClass": "Rule-Obj-Flow", "pyRuleName": "...", ... },
  { "pxObjClass": "Rule-Obj-When", "pyRuleName": "...", ... }
]
```

### Format C: Grouped by Type
```json
{
  "flows": [ { ... } ],
  "decisions": [ { ... } ],
  "sections": [ { ... } ],
  "connectors": [ { ... } ]
}
```

### Format D: Product Rule Export (RAP/ZIP manifest)
```json
{
  "pxObjClass": "Data-Admin-Product-Rule",
  "pyProductName": "MyApp",
  "pyProductVersion": "01.01.01",
  "pyRuleSetList": [
    { "pyRuleSet": "MSFWApp", "pyRuleSetVersion": "01-01-01" }
  ],
  "pyRules": [ { ... } ]
}
```

**Agent instruction**: Try to identify which format the user's manifest uses, then navigate to the rule array accordingly.

## Common Rule Entry Fields

Every rule entry typically has these fields:

```json
{
  // Identity
  "pxObjClass": "Rule-Obj-Flow",           // Rule type (MOST IMPORTANT for routing)
  "pzInsKey": "RULE-OBJ-FLOW MYAPP-WORK LOANORIGINATION #20240101T120000.000 GMT",
  "pyRuleName": "LoanOrigination",          // Short rule name
  "pyLabel": "Loan Origination Process",    // Human-readable label

  // Classification
  "pyClassName": "MyApp-Work-Loan",         // Class this rule belongs to
  "pyRuleSet": "MSFWApp",                   // Ruleset (≈ application layer)
  "pyRuleSetVersion": "01-01-01",           // Version

  // Metadata
  "pxCreateDateTime": "2024-01-15T10:30:00Z",
  "pxUpdateDateTime": "2024-06-20T14:22:00Z",
  "pyDescription": "Main loan origination flow",
  "pxCreateOperator": "admin@company",

  // Content (varies by rule type — see below)
  "pySteps": [ ... ],         // For flows
  "pyConditions": [ ... ],    // For decisions
  "pyProperties": [ ... ]     // For sections
}
```

## Flow Rule Content

```json
{
  "pxObjClass": "Rule-Obj-Flow",
  "pyFlowType": "LoanOrigination",

  "pySteps": [
    {
      "pyStepID": "Step1",
      "pyStepType": "START",
      "pyStepLabel": "Begin Application",
      "pyStepPage": ""
    },
    {
      "pyStepID": "Step2",
      "pyStepType": "ASSIGNMENT",
      "pyStepLabel": "Enter Applicant Info",
      "pyFlowAction": "SubmitApplication",
      "pyHarness": "Perform",
      "pySection": "ApplicantInfoSection",
      "pyAssignTo": "CurrentUser",
      "pyAssignmentType": "WorkList"
    },
    {
      "pyStepID": "Step3",
      "pyStepType": "DECISION",
      "pyStepLabel": "Check Eligibility",
      "pyWhenRule": "isEligible",
      "pyDecisionTable": "EligibilityCheck"
    },
    {
      "pyStepID": "Step4",
      "pyStepType": "SUBPROCESS",
      "pyStepLabel": "Credit Check Flow",
      "pyFlowType": "CreditCheckProcess",
      "pyClassName": "MyApp-Work-Loan"
    },
    {
      "pyStepID": "Step5",
      "pyStepType": "UTILITY",
      "pyStepLabel": "Calculate Rate",
      "pyActivityName": "CalculateInterestRate",
      "pyClassName": "MyApp-Work-Loan"
    },
    {
      "pyStepID": "Step6",
      "pyStepType": "INTEGRATOR",
      "pyStepLabel": "Call Credit Bureau",
      "pyConnectorName": "CreditBureauService",
      "pyDataPageName": "D_CreditReport"
    },
    {
      "pyStepID": "Step7",
      "pyStepType": "END",
      "pyStepLabel": "Application Complete",
      "pyStatusValue": "Resolved-Completed"
    }
  ],

  "pyConnectors": [
    {
      "pyFromStep": "Step1",
      "pyToStep": "Step2",
      "pyConnectorType": "ALWAYS",
      "pyConnectorLabel": ""
    },
    {
      "pyFromStep": "Step3",
      "pyToStep": "Step4",
      "pyConnectorType": "WHEN_TRUE",
      "pyConnectorLabel": "Eligible",
      "pyWhenRule": "isEligible"
    },
    {
      "pyFromStep": "Step3",
      "pyToStep": "StepReject",
      "pyConnectorType": "WHEN_FALSE",
      "pyConnectorLabel": "Not Eligible"
    },
    {
      "pyFromStep": "Step3",
      "pyToStep": "StepManual",
      "pyConnectorType": "OTHERWISE",
      "pyConnectorLabel": "Manual Review"
    }
  ]
}
```

## Decision Table Content

```json
{
  "pxObjClass": "Rule-Obj-DecisionTable",
  "pyRuleName": "EligibilityCheck",
  "pyPurpose": "Checks if applicant meets minimum criteria",

  "pyEvaluationMode": "FIRST_MATCH",

  "pyConditionColumns": [
    {
      "pyColumnName": "Age",
      "pyProperty": ".Applicant.Age",
      "pyOperator": ">=",
      "pyColumnType": "Integer"
    },
    {
      "pyColumnName": "Income",
      "pyProperty": ".Applicant.MonthlyIncome",
      "pyOperator": ">=",
      "pyColumnType": "Decimal"
    }
  ],

  "pyResultColumns": [
    {
      "pyColumnName": "Eligibility",
      "pyProperty": ".Application.IsEligible",
      "pyColumnType": "Boolean"
    },
    {
      "pyColumnName": "Reason",
      "pyProperty": ".Application.EligibilityReason",
      "pyColumnType": "Text"
    }
  ],

  "pyRows": [
    {
      "pyConditions": ["18", "3000"],
      "pyResults": ["true", "Meets all criteria"]
    },
    {
      "pyConditions": ["", ""],
      "pyResults": ["false", "Does not meet minimum criteria"],
      "pyIsOtherwise": true
    }
  ]
}
```

## Section Rule Content

```json
{
  "pxObjClass": "Rule-Obj-Section",
  "pyRuleName": "ApplicantInfoSection",
  "pyClassName": "MyApp-Work-Loan",

  "pyLayout": "INLINE_GRID_DOUBLE",

  "pyFields": [
    {
      "pyPropertyName": ".Applicant.FirstName",
      "pyLabel": "First Name",
      "pyControlType": "pxTextInput",
      "pyRequired": true,
      "pyReadOnly": false,
      "pyMaxLength": 50,
      "pyVisibleWhen": "",
      "pyEditableWhen": ""
    },
    {
      "pyPropertyName": ".Loan.Amount",
      "pyLabel": "Loan Amount",
      "pyControlType": "pxCurrency",
      "pyRequired": true,
      "pyReadOnly": false,
      "pyMinValue": 1000,
      "pyMaxValue": 500000,
      "pyVisibleWhen": "",
      "pyEditableWhen": ""
    },
    {
      "pyPropertyName": ".Loan.Purpose",
      "pyLabel": "Loan Purpose",
      "pyControlType": "pxDropdown",
      "pyRequired": true,
      "pyDataSource": "D_LoanPurposeList",
      "pyDisplayProperty": ".pyLabel",
      "pyValueProperty": ".pyCode"
    }
  ],

  "pyButtons": [
    {
      "pyLabel": "Submit",
      "pyActionType": "FlowAction",
      "pyFlowActionName": "SubmitApplication"
    },
    {
      "pyLabel": "Save for Later",
      "pyActionType": "LocalAction",
      "pyLocalActionName": "SaveDraft"
    }
  ]
}
```

## Connect-REST Content

```json
{
  "pxObjClass": "Rule-Connect-REST",
  "pyRuleName": "CreditBureauService",

  "pyServiceURL": "https://api.creditbureau.com/v2/credit-check",
  "pyHTTPMethod": "POST",
  "pyContentType": "application/json",

  "pyAuthentication": {
    "pyAuthType": "API_KEY",
    "pyHeaderName": "X-API-Key",
    "pyKeyReference": "CreditBureauAPIKey"
  },

  "pyTimeout": 30,
  "pyRetryCount": 1,

  "pyRequestDataTransform": "MapCreditRequest",
  "pyResponseDataTransform": "MapCreditResponse",

  "pyErrorHandling": {
    "pyOnTimeout": "RETRY_THEN_MANUAL",
    "pyOnError400": "DISPLAY_ERROR",
    "pyOnError500": "ROUTE_TO_QUEUE"
  }
}
```

## Binary Reference Pattern

When a rule's content is stored in a binary file:

```json
{
  "pxObjClass": "Rule-Obj-Flow",
  "pyRuleName": "ComplexFlow",
  "pyBinaryFile": true,
  "pyBinaryRef": "export/rules/Rule-Obj-Flow_ComplexFlow.bin",
  "pyContent": null
}
```

**Agent response**: Flag this and ask user for an alternative:
- Re-export with JSON content instead of binary
- Provide a screenshot from Designer Studio
- Provide any documentation about this rule
