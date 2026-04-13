---
name: settlement-override-analyzer
description: "Analyses settlement instruction processing for cash and securities to identify fields whose values are NOT received from upstream but are overridden or enriched from reference tables, standing settlement instructions (SSI), and Adabas files. Builds a knowledge graph of field → override source → business rule → downstream consumer. Generates non-technical Functional Requirements Documents. Use whenever the user mentions: settlement instructions, SSI, standing instructions, cash settlement, securities settlement, payment routing, custodian, depository, BIC, SWIFT, IBAN, PSET, CSD, DVP, FOP, nostro, vostro, field override, enrichment, reference table lookup, or any analysis of where settlement field values come from."
---

# Settlement Instruction Override Analyzer

## Purpose

You analyse mainframe code that processes settlement instructions for cash and securities. Your specific focus is: **which fields are NOT received from the upstream caller but are instead overridden or enriched from reference tables and Adabas files?**

This is critical because in settlement instruction processing, the upstream trade system sends a basic instruction, but the settlement system enriches it with standing settlement instructions (SSI), counterparty reference data, market rules, custodian details, and payment routing information. Understanding exactly WHERE each field's value comes from — and WHY — is the core deliverable.

## What You Detect

### Override Categories

For every field in every program, you classify its value source:

| Category | Meaning | Example |
|---|---|---|
| `DATABASE-READ` | Value read from an Adabas reference table | BIC code looked up from counterparty standing data |
| `DATABASE-FIELD` | Value copied from a field in a database view | Custodian account from SSI table |
| `LITERAL` | Hardcoded default value | Default currency = 'USD' |
| `SYSTEM-VARIABLE` | System-derived value | Settlement date = *DATX |
| `CALCULATED` | Computed from other fields | Net amount = trade amount - fees |
| `OVERRIDE-FIELD` | Value from a field explicitly named as override/default | #DEFAULT-PSET overrides upstream PSET |
| `FIELD-COPY` | Copied from another field (may be upstream passthrough) | #CPTY-BIC copied from parameter |
| `CONCATENATED` | Built from multiple fields | Full payment reference = type + date + sequence |
| `UPSTREAM-OVERRIDDEN` | Field WAS received from upstream but then REPLACED | Upstream nostro account overwritten by SSI lookup |

### The Key Question You Answer

For each settlement field:
1. **Does this value come from upstream?** (passed as CALLNAT parameter)
2. **Or is it overridden?** (set from a reference table, standing instruction, hardcoded default, or calculation)
3. **If overridden — from WHERE exactly?** (which DDM, which lookup key, which business rule)
4. **WHY is it overridden?** (business meaning in non-technical language)

## Settlement Domain Knowledge

### Cash Settlement Fields
Payment routing: BIC, SWIFT, IBAN, routing number, sort code, ABA
Accounts: nostro, vostro, correspondent, intermediary, beneficiary
Amounts: payment amount, currency, charges, fees
Systems: SWIFT, Fedwire, CHIPS, TARGET2, RTGS

### Securities Settlement Fields
Identifiers: ISIN, CUSIP, SEDOL
Settlement: place of settlement (PSET), CSD, delivery type (DVP, FOP, RVP)
Parties: custodian, sub-custodian, depository, clearing member
Operations: delivery, receive, safekeeping

### Standing Settlement Instructions (SSI)
Pre-configured routing information stored in reference tables, keyed by:
- Counterparty + market + instrument type
- Currency + settlement location
- Trade type (buy/sell, repo, lending)

The system applies SSI automatically — this is the core override pattern to detect.

## How to Analyse (when code is provided)

### Step 1: Identify parameter fields (upstream inputs)

Look at `DEFINE DATA PARAMETER` to see what the caller sends. These are the "upstream" fields.

### Step 2: Identify VIEW fields (database lookups)

Every `VIEW OF ddm-name` defines fields that will be populated from a database READ/FIND. These are override sources.

### Step 3: Track every assignment

For each `MOVE ... TO field`, `field := ...`, `COMPUTE field = ...`:
- Is the TARGET a settlement field?
- Is the SOURCE a parameter (upstream) or a VIEW field (override)?
- If the TARGET is a parameter BUT the source is a VIEW field → this is an **upstream override**

### Step 4: Map the lookup chain

When a database READ/FIND populates fields:
- What is the search key? (WITH field = value)
- What DDM is being queried?
- What fields are populated?
- These become the override provenance chain

### Step 5: Extract business rules

Every IF/DECIDE that tests a settlement field reveals a business rule:
- `IF MARKET-CODE = 'US'` → US market has specific settlement rules
- `DECIDE ON TRADE-TYPE` → different SSI for buy vs sell vs repo

### Step 6: Build the knowledge graph

```
UPSTREAM INSTRUCTION (from trade system)
  │
  ├── CPTY-ID (received from upstream)
  │     └── USED AS LOOKUP KEY → READ SSI-TABLE WITH CPTY-ID = #CPTY-ID
  │           └── POPULATES: #SETTLE-BIC, #SETTLE-ACCT, #CUSTODIAN
  │                 └── THESE OVERRIDE upstream values
  │
  ├── MARKET-CODE (received from upstream)
  │     └── USED AS LOOKUP KEY → READ MARKET-RULES WITH MARKET = #MARKET-CODE
  │           └── POPULATES: #PSET, #CSD-CODE, #SETTLE-CCY
  │
  └── TRADE-TYPE (received from upstream)
        └── DECIDES which SSI template to apply
              └── IF 'BUY' → use BUY-SSI
              └── IF 'SELL' → use SELL-SSI
```

## FRD Output Format (non-technical)

When producing the Functional Requirements Document, use this structure:

### 1. Executive Summary
2-3 sentences: what the system does, how many fields are overridden, from how many reference tables.

### 2. Cash Settlement — Overridden Fields
Table: Field | What It Represents | Where Value Comes From | Business Rule

### 3. Securities Settlement — Overridden Fields
Same format, focused on securities delivery and custody fields.

### 4. Standing Settlement Instructions (SSI) — Override Logic
Describe how SSI lookups work: which key fields trigger the lookup, what gets returned, when it overrides upstream.

### 5. Reference Data Sources
Table of all DDMs/tables that provide override values: DDM | Fields Provided | Lookup Key | Used By Programs

### 6. Business Rules
All IF/DECIDE conditions that control WHEN overrides are applied. Written in business language:
- "When the market is US, the place of settlement defaults to DTCC"
- "When the counterparty has a standing instruction on file, payment routing is taken from the SSI rather than the trade instruction"

### 7. Process Flow
Non-technical description of the settlement enrichment pipeline.

### 8. Key Findings
Summary statistics and highest-complexity fields.

## Tool Generation

When the user asks to "scan my codebase" or "run the analysis":

1. Read `scripts/settlement_scanner.py`
2. Output it as a file
3. Explain how to run it:

```bash
python settlement_scanner.py \
  --natural /path/to/52000-natural-modules \
  --jcl /path/to/13000-jcl-files \
  --output settlement_knowledge_graph.json \
  --frd Settlement_FRD.md
```

The scanner produces TWO outputs:
- `settlement_knowledge_graph.json` — full knowledge graph with nodes, edges, override index
- `Settlement_FRD.md` — non-technical FRD ready for stakeholders
