# Skill: Manifest Parser

> **Referenced by**: All agents
> **Purpose**: Understands PEGA manifest JSON structure and extracts relevant data

---

## WHEN TO USE THIS SKILL

Use whenever you receive a raw manifest JSON file and need to locate specific rule types within it.

## PEGA MANIFEST STRUCTURE

A PEGA export manifest typically contains an array of rule entries. Each entry represents one PEGA rule (a flow, decision, section, connector, etc.).

### Common Top-Level Fields

```json
{
  "pxObjClass": "Rule-Obj-Flow",          // Rule type class
  "pyClassName": "MyApp-Work-Loan",        // Application class this belongs to
  "pyRuleName": "LoanOrigination",         // Rule name
  "pyRuleSet": "MSFWApp",                  // Which ruleset (≈ layer)
  "pyRuleSetVersion": "01-01-01",          // Version
  "pyLabel": "Loan Origination Process",   // Human-readable label
  "pzInsKey": "RULE-OBJ-FLOW ...",         // Unique key
  "pyPurpose": "...",                      // Description if available
  "content": { ... }                       // The actual rule content (or binary ref)
}
```

### Rule Type Identification

```
pxObjClass value          → What it is            → Which agent handles it
──────────────────────────────────────────────────────────────────────────
Rule-Obj-Flow             → Process flow           → Agent 01 / 05
Rule-Obj-FlowAction       → Flow action (submit)   → Agent 04
Rule-Obj-When             → When condition          → Agent 02
Rule-Obj-DecisionTable    → Decision table          → Agent 02
Rule-Obj-DecisionTree     → Decision tree           → Agent 02
Rule-Obj-MapValue         → Map value lookup        → Agent 02
Rule-Obj-Section          → UI section              → Agent 04
Rule-Obj-Harness          → UI harness/screen       → Agent 04
Rule-Connect-REST         → REST connector          → Agent 03
Rule-Connect-SOAP         → SOAP connector          → Agent 03
Rule-Connect-SQL          → SQL connector           → Agent 03
Rule-Obj-DataPage         → Data page definition    → Agent 03
Rule-Obj-Activity         → Activity (code)         → Agent 01 (note it)
Rule-Obj-DataTransform    → Data transform (mapping)→ Agent 03
Rule-Obj-Validate         → Validation rule         → Agent 04
Rule-Obj-Property         → Property definition     → Agent 04
Rule-Obj-Declare-Expr     → Declare expression      → Agent 02
Rule-Obj-Declare-Constr   → Constraint              → Agent 02
Rule-Obj-Report-Def       → Report definition       → (note for FRD)
Rule-Obj-Correspondence   → Email/notification      → Agent 03
Rule-Obj-SLA              → SLA rule                → Agent 01
```

### Finding Flow Content

Flow rules contain shape and connector data in their content. Look for:

```json
{
  "content": {
    "pySteps": [                    // Array of flow shapes
      {
        "pyStepType": "ASSIGNMENT", // Shape type
        "pyStepLabel": "Enter Info",// Label
        "pyFlowAction": "Submit",   // For assignments: which flow action
        "pyHarness": "Perform",     // For assignments: which harness
        "pySection": "ApplicantInfo"// For assignments: which section
      }
    ],
    "pyConnectors": [               // Array of connections
      {
        "pyFromStep": "Step1",
        "pyToStep": "Step2",
        "pyConnectorType": "ALWAYS",
        "pyWhenRule": ""            // When rule name if conditional
      }
    ]
  }
}
```

### Finding Decision Content

```json
{
  "pxObjClass": "Rule-Obj-DecisionTable",
  "content": {
    "pyConditions": [               // Columns
      { "pyProperty": ".Age", "pyOperator": ">=", "pyCompareValue": "18" }
    ],
    "pyResults": [                  // Rows × actions
      { "pyConditionValues": ["18"], "pyActionValue": "ELIGIBLE" }
    ],
    "pyEvaluationMode": "FIRST_MATCH"
  }
}
```

### Handling Binary References

When content points to a binary file instead of inline JSON:

```json
{
  "pyRuleName": "ComplexFlow",
  "content": {
    "pyBinaryRef": "rules/flows/ComplexFlow_v2.bin"
  }
}
```

**Response protocol**:
1. Note the binary reference
2. Ask: "This rule's content is in binary format at [path]. Can you either export the JSON version or provide a screenshot?"
3. Continue analyzing other rules
4. Add to pending items

## QUICK SEARCH PATTERNS

To find specific items in a large manifest:

```
All flows:        filter where pxObjClass contains "Flow" and NOT "FlowAction"
All decisions:    filter where pxObjClass contains "Decision" or "When" or "MapValue"
All connectors:   filter where pxObjClass contains "Connect"
All UI screens:   filter where pxObjClass contains "Section" or "Harness"
All properties:   filter where pxObjClass contains "Property"
All data pages:   filter where pxObjClass contains "DataPage"
By layer:         filter where pyRuleSet = "[layer name]"
By class:         filter where pyClassName = "[class name]"
```
