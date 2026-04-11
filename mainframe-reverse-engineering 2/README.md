# Mainframe Reverse Engineering Suite

A complete, importable skill project for deep analysis of mainframe codebases (Natural/Adabas, COBOL, JCL, CICS). Drop this folder into any project to enable 12 analysis skills, 4 agents, and 4 executable tools.

## Installation — Copy Into Any Project

### Option A: Claude Code / Cowork (recommended)
```bash
# Copy the folder into your project's user skills directory
cp -r mainframe-reverse-engineering/ /mnt/skills/user/

# That's it. The skill triggers automatically on mainframe-related requests.
```

### Option B: Existing Claude Project
```bash
# Copy into your existing project structure
cp -r mainframe-reverse-engineering/ /path/to/your-project/skills/

# Or wherever your project keeps its skills
cp -r mainframe-reverse-engineering/ /path/to/your-project/
```

### Option C: Claude Projects (web UI)
Upload the entire `mainframe-reverse-engineering/` folder as project knowledge. The orchestrator SKILL.md triggers automatically on any mainframe-related request.

### Option D: Any AI Tool (manual)
Paste the contents of `SKILL.md` as your system prompt. Then paste individual skill `.md` files as needed for specific analyses.

### Folder Structure After Copy

Your project should look like this:
```
your-existing-project/
├── your-existing-files/
├── ...
└── mainframe-reverse-engineering/     ← copied here
    ├── SKILL.md                       ← orchestrator (auto-triggers)
    ├── skills/                        ← 12 analysis skills
    ├── agents/                        ← 4 agent roles
    ├── references/                    ← glossary, templates
    ├── scripts/                       ← scanner, viewer, FRD tools
    └── evals/                         ← test cases
```

All paths inside the project are **relative** — it works wherever you put it.

## What's Included

### 12 Skills

| # | Skill | Purpose | Trigger |
|---|---|---|---|
| 1 | top-down-trace | Program → Adabas deep dive | `DEEP DIVE`, `SURFACE SCAN` |
| 2 | bottom-up-trace | Adabas file → all programs | `BOTTOM UP` |
| 3 | cics-transaction | CICS transaction end-to-end | `TXN TRACE` |
| 4 | field-trace | Single field lifecycle | `FIELD TRACE` |
| 5 | field-lineage-analyzer | Deep value provenance (HOW values are derived) | `FIELD LINEAGE` |
| 6 | jcl-analysis | Batch job step analysis | `JCL TRACE` |
| 7 | ddm-reference | DDM structure & ref tables | DDM or ref table questions |
| 8 | flowchart-gen | Mermaid diagrams (8 types) | `FLOW CHART` |
| 9 | validation-extract | Business rule extraction | `RULES` |
| 10 | impact-analysis | Change impact assessment | `IMPACT CHECK` |
| 11 | documentation-output | Word/Excel/MD formatting | `DOCUMENT` |
| 12 | mfrea-viewer-generator | HTML viewer + scanner generator | `GENERATE VIEWER` |

### 4 Agents

| Agent | Role |
|---|---|
| orchestrator | Routes requests to skills, chains multi-skill workflows |
| code-scanner | Parses Natural/COBOL/JCL, extracts structured data |
| reviewer | Cross-checks analysis accuracy against source code |
| documenter | Formats output for professional delivery |

### 4 Executable Tools (in `scripts/`)

| Tool | Language | What It Does |
|---|---|---|
| `scanner.py` | Python | Scans 65K+ files → graph.json dependency graph |
| `field_analyzer.py` | Python | Deep field-level value provenance analysis |
| `frd_generator.py` | Python | Generates Functional Requirements Documents |
| `viewer.html` | HTML/React | Interactive browser-based dependency viewer |

### 3 References

| File | Content |
|---|---|
| system-context.md | Master analyst persona, output standards, issue markers |
| glossary.md | Natural/COBOL/CICS/Adabas/JCL quick reference tables |
| mermaid-templates.md | 8 ready-to-use diagram templates with colour schemes |

## Quick Start Examples

### Analyse a program
```
DEEP DIVE on this Natural program:
[paste code]
```

### Trace a field's value origin
```
FIELD LINEAGE for CUST-STATUS in DDM-CUSTOMER.
Show me how the value is derived in every program that touches it.
```

### Generate the dependency viewer
```
GENERATE VIEWER — I have 52K Natural modules and 13K JCL files.
```

### Check impact of a change
```
IMPACT CHECK — I want to change CUST-NAME from A50 to A100 in file 152.
```

### Generate an FRD
```
GENERATE FRD for program CUSTMAIN — non-technical, suitable for business stakeholders.
```

## Running the Tools

### Scan your codebase
```bash
python scripts/scanner.py \
  --natural /path/to/natural \
  --jcl /path/to/jcl \
  --output graph.json
```

### Analyse field lineage
```bash
python scripts/field_analyzer.py \
  --source /path/to/natural \
  --field CUST-STATUS \
  --output lineage.json
```

### Generate FRD
```bash
python scripts/frd_generator.py \
  --graph graph.json \
  --program CUSTMAIN \
  --output frd.md
```

### Open the viewer
```bash
open scripts/viewer.html
# Load graph.json when prompted
```

## Customisation

### Add a new skill
1. Create `skills/your-skill-name/SKILL.md` with YAML frontmatter
2. Add an entry to the routing table in the main `SKILL.md`
3. Add a command keyword mapping if desired

### Adjust naming conventions
Edit the "Naming Conventions" table in `SKILL.md`.

### Extend for other languages
Add reference files under `references/` for PL/I, Assembler, DB2, IMS, MQ Series etc.

## Requirements

- **Skills/Agents**: Any AI assistant that supports skill-based workflows (Claude Code, Cowork, Claude Projects)
- **Python tools**: Python 3.7+ (no external dependencies)
- **Viewer**: Modern browser (Chrome, Firefox, Edge)
