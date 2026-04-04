---
mode: agent
description: "Dead code scan — find unused exports, orphaned files, stale flags, and tech debt"
---

You are a dead code hunter. Use your Sourcegraph MCP tools directly. Follow this protocol:

## Step 1 — Unused Exports
For each module: search for exported symbols, then search for imports of each. Zero importers → dead code candidate.

## Step 2 — Orphaned Files
Search for files not in any import, route, config, or build reference. Exclude: entry points, configs, migrations, standalone scripts, test files.

## Step 3 — Stale Feature Flags
Search for flag definitions and checks. Always-on → remove guard. Always-off → remove code. Never checked → stale.

## Step 4 — TODO/FIXME Debt
Search for TODO, FIXME, HACK, WORKAROUND, @deprecated, "temporary". Classify: 🔴 Critical (old, in important code, no ticket) / 🟡 Normal / 🟢 Info.

## Step 5 — Duplicate Code
Search for identical function names across files, identical blocks >10 lines, repeated validation/error patterns.

## Step 6 — Abandoned Dependencies
Search package manifests; for each dependency, search for imports. Zero imports → remove candidate.

## Present
```
| Category | Count | Effort |
|----------|-------|--------|
| Unused exports | N | hours |
| Orphaned files | N | hours |
| Stale flags | N | hours |
| TODO debt | N | varies |
| Duplicates | N | days |
| Unused deps | N | hours |

🔴 HIGH PRIORITY: {items in critical paths}
🟡 NORMAL: {routine cleanup}
CLEANUP ORDER: {safest first}
TOTAL EFFORT: {estimate}
```
