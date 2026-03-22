# Skill: Recursive Flow Tracer

> **Referenced by**: Agent 01 (Flow Analyzer), Agent 05 (Deep Analyzer)
> **Purpose**: Provides the recursive algorithm for tracing sub-flow chains

---

## WHEN TO USE THIS SKILL

Use when you encounter a **subprocess** or **sub-flow** reference in a flow analysis. The parent flow calls another flow, and that flow may call others, creating a chain that must be fully traced.

## RECURSIVE TRACING ALGORITHM

```
FUNCTION trace_flow(flow_manifest_entry, depth, parent_context):

  IF depth > 10:
    WARN "Maximum recursion depth reached — possible circular reference"
    RETURN partial_result + flag_circular_warning

  1. EXTRACT all shapes from flow_manifest_entry
  2. EXTRACT all connectors

  3. FOR EACH shape WHERE type = "subprocess" OR type = "utility":
     a. GET referenced_rule_name from shape properties
     b. SEARCH manifest for referenced_rule_name
     c. IF found:
        result = trace_flow(referenced_manifest_entry, depth + 1, current_flow)
        ATTACH result as children of this shape
     d. IF not found:
        FLAG "Unresolved reference: [rule_name] — may be in another layer"
        ADD to pending_items: "Locate [rule_name] in [other layers]"

  4. FOR EACH shape WHERE type = "integrator" OR references a Connect rule:
     FLAG for Integration Scanner (Agent 03)

  5. FOR EACH shape WHERE type = "decision":
     FLAG for Decision Mapper (Agent 02)

  6. RETURN {
       flow_name: [name],
       depth: [current depth],
       nodes: [list],
       edges: [list],
       child_flows: [recursively traced results],
       unresolved: [list of things not found],
       integrations_found: [list],
       decisions_found: [list]
     }
```

## CALL CHAIN TRACKING

Maintain a call chain to detect circular references:

```
Call chain: MainFlow → CreditCheckFlow → VerificationSubFlow → ...

If any flow appears twice in the chain → CIRCULAR REFERENCE
  Action: Stop recursion, flag the circular path, continue with other branches
```

## CROSS-LAYER RESOLUTION

When a sub-flow reference points to a different application layer:

```
Current flow layer: MSFWApp
Sub-flow reference: "CreditCheckProcess"
Not found in MSFWApp manifest

SEARCH ORDER:
  1. Same layer (MSFWApp)
  2. Parent layer (CRDFWApp) — framework flows
  3. Grandparent layer (COB) — core business flows
  4. Base layer (PegaRules) — base PEGA rules

If found in another layer:
  Note: "CreditCheckProcess found in CRDFWApp layer"
  Continue tracing from that layer's manifest

If not found in any layer:
  Flag: "UNRESOLVED — may be a standard PEGA OOTB flow or custom extension"
  Ask user for clarification
```

## OUTPUT: CALL CHAIN TREE

```
MainFlow (MSFWApp, depth 0)
├── Step 3: CreditCheckFlow (CRDFWApp, depth 1)
│   ├── Step 2: BureauCallActivity (CRDFWApp, depth 2) [INTEGRATION]
│   └── Step 5: ScoreCalculation (COB, depth 2) [DECISION]
├── Step 7: DocumentUploadFlow (MSFWApp, depth 1)
│   └── Step 3: OCRExtractionCall (MSFWApp, depth 2) [INTEGRATION]
└── Step 11: AccountSetupFlow (PegaRules, depth 1)
    └── Step 4: CoreBankingCall (COB, depth 2) [INTEGRATION]
```

## DEPTH TRACKING FORMAT

```
Each traced item records:
  - flow_name: which flow
  - layer: which application layer
  - depth: how many levels deep from the original flow
  - parent: which flow called this one
  - type: flow / activity / decision / integration
```
