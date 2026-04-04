# Mainframe Analyst — AI Skill Suite

A modular, importable skill project for deep analysis of mainframe codebases (Natural/Adabas, COBOL, JCL, CICS). Designed for use with Claude and other AI assistants that support skill-based workflows.

## What This Does

Drop your mainframe source code into a conversation and use command keywords to get:

| Command | Result |
|---------|--------|
| `DEEP DIVE` | Full recursive program trace with call chains, DB access, flowcharts |
| `SURFACE SCAN` | Quick one-page program summary |
| `BOTTOM UP` | Trace from Adabas file/field upward to every program that uses it |
| `FIELD TRACE` | End-to-end lineage of a single field across the entire system |
| `TXN TRACE` | Complete CICS transaction analysis: screens, fields, validations |
| `JCL TRACE` | Batch job flow with step breakdown and data pipeline |
| `IMPACT CHECK` | Ripple-effect analysis for proposed changes |
| `RULES` | Extract all validation and business rules |
| `FLOW CHART` | Generate Mermaid diagrams of any analysis |
| `DOCUMENT` | Format output as Word/Excel/Markdown |

## Project Structure

```
mainframe-analyst/
├── SKILL.md                          # Main orchestrator (start here)
├── README.md                         # This file
│
├── agents/                           # Agent role definitions
│   ├── orchestrator.md               # Routes requests to skills
│   ├── code-scanner.md               # Parses and extracts from source
│   ├── reviewer.md                   # Verifies analysis accuracy
│   └── documenter.md                 # Formats professional output
│
├── skills/                           # Modular analysis skills
│   ├── top-down-trace/SKILL.md       # Program → Adabas trace
│   ├── bottom-up-trace/SKILL.md      # Adabas → Program trace
│   ├── cics-transaction/SKILL.md     # CICS transaction analysis
│   ├── field-trace/SKILL.md          # Field lineage tracking
│   ├── jcl-analysis/SKILL.md         # JCL job flow analysis
│   ├── ddm-reference/SKILL.md        # DDM & reference table analysis
│   ├── flowchart-gen/SKILL.md        # Mermaid diagram generation
│   ├── validation-extract/SKILL.md   # Business rule extraction
│   ├── impact-analysis/SKILL.md      # Change impact assessment
│   └── documentation-output/SKILL.md # Output formatting (Word/Excel/MD)
│
├── references/                       # Supporting reference docs
│   ├── system-context.md             # Master persona & standards
│   ├── glossary.md                   # Mainframe terminology reference
│   └── mermaid-templates.md          # Ready-to-use diagram templates
│
└── evals/                            # Test cases
    └── evals.json                    # 5 test prompts for validation
```

## How to Use

### Option 1: Import as a Skill (Claude Code / Cowork)

1. Copy the `mainframe-analyst/` folder into your skills directory
2. The orchestrator SKILL.md will trigger automatically when mainframe code is discussed
3. Sub-skills are loaded on demand based on the analysis type

### Option 2: Manual Usage (Claude.ai / ChatGPT)

1. Start a new conversation
2. Paste the contents of `SKILL.md` as your first message (or system prompt)
3. Paste the contents of `references/system-context.md` as context
4. Paste your mainframe code with its file path prefix
5. Use command keywords (DEEP DIVE, SURFACE SCAN, etc.)

### Option 3: Cherry-Pick Individual Skills

Each skill in `skills/` is self-contained. You can use any individual skill independently:

1. Open the skill's `SKILL.md` file
2. Paste it as context into your AI session
3. Follow the templates in that skill

## Expected Code Organisation

The skills expect your mainframe code to be organised by Natural library:

```
/mainframe-code/
  /CUSTLIB/                    # Library name
    /natural/                   # Natural programs
    /cobol/                     # COBOL programs
    /jcl/                       # JCL job streams
    /jobs/                      # Scheduled jobs
    /ddm/                       # Adabas DDM definitions
    /adabas/                    # Adabas FDT definitions
    /copybooks/                 # Copybooks / copycodes
    /maps/                      # Screen maps
    /ref-tables/                # Reference tables
```

Adjust folder names in `SKILL.md` Section "Folder Structure Awareness" if your layout differs.

## Workflow Examples

### "I want to understand what program CUSTMAIN does"

```
1. Paste SKILL.md as system context
2. Say: DEEP DIVE
3. Paste the program code prefixed with its path
4. Get: Full call chain, DB access map, flowchart, issues
5. Say: FLOW CHART — to get just the Mermaid diagram
6. Say: DOCUMENT — to get a formatted Word report
```

### "What happens if we change CUST-STATUS from A1 to A3?"

```
1. Paste SKILL.md as system context
2. Say: IMPACT CHECK on field CUST-STATUS in file 152 (DDM-CUSTOMER)
        The change is: increase length from A1 to A3
3. Paste all programs that reference this DDM
4. Get: Full impact matrix, risk ratings, action plan
```

### "Map the complete nightly batch process"

```
1. Paste SKILL.md as system context
2. Say: JCL TRACE
3. Paste the JCL job stream
4. Paste source for each program referenced in the JCL
5. Get: Step breakdown, program analysis, data pipeline, flowchart
```

## Customisation

### Adding New Skills

1. Create a new folder under `skills/`
2. Add a `SKILL.md` with YAML frontmatter (name, description)
3. Add an entry to the routing table in the main `SKILL.md`
4. Add a command keyword mapping if desired

### Modifying Naming Conventions

Edit the "Naming Conventions" table in the main `SKILL.md` to match your organisation's standards.

### Extending for Other Languages

The skill architecture supports adding new language modules. Create reference files under `references/` for:
- PL/I programs
- Assembler programs  
- DB2 / SQL analysis
- IMS database access
- MQ Series message flow

## Test Cases

The `evals/evals.json` file contains 5 test prompts covering:
1. Top-down Natural program analysis
2. Bottom-up Adabas file trace
3. CICS transaction trace
4. Field-level lineage
5. JCL batch job analysis

Use these to validate the skill works correctly after any modifications.
