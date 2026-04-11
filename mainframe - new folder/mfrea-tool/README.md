# MFREA Tool — Mainframe Reverse Engineering Agent

A Python scanner + interactive HTML viewer for analysing 52,000+ Natural modules and 13,000+ JCL files.

## What It Does

**Scanner** (`scanner.py`) — Parses all your Natural and JCL files using regex to extract:
- Every CALLNAT / FETCH / PERFORM / EXEC PGM call chain
- Every Adabas DDM access with operation type and field names
- Every reference table lookup
- Bidirectional dependency links (who calls whom, who is called by whom)
- Outputs a single `graph.json` file

**Viewer** (`viewer/index.html`) — Interactive browser-based UI with 4 tabs:

| Tab | What It Does |
|-----|-------------|
| **Dependency Tree** | Searchable tree of all 65K+ modules. Click any node to highlight upstream (green) and downstream (orange) dependencies. Expand/collapse branches. |
| **Adabas Files** | Select any DDM → see every program that accesses it. Filter by operation (READ/STORE/UPDATE/DELETE) and by specific field name. |
| **Ref Tables** | Select any reference table → see every program that reads it with the lookup field used. |
| **Functional / FRD** | Non-technical functional decomposition tree. Select any program or table and generate a complete Functional Requirements Document (downloadable as .md). |

**FRD Generator** (`frd_generator.py`) — Command-line tool to generate FRDs for:
- A specific program (top-down functional decomposition)
- A specific DDM/Adabas file (all programs and field usage)
- A specific field within a DDM (full field lineage)

## Quick Start

### Step 1: Scan your codebase

```bash
python scanner/scanner.py \
  --natural /path/to/your/52000-natural-modules \
  --jcl /path/to/your/13000-jcl-files \
  --output graph.json \
  --workers 8
```

This will:
- Scan all files using 8 parallel workers
- Extract all relationships
- Build bidirectional dependency graph
- Output `graph.json` (~50-200 MB depending on codebase size)

Expected runtime: **3-10 minutes** for 65K files on modern hardware.

### Step 2: Open the viewer

```bash
# Simply open the HTML file in your browser
open viewer/index.html
# or
python -m http.server 8080 --directory viewer/
# then open http://localhost:8080
```

Click **"Load graph.json"** and select the file generated in Step 1.

### Step 3: Generate FRDs (optional command-line)

```bash
# FRD for a specific program
python scanner/frd_generator.py \
  --graph graph.json \
  --program CUSTMAIN \
  --output frd_CUSTMAIN.md

# FRD for an Adabas file/DDM
python scanner/frd_generator.py \
  --graph graph.json \
  --ddm DDM-CUSTOMER \
  --output frd_customer.md

# FRD for a specific field
python scanner/frd_generator.py \
  --graph graph.json \
  --ddm DDM-CUSTOMER \
  --field CUST-STATUS \
  --output frd_custstatus.md
```

## Project Structure

```
mfrea-tool/
├── scanner/
│   ├── scanner.py          # Main scanner (Natural + JCL parser)
│   └── frd_generator.py    # FRD generation (program, DDM, field)
├── viewer/
│   └── index.html          # Interactive HTML viewer (React-based)
├── output/                 # Default output directory
└── README.md
```

## Viewer Features

### 1. Dependency Tree (Tab 1)
- Left sidebar shows all root programs (programs not called by anything)
- **Search** by program name — filters the entire tree instantly
- **Click** any node to select it:
  - Green highlight = upstream callers (who calls this program)
  - Orange highlight = downstream callees (what this program calls)
- **Expand/collapse** branches to navigate the call hierarchy
- Right panel shows full detail: calls, callers, DB access, maps, ref tables

### 2. Adabas File Filter (Tab 2)
- Dropdown lists all DDMs found in the codebase with program count
- Select a DDM → see every program accessing it
- **Filter by operation**: click READ, STORE, UPDATE, DELETE, etc.
- **Filter by field**: type a field name to find only programs using that field
- Click any program row to jump to its detail in Tab 1

### 3. Reference Table Filter (Tab 3)
- Dropdown lists all detected reference tables
- Shows every program reading each table with the lookup field used
- Click any program to navigate to its detail

### 4. Functional View + FRD (Tab 4)
- Shows a **non-technical** decomposition tree for the selected program
  - No code details, just function names and inferred purposes
  - Shows which screens and data entities each function uses
- **Generate FRD** button creates a downloadable Functional Requirements Document
  - Supports: Program FRD, DDM FRD, Field lineage FRD
  - Includes: functional overview, user interface, data entities, process flow, business rules

## Scanner Details

### Natural Patterns Detected

| Pattern | Example |
|---------|---------|
| CALLNAT | `CALLNAT 'CUSTUPD' #ID #NAME` |
| FETCH | `FETCH 'MAINMENU'` |
| MAP usage | `INPUT USING MAP 'M-CUSTDISP'` |
| DB READ | `READ CUST-VIEW BY CUST-ID` |
| DB FIND | `FIND CUST-VIEW WITH STATUS = 'A'` |
| DB STORE | `STORE CUST-VIEW` |
| DB UPDATE | `UPDATE CUST-VIEW` |
| DB DELETE | `DELETE CUST-VIEW` |
| VIEW definition | `1 CV VIEW OF DDM-CUSTOMER` |
| Data areas | `LOCAL USING LDA-CUSTDATA` |
| Ref table | `READ REF-STATUS WITH KEY = #CODE` |

### JCL Patterns Detected

| Pattern | Example |
|---------|---------|
| EXEC PGM | `//STEP01 EXEC PGM=NATBATCH` |
| PARM (Natural programs) | `PARM='CUSTLIB,EXTCUST'` |
| DD DSN | `//INPUT DD DSN=PROD.CUST.DATA` |

### Performance

The scanner uses Python's `ProcessPoolExecutor` for parallel file processing:

| Files | Workers | Approx Time |
|-------|---------|-------------|
| 10,000 | 4 | ~30 seconds |
| 30,000 | 8 | ~2 minutes |
| 65,000 | 8 | ~5 minutes |

### Output Format (graph.json)

```json
{
  "metadata": { "generated": "...", "stats": { ... } },
  "modules": {
    "PROGNAME": {
      "name": "PROGNAME",
      "type": "program|subprogram|jcl|map|...",
      "library": "LIBNAME",
      "calls": [{"target": "SUBPROG", "type": "CALLNAT"}],
      "called_by": ["MAINPROG"],
      "db_access": [{"ddm": "DDM-CUSTOMER", "operation": "READ", "fields": ["CUST-ID","CUST-NAME"]}],
      "maps": ["M-CUSTDISP"],
      "ref_tables": [{"table": "REF-STATUS", "field": "STATUS-CODE", "type": "LOOKUP"}]
    }
  },
  "adabas_index": { "DDM-CUSTOMER": { "programs": [...], "fields": [...] } },
  "ref_table_index": { "REF-STATUS": [...] },
  "roots": ["MAINMENU", "JCL-NIGHTLY", ...],
  "leaves": ["SUB-FORMAT", "HELP-DATE", ...]
}
```

## Customisation

### Adding new Natural file extensions
Edit `NATURAL_EXTENSIONS` dictionary in `scanner.py`.

### Adjusting field extraction depth
Change the `[:8]` and `[:20]` limits in `_extract_fields_from_context()` to capture more or fewer fields per DB access.

### Viewer styling
The viewer uses CSS variables at the top of `index.html` — adjust colours to match your organisation's branding.

## Requirements

- **Python 3.7+** (no external dependencies — stdlib only)
- **Modern browser** (Chrome, Firefox, Edge) for the viewer
- ~2-4 GB RAM for scanning 65K files
- graph.json can be 50-200 MB; the viewer loads it client-side
