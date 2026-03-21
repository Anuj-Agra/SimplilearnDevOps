# Recursive Analysis Workflow

How the engine processes a full PEGA KYC codebase, rule by rule, with checkpoint/resume.

---

## The problem it solves

A production PEGA KYC codebase may contain:
- 4–8 Case Types (`Rule-Obj-CaseType`)
- 20–60 Flow rules (`Rule-Obj-Flow`)
- 30–80 Activities (`Rule-Obj-Activity`)
- 20–50 Flow Actions / Flowsections (`Rule-Obj-Flowsection`)
- 40–100 Section rules (`Rule-HTML-Section`)
- 30–80 When conditions (`Rule-Obj-When`)

**Total: 150–400+ rules.** Passing them all to an LLM at once is impossible.

The recursive engine solves this by:
1. Analysing rules in dependency order (roots first, leaves later)
2. Keeping each LLM call within a token budget (6,000 input tokens by default)
3. Using already-completed analyses as compressed context for subsequent rules
4. Saving every output to disk so no work is ever lost on interruption

---

## Rule dependency graph

```
Rule-Obj-CaseType           ← Start here (root)
    │
    ├── pyStartingFlow      → Rule-Obj-Flow
    │
    └── pyStages[].pyProcesses[].pyFlowName
              │
              └── Rule-Obj-Flow
                      │
                      ├── Assignment step → Rule-Obj-Flowsection
                      │                         │
                      │                         ├── pyScreenName     → Rule-HTML-Section
                      │                         │       │
                      │                         │       └── pyEmbeddedSections → Rule-HTML-Section
                      │                         │
                      │                         ├── pyPreActivity    → Rule-Obj-Activity
                      │                         └── pyPostActivity   → Rule-Obj-Activity
                      │                                  │
                      │                                  └── CallActivity → Rule-Obj-Activity
                      │
                      ├── Utility step   → Rule-Obj-Activity
                      │                         └── [same as above]
                      │
                      ├── SubFlow step   → Rule-Obj-Flow    [recurse]
                      ├── Spinoff step   → Rule-Obj-Flow    [async — recurse]
                      │
                      ├── Decision step  → Rule-Obj-When    ← terminal
                      └── Connector[].pyWhenName
                                         → Rule-Obj-When    ← terminal
```

---

## Analysis order (BFS from CaseType root)

Rules are analysed breadth-first from the root CaseType, sorted by (depth, priority):

```
Priority 1  — Rule-Obj-CaseType        (depth 0)
Priority 2  — Rule-Obj-Flow            (depth 1 — stage entry flows)
Priority 3  — Rule-Obj-Flowsection     (depth 2 — screens for assignments)
Priority 2  — Rule-Obj-Flow            (depth 2 — sub-flows)
Priority 4  — Rule-Obj-Activity        (depth 3 — activities from flows and flowsections)
Priority 5  — Rule-HTML-Section        (depth 3 — sections from flowsections)
Priority 8  — Rule-Obj-When            (depth 3+ — terminal nodes, analysed last)
Priority 4  — Rule-Obj-Activity        (depth 4 — activities called by activities)
Priority 5  — Rule-HTML-Section        (depth 4 — embedded sections)
```

This order ensures that when a flow is analysed, its sub-flows have already been analysed and their narratives are available as context.

---

## Token budget management per LLM call

```
Total context budget: 6,000 tokens (configurable via --token-budget)

Allocated as:
  ┌─────────────────────────────────────────────────────┐
  │ Tier 1: Rule JSON (full)                 ~1,500 tok  │ ← Never truncated
  │ Tier 2: CaseType overview                 ~500 tok   │ ← Always included
  │ Tier 3: Dependency summaries             ~2,500 tok  │ ← Priority order; truncated last
  │ Tier 4: Skills + role adapter            ~1,500 tok  │ ← Capped at 25%
  └─────────────────────────────────────────────────────┘

For each dependency:
  IF dependency already analysed:
    Use its narrative.md   (most informative, compressed to ~200–400 chars)
  ELSE:
    Use JSON summary        (key fields only, ~100–200 chars)
  IF budget exceeded:
    Drop lowest-priority deps and log as truncated
```

---

## Workspace layout (one per workflow / codebase)

```
workspaces/
└── {workflow-name}/                    ← Created by run.py
    ├── manifest.json                   ← All rules + status (pending/done/failed)
    ├── queue.json                      ← Ordered list of pending rule_ids
    ├── rule_graph.json                 ← Full directed dependency graph
    ├── session_log.jsonl               ← Audit log of every LLM call
    │
    ├── rules/
    │   └── {class}__{rule_name}.parsed.json   ← Phase-1 parsed rule (LLM input)
    │
    ├── analysis/
    │   ├── {rule_id}.narrative.md      ← Agent 09 output: plain-English analysis
    │   ├── {rule_id}.frd-fragment.md   ← Agent 09 output: FRD FR block
    │   └── {rule_id}.ac-fragment.md   ← Agent 09 output: acceptance criteria
    │
    ├── context/
    │   └── {rule_id}.context.json      ← Assembled context bundle (debug)
    │
    └── aggregated/
        ├── full_flow_narrative.md      ← All narratives concatenated in depth order
        └── frd_fragments.md            ← All FRD fragments concatenated
```

---

## Session lifecycle

```
Session 1 (e.g. 50 rules processed, token limit hit at rule 51)
  ├── manifest.json: rules 1–50 = done, rule 51 = in_progress (crashed), 52+ = pending
  └── Output: 50 analysis files saved

Session 2 (re-run same command)
  ├── Load checkpoint
  ├── Reset rule 51 from in_progress → pending  (crash recovery)
  ├── Continue from rule 51
  └── Output: 50 + N more analysis files

Session N (all rules done)
  ├── Phase 3 aggregation runs automatically
  └── Output: full_flow_narrative.md + frd_fragments.md
```

---

## Complete command reference

```bash
# Step 1 — Inspect the rule graph without calling the LLM
python tools/run.py graph \
  --rules-dir ./my-pega-export \
  --workspace ./workspaces/kyc-cdd-v1 \
  --root-casetype KYC-Work-CDD

# Step 2 — Run full analysis (up to 50 rules this session)
python tools/run.py analyse \
  --rules-dir ./my-pega-export \
  --workspace ./workspaces/kyc-cdd-v1 \
  --root-casetype KYC-Work-CDD \
  --role ba \
  --max-rules 50

# Step 2b — Resume after interruption (same command, same workspace)
python tools/run.py analyse \
  --workspace ./workspaces/kyc-cdd-v1

# Check progress at any time
python tools/run.py status \
  --workspace ./workspaces/kyc-cdd-v1

# Aggregate outputs (even if analysis is partial)
python tools/run.py aggregate \
  --workspace ./workspaces/kyc-cdd-v1

# Reset and start over (keeps rule JSON files)
python tools/run.py reset \
  --workspace ./workspaces/kyc-cdd-v1
```

---

## Preparing your PEGA JSON export

The engine expects one `.json` file per rule, each with at minimum:
- `pxObjClass` — the rule type (e.g. `Rule-Obj-Flow`)
- `pyRuleName` — the rule name
- `pyClassName` — the class the rule belongs to

Files may be nested in subdirectories — the engine scans recursively.

### Exporting from PEGA Dev Studio

1. In Dev Studio, go to **Records** in the Explorer panel
2. Filter by rule type (Flow, Activity, Section, etc.)
3. Right-click → **Export** → choose JSON format
4. Repeat for each rule type you want to include
5. Place all exported `.json` files in a single directory

### Handling BIN files

If you only have `.bin` files:
1. Use Agent 06 (PEGA Expert) to decode specific files you need to understand first
2. For bulk export, ask your PEGA developer to use **Application → Export** in Dev Studio and select JSON format
3. The engine cannot parse binary BIN files directly — JSON export is required

---

## Multi-CaseType analysis

If your codebase has multiple Case Types (CDD, EDD, SAR, PeriodicReview), create a separate workspace per CaseType:

```bash
# Workspace 1: CDD
python tools/run.py analyse \
  --rules-dir ./export \
  --workspace ./workspaces/kyc-cdd \
  --root-casetype KYC-Work-CDD

# Workspace 2: EDD
python tools/run.py analyse \
  --rules-dir ./export \
  --workspace ./workspaces/kyc-edd \
  --root-casetype KYC-Work-EDD
```

Shared rules (e.g. `KYC_SanctionsScreening` used by both CDD and EDD flows) will be analysed independently in each workspace, with the appropriate parent CaseType as orientation context.
