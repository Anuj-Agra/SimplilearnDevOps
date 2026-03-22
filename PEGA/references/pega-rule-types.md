# PEGA Rule Types — Quick Reference

> **For agents**: Use this to identify what you're looking at in a manifest.

## Rule Categories

### Process Rules (Agents 01, 05)
| Rule Type | pxObjClass | What It Does |
|-----------|-----------|--------------|
| Flow | Rule-Obj-Flow | Visual process flow (the main diagrams) |
| Flow Action | Rule-Obj-FlowAction | What happens when user submits a form step |
| Activity | Rule-Obj-Activity | Server-side code/logic (like a function) |
| Data Transform | Rule-Obj-DataTransform | Maps data from A to B (copy/set properties) |
| SLA | Rule-Obj-SLA | Service Level Agreement (deadlines/escalations) |

### Decision Rules (Agent 02)
| Rule Type | pxObjClass | What It Does |
|-----------|-----------|--------------|
| Decision Table | Rule-Obj-DecisionTable | Grid of conditions → actions |
| Decision Tree | Rule-Obj-DecisionTree | Branching if/then/else tree |
| When Rule | Rule-Obj-When | Single true/false condition check |
| Map Value | Rule-Obj-MapValue | Key → value lookup table |
| Declare Expression | Rule-Obj-Declare-Expr | Auto-calculated property |
| Declare Constraint | Rule-Obj-Declare-Constr | Validation constraint |

### Integration Rules (Agent 03)
| Rule Type | pxObjClass | What It Does |
|-----------|-----------|--------------|
| Connect REST | Rule-Connect-REST | Calls a REST API |
| Connect SOAP | Rule-Connect-SOAP | Calls a SOAP web service |
| Connect SQL | Rule-Connect-SQL | Runs a database query |
| Connect File | Rule-Connect-File | Reads/writes files |
| Data Page | Rule-Obj-DataPage | Cached data (often backed by a connector) |
| Data Type | Rule-Obj-DataType | Defines a data structure for integrations |

### UI Rules (Agent 04)
| Rule Type | pxObjClass | What It Does |
|-----------|-----------|--------------|
| Harness | Rule-Obj-Harness | Top-level screen layout (frame) |
| Section | Rule-Obj-Section | Reusable UI panel with fields |
| Flow Action | Rule-Obj-FlowAction | Form submit behavior |
| Validate | Rule-Obj-Validate | Field/form validation logic |
| UI Action | Rule-Obj-UIAction | Button click behavior |
| Correspondence | Rule-Obj-Correspondence | Email/notification template |

### Data Model Rules
| Rule Type | pxObjClass | What It Does |
|-----------|-----------|--------------|
| Property | Rule-Obj-Property | Single data field definition |
| Class | Rule-Obj-Class | Object type definition (like a table) |
| Report Definition | Rule-Obj-Report-Def | Saved report/query |

## Inheritance and Layers

```
PEGA resolves rules by searching UP the hierarchy:

  Your App Layer (e.g., MSFWApp)
       ↑ if not found, check parent
  Framework Layer (e.g., CRDFWApp)
       ↑ if not found, check parent
  Organization Layer (e.g., COB)
       ↑ if not found, check parent
  PegaRules (base PEGA platform)

This means a flow in MSFWApp can reference a decision table
defined in CRDFWApp — it "inherits" it from the parent layer.
```

## Common PEGA System Classes

```
Work-              → Work items (cases)
Data-              → Data objects (reference data, lookups)
Embed-             → Embedded objects (child records)
Assign-            → Assignment/task objects
History-           → Audit/history records
Index-             → Search index entries
Rule-              → Rule definitions themselves
```
