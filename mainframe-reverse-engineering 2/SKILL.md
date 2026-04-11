---
name: mainframe-reverse-engineering
description: "Complete mainframe reverse engineering suite for Natural/Adabas, COBOL, JCL, and CICS codebases. Provides 12 specialised skills covering: top-down program tracing, bottom-up Adabas file tracing, CICS transaction analysis, field-level lineage and value provenance, JCL batch job analysis, DDM and reference table mapping, Mermaid flowchart generation, validation and business rule extraction, change impact analysis, documentation output (Word/Excel/MD), interactive HTML dependency viewer generation, and deep field-level value derivation analysis. Use this skill whenever the user mentions mainframe code, Natural programs, Adabas files, DDMs, COBOL, JCL jobs, CICS transactions, field lineage, reverse engineering, program dependencies, call chains, data flows, impact analysis, FRD generation, or wants any form of analysis on legacy mainframe systems. Even casual requests like 'what does this code do' or 'trace this program' should trigger this skill if the code is Natural, COBOL, or JCL."
---

# Mainframe Reverse Engineering Suite

A complete, modular toolkit for deep analysis of mainframe codebases. Copy this entire folder into your project's skills directory to enable all capabilities.

## Quick Start

1. Copy `mainframe-reverse-engineering/` into your `/mnt/skills/user/` directory
2. All 12 skills activate automatically based on user requests
3. Use command keywords (below) for precise control

## Installation

```
/mnt/skills/user/mainframe-reverse-engineering/   ← copy this entire folder
```

The orchestrator SKILL.md (this file) triggers on any mainframe-related request. It reads the matching sub-skill before producing output.

## Command Keywords

| Command | Skill Invoked | What It Does |
|---|---|---|
| `DEEP DIVE` | top-down-trace | Full recursive program trace to Adabas |
| `SURFACE SCAN` | top-down-trace (surface mode) | Quick one-page summary |
| `BOTTOM UP` | bottom-up-trace | Trace from Adabas file/field to all programs |
| `FIELD TRACE` | field-trace | Follow one field end-to-end |
| `FIELD LINEAGE` | field-lineage-analyzer | Deep value provenance (how each value was derived) |
| `TXN TRACE` | cics-transaction | Full CICS transaction analysis |
| `JCL TRACE` | jcl-analysis | Batch job step-by-step analysis |
| `IMPACT CHECK` | impact-analysis | Ripple-effect analysis for proposed changes |
| `FLOW CHART` | flowchart-gen | Generate Mermaid diagrams |
| `RULES` | validation-extract | Extract validations and business rules |
| `DOCUMENT` | documentation-output | Format output for Word/Excel/MD |
| `GENERATE VIEWER` | mfrea-viewer-generator | Build the interactive HTML dependency viewer |
| `GENERATE SCANNER` | mfrea-viewer-generator | Build the Python codebase scanner |
| `GENERATE FRD` | documentation-output + field-lineage-analyzer | Produce functional requirements doc |

## Routing Table

When a user request arrives, read the matching skill BEFORE producing any output:

| User Wants To... | Read This Skill |
|---|---|
| Trace a program top-down to Adabas | `skills/top-down-trace/SKILL.md` |
| Trace from Adabas file/field up to programs | `skills/bottom-up-trace/SKILL.md` |
| Analyse a CICS transaction end-to-end | `skills/cics-transaction/SKILL.md` |
| Follow a specific field across the system | `skills/field-trace/SKILL.md` |
| Understand how a field's value was derived | `skills/field-lineage-analyzer/SKILL.md` |
| Analyse JCL jobs and batch flows | `skills/jcl-analysis/SKILL.md` |
| Analyse DDMs or reference/lookup tables | `skills/ddm-reference/SKILL.md` |
| Generate Mermaid flowcharts or diagrams | `skills/flowchart-gen/SKILL.md` |
| Extract validation or business rules | `skills/validation-extract/SKILL.md` |
| Assess impact of a proposed change | `skills/impact-analysis/SKILL.md` |
| Format output for Word/Excel/documentation | `skills/documentation-output/SKILL.md` |
| Generate the interactive HTML viewer tool | `skills/mfrea-viewer-generator/SKILL.md` |
| Generate the Python scanner or FRD tool | `skills/mfrea-viewer-generator/SKILL.md` |
| Deep field value provenance analysis | `skills/field-lineage-analyzer/SKILL.md` |

## Multi-Skill Chaining

Complex requests require multiple skills in sequence:

| Goal | Chain |
|---|---|
| Understand a single program | top-down-trace → flowchart-gen → documentation-output |
| Full transaction analysis | cics-transaction → field-trace → flowchart-gen |
| Adabas change impact | bottom-up-trace → field-lineage-analyzer → impact-analysis |
| Document the nightly batch | jcl-analysis → top-down-trace → flowchart-gen → documentation-output |
| Full field provenance with FRD | field-lineage-analyzer → field-trace → documentation-output |
| Build analysis tooling | mfrea-viewer-generator (generates scanner + viewer + FRD tool) |
| Map all fields in a DDM | ddm-reference → field-lineage-analyzer → documentation-output |

## Project Structure

```
mainframe-reverse-engineering/
├── SKILL.md                              ← You are here (orchestrator)
├── README.md                             ← Setup and usage guide
│
├── skills/                               ← 12 modular analysis skills
│   ├── top-down-trace/SKILL.md           ← Program → Adabas trace
│   ├── bottom-up-trace/SKILL.md          ← Adabas → Program trace
│   ├── cics-transaction/SKILL.md         ← CICS transaction analysis
│   ├── field-trace/SKILL.md              ← Field lifecycle tracking
│   ├── field-lineage-analyzer/SKILL.md   ← Deep value provenance
│   ├── jcl-analysis/SKILL.md             ← JCL job flow analysis
│   ├── ddm-reference/SKILL.md            ← DDM & reference table mapping
│   ├── flowchart-gen/SKILL.md            ← Mermaid diagram generation
│   ├── validation-extract/SKILL.md       ← Business rule extraction
│   ├── impact-analysis/SKILL.md          ← Change impact assessment
│   ├── documentation-output/SKILL.md     ← Word/Excel/MD formatting
│   └── mfrea-viewer-generator/SKILL.md   ← HTML viewer + scanner generator
│
├── agents/                               ← 4 agent role definitions
│   ├── orchestrator.md                   ← Routes and chains workflows
│   ├── code-scanner.md                   ← Parses source code
│   ├── reviewer.md                       ← Verifies analysis accuracy
│   └── documenter.md                     ← Formats professional output
│
├── references/                           ← Supporting reference docs
│   ├── system-context.md                 ← Master persona & output standards
│   ├── glossary.md                       ← Mainframe terminology reference
│   └── mermaid-templates.md              ← 8 diagram type templates
│
├── scripts/                              ← Executable tools
│   ├── scanner.py                        ← Scans 65K+ Natural/JCL files → graph.json
│   ├── field_analyzer.py                 ← Deep field lineage scanner
│   ├── frd_generator.py                  ← FRD document generator
│   └── viewer.html                       ← Interactive HTML dependency viewer
│
└── evals/                                ← Test cases
    └── evals.json                        ← 5 validation prompts
```

## Naming Conventions

All output uses these consistent prefixes:

| Prefix | Meaning | Example |
|---|---|---|
| `PGM-` | Natural or COBOL program | PGM-CUSTMAINT |
| `SUB-` | Subprogram / helproutine | SUB-VALDATE |
| `MAP-` | Screen map definition | MAP-CUSTINQ |
| `JCL-` | JCL job stream | JCL-NIGHTBATCH |
| `DDM-` | Data Definition Module | DDM-CUSTOMER |
| `FILE-` | Adabas file (by number) | FILE-152 |
| `TXN-` | CICS transaction ID | TXN-CI01 |
| `REF-` | Reference/lookup table | REF-COUNTRYCODES |
| `LDA-` | Local Data Area | LDA-CUSTDATA |
| `GDA-` | Global Data Area | GDA-SESSION |

## Codebase Folder Structure

The skills expect code organised by Natural library:

```
/mainframe-code/
  /[LIBRARY-NAME]/
    /natural/       # .NSP .NSN .NSL .NSH .NSA .NSM .NSG
    /cobol/         # .CBL .COB
    /jcl/           # JCL job streams
    /ddm/           # Adabas DDM definitions
    /maps/          # Natural maps (screen layouts)
    /copybooks/     # Copybooks / copycodes
    /ref-tables/    # Reference/lookup tables
```

## Output Standards

Every analysis output must include:

1. **Identity block**: Program name, library, type, purpose
2. **Structured tables**: Markdown tables for inventories and matrices
3. **Mermaid diagrams**: Fenced ```mermaid blocks for all flowcharts
4. **Issue flags**: ⚠️ RISK, 🔴 MISSING, 💀 DEAD CODE, 📌 NOTE, ❓ UNRESOLVED
5. **Cross-references**: Links between related components
6. **Field provenance**: For every field, HOW its value was achieved

## Error Handling

When code is incomplete or references cannot be resolved:
- Mark with `[UNRESOLVED: reason]`
- List external dependencies needed
- Never guess at missing code — flag explicitly
- Suggest which files the user should provide next
