---
name: prea
description: >
  Pega Reverse Engineering Agent (PREA) — Use this skill for ANY task involving a Pega
  Platform codebase, rule estate, or application export. Triggers include: analysing Pega
  .bin binary files, extracting rules from Pega exports (.zip, .jar, .bin, manifest JSON),
  building rule dependency graphs, tracing flow execution paths, documenting Pega applications,
  generating Functional Requirements Documents (FRDs) from Pega rule sets, identifying
  decommission candidates, analysing UI rules (Sections, Harnesses, UI Forms), mapping
  Decision Tables, reverse engineering Data Transforms, and any request mentioning Pega,
  PRPC, Pega Platform, Pega Infinity, rule sets, ruleset versions, class hierarchy, 
  pyWorkPage, pxFlow, clipboard properties, or Pega-specific constructs.
  Always use this skill when the user uploads .bin files alongside manifest JSONs or
  mentions a layered Pega application structure (Framework / Industry / Enterprise / 
  Implementation).
---

# PREA — Pega Reverse Engineering Agent

A comprehensive skill for extracting, analysing, graphing, and documenting Pega Platform
applications from binary rule exports and manifest files.

---

## Architecture Overview

```
prea/
├── SKILL.md                      ← This file (orchestration entry point)
├── agents/
│   ├── binary-extractor.md       ← Agent: parse .bin files → rule records
│   ├── dependency-graph.md       ← Agent: build rule dependency graph
│   ├── flow-tracer.md            ← Agent: trace flow step chains
│   ├── frd-generator.md          ← Agent: produce FRD from rule inventory
│   └── decommission-scorer.md    ← Agent: score decommission candidates
├── scripts/
│   ├── pega_bin_extractor.py     ← Core binary parser (ALWAYS run first)
│   ├── pega_manifest_parser.py   ← Parse manifest JSONs → layer map
│   ├── pega_graph_builder.py     ← Build NetworkX dependency graph
│   ├── pega_flow_tracer.py       ← Trace flow execution paths
│   ├── pega_frd_writer.py        ← Write FRD to .docx
│   └── prea_orchestrator.py      ← Master pipeline runner
├── references/
│   ├── pega-rule-types.md        ← Complete Pega rule type reference
│   ├── pega-class-hierarchy.md   ← Pega class naming conventions
│   └── layer-override-rules.md   ← Layer precedence and override logic
└── tests/
    └── test_extractor.py         ← Unit tests for binary parser
```

---

## Step 0 — Determine Entry Point

Read the user's request and decide which path to take:

| User has... | Start at... |
|---|---|
| .bin files + manifest JSON | Step 1 (Binary Extraction) |
| Extracted rule CSV/JSON | Step 2 (Graph & Analysis) |
| Rule inventory, wants FRD | Step 4 (FRD Generation) |
| Specific flow to trace | Step 3 (Flow Tracing) |
| Decommission question | Step 5 (Decommission Scoring) |

---

## Step 1 — Binary Extraction (`.bin` files)

> Read `agents/binary-extractor.md` for full instructions.

**Quick path:**
```bash
# Install deps
pip install construct lxml tqdm anthropic --break-system-packages

# Run the extractor on a directory of .bin files
python scripts/pega_bin_extractor.py \
  --input-dir /path/to/bin/files \
  --manifest /path/to/manifest.json \
  --output /path/to/rules_extracted.json \
  --verbose

# Parse manifest for layer metadata
python scripts/pega_manifest_parser.py \
  --manifests /path/to/manifests/ \
  --output /path/to/layer_map.json
```

**Output:** `rules_extracted.json` — array of rule records:
```json
{
  "rule_id": "RULE-00001",
  "name": "ProcessKYCSubmission",
  "type": "Flow",
  "class": "Work-KYC-Case",
  "layer": "Enterprise",
  "ruleset": "KYCPlatform",
  "ruleset_version": "01-01-01",
  "status": "Active",
  "created": "2022-03-15",
  "updated": "2024-11-02",
  "checksum": "a3f7...",
  "raw_xml": "<flow>...</flow>",
  "dependencies": ["ValidateClientData", "EvaluateRiskScore"],
  "ui_fields": [],
  "conditions": [],
  "actors": []
}
```

---

## Step 2 — Graph Building

> Read `agents/dependency-graph.md` for full instructions.

```bash
python scripts/pega_graph_builder.py \
  --rules /path/to/rules_extracted.json \
  --output-graph /path/to/rule_graph.json \
  --output-html /path/to/rule_graph.html \
  --layer-filter Enterprise,Implementation
```

**Output:** Interactive D3.js force-directed graph HTML + `rule_graph.json` for downstream use.

---

## Step 3 — Flow Tracing

> Read `agents/flow-tracer.md` for full instructions.

```bash
python scripts/pega_flow_tracer.py \
  --rules /path/to/rules_extracted.json \
  --flow "ProcessKYCSubmission" \
  --output /path/to/flow_trace.json \
  --depth 10
```

**Output:** Step-by-step execution chain with conditions, actors, and branching logic.

---

## Step 4 — FRD Generation

> Read `agents/frd-generator.md` for full instructions.

```bash
python scripts/pega_frd_writer.py \
  --rules /path/to/rules_extracted.json \
  --graph /path/to/rule_graph.json \
  --flows /path/to/flow_traces/ \
  --output /path/to/FRD_output.docx \
  --system-name "KYC Platform" \
  --version "2.0"
```

---

## Step 5 — Decommission Scoring

> Read `agents/decommission-scorer.md` for full instructions.

```bash
python scripts/prea_orchestrator.py decomm \
  --rules /path/to/rules_extracted.json \
  --graph /path/to/rule_graph.json \
  --output /path/to/decomm_scorecard.xlsx
```

---

## Key Pega Concepts for Analysis

See `references/pega-rule-types.md` for the complete type reference.

**Critical rule types to identify in binary extraction:**

| Type Code | Rule Type | Binary Marker |
|---|---|---|
| `RULE-OBJ-FLOW` | Flow | `<flow` in XML |
| `RULE-OBJ-ACTIVITY` | Activity | `<activity` |
| `RULE-OBJ-FORM` | Section/UI | `<section` |
| `RULE-OBJ-DECISION` | Decision Table | `<decision` |
| `RULE-OBJ-MAP` | Data Transform | `<map` |
| `RULE-OBJ-DECLARE` | Declare Expression | `<declare` |
| `RULE-OBJ-WHEN` | When Rule | `<when` |
| `RULE-OBJ-VALIDATE` | Validate | `<validate` |
| `RULE-OBJ-CORR` | Correspondence | `<correspondence` |
| `RULE-OBJ-REPORT` | Report Definition | `<report` |

**Layer override precedence (highest to lowest):**
```
Implementation > Enterprise > Industry > Framework
```

---

## Output Quality Checklist

Before delivering any output:
- [ ] All 4 layers represented in extraction
- [ ] Rule type distribution matches expected (UI rules typically 30-40% of total)
- [ ] Dependency graph has no orphan clusters > 50 nodes (indicates parse error)
- [ ] Flow traces reach a terminal step (End, Error, or Assignment)
- [ ] FRD uses business language only — zero Pega-specific technical terms
- [ ] Decommission scores account for cross-layer override chains
