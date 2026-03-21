# Tools — Recursive Analysis Engine

The `tools/` directory contains the recursive analysis engine that processes a PEGA KYC
codebase rule by rule, with full checkpoint/resume support.

---

## Two operating modes

### Mode 1 — Hierarchy mode *(for real PEGA exports: COB / CRDFWApp / MSFWApp / PegaRules)*

Your PEGA export is organised as 4 folders, each containing:
- **Multiple `.json` manifest files** — rule inventory metadata (which one to use is set in config)
- **Multiple `.bin` files** — native PEGA binary rule content

```
pega-export/
  COB/          ← most specific (client overrides)        [tier 0]
  CRDFWApp/     ← client framework application            [tier 1]
  MSFWApp/      ← shared PEGA framework                   [tier 2]
  PegaRules/    ← base PEGA rules                         [tier 3]
```

Edit `config/analysis_config.yaml`, then run:

```bash
# Validate your config before any LLM calls
python tools/run.py validate-config --config config/analysis_config.yaml

# Phase 1: build graph (zero cost — no LLM)
python tools/run.py graph --config config/analysis_config.yaml

# Phase 2+3: analyse and aggregate (uses Anthropic API)
python tools/run.py analyse --config config/analysis_config.yaml

# Resume after interruption (same command — no flags needed)
python tools/run.py analyse --config config/analysis_config.yaml
```

### Mode 2 — Legacy mode *(for flat directories of exported JSON rule files)*

```bash
python tools/run.py analyse \
  --rules-dir ./my-pega-export \
  --workspace ./workspaces/kyc-cdd-v1 \
  --root-casetype KYC-Work-CDD \
  --role ba
```

---

## Architecture

```
tools/
├── run.py                              ← CLI entry point (5 commands)
├── requirements.txt                    ← pip install -r tools/requirements.txt
│
├── config/
│   └── config_loader.py               ← Loads analysis_config.yaml; resolves manifest versions
│
├── parser/
│   ├── manifest_loader.py             ← Reads manifest JSON → list of rule records + BIN matches
│   ├── bin_reader.py                  ← Extracts strings/references from PEGA .bin files
│   └── hierarchy_loader.py            ← Merges all 4 tiers with most-specific-wins inheritance
│
├── traversal/
│   ├── reference_extractor.py         ← Extracts cross-rule references from any rule type
│   └── rule_graph.py                  ← Directed dependency graph; BFS queue; cycle detection
│                                         NEW: from_hierarchy_config() classmethod
│
├── checkpoint/
│   ├── checkpoint_manager.py          ← Persists manifest + queue + outputs to disk
│   └── context_assembler.py           ← Builds bounded LLM context (token-budget aware)
│
├── runner/
│   └── recursive_analyser.py          ← Main Phase 1/2/3 loop
│                                         NEW: accepts analysis_config= for hierarchy mode
│
└── tests/
    ├── test_reference_extractor.py    ← 20 tests for all 6 rule types
    └── test_hierarchy_loading.py      ← 23 tests: config, manifest, BIN, hierarchy, integration
```

---

## config/analysis_config.yaml — key settings

| Setting | What it does |
|---------|-------------|
| `hierarchy[n].folder` | Path to this app's folder (COB / CRDFWApp / MSFWApp / PegaRules) |
| `hierarchy[n].manifest_version` | `"latest"` = auto-pick highest version; `"01-02-03"` = exact match |
| `hierarchy[n].include_in_analysis` | `true` = queue for LLM; `false` = load as context only |
| `analysis.root_casetype` | `pyRuleName` of the root Case Type (e.g. `KYC-Work-CDD`) |
| `analysis.role` | `ba` / `po` / `dev` / `qa` — tunes output language depth |
| `analysis.max_rules_per_session` | Rules to process per run (re-run to continue) |
| `analysis.token_budget_per_rule` | Input tokens for LLM context assembly (default 6000) |
| `rule_type_filter` | Include/exclude rule types from the graph |
| `bin_extraction.enabled` | Whether to extract strings from `.bin` files |

---

## How manifest version resolution works

For each app folder the engine scans for `.json` files that look like PEGA manifests
(contain `pxResults`, `rules`, `pyRuleSetName`, or a `pyRuleName` array).

With `manifest_version: "latest"`:
1. Reads `pyRuleSetVersion` field from each manifest's content
2. Falls back to version string in filename (e.g. `manifest-01-02-03.json`)
3. Picks the file with the highest version string

With `manifest_version: "01-02-03"`:
1. Exact match on `pyRuleSetVersion` field (dashes or dots both work)
2. Falls back to filename match if content version not found

---

## How BIN extraction works

PEGA `.bin` files are Java-serialised objects. The engine uses two strategies:
1. **Regex extraction** — scans raw bytes for printable ASCII segments ≥ 4 chars
2. **Java short-string format** — reads 2-byte length-prefixed UTF-8 strings

From the extracted strings it identifies:
- Rule type (`pxObjClass`) — looks for known PEGA rule type strings
- Cross-rule references — `pyActivityName`, `pySubFlowName`, `pyFlowActionName`, etc.
- Partial flow step reconstruction — detects Assignment/Utility/SubFlow/Decision patterns

This gives the reference extractor enough information to build the dependency graph
even without full JSON rule content.

---

## Most-specific-wins inheritance

When the same rule (`pyClassName::pyRuleName`) exists in multiple tiers:

```
COB (tier 0) wins over CRDFWApp (tier 1) wins over MSFWApp (tier 2) wins over PegaRules (tier 3)
```

The winning rule is queued for LLM analysis (if its app has `include_in_analysis: true`).
The overridden rules are discarded — they are not loaded as phantom context nodes.

---

## CLI commands

| Command | Purpose |
|---------|---------|
| `validate-config --config FILE` | Check all paths resolve; show manifest counts and selected files |
| `graph --config FILE` | Build graph, print stats and analysis queue — no LLM, no cost |
| `analyse --config FILE` | Run full analysis; resume automatically if re-run |
| `status --workspace DIR` | Show current progress |
| `aggregate --workspace DIR` | Concatenate outputs into `full_flow_narrative.md` + `frd_fragments.md` |
| `reset --workspace DIR` | Wipe analysis outputs, keep BIN/rule files |

---

## Running tests

```bash
pip install -r tools/requirements.txt
python tools/tests/test_reference_extractor.py    # 20 tests
python tools/tests/test_hierarchy_loading.py       # 23 tests
```
