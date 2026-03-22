# Skill: Condition Extractor

> **Referenced by**: Agent 01, Agent 02, Agent 05
> **Purpose**: Parses PEGA condition expressions and when rules into readable English

---

## WHEN TO USE THIS SKILL

Use whenever you encounter a condition expression in a connector, decision rule, or visibility rule that needs to be translated to plain English.

## PEGA EXPRESSION SYNTAX → ENGLISH

### Comparison Operators
```
PEGA Expression              → Plain English
──────────────────────────────────────────────
.Property = "value"          → [Property] equals "value"
.Property != "value"         → [Property] is not "value"
.Property > 100              → [Property] is greater than 100
.Property >= 100             → [Property] is 100 or more
.Property < 100              → [Property] is less than 100
.Property <= 100             → [Property] is 100 or less
.Property == ""              → [Property] is blank/empty
.Property != ""              → [Property] has a value
.Property IS_IN "A,B,C"     → [Property] is one of: A, B, or C
.Property NOT_IN "A,B,C"    → [Property] is not A, B, or C
.Property STARTS_WITH "X"   → [Property] starts with "X"
.Property CONTAINS "X"      → [Property] contains "X"
```

### Logical Operators
```
cond1 AND cond2              → Both [condition 1] AND [condition 2] must be true
cond1 OR cond2               → Either [condition 1] OR [condition 2] must be true
NOT cond1                    → [condition 1] is NOT true
(cond1 OR cond2) AND cond3  → ([cond 1] or [cond 2]) AND also [cond 3]
```

### Property Path Navigation
```
.Applicant.FirstName         → the applicant's first name
.Application.Status          → the application's current status
.Loan.Amount                 → the loan amount
.CreditReport.Score          → the credit score from the credit report
.pyStatusWork                → the work item's status (PEGA system property)
.pxUrgencyWork               → the work item's urgency level
.pxAssignedOperatorID        → who the task is currently assigned to
```

### Common PEGA System Properties
```
.pyStatusWork                → Case/work item status
.pxUrgencyWork               → Urgency (higher = more urgent)
.pxCreateDateTime            → When the item was created
.pxUpdateDateTime            → When the item was last modified
.pxAssignedOperatorID        → Currently assigned user
.pyWorkGroup                 → Team/work group
.pyWorkParty                 → Involved parties
.pySLADeadline               → SLA deadline timestamp
.pySLAGoal                   → SLA goal timestamp
```

## TRANSLATION EXAMPLES

```
INPUT:  .Applicant.Age >= 18 AND .Applicant.ResidentStatus IS_IN "Citizen,Resident"
OUTPUT: "The applicant must be 18 years or older AND must be either a Citizen or Resident"

INPUT:  .Loan.Amount > 100000 AND .CreditReport.Score < 650
OUTPUT: "The loan amount exceeds $100,000 AND the credit score is below 650"

INPUT:  .pyStatusWork = "Pending-Approval" AND .pxUrgencyWork > 50
OUTPUT: "The case is in Pending-Approval status AND has high urgency (above 50)"

INPUT:  NOT(.Documents.IDProof != "") OR NOT(.Documents.AddressProof != "")
OUTPUT: "Either the ID proof document has not been uploaded OR the address proof has not been uploaded"
```

## HANDLING COMPLEX CONDITIONS

For deeply nested conditions, use indentation:

```
IF all of the following are true:
  1. The applicant is 18 or older
  2. AND one of the following:
     a. The applicant is a citizen
     b. OR the applicant is a permanent resident
  3. AND the loan amount is between $1,000 and $500,000
  4. AND the applicant has no bankruptcy in the last 7 years
THEN: Mark as eligible
OTHERWISE: Mark as ineligible with reason code
```

## WHEN RULE RESOLUTION

When a connector references a When rule by name (not inline expression):
1. Note the When rule name
2. Look for it in the manifest (pxObjClass = "Rule-Obj-When")
3. Extract its condition expression
4. Translate using the patterns above
5. If not found in manifest, flag as pending
