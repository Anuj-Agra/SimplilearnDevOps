# Tools — Recursive Analysis Engine

The `tools/` directory contains the recursive analysis engine that processes a PEGA KYC codebase rule by rule, with full checkpoint/resume support.

---

## Architecture

```
tools/
├── run.py                          ← CLI entry point (run this)
├── requirements.txt                ← pip install -r tools/requirements.txt
│
├── traversal/
│   ├── reference_extractor.py      ← Extracts cross-rule refs from any rule type
│   └── rule_graph.py               ← Directed graph of all rules + dependencies
│
├── checkpoint/
│   ├── checkpoint_manager.py       ← Saves/loads analysis state to disk
│   └── context_assembler.py        ← Builds bounded LLM context per rule
│
├── runner/
│   └── recursive_analyser.py       ← Main analysis loop (Phase 1 → 2 → 3)
│
└── tests/
    └── test_reference_extractor.py ← Unit tests (run with pytest)
```

---

## How it works

### The token window problem

A complex PEGA KYC codebase may contain hundreds of rules. A single flow can reference 20+ other rules (activities, when conditions, sub-flows, sections). Passing everything to the LLM at once is impossible.

### The solution: 3-phase pipeline with checkpointing

```
Phase 1 — Graph (no LLM, seconds)
  ├── Load all rule JSON files from your export directory
  ├── Parse each rule type (CaseType, Flow, Activity, Flowsection, Section, When)
  ├── Extract all cross-rule references
  ├── Build a directed dependency graph
  ├── Topological sort → ordered analysis queue
  └── Save: rule_graph.json + manifest.json + queue.json

Phase 2 — Analyse (LLM, minutes to hours depending on codebase size)
  ├── Pop next rule from queue
  ├── Assemble bounded context:
  │     - The rule's own JSON (always)
  │     - Summaries of direct dependencies (priority order, token-capped)
  │     - CaseType overview as orientation (always)
  │     - PEGA knowledge + KYC domain skills
  ├── Call Claude API with appropriate agent system prompt
  ├── Save output to analysis/{rule_id}.narrative.md
  ├── Mark rule as done in checkpoint
  └── Repeat — safe to interrupt at any point

Phase 3 — Aggregate (no LLM, seconds)
  ├── Concatenate all narratives → full_flow_narrative.md
  └── Concatenate FRD fragments → frd_fragments.md
```

### Resuming after token limit / interruption

When you run the analyser again with the same `--workspace`, it:
1. Loads the existing checkpoint (manifest + queue)
2. Resets any `in_progress` rules back to `pending` (crash recovery)
3. Skips all `done` rules
4. Continues from exactly the next `pending` rule

You never lose completed analysis.

---

## Quick start

### 1. Install dependencies

```bash
pip install -r tools/requirements.txt
```

### 2. Export your PEGA rules to JSON

In PEGA Dev Studio or App Studio:
- Go to **Records** → select rule type
- Export as JSON (one file per rule, or a zip of JSON files)
- Place all `.json` files in a directory (e.g. `./my-rules/`)

The files can be in subdirectories — the engine scans recursively.

### 3. Run Phase 1 (inspect graph before analysis)

```bash
python tools/run.py graph \
  --rules-dir ./my-rules \
  --workspace ./workspaces/kyc-v1 \
  --root-casetype KYC-Work-CDD
```

This shows you the rule graph stats and analysis queue order **without calling the LLM**.
Review the output — check for missing references and circular dependencies.

### 4. Run full analysis

```bash
python tools/run.py analyse \
  --rules-dir ./my-rules \
  --workspace ./workspaces/kyc-v1 \
  --root-casetype KYC-Work-CDD \
  --role ba \
  --max-rules 20
```

This processes up to 20 rules per session. Re-run the same command to continue.

### 5. Check progress

```bash
python tools/run.py status --workspace ./workspaces/kyc-v1
```

### 6. Aggregate when complete

```bash
python tools/run.py aggregate --workspace ./workspaces/kyc-v1
```

---

## Workspace layout

```
workspaces/{name}/
├── manifest.json            ← Master rule list + status
├── queue.json               ← Ordered pending rule IDs
├── rule_graph.json          ← Full dependency graph
├── session_log.jsonl        ← One line per completed LLM call
│
├── rules/
│   └── {rule_id}.parsed.json    ← Phase-1 parsed rule (input to LLM)
│
├── analysis/
│   ├── {rule_id}.narrative.md   ← Agent output: plain-English narrative
│   ├── {rule_id}.frd-fragment.md← Agent output: FRD FR blocks
│   └── {rule_id}.ac-fragment.md ← Agent output: acceptance criteria
│
├── context/
│   └── {rule_id}.context.json   ← Assembled LLM context (for debugging)
│
└── aggregated/
    ├── full_flow_narrative.md   ← All narratives concatenated
    └── frd_fragments.md         ← All FRD fragments concatenated
```

---

## Rule type processing

| Rule type | What is extracted | References followed |
|-----------|------------------|-------------------|
| `Rule-Obj-CaseType` | Stages, processes, entry flows, child cases | All stage flows, action flows, child CaseTypes |
| `Rule-Obj-Flow` | Steps, decisions, assignments, connectors | SubFlow, Spinoff, Flowsection, Activity, When |
| `Rule-Obj-Activity` | Steps, parameters, called activities | CallActivity (recursive), When conditions |
| `Rule-Obj-Flowsection` | Screen, buttons, pre/post activities | Rule-HTML-Section, Activity, When |
| `Rule-HTML-Section` | Fields, embedded sections, data pages | Embedded sections, When conditions |
| `Rule-Obj-When` | Boolean expression, properties used | None (terminal node) |

---

## Tuning token budget

The `--token-budget` flag controls how much context is assembled per LLM call (default: 6000 tokens).

| Budget | Use when |
|--------|---------|
| 3000 | Very large flows with many dependencies — prioritise the rule itself |
| 6000 | Default — good balance of rule content + dependency context |
| 8000 | Deep analysis needed — maximise dependency context |

The assembler always includes the rule itself fully. If budget runs short, it truncates dependency summaries (starting from lowest-priority) rather than truncating the main rule.

---

## Running tests

```bash
python -m pytest tools/tests/ -v
```
