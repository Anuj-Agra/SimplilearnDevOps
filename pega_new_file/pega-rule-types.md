# Pega Rule Types — Complete Reference

## Rule Type Classification

Pega Platform organises all system behaviour into "rules". Each rule has a
**class** (the data context it operates on) and a **type** (what it does).

---

## Core Rule Types

### Flow Rules (`RULE-OBJ-FLOW`)
**Purpose:** Define the end-to-end lifecycle of a case or work item.
**XML marker:** `<flow ...>`
**Key attributes:**
- `pyRuleName` — flow name
- Steps: `<step>`, `<assignment>`, `<subprocess>`, `<split>`, `<join>`
- Transitions: `<connector>` with `<when>` conditions

**PREA extraction notes:**
- Flow steps have `methodName` pointing to called activities
- `workParty` attributes identify human actors
- `<localflow>` elements are sub-flow calls

### Activities (`RULE-OBJ-ACTIVITY`)
**Purpose:** Procedural logic executed by the system or as flow steps.
**XML marker:** `<activity ...>`
**Key attributes:**
- Steps: `<step methodName="..." />` — calls Java methods or other activities
- Parameters passed via clipboard properties

### Data Transforms (`RULE-OBJ-MAP` / `RULE-OBJ-DATAMAP`)
**Purpose:** Map data between clipboard pages (equivalent to ETL transforms).
**XML marker:** `<map ...>` or `<dataTransform ...>`
**PREA extraction:** `data_mappings` array captures source→target pairs.

### Decision Tables (`RULE-OBJ-DECISION`)
**Purpose:** Tabular if/else logic producing a single result.
**XML marker:** `<decision ...>`
**PREA extraction:** `decision_rows` array with conditions and results.
**Business meaning:** Always translate to plain English business rules.

### Decision Trees
**Purpose:** Hierarchical branching decision logic.
**XML marker:** `<decisionTree ...>` or nested `<decision>` elements.

### When Rules (`RULE-OBJ-WHEN`)
**Purpose:** Named boolean conditions reused across the application.
**XML marker:** `<when ...>`
**PREA extraction:** `conditions` array captures the expression.
**Business meaning:** Each When Rule is typically one business rule statement.

### Validate Rules (`RULE-OBJ-VALIDATE`)
**Purpose:** Field and page-level validation executed on submit.
**XML marker:** `<validate ...>`
**PREA extraction:** `conditions` captures validation expressions.

### Declare Expressions (`RULE-OBJ-DECLARE`)
**Purpose:** Forward-chaining calculations that auto-execute when referenced properties change.
**XML marker:** `<declare ...>`
**Business meaning:** Automatically derived/calculated fields.

---

## UI Rules

### Section (`RULE-OBJ-FORM`, `pySection`)
**Purpose:** Reusable UI panel rendered within a harness.
**XML marker:** `<section ...>`
**PREA extraction:** `ui_fields` captures all field/control definitions.

### Harness (`RULE-OBJ-HARNESS`)
**Purpose:** Full-page UI layout container. Equivalent to a "page" or "screen".
**XML marker:** `<harness ...>`

### Header / Footer
**Purpose:** Page-level chrome elements within a harness.

### Portal (`RULE-OBJ-PORTAL`)
**Purpose:** Application entry point and navigation structure.

---

## Correspondence Rules

### Correspondence (`RULE-OBJ-CORR`)
**Purpose:** Email, letter, and document templates.
**XML marker:** `<correspondence ...>`
**Business meaning:** User-visible communications and notifications.

---

## Integration Rules

### Service REST / SOAP
**Purpose:** Expose Pega functionality as an API endpoint.
**XML marker:** `<servicerest ...>` / `<servicesoap ...>`

### Connector REST / SOAP
**Purpose:** Call external APIs from within Pega.
**XML marker:** `<connectorrest ...>` / `<connectorsoap ...>`

### Data Page (`RULE-OBJ-DATAPAGE`)
**Purpose:** Named, cacheable data source loaded onto the clipboard.
**XML marker:** `<datapage ...>`
**Business meaning:** "Where does the data come from?"

---

## Report Rules

### Report Definition (`RULE-OBJ-REPORT`)
**Purpose:** Structured query for lists and summaries displayed in grids.
**XML marker:** `<report ...>`

---

## Layer Override Mechanics

When the same rule exists in multiple layers, Pega uses the **highest layer**
at runtime:

```
Implementation (highest priority)
    ↓ overrides
Enterprise
    ↓ overrides
Industry
    ↓ overrides
Framework (lowest priority — Pega base)
```

**In PREA analysis:**
- Rules with `notes` containing "Overrides X layer" are override copies
- The decommission scorer increases risk for rules with active overrides
- Flow traces always follow the highest-layer version

---

## Class Hierarchy Conventions

Pega uses a dot-notation class hierarchy:

| Pattern | Meaning |
|---|---|
| `Work-` prefix | Work/case object (e.g. `Work-KYC-Case`) |
| `Data-` prefix | Data record (e.g. `Data-Party-Client`) |
| `Embed-` prefix | Embedded page (sub-object) |
| `Int-` prefix | Integration object |
| `@baseclass` | Applies to all classes |
| `@anyclass` | Applies regardless of class context |

**In PREA layer analysis:**
- `pega_class` in the rule record maps to these patterns
- Classes with `Work-` are typically the most business-critical
- `Embed-` classes contain reusable sub-forms
