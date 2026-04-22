---
mode: 'agent'
description: 'Scan both repos for OpenSpec changes that affect the API surface but have no linked proposal in the other repo'
tools: ['search/codebase']
---

# Detect Unlinked Cross-Repo Changes

## Task
Scan both repos' openspec/changes/ directories and identify changes that modify the API boundary but don't have a corresponding linked proposal in the other repo.

## Steps
1. Read active changes in both repos (exclude archive/)
2. For each change, read proposal.md and delta specs to determine if it affects the API surface
3. Check if the other repo has a change with the same change-id
4. Report as a table: Change ID | API Surface? | Linked? | Action Needed
5. Suggest /xspec-propagate for each unlinked change
