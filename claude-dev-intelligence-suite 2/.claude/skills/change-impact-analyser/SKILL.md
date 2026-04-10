---
name: change-impact-analyser
description: >
  Given a Jira ticket, PR description, or list of changed files, trace the full
  downstream impact: which modules need retesting, which FRD sections need updating,
  which test cases must rerun, and which teams need to be notified. Use when asked:
  'impact of this change', 'what do I need to retest', 'change impact', 'PR impact',
  'what breaks if I change X', 'regression scope', 'what modules are affected',
  'who needs to know about this change'. Turns a PR description into a scoped
  regression plan. Requires repo-graph.json.
---
# Change Impact Analyser

Map the full blast radius of a proposed or completed change.

## Step 0 — Load Graph + Identify Changed Modules
```bash
python3 scripts/project_graph.py --graph repo-graph.json --mode index
```

From the user's input (PR description / Jira ticket / file list), extract which
module(s) are changing. Map file paths to module IDs using the graph index.

## Step 1 — Compute Impact Set
```bash
# For each changed module, get its full impact set
python3 scripts/project_graph.py --graph repo-graph.json --mode impact --node <module>
```

## Step 2 — Classify Impact Type per Affected Module
For each module in the impact set:
- **API contract change?** (method signature, request/response shape) → ALL consumers affected
- **Business rule change?** (service logic) → test cases for that rule + all consumers
- **Data model change?** (entity field add/remove/rename) → migration needed, all consumers
- **Configuration change?** → runtime impact only, no recompilation needed
- **Internal refactor?** (same behaviour, different implementation) → unit tests only

## Step 3 — Regression Scope Report

```
CHANGE IMPACT ANALYSIS
Change: [Description from PR/ticket]
Changed module(s): [list]

DIRECT IMPACT ([N] modules):
  [module] — reason: directly depends on changed module
  Test cases to rerun: TC-[MOD]-[###], TC-[MOD]-[###]

TRANSITIVE IMPACT ([N] modules):
  [module] — chain: changed → A → B → this module
  Smoke test recommended: [yes/no based on distance]

FRD SECTIONS NEEDING UPDATE:
  Section 5 FR-[MOD]-[###]: [which requirement changed]
  Section 8 BR-[MOD]-[###]: [which business rule changed]

TEAMS TO NOTIFY:
  [Team/squad owning each impacted module]

REGRESSION TEST PLAN:
  Priority 1 — Run immediately: [test cases for directly impacted modules]
  Priority 2 — Run before release: [test cases for transitively impacted modules]
  Priority 3 — Regression suite: [full E2E for entry-point modules]

MIGRATION REQUIRED: [Yes/No — explain if yes]
DEPLOYMENT ORDER: [If multiple services, the safe deployment sequence]
```
