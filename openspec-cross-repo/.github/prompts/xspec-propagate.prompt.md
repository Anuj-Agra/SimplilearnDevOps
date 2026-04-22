---
mode: 'agent'
description: 'Read an OpenSpec change from one repo and create a linked proposal in the other repo'
tools: ['search/codebase', 'editFiles']
---

# Propagate Change Across Repos

## Task
Given a change-id, read the OpenSpec change from the source repo and create a linked proposal in the target repo.

## Steps
1. Find the change in either repo's openspec/changes/<change-id>/
2. Read ALL artifacts: proposal.md, design.md, tasks.md, specs/
3. Determine target repo (Java→Angular or Angular→Java)
4. Scan target repo's existing code for conventions
5. Create linked proposal in target repo with same change-id:
   - proposal.md with "Linked From" reference and target-perspective intent
   - specs/<domain>/spec.md with delta specs (ADDED/MODIFIED/REMOVED)
   - design.md with target-stack technical approach
   - tasks.md with implementation checklist
6. Update contract spec
7. Report what was created and suggest next step
