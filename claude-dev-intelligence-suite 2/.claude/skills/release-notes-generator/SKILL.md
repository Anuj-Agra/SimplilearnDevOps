---
name: release-notes-generator
description: >
  Generate user-facing release notes in plain English from a git log between two tags,
  a Jira release, or a list of changes. Groups changes by user role rather than by
  commit. Use when asked: 'release notes', 'what changed in this release', 'write
  changelog', 'sprint summary', 'release announcement', 'what is new in version X',
  'user-facing changes'. Produces release notes readable by non-technical stakeholders.
---
# Release Notes Generator

Produce plain-English release notes grouped by user role, not by commit.

## Step 0 — Gather Change Data
Options (ask user which they have):
1. **Git log**: `git log v1.0.0..v1.1.0 --oneline --no-merges`
2. **Jira release**: list of ticket IDs in a version
3. **Change description**: free-text list of changes

## Step 1 — Enrich with FRD Context
If FRD exists: map each change to its FRD section (FR-XXX, BR-XXX) to understand
the business impact in user terms.

If graph exists: use impact analysis to identify which user-facing modules changed.

## Step 2 — Categorise Changes
Map technical changes to user-impact categories:
- **New feature** — something users couldn't do before
- **Improvement** — something that works better or faster
- **Bug fix** — something that was broken, now fixed
- **Change** — behaviour that users need to know has changed
- **Removed** — something no longer available

## Step 3 — Group by User Role
From the FRD's role definitions, assign each change to the roles it affects.

## Step 4 — Output

```
RELEASE NOTES — [System Name] v[X.Y.Z]
Released: [date]

OVERVIEW
[2-3 sentence summary of the most important changes in plain English]

WHAT'S NEW FOR [ROLE A — e.g. Customer Service Agents]
  ✨ [Feature]: [Plain English description of what they can now do]
  ✨ [Feature]: [...]
  🔧 [Improvement]: [What works better]
  🐛 [Fix]: [What was broken that now works]

WHAT'S NEW FOR [ROLE B — e.g. Managers]
  ...

CHANGES THAT AFFECT ALL USERS
  ⚠️  [Change]: [Description — include "previously X, now Y" if behaviour changed]

KNOWN ISSUES
  [Any known issues in this release with workarounds]

COMING NEXT
  [Preview of next release — optional]
```

## Writing Rules
- No commit hashes, branch names, or technical identifiers
- No class names, API paths, or database terms
- Every item starts with what the user can now DO or what changed for THEM
- "Bug fix" → describe what the user experienced before and what they see now
