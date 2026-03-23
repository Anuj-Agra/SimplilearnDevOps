# Workflow: Dead Code & Tech Debt Scan

Use this workflow to find unused code, orphaned modules, stale feature flags, and accumulated tech debt.

## Step-by-Step Protocol

### Step 1 — Find Unused Exports
```
TASK: Identify exported symbols that nothing imports

For each module:
1. Search for all exported functions, classes, types, constants
2. For each export, search for import statements referencing it
3. If zero importers found → candidate for dead code

Focus on:
- Exported functions with zero callers
- Exported types/interfaces with zero references
- Exported constants that are never read
- Re-exports that chain to unused code
```

### Step 2 — Find Orphaned Files
```
TASK: Identify files that nothing imports or references

Search for:
- Files not referenced in any import statement
- Files not referenced in any route definition
- Files not referenced in any config or build file
- Files not included in any test

Exclude from false positives:
- Entry points (main, index, app)
- Config files
- Migration files
- Script files meant to run standalone
- Test files (they import others, rarely imported themselves)
```

### Step 3 — Find Stale Feature Flags
```
TASK: Identify feature flags that are always on/off or no longer toggled

Search for:
- Feature flag definitions (featureFlags, flags, toggles, experiments)
- Feature flag checks (if flag.enabled, isFeatureOn, hasFeature)
- Feature flag configuration (env vars, remote config)

For each flag:
- Is it checked in code? (if defined but never checked → stale)
- Is it always set to the same value? (always true → remove guard, always false → remove code)
- When was it last modified? (old flags are candidates for cleanup)
```

### Step 4 — Find TODO / FIXME / HACK Debt
```
TASK: Catalog all tech debt markers in the codebase

Search for:
- TODO comments (with and without assignees)
- FIXME comments
- HACK / WORKAROUND comments
- @deprecated markers
- "temporary" / "temp" / "quick fix" in comments

For each:
- How old is it? (git blame)
- Is it in critical code? (payment, auth, data integrity)
- Is there a related issue/ticket?

Categorize:
- 🔴 Critical debt (in important code paths, old, no ticket)
- 🟡 Normal debt (has a ticket or is in non-critical code)
- 🟢 Informational (clarifications, not actual debt)
```

### Step 5 — Find Duplicate Code
```
TASK: Identify code that's been copy-pasted across files

Search for:
- Functions with identical or near-identical names across files
- Identical code blocks (>10 lines) in different locations
- Similar error handling patterns that could be extracted
- Repeated validation logic
- Duplicate utility functions

For each duplicate:
- How many copies exist?
- Are they identical or slightly different?
- Could they be extracted into a shared utility?
```

### Step 6 — Find Abandoned Dependencies
```
TASK: Identify installed packages that are no longer used

Search for:
- Packages in package.json / requirements.txt / go.mod / Cargo.toml
- For each package, search for imports referencing it
- If zero imports → candidate for removal

Also check:
- Packages only used in removed/dead code
- Dev dependencies used by removed test frameworks
- Peer dependencies that are no longer needed
```

### Step 7 — Synthesize Report
```
OUTPUT: Tech debt and dead code report

## 🧹 Dead Code & Tech Debt Report

### Summary
| Category | Count | Estimated Cleanup Effort |
|----------|-------|------------------------|
| Unused exports | N | hours |
| Orphaned files | N | hours |
| Stale feature flags | N | hours |
| TODOs/FIXMEs | N | varies |
| Duplicate code | N | days |
| Unused dependencies | N | hours |

### 🔴 High Priority Cleanup
{items that are in critical code paths or cause confusion}

### 🟡 Normal Priority
{items worth cleaning up in normal development}

### 🟢 Low Priority / Informational
{minor items, can be cleaned up opportunistically}

### Recommended Cleanup Order
1. {safest, highest-impact cleanup first}
2. {next priority}
3. {etc.}

### Estimated Total Effort
{X} developer-days to clean all high + normal priority items
```

## Example Prompt

```
Follow the workflow in @workspace workflows/dead-code-scan.md to scan:

Find all dead code, unused dependencies, and stale feature flags 
in the backend service. Focus on the /services and /routes directories.
```
