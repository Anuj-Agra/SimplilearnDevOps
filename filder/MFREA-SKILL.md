---
name: mainframe-reverse-engineer
description: >
  Reverse-engineer a Natural/ADABAS + JCL mainframe estate into six structured intelligence views:
  (1) interactive top-down / bottom-up JCL→Program→Module dependency tree with upstream/downstream
  node highlighting, (2) ADABAS file usage map showing every program, its access mode, and the
  specific fields it reads or writes, (3) reference table usage map inferring consumed fields from
  read-by-length patterns, (4) a plain-English functional view of what each program does with no
  technical content, (5) a program-level decommission scorecard correlated against a monthly usage
  extract, and (6) a job-level decommission checklist including output datasets, ADABAS dependencies,
  scheduler entries, and a step-by-step decommission action list.
  Triggers: "reverse engineer mainframe", "Natural module analysis", "JCL dependency tree",
  "ADABAS file usage", "what programs call this file", "reference table consumers",
  "which programs can be decommissioned", "mainframe call hierarchy", "Natural program hierarchy",
  "JCL call tree", "what does this batch job do", "decommission mainframe job".
  Input: a folder of Natural source modules (.NSN / .NSP / .NSS / .NSD / plain text) and a folder
  of JCL members, plus optionally an Excel file of monthly program run counts.
---

# Mainframe Reverse Engineering Agent (MFREA)

Analyse a Natural/ADABAS + JCL estate and produce six intelligence views that support modernisation,
decommission, impact analysis, and business understanding.

---

## Scope and Terminology

| Term | Meaning |
|---|---|
| **Natural module** | Any Natural source member: program (.NSP), subprogram (.NSN), subroutine (.NSS), map (.NSM), data area (.NSD), copycode (.NSC) |
| **JCL member** | A JCL job member that executes Natural steps via `EXEC PGM=NATBATCH` or similar |
| **Program** | A Natural subprogram called via `CALLNAT` — the primary unit of reuse |
| **Module** | Any Natural member below program level (subroutine, copycode, map, data area) |
| **ADABAS file** | A numbered ADABAS database file referenced in Natural via `READ FILE nnn` / `STORE FILE nnn` / `UPDATE` / `DELETE` |
| **Reference table** | A sequential ADABAS file read exclusively in READ LOGICAL or READ BY ISN mode with a fixed record length, typically used as a code/lookup table |
| **Shared module** | A module that appears as a dependency of more than one program or JCL path — deduplication marker `*` |
| **Call graph** | Directed graph where edges represent: JCL invokes Program, Program CALLNAT's Subprogram, Subprogram PERFORM's Subroutine |
| **Usage extract** | An Excel/CSV file with columns `PROGRAM-NAME` and `RUN-COUNT` representing last-month execution counts from SMF or scheduler logs |

---

## Step 0 — Clarify Inputs

Before scanning any source, confirm with the user:

1. **Natural source path** — folder containing all `.NSN`, `.NSP`, `.NSS`, `.NSD`, `.NSC`, `.NSM` files, or plain-text members
2. **JCL source path** — folder containing all JCL members
3. **Usage extract** — optional Excel/CSV with `PROGRAM-NAME` / `RUN-COUNT` for last month
4. **Scope filter** — analyse the full estate, or a named subset (e.g. "only jobs starting with DAILY")
5. **Output format** — single self-contained HTML file (default), or separate Markdown files per view

If the user provides paths without specifying scope, default to full estate and HTML output.

---

## Step 1 — Parse JCL Members

### Goal
Extract which Natural program each JCL job executes and what datasets it reads/writes.

### Key patterns to scan for

```bash
# Find all JCL members
find <jcl_path> -type f | head -500

# Find Natural batch steps
grep -rn "EXEC PGM=NATBATCH\|EXEC PGM=NAT\|//.*PARM=" <jcl_path>

# Find SYSIN DD statements (carry the Natural program name)
grep -rn "SYSIN\|PROGRAM=\|RUN=\|FIRSTPGM=" <jcl_path>

# Find all DD statements (dataset I/O)
grep -rn "^//[A-Z].*DD " <jcl_path>

# Find GDG references
grep -rn "\.G[0-9][0-9][0-9][0-9]V[0-9][0-9]" <jcl_path>
```

### Fields to extract per JCL member

| Field | Source | Example |
|---|---|---|
| `JCL_NAME` | Member name or `//JOBNAME` | `DAILY001` |
| `ENTRY_PROGRAM` | `PARM='PROGRAM=xxx'` or `SYSIN` content | `PGMACCT` |
| `STEP_PROGRAMS` | All programs invoked across steps | `[PGMACCT, PGMRISK]` |
| `INPUT_DATASETS` | `DD DISP=SHR` or `DD DISP=(OLD,...)` | `ACCT.MASTER.FILE` |
| `OUTPUT_DATASETS` | `DD DISP=(NEW,...,DELETE)` or GDG `(+1)` | `ACCT.RECON.DAILY` |
| `SCHEDULER_ENTRY` | Comment blocks with `TWS:` / `CA7:` / `CTRL-M:` | `TWS: ACCT-DAILY Mon-Fri 19:00` |
| `CONDITIONAL_STEPS` | `IF (STEP.RC = 0)` blocks | Downstream step dependencies |

### Parsing algorithm

```
FOR each JCL file:
  SCAN for //JOBNAME card → extract job name
  SCAN for //stepname EXEC PGM= cards:
    IF PGM contains NATBATCH or NAT:
      LOOK for SYSIN DD * content
      EXTRACT lines matching PROGRAM=xxx or CALLNAT xxx
      RECORD (JCL_NAME, STEP_NAME, PROGRAM_NAME)
  SCAN all //ddname DD cards:
    IF DISP indicates input → add to INPUT_DATASETS
    IF DISP indicates output → add to OUTPUT_DATASETS
```

---

## Step 2 — Parse Natural Source Members

### Goal
Build the complete call graph: which modules call which, which ADABAS files are accessed and how,
and which reference tables are read and at what length.

### 2a. Classify each member

```bash
# Count by type
grep -rln "^DEFINE DATA" <natural_path>   # programs / subprograms
grep -rln "^CALLNAT"      <natural_path>   # callers
grep -rln "^PERFORM"      <natural_path>   # subroutine callers
grep -rln "^READ FILE"    <natural_path>   # ADABAS readers
grep -rln "^STORE FILE\|^UPDATE\|^DELETE"  <natural_path>  # ADABAS writers
grep -rln "^READ LOGICAL\|^READ BY ISN"    <natural_path>  # reference table reads
```

### 2b. Extract call edges

```bash
# All CALLNAT statements (program-to-subprogram edges)
grep -rn "^[[:space:]]*CALLNAT" <natural_path> | sed "s/.*CALLNAT[[:space:]]*'\([^']*\)'.*/\1/"

# All PERFORM statements (subroutine calls within the same module)
grep -rn "^[[:space:]]*PERFORM" <natural_path>

# All FETCH / FETCH RETURN (Dynamic program invocations)
grep -rn "^[[:space:]]*FETCH" <natural_path>
```

For each source file, extract:

| Field | Pattern | Note |
|---|---|---|
| `MODULE_NAME` | Filename or `DEFINE MODULE=` | Strip extension |
| `MODULE_TYPE` | `DEFINE DATA LOCAL/GLOBAL/PARAMETER` → program; `DEFINE SUBROUTINE` → subroutine | |
| `CALLNAT_LIST` | `CALLNAT 'PGMXXX'` | Outbound subprogram calls |
| `PERFORM_LIST` | `PERFORM SUBRNAME` | Outbound subroutine calls |
| `ADABAS_READS` | `READ FILE nnn` / `FIND FILE nnn` | File number + field list from `WITH` / `WHERE` |
| `ADABAS_WRITES` | `STORE FILE nnn` / `UPDATE (nnn)` / `DELETE (nnn)` | File number |
| `REF_READS` | `READ LOGICAL BY nnn` / `READ BY ISN nnn` | File number + read length (bytes) |
| `ADABAS_FIELDS` | Field names in `READ`, `FIND`, `UPDATE` blocks | Match against FDT if available |

### 2c. Infer reference table field coverage from read length

Reference tables in Natural are read via `READ WORK FILE` or `GET FILE` with a fixed record layout.
Because there are no field-level ADABAS descriptors, field coverage must be inferred from the number
of bytes the program reads:

```
ALGORITHM:
  FOR each reference table file number:
    GATHER all programs that read it
    FOR each program, extract the READ length (bytes)
    SORT reference table record layout by cumulative offset
    FOR each program's readLen:
      MARK all fields where (field_start_offset + field_length) <= readLen as CONSUMED
      MARK remaining fields as NOT_CONSUMED
  OUTPUT: per-program field coverage map
```

Example — CURRENCY-REF layout (total record = 40 bytes):

| Offset | Length | Field name | Consumed when readLen ≥ |
|---|---|---|---|
| 1 | 3 | CCY-CODE | 3 |
| 4 | 30 | CCY-DESC | 33 |
| 34 | 4 | CCY-SYMBOL | 37 |
| 38 | 1 | CCY-DECIMAL | 38 |
| 39 | 1 | CCY-ROUND-RULE | 39 |

A program with `readLen=6` consumes only `CCY-CODE` + partial `CCY-DESC` → inferred as `CCY-CODE` only.
A program with `readLen=39` consumes all fields.

---

## Step 3 — Build the Six Data Models

After parsing, assemble these in-memory structures. All six views are derived from them.

### 3a. Call graph (for Dependency Tree view)

```
NODES:
  { name, type: jcl|program|module, desc, isShared }

EDGES:
  { from, to, edgeType: invokes|callnat|perform|fetch }

ADJACENCY:
  parentMap[module] = [list of modules/programs/JCL that call it]
  childMap[module]  = [list of modules/programs/JCL it calls]
```

Mark `isShared = true` for any node that appears in `parentMap` with more than one distinct parent.

### 3b. ADABAS usage map

```
FOR each ADABAS file number:
  { fileNo, fileName, desc, records, sizeGB,
    programs: [
      { name, accessMode: R|W|RW, fields: [field names] }
    ]
  }
```

`accessMode` rules:
- `R` if only `READ FILE` / `FIND FILE` / `GET FILE` statements found
- `W` if only `STORE FILE` / `UPDATE` / `DELETE` found
- `RW` if both read and write statements found

### 3c. Reference table usage map

```
FOR each reference table file:
  { tableName, desc,
    layout: [ { name, offset, length, desc } ],
    programs: [
      { name, readLen, inferredFields: [field names], monthlyRuns }
    ]
  }
```

### 3d. Functional descriptions

For each program and JCL, generate a business-language description using these heuristics:

| Code pattern found | Business description fragment |
|---|---|
| `READ FILE 005` (client master) | "reads client identity and compliance status" |
| `UPDATE FILE 012` | "updates the account record" |
| `READ LOGICAL` on reference table | "validates against the [table name] lookup" |
| `CALLNAT 'RPT*'` | "produces a report for downstream consumption" |
| `WRITE WORK FILE` / GDG output | "writes output to [dataset name] for downstream processing" |
| `IF ... STATUS ... = 'DORMANT'` | "applies dormancy rules" |
| Program name starts with `RPT` / `REP` | "reporting program" |
| Program name starts with `VAL` / `CHK` | "validation routine" |
| Program name starts with `UPD` / `MNT` | "update / maintenance routine" |
| Program name starts with `GET` / `RD` | "data retrieval routine" |
| Program name starts with `CALC` / `MATH` | "calculation engine" |
| Program name starts with `ARCH` | "archival routine" |

**Zero-hallucination rule**: never invent a business description that cannot be traced to a code
pattern. If a program's purpose is ambiguous, write: "Purpose requires clarification — no
deterministic pattern found."

### 3e. Decommission scorecard

```
FOR each program:
  monthlyRuns  = lookup from usage extract (0 if not found)
  status       = DECOMMISSION (runs=0) | REVIEW (0 < runs < 500) | KEEP (runs >= 500)
  calledBy     = parentMap[program]  — warn if non-empty even for zero-run programs
  callsTo      = childMap[program]
```

Thresholds are configurable. Default: 0 = decommission candidate, 1-499 = review, ≥500 = keep.

### 3f. Job decommission checklist

For each JCL candidate (status = DECOMMISSION or REVIEW):

```
CHECKLIST items (auto-generated):
  [ ] Confirm no downstream GDG consumers — reference any existing FOT/Jira ticket if found in comments
  [ ] Archive output datasets (list each with retention period from JCL comments if present)
  [ ] Remove scheduler entry (extract name from JCL comment)
  [ ] Move JCL member to ARCHIVE.JCL.LIB
  [ ] Move Natural source members to ARCHIVE library (list all programs called by this JCL)
  [ ] Check ADABAS file dependencies — FOR EACH file accessed, flag if any other KEEP job shares it
  [!] WARNING: If ADABAS file is shared with active jobs → do NOT drop the file
  [ ] Raise ServiceNow CI decommission workflow
  [ ] Notify Release Management (no CAB required for archive-only changes — confirm with local policy)
```

Shared-file warning rule: if `file_used_by_job_being_decommissioned` also appears in
`files_used_by_KEEP_jobs`, emit a `[!] WARNING` item with the names of the active jobs that
still depend on it.

---

## Step 4 — Produce the UI (Single HTML File)

The primary deliverable is a single self-contained HTML file with six tabs. It requires no server.
All data is embedded as JavaScript constants. The file must work by opening in any modern browser.

### 4a. Required tabs

| Tab # | Tab label | Content |
|---|---|---|
| 1 | Dependency tree | D3.js radial or horizontal tree, top-down and bottom-up toggle, click-to-highlight, search box, side panel |
| 2 | ADABAS file usage | Dropdown to select file, table of programs × access mode × fields × run count, field filter chip row |
| 3 | Reference table usage | Dropdown to select table, inferred layout strip, table of programs × readLen × inferred fields × run count |
| 4 | Functional view | Collapsible business-language tree, badge-coded (Core / Risk / Report / Validate / Legacy), search box |
| 5 | Program decommission | Metric cards, zero-run list, low-usage list, full bar chart colour-coded by status |
| 6 | Job decommission | Expandable job cards per job with checklist, progress bar, dataset list, ADABAS dependencies, scheduler info |

### 4b. Dependency Tree — interaction specification

**Top-down mode**: root = PROD environment → JCL jobs → entry programs → subprograms → modules

**Bottom-up mode**: root = selected leaf module → parents → grandparents → JCL jobs

**Node click behaviour**:
1. Selected node: gold fill + gold stroke, bright label
2. Upstream callers (BFS traversal up parentMap): blue fill + blue stroke
3. Downstream dependencies (BFS traversal down childMap): green fill + green stroke
4. Unreachable nodes: dim to 25% opacity
5. Side panel: show node name, type, description, upstream list (capped at 10 + count), downstream list

**Node visual encoding**:

| Node type | Shape | Fill | Stroke |
|---|---|---|---|
| JCL job | Circle r=8 | Dark purple | Purple |
| Natural program | Circle r=7 | Dark green | Teal |
| Module / subprogram | Circle r=5 | Dark blue | Slate |
| Selected node | Any | Dark gold | Gold |
| Upstream | Any | Dark blue | Sky blue |
| Downstream | Any | Dark green | Mint |

**Shared module indicator**: append ` *` to the node label. In the side panel, list all other
programs that call this shared module.

**Search**: on keyup, dim nodes whose name does not contain the search string to 12% opacity.

### 4c. ADABAS view — interaction specification

- Dropdown populated from all parsed file numbers + names
- On selection, show: record count, size on disk, description
- Table columns: Program | Access (R / W / RW badge) | Fields accessed (chips) | Monthly runs | Status
- Field filter input: highlight chips containing the filter string in gold; dim rows with no matching field
- Access filter dropdown: All / Read only / Write only / Read + Write

### 4d. Reference table view — interaction specification

- Dropdown populated from all parsed reference table names
- On selection, show: description, inferred layout strip
- Layout strip: for each field show `+offset/len FIELD-NAME — description` as inline code chips
- Table columns: Program | Read length (bytes) | Inferred fields consumed (gold chips) | Monthly runs | Status
- Consumed fields highlighted in gold; unconsumed fields shown in grey

### 4e. Functional view — interaction specification

- Collapsible tree mirroring the JCL → Program → Module hierarchy
- Each node shows: business label | domain badge | module name (monospace, muted)
- Domain badges: `core` (purple) | `risk` (red) | `report` (green) | `validate` (amber) | `legacy` (red outline)
- Legacy nodes automatically inherit `legacy` badge if their run count = 0 or name matches decommission candidates
- Expand all / Collapse all buttons
- Search filters nodes by business label text

### 4f. Decommission views — interaction specification

**Program tab**:
- 4 metric cards: Total programs | Zero-run (red) | Low-usage (amber) | Active (green)
- Two-column layout: left = zero-run decommission list, right = low-usage review list
- Full bar chart: all programs sorted by run count, bars colour-coded by status
- Filter buttons: All | Zero runs | Low (&lt;500)

**Job tab**:
- Filter buttons: All | Decommission candidates | Review | Active / Keep
- Each job as an expandable card showing status badge, run count, description
- Expanded body (two-column grid):
  - Left: programs called (with run counts), output datasets, ADABAS dependencies with shared-file warnings, scheduler entry
  - Right: decommission checklist with ✓ done / ○ todo / ! warning icons, progress bar

---

## Step 5 — Generate Markdown Output Files (Optional)

If the user requests Markdown instead of (or in addition to) the HTML, produce one `.md` file per view:

| Filename | Contents |
|---|---|
| `01-dependency-tree.md` | ASCII call hierarchy tree (one level of indentation per depth level) |
| `02-adabas-usage.md` | Table per ADABAS file: programs × access × fields |
| `03-ref-table-usage.md` | Table per reference table: programs × readLen × inferred fields |
| `04-functional-view.md` | Nested heading structure (H2 = JCL, H3 = Program, H4 = Module) with business descriptions |
| `05-program-decommission.md` | Table: Program | Monthly runs | Status | Called by | Calls to |
| `06-job-decommission.md` | One section per job with checklist in GitHub-Flavoured Markdown task list format (`- [ ]` / `- [x]`) |

---

## Step 6 — Parsing Command Reference

All commands below assume the estate is accessible at the paths given.

### JCL parsing

```bash
# List all JCL members
find <jcl_path> -maxdepth 2 -type f | head -200

# Extract job names and entry programs
grep -rn "EXEC PGM=NAT\|FIRSTPGM=\|PROGRAM=" <jcl_path> | head -100

# Extract all DD dataset names
grep -rn "^//[A-Z0-9]* *DD " <jcl_path> | grep "DSN=" | sed "s/.*DSN=\([^,)]*\).*/\1/" | sort -u

# Find GDG base names
grep -rn "GDG\|G[0-9][0-9][0-9][0-9]V" <jcl_path> | grep "DSN=" | sort -u

# Extract TWS / CA7 scheduler comments
grep -rn "TWS\|CA7\|CTRL-M\|SCHEDULE\|FREQUENCY" <jcl_path>
```

### Natural parsing

```bash
# Count Natural members by type indicator in source
grep -rln "^DEFINE DATA"       <natural_path> | wc -l   # Programs
grep -rln "^DEFINE SUBROUTINE" <natural_path> | wc -l   # Subroutines
grep -rln "^DEFINE MAP"        <natural_path> | wc -l   # Maps
grep -rln "^DEFINE DATA GLOBAL"<natural_path> | wc -l   # Global data areas

# Extract all CALLNAT targets (outbound edges)
grep -rn "CALLNAT" <natural_path> | \
  sed "s/.*CALLNAT[[:space:]]*'\([^']*\)'.*/\1/" | sort | uniq -c | sort -rn

# Extract all ADABAS file numbers accessed
grep -rn "READ FILE\|FIND FILE\|STORE FILE\|UPDATE (" <natural_path> | \
  grep -oP "FILE \K[0-9]+" | sort -n | uniq -c

# Extract all PERFORM targets (subroutine calls)
grep -rn "^[[:space:]]*PERFORM " <natural_path> | \
  awk '{print $2}' | sort | uniq -c | sort -rn

# Extract ADABAS field names used in READ/FIND blocks
# (fields appear between the READ FILE statement and the END-READ)
grep -rn "READ FILE [0-9]" <natural_path> -A 20 | grep -v "^--$" | head -500

# Identify reference table reads (by ISN or LOGICAL with fixed length)
grep -rn "READ LOGICAL\|READ BY ISN\|GET FILE" <natural_path>

# Find programs that write to work files (potential GDG producers)
grep -rn "WRITE WORK FILE\|CLOSE WORK FILE" <natural_path>
```

---

## Step 7 — Handling Scale (52,000+ modules)

Do not attempt to read every file individually. Use the following chunked strategy:

### Phase 1 — Index (fast, grep-based)

Build the call graph index purely from `grep` output without opening individual files:

```bash
# Build CALLNAT edge list in one pass
grep -rn "CALLNAT" <natural_path> --include="*.NSP" --include="*.NSN" | \
  awk -F: '{gsub(/.*CALLNAT[ \x27]+/,"",$2); gsub(/[\x27 ].*/,"",$2); print $1, $2}' | \
  sed "s|<natural_path>/||" > /tmp/callnat_edges.txt

# Build ADABAS access index in one pass
grep -rn "READ FILE\|STORE FILE\|UPDATE (" <natural_path> | \
  grep -oP "([\w/]+\.NS[PNSDC]).*FILE \K[0-9]+" > /tmp/adabas_access.txt

# Build reference table read-length index
grep -rn "READ LOGICAL BY\|READ BY ISN" <natural_path> | head -5000 > /tmp/ref_reads.txt
```

### Phase 2 — Targeted deep reads

After building the index, open individual files only for:
- Entry programs named in JCL (highest priority — ~50 files)
- Modules with the highest fan-in (called by 10+ programs) — these are shared utilities
- Programs flagged as decommission candidates (verify purpose before recommending removal)
- Any module whose grep output is ambiguous

### Phase 3 — Incremental refinement

If the full estate cannot be processed in a single session:
1. Deliver the HTML prototype with available data and mark unresolved nodes as `[PENDING ANALYSIS]`
2. On each subsequent session, pass in additional parsed data to expand the graph
3. The HTML file is regenerated each time — all data is embedded, no database required

---

## Output File Specification

All output files are written to `/mnt/user-data/outputs/`.

| File | When produced | Description |
|---|---|---|
| `mfrea.html` | Always | Self-contained HTML with all six tabs and embedded data |
| `01-dependency-tree.md` | If user requests Markdown | ASCII call hierarchy |
| `02-adabas-usage.md` | If user requests Markdown | Per-file program × field tables |
| `03-ref-table-usage.md` | If user requests Markdown | Per-table readLen inference |
| `04-functional-view.md` | If user requests Markdown | Business description tree |
| `05-program-decommission.md` | If user requests Markdown | Decommission scorecard table |
| `06-job-decommission.md` | If user requests Markdown | Per-job checklist |
| `mfrea-data.json` | Optional | Raw parsed data in JSON for downstream tools |

---

## Zero-Hallucination Rules

1. **Never invent a description** not derivable from code patterns. Use "Purpose requires clarification" when ambiguous.
2. **Never mark a module as safe to decommission** if it appears in `parentMap` with active (KEEP-status) callers — even if its own run count is zero. Surface the conflict explicitly.
3. **Never drop an ADABAS file** because a single job using it is decommissioned. Always check whether any other KEEP job accesses the same file.
4. **Never infer field names** for ADABAS structured files from reference table logic. Apply read-length field inference only to reference table files (those read exclusively in READ LOGICAL / BY ISN mode with no write access).
5. **Never assume a program's purpose** from its name alone. Confirm from code patterns. Names can be misleading on legacy estates.
6. **Flag every assumption** in the relevant card / node description as `[ASSUMED — verify with team]`.

---

## Domain Knowledge — CRD Mainframe Context

These mappings are specific to the CRD (Client Reference Data) Natural/ADABAS estate at Morgan Stanley
and should be applied when naming ADABAS files and reference tables if file numbers are recognised:

| File no. | Likely name | Domain |
|---|---|---|
| 005 | CLIENTS | Client master — KYC, identity, domicile |
| 007 | POSITIONS | Portfolio positions — ISIN, quantity, market value |
| 012 | ACCOUNTS | Account records — balance, status, currency |
| 019 | MARKET-DATA | Settlement prices and FX rates |
| 031 | TRANSACTIONS | Full transaction history |
| 044 | RISK-RESULTS | VaR and stress test output |

Common reference tables:

| Table name | Content |
|---|---|
| CURRENCY-REF | ISO 4217 codes, decimal places, rounding rules |
| COUNTRY-REF | ISO 3166-1 alpha-2 codes, region groupings |
| STATUS-REF | Account and client status codes with transition rules |
| PRODUCT-REF | Product catalogue, fee schedules, compliance flags |
| RATING-REF | Credit rating agency equivalence map |

Common Natural naming conventions observed in CRD estate:

| Prefix | Typical purpose |
|---|---|
| `PGM*` | Top-level program invoked directly by JCL |
| `GET*` | Read-only ADABAS retrieval subprogram |
| `UPD*` | Update / write subprogram |
| `RPT*` / `RPTOUT` | Report output writer |
| `CALC*` | Calculation engine |
| `VAL*` / `CHK*` | Validation routine |
| `ARCH*` | Archival program |
| `ADA*` | Generic ADABAS I/O utility |
| `MATH*` | Shared maths / statistical library |
| `FMT*` | Formatting utility |

---

## Decommission Guidance — Decision Rules

Apply these rules to classify each program and each job:

### Program status

| Condition | Status | Colour |
|---|---|---|
| Monthly runs = 0 AND no active callers in parentMap | DECOMMISSION | Red |
| Monthly runs = 0 BUT has active callers | INVESTIGATE — do not decommission without caller analysis | Amber |
| 0 < monthly runs < 500 | REVIEW — confirm business need | Amber |
| Monthly runs ≥ 500 | KEEP — active | Green |
| Not found in usage extract | UNKNOWN — treat as REVIEW | Grey |

### Job status

| Condition | Status |
|---|---|
| All programs called by job have status DECOMMISSION + no active output consumers confirmed | DECOMMISSION |
| Entry program runs = 0 but output dataset consumed by another active job | INVESTIGATE |
| Entry program runs < 500 | REVIEW |
| Entry program runs ≥ 500 | KEEP |

### Shared module rule

If a module is DECOMMISSION status but appears in `parentMap` of any KEEP-status program:
- Do **not** mark it for decommission
- Instead flag it: `⚠ SHARED — called by [list of active programs] — remove only after those callers are retired`

### Shared ADABAS file rule

Before recommending removal of any ADABAS file referenced by a decommission candidate:
- Check all other programs in the estate for access to the same file number
- If any KEEP program accesses the file → emit: `⚠ ADABAS File NNN still needed by: [program list] — do NOT drop`

---

## Quality Checklist

Before delivering any output, verify:

- [ ] All JCL jobs have been parsed and appear in the dependency tree
- [ ] All CALLNAT edges are bidirectional in parentMap and childMap
- [ ] Shared modules are marked with `*` and listed in the side panel
- [ ] ADABAS access mode (R/W/RW) is correctly assigned — not guessed from name
- [ ] Reference table field inference uses read-length algorithm, not assumed field names
- [ ] Every program in the usage extract has been matched to a parsed module (report unmatched names)
- [ ] Every zero-run program has been checked against parentMap before being recommended for decommission
- [ ] Every decommission JCL checklist includes the shared ADABAS file warning where applicable
- [ ] Functional descriptions contain no technical content (no file numbers, no SQL, no Natural keywords)
- [ ] All output files are in `/mnt/user-data/outputs/`
- [ ] HTML file opens and renders correctly without a server (all CDN scripts load from cdnjs or jsdelivr)

---

## Extending the Agent

The following views can be added in future iterations:

| Planned view | Description |
|---|---|
| **ADABAS schema explorer** | Upload FDT export to resolve field names from field descriptors rather than inferring from READ statements |
| **Impact analyser** | Given a proposed field rename or file structure change, list every program that would be affected |
| **Migration planner** | Map Natural programs to candidate Java/Spring equivalents based on function type |
| **Batch window optimiser** | Plot job run-times from SMF records against TWS schedule to identify parallelisation opportunities |
| **Regulatory tagging** | Tag each program with applicable regulations (MiFID II, EMIR, GDPR, AML) based on ADABAS files accessed and field names |
| **Dead code scanner** | Identify Natural subroutines that are defined (DEFINE SUBROUTINE) but never referenced in any PERFORM statement across the estate |
