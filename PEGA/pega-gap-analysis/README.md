# PEGA Gap Analysis — Bridge Between Source & Target

## What This Is

A **bridge toolkit** that connects two projects and finds every gap between them:

- **Source Project** = PEGA Reverse Engineering output (your FRD, flows, decisions, integrations, UI specs)
- **Target Project** = Your new application being built
- **Deep Search Agents** = Your existing deep search project used to scan both codebases

This toolkit links all three, runs systematic comparison, and surfaces exactly what's missing, incomplete, or different in the new project.

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐
│  PEGA RE Project     │     │  New Target Project   │
│  (Source of Truth)   │     │  (Being Built)        │
│                      │     │                       │
│  • FRD findings      │     │  • Source code         │
│  • Flow analyses     │     │  • API definitions     │
│  • Decision rules    │     │  • UI components       │
│  • Integration specs │     │  • DB schemas          │
│  • UI field specs    │     │  • Config files        │
└──────────┬───────────┘     └──────────┬────────────┘
           │                            │
           ▼                            ▼
    ┌──────────────────────────────────────────┐
    │        GAP ANALYSIS BRIDGE               │
    │                                          │
    │  Agent 10: Source Indexer                 │
    │  Agent 11: Target Scanner (Deep Search)  │
    │  Agent 12: Requirement Mapper            │
    │  Agent 13: Gap Detector                  │
    │  Agent 14: Impact Assessor               │
    │  Agent 15: Gap Report Generator          │
    │                                          │
    │  Skills:                                 │
    │  • deep-search-linker                    │
    │  • cross-project-mapper                  │
    │  • coverage-calculator                   │
    │  • gap-classifier                        │
    └──────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  GAP REPORT          │
    │  • Missing features  │
    │  • Partial impls     │
    │  • Logic gaps        │
    │  • UI field gaps     │
    │  • Integration gaps  │
    │  • Decision rule gaps│
    └──────────────────────┘
```

## Quick Start

```
1. Copy this folder alongside your existing projects
2. Edit config/bridge-config.md with paths to BOTH projects
3. Paste ORCHESTRATOR-BRIDGE.md into Copilot Chat
4. Follow the 6-phase workflow
5. Track progress in workspace/GAP-TASK-LIST.md
```

## Folder Structure

```
pega-gap-analysis/
├── README.md
├── ORCHESTRATOR-BRIDGE.md        ← Start here
├── config/
│   └── bridge-config.md          ← Paths to both projects
├── agents/
│   ├── 10-source-indexer.md      ← Index all PEGA RE findings
│   ├── 11-target-scanner.md      ← Deep search the new project
│   ├── 12-requirement-mapper.md  ← Map source requirements → target
│   ├── 13-gap-detector.md        ← Find what's missing/incomplete
│   ├── 14-impact-assessor.md     ← Score severity of each gap
│   └── 15-gap-report-generator.md← Compile final gap report
├── skills/
│   ├── deep-search-linker.md     ← Connect to your deep search agents
│   ├── cross-project-mapper.md   ← Map artifacts across projects
│   ├── coverage-calculator.md    ← Calculate % implementation coverage
│   └── gap-classifier.md         ← Classify gap type and severity
├── workspace/
│   ├── GAP-TASK-LIST.md          ← Master tracking
│   ├── gaps/                     ← Individual gap reports
│   ├── mappings/                 ← Source→Target mapping files
│   └── deep-search-results/      ← Deep search agent outputs
└── references/
    └── gap-taxonomy.md           ← Classification of gap types
```

## Workflow

```
Phase 1: INDEX SOURCE — Catalog every requirement from PEGA RE output
Phase 2: SCAN TARGET — Deep search the new project for implementations
Phase 3: MAP — Link each source requirement to target implementation
Phase 4: DETECT GAPS — Find missing, partial, and divergent items
Phase 5: ASSESS IMPACT — Score each gap by severity and risk
Phase 6: REPORT — Generate comprehensive gap analysis report
```
