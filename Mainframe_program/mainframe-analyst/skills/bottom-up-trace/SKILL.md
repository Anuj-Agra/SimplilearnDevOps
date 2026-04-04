---
name: bottom-up-trace
description: "Traces from an Adabas file number, DDM name, or specific field upward to find every program, map, JCL job, and CICS transaction that references it. Use when the user asks 'what programs use this file', 'who reads/writes file X', 'where is this field used', 'bottom up trace', 'impact check on file', 'which programs access DDM-X', or any reverse-lookup from database to code. Essential before making Adabas file structure changes."
---

# Bottom-Up Trace (Adabas → Programs)

Trace from an Adabas file, DDM, or field upward through every program that touches it, up to the top-level entry point.

## Mode 1: File-Level Trace

When the user specifies an Adabas **file number** or **DDM name**, search the entire codebase for every reference.

### Analysis Steps

1. **Scan all programs** across all libraries for any statement referencing this DDM or file number
2. **Categorise each access** by operation type
3. **Trace callers** — for each program found, trace upward to find who calls it
4. **Identify triggers** — is it invoked online (CICS), batch (JCL), or interactively (menu)?

### Output Template

#### 1. File Identity
```
ADABAS FILE:  [number]
DDM NAME:     [name]
DATABASE ID:  [if known]
DESCRIPTION:  [inferred purpose from DDM field names]
```

#### 2. Program Access Inventory

| # | Program | Library | Type | Operation | Fields Read | Fields Written | Search Keys Used | Loop/Single | Error Handling | Top-Level Caller | Trigger (TXN/JCL/Menu) |
|---|---------|---------|------|-----------|-------------|----------------|------------------|-------------|----------------|-----------------|------------------------|

#### 3. Access Pattern Summary

| Operation | Count | Programs |
|-----------|-------|----------|
| READ / FIND | | |
| GET (by ISN) | | |
| STORE (insert) | | |
| UPDATE | | |
| DELETE | | |
| HISTOGRAM | | |

#### 4. Caller Chain (trace UP for each program)

For each program that accesses the file, build the upward chain:
```
FILE-152 ← PGM-UPDCUST ← PGM-CUSTMAINT ← TXN-CI01
FILE-152 ← SUB-GETCUST ← PGM-ORDERENTRY ← JCL-NIGHTBATCH Step 3
FILE-152 ← SUB-GETCUST ← PGM-CUSTINQ ← TXN-CI02
```

Show this as a Mermaid diagram with the file at the centre:

```mermaid
graph RL
    classDef file fill:#607D8B,color:#fff
    classDef read fill:#4CAF50,color:#fff
    classDef write fill:#FF9800,color:#fff
    classDef update fill:#2196F3,color:#fff
    classDef delete fill:#F44336,color:#fff

    DB[(FILE-nnn)]:::file
    P1[PGM-xxx: READ]:::read --> DB
    P2[PGM-yyy: UPDATE]:::update --> DB
    P3[PGM-zzz: STORE]:::write --> DB
    T1[TXN-xxxx] --> P1
    J1[JCL-jobname] --> P2
```

#### 5. Field Usage Matrix (which fields each program touches)

| Field Name | Short Name | PGM-1 (R/W) | PGM-2 (R/W) | PGM-3 (R/W) | ... |
|-----------|-----------|-------------|-------------|-------------|-----|

Mark each cell with R (read), W (write), RW (both), S (search key), or - (not used).

#### 6. Risk Assessment

- Fields written by multiple programs without coordination (conflict risk)
- Programs that UPDATE without reading first (blind update risk)
- Programs that DELETE without confirmation logic
- Missing ON ERROR handling on any database access

---

## Mode 2: Field-Level Reverse Trace

When the user specifies a **specific field** within a file, trace that single field everywhere.

### Output Template

#### 1. Field Identity
```
FIELD:        [long name]
SHORT NAME:   [2-char Adabas name]
FILE:         [number]
DDM:          [name]
FORMAT:       [A/N/P/B + length]
DESCRIPTOR:   [Y/N, super/sub/phonetic details]
```

#### 2. Write Origins (how data gets INTO this field)

For each program that writes this field:

| # | Program | Source of Value | Validation Before Write | Transformation Applied |
|---|---------|----------------|------------------------|----------------------|

**Source types**: user-input (from MAP field), calculation, another-file (FILE-mmm.FIELD), literal/hardcode, system-variable (*DATX, *TIMX, *USER), parameter-from-caller

#### 3. Read Destinations (how stored data is USED)

For each program that reads this field:

| # | Program | Assigned To | Used For | Passed To |
|---|---------|-------------|----------|-----------|

**Used for types**: display-on-map, if-condition, calculation, search-key, parameter-to-callnat, write-to-other-file, report-output

#### 4. Selection Usage

| # | Program | Statement | Comparison | Purpose |
|---|---------|-----------|------------|---------|

(e.g., FIND DDM-CUSTOMER WITH CUST-STATUS = 'A')

#### 5. Screen Presence

| # | Map Name | Map Field Name | Label on Screen | Editable? | AD= | EM= (mask) | CD= (colour) |
|---|----------|---------------|-----------------|-----------|-----|------------|--------------|

#### 6. Field Lineage Diagram (Mermaid)

```mermaid
graph LR
    classDef input fill:#4CAF50,color:#fff
    classDef process fill:#2196F3,color:#fff
    classDef store fill:#607D8B,color:#fff
    classDef display fill:#9C27B0,color:#fff

    I1[MAP-xxx: user input]:::input --> V1[PGM-validate]:::process
    I2[FILE-mmm.other-field]:::store --> C1[PGM-calculate]:::process
    V1 --> S1[(STORE FILE-nnn.FIELD)]:::store
    C1 --> U1[(UPDATE FILE-nnn.FIELD)]:::store
    R1[(READ FILE-nnn.FIELD)]:::store --> D1[MAP-zzz: display]:::display
    R1 --> P1[PGM-report: print]:::process
```

## Cross-File Field Propagation

If this field's value is copied to other Adabas files, trace those too:

```
FILE-152.CUST-NAME → PGM-ORDERPROC → FILE-200.ORDER-CUST-NAME
FILE-152.CUST-NAME → PGM-HISTORY → FILE-300.HIST-NAME
```

Flag any cases where the field exists in multiple files but may drift out of sync.
