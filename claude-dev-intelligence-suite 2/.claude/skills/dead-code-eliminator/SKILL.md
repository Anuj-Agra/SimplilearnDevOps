---
name: dead-code-eliminator
description: >
  Safely sequence the removal of dead modules, unused classes, and unreachable code.
  Goes beyond detection to produce a validated decommission runbook. Use when asked:
  'remove dead code', 'clean up unused modules', 'decommission', 'delete unused',
  'safe to remove', 'unused code', 'dead module cleanup'. Checks reflection-based
  references, config-driven loading, and Spring bean wiring before flagging as safe.
---
# Dead Code Eliminator

Produce a validated, sequenced decommission runbook — not just a list of dead modules.

## Step 1 — Identify Dead Candidates (from graph)
```bash
python3 scripts/project_graph.py --graph repo-graph.json --mode dead
```

## Step 2 — Validate Each Candidate (never delete without this)
For each dead module, run these safety checks:

```bash
# Check 1: Reflection-based loading (class.forName, @ConditionalOnProperty)
grep -rn "Class.forName\|forName(\|@ConditionalOnProperty\|@ConditionalOnBean" \
  <codebase> --include="*.java" | grep -i "<module_name>"

# Check 2: Spring config/XML wiring
grep -rn "<bean\|@Import\|@ComponentScan\|scanBasePackages" \
  <codebase> --include="*.java" --include="*.xml" --include="*.yml"

# Check 3: External consumers (other repos, API gateways)
# Flag: manual check required — cannot be automated

# Check 4: Feature flags / A-B testing
grep -rn "featureFlag\|isEnabled\|@ConditionalOn" \
  <codebase> --include="*.java" | grep -i "<module_name>"

# Check 5: Scheduled batch jobs that may load this dynamically
grep -rn "@Scheduled\|JobBuilder\|StepBuilder" <codebase> --include="*.java"
```

## Step 3 — Decommission Runbook (per module)

```
DECOMMISSION: [module-name]
Safety checks: [PASSED / FAILED — list results]
Estimated LOC removed: [N]
Estimated build time saving: [%]

Step 1: Add @Deprecated annotation + log warning (1 sprint)
Step 2: Monitor — any calls appear in logs? If yes → stop, investigate
Step 3: Remove from build file dependencies
Step 4: Delete source directory
Step 5: Remove from graph (re-run repo-graph-architect)
Step 6: Update FRD to mark feature as retired

Rollback: git revert [commit] — no downstream impact as fan-in = 0
```

## Output
Prioritised decommission backlog ordered by:
1. LOC saved (biggest wins first)
2. Safety confidence (all checks passed = high confidence)
3. Dependency on other dead modules (remove leaves first)
