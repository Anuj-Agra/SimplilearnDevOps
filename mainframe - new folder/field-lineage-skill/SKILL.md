---
name: field-lineage-analyzer
description: "Deep field-level analysis agent for mainframe Natural/COBOL programs. Traces exactly how each field gets its value — from user input, database reads, calculations, literals, system variables, parameter passing, and cross-file copies. Use this skill whenever the user asks: 'where does this field get its value', 'how is this field populated', 'field lineage', 'field provenance', 'trace the value of field X', 'what sets field X', 'how is this value calculated', 'where does the data come from', 'field usage analysis', 'identify all fields in program X', 'what fields are in this file', 'how is field X used across programs', 'field-level impact analysis', or any question about HOW a field's value is derived or WHERE it flows."
---

# Field Lineage Analyzer Agent

This skill performs deep field-level analysis to answer: **for every field in a program or Adabas file, where is it used and how was its value derived?**

## What It Detects

### Value Source Types

The analyzer classifies every field assignment into one of these source types:

| Source Type | Natural Pattern | Example |
|---|---|---|
| `USER-INPUT` | INPUT USING MAP | User typed a value on screen |
| `FIELD-COPY` | MOVE #A TO #B, #B := #A | Value copied from another field |
| `CALCULATED` | COMPUTE, ADD, SUBTRACT, MULTIPLY, DIVIDE | Arithmetic result |
| `CONCATENATED` | COMPRESS #A #B INTO #C | Multiple values joined |
| `LITERAL` | MOVE 'ABC' TO #X, #X := 100 | Hardcoded constant |
| `CONSTANT` | MOVE SPACES/ZEROS/TRUE TO #X | Named constant |
| `SYSTEM-VARIABLE` | MOVE *DATX TO #DATE | System value (*DATX, *USER, *TIMX, etc.) |
| `DATABASE-READ` | READ/FIND/GET populates VIEW fields | Value from Adabas record |
| `EXTRACTED` | SEPARATE #A INTO #B #C | Part extracted from another field |
| `TRANSFORMED` | EXAMINE #A FOR 'x' REPLACE 'y' | In-place modification |
| `PARAMETER-PASS` | CALLNAT 'PGM' #FIELD | Passed to/from another program |
| `RESET` | RESET #FIELD | Cleared to default value |

### Field Usage Tracking

For every field, the analyzer also tracks:
- **Defined in** — which program, what scope (LOCAL/GLOBAL/PARAMETER/VIEW), format
- **DDM mapping** — if the field is part of a VIEW OF ddm-name
- **Condition usage** — every IF/DECIDE that tests this field
- **Search key usage** — FIND/READ BY using this field as a descriptor
- **Screen presence** — which MAPs display or accept this field
- **Parameter passing** — which CALLNATs pass this field, at which position
- **Database operations** — READ (populates), STORE/UPDATE (persists)

## How to Use This Skill

### Mode 1: Analyze a single program

When the user provides a program and asks "what fields does this use" or "how are values derived":

1. Read the template: `view` the file at `references/field-analyzer-template.py`
2. If the user has pasted source code, perform the analysis inline using the patterns from the template
3. Produce output in this format:

```
## Field Analysis: PROGRAM-NAME

### Field Inventory
| Field | Format | Scope | DDM | Value Source(s) |
|---|---|---|---|---|

### Value Derivation Chain
For each field, show HOW the value was achieved:

**#CUST-NAME** (A50, VIEW of DDM-CUSTOMER)
  └─ Value source: DATABASE-READ from DDM-CUSTOMER.CUST-NAME
     via: READ CUST-VIEW BY CUST-ID

**#FULL-ADDRESS** (A200, LOCAL)
  └─ Value source: CONCATENATED
     via: COMPRESS #ADDR-LINE1 #ADDR-LINE2 #CITY #POSTCODE INTO #FULL-ADDRESS
     └─ #ADDR-LINE1 ← DATABASE-READ from DDM-CUSTOMER.ADDR-LINE1
     └─ #CITY ← DATABASE-READ from DDM-CUSTOMER.ADDR-CITY

**#UPDATE-DATE** (A8, LOCAL)
  └─ Value source: SYSTEM-VARIABLE *DATX (Current date YYYYMMDD)

**#TOTAL-AMOUNT** (N10.2, LOCAL)
  └─ Value source: CALCULATED
     via: COMPUTE #TOTAL-AMOUNT = #UNIT-PRICE * #QUANTITY
     └─ #UNIT-PRICE ← DATABASE-READ from DDM-PRODUCT.PRICE
     └─ #QUANTITY ← USER-INPUT from MAP M-ORDERENTRY
```

### Mode 2: Trace a specific field across all programs

When the user asks "where is field CUST-STATUS used" or "trace CUST-STATUS":

1. Search all provided programs for references to that field
2. Produce a cross-program lineage:

```
## Field Lineage: CUST-STATUS

### Where Defined
| Program | Scope | DDM | Format |
|---|---|---|---|

### Value Origins (how the value is SET)
| Program | Source Type | Source | Context |
|---|---|---|---|
| CUSTCREATE | LITERAL | 'A' | MOVE 'A' TO CUST-STATUS (default active) |
| CUSTUPDATE | USER-INPUT | MAP M-CUSTEDIT | User selects new status |
| CUSTDEACT | LITERAL | 'I' | MOVE 'I' TO CUST-STATUS (deactivation) |
| BATCHPURGE | LITERAL | 'D' | MOVE 'D' TO CUST-STATUS (mark for delete) |

### Value Consumers (how the value is USED)
| Program | Usage Type | Context |
|---|---|---|
| CUSTINQ | DISPLAY | Shown on MAP M-CUSTDISP |
| ORDERENTRY | CONDITION | IF CUST-STATUS = 'A' (only active customers) |
| RPTACTIVE | SEARCH-KEY | FIND DDM-CUSTOMER WITH CUST-STATUS = 'A' |
| CUSTMAINT | PARAMETER | CALLNAT 'CUSTUPD' ... #CUST-STATUS at pos 4 |

### Provenance Chain (visual)
```
USER-INPUT (MAP M-CUSTEDIT)
  └─→ PGM-CUSTUPDATE: #CUST-STATUS := user value
       └─→ UPDATE DDM-CUSTOMER.CUST-STATUS
            └─→ READ by PGM-CUSTINQ → display on MAP M-CUSTDISP
            └─→ FIND by PGM-RPTACTIVE (WHERE CUST-STATUS = 'A')
            └─→ CALLNAT param to PGM-CUSTMAINT
```

### Mode 3: Analyze all fields in an Adabas file/DDM

When the user asks "what fields are in file 152" or "show me DDM-CUSTOMER field usage":

1. Find all programs that reference this DDM
2. For each DDM field, show which programs read it, write it, and how values are derived

```
## DDM Field Analysis: DDM-CUSTOMER (FILE-152)

| Field | Programs Reading | Programs Writing | Value Sources | Screens |
|---|---|---|---|---|
| CUST-ID | CUSTINQ, ORDERENTRY | CUSTCREATE | COUNTER (auto-generated) | M-CUSTDISP(display) |
| CUST-NAME | CUSTINQ, RPTACTIVE | CUSTCREATE, CUSTUPDATE | USER-INPUT (M-CUSTEDIT) | M-CUSTDISP, M-CUSTEDIT |
| CUST-STATUS | CUSTINQ, ORDERENTRY | CUSTUPDATE, CUSTDEACT | LITERAL('A'), USER-INPUT | M-CUSTDISP |
```

### Mode 4: Generate the Python analyzer tool

When the user asks to "generate the field analyzer" or "create the field analysis scanner":

1. Read `references/field-analyzer-template.py`
2. Output it as a file to `/mnt/user-data/outputs/field_analyzer.py`
3. Explain usage:

```bash
# Analyze all programs
python field_analyzer.py --source /path/to/natural --output field_lineage.json

# Analyze single program
python field_analyzer.py --source /path/to/natural --program CUSTMAIN --output lineage.json

# Trace a specific field
python field_analyzer.py --source /path/to/natural --field CUST-STATUS --output cust_status.json
```

## System Variables Reference

When a field is assigned from a system variable, include the meaning:

| Variable | Meaning |
|---|---|
| *DATX | Current date (YYYYMMDD) |
| *DAT4I | Current date (YYYY-MM-DD) |
| *TIMX | Current time (HHIISS) |
| *USER | Current user ID |
| *PROGRAM | Current program name |
| *ISN | Last Adabas ISN accessed |
| *NUMBER | Record count from last FIND/READ |
| *COUNTER | Current loop counter |
| *PF-KEY | Last PF key pressed |
| *ERROR-NR | Last error number |
| *LIBRARY | Current library |

## Output Standards

1. Always show the **full derivation chain** — if field A comes from field B, show where B comes from too
2. Use consistent terminology: "Value source", "Value consumer", "Provenance chain"
3. For calculated fields, show the **formula** not just "calculated"
4. For COMPRESS, show the **component fields** that were joined
5. For parameters, show the **position** in the CALLNAT parameter list
6. For conditions, show the **comparison operator and value** (IF X = 'A', not just "used in IF")
7. Flag fields with **no validation before write** as ⚠️ risk
8. Flag fields with **multiple conflicting sources** across programs as ⚠️ potential inconsistency
