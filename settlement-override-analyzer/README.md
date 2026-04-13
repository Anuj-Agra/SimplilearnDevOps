# Settlement Instruction Override Analyzer

Analyses 52K+ Natural modules and 13K+ JCL files to find fields where values are NOT received from upstream but are **overridden from reference tables and Adabas files** — specifically for **cash and securities settlement instruction** processing.

## The Problem This Solves

In settlement instruction processing, the upstream trade system sends a basic instruction. But the settlement system **enriches** it by:
- Looking up standing settlement instructions (SSI) by counterparty + market
- Applying custodian and depository details from reference tables
- Defaulting payment routing (BIC, account, agent) from standing data
- Overriding upstream values with market-specific rules

This tool traces exactly **which fields** are overridden, **from where**, and **why** — then produces a non-technical FRD.

## Quick Start

```bash
python scanner/settlement_scanner.py \
  --natural /path/to/52000-natural-modules \
  --jcl /path/to/13000-jcl-files \
  --output settlement_knowledge_graph.json \
  --frd Settlement_FRD.md \
  --workers 8
```

**Outputs:**
- `settlement_knowledge_graph.json` — Full knowledge graph (nodes, edges, override index, business rules)
- `Settlement_FRD.md` — Non-technical Functional Requirements Document for stakeholders

## What It Detects

For every field in every program, the scanner classifies:

| Question | Answer |
|---|---|
| Does this value come from upstream? | Checks if field is in DEFINE DATA PARAMETER |
| Or is it overridden? | Tracks MOVE/ASSIGN from VIEW fields (= database lookup) |
| From where exactly? | Names the DDM, the lookup key, the source field |
| Why? | Infers business meaning from field names and domain keywords |

### Override types detected:
- **enriched-from-database** — Value read from Adabas reference table
- **hardcoded-default** — Literal value (e.g., default currency = 'USD')
- **system-derived** — System variable (*DATX, *USER)
- **calculated-value** — Computed from formula
- **explicit-override** — Field with "DEFAULT"/"OVERRIDE"/"ENRICH" in its name
- **upstream-overridden** — Field WAS from upstream but then REPLACED

### Domain keywords recognised:
Cash: BIC, SWIFT, IBAN, nostro, vostro, correspondent, payment, routing, currency
Securities: ISIN, CUSIP, SEDOL, PSET, CSD, DVP, FOP, custodian, depository
SSI: standing instruction, settlement template, default agent, counterparty lookup

## Knowledge Graph Structure

```json
{
  "nodes": {
    "PGM:CUSTSETL": { "type": "PROGRAM", ... },
    "DDM:SSI-TABLE": { "type": "DDM", ... },
    "FIELD:SETTLE-BIC": { "type": "FIELD", "override_sources": [...] },
    "RULE:CUSTSETL:MARKET-CODE": { "type": "BUSINESS-RULE", "condition": "IF MARKET-CODE = 'US'" }
  },
  "edges": [
    { "from": "PGM:CUSTSETL", "to": "FIELD:SETTLE-BIC", "type": "OVERRIDES" },
    { "from": "DDM:SSI-TABLE", "to": "FIELD:SETTLE-BIC", "type": "PROVIDES" }
  ],
  "override_summary": {
    "SETTLE-BIC": {
      "total_overrides": 5,
      "programs_overriding": ["CUSTSETL", "PAYROUTE"],
      "primary_source": { "category": "DATABASE-READ", "source": "DDM-SSI.SETTLE-BIC" }
    }
  }
}
```

## FRD Output

The generated FRD is organised by business domain:

1. **Executive Summary** — what the system does, scope of overrides
2. **Cash Settlement Fields** — payment routing overrides (BIC, accounts, agents)
3. **Securities Settlement Fields** — custody and delivery overrides (PSET, CSD, custodian)
4. **Standing Settlement Instructions** — how SSI lookups work
5. **Reference Data Sources** — all DDMs/tables providing override values
6. **Business Rules** — conditions controlling when overrides apply
7. **Process Flow** — non-technical enrichment pipeline
8. **Key Findings** — stats and highest-complexity fields

## As a Skill

Copy `skill/SKILL.md` into your project's skills directory. It auto-triggers on settlement-related questions and uses `agents.md` pattern matching for:
- "where does the BIC come from"
- "how is the custodian determined"
- "what overrides the upstream nostro account"
- "generate the settlement FRD"
- "scan my settlement code"

## Requirements

- Python 3.7+ (no external dependencies)
- ~5 minutes for 65K files on 8 workers
- Output JSON can be 50-200MB depending on codebase size
