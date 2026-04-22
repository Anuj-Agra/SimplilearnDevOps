---
mode: 'agent'
description: 'Propose a new feature that spans both repos — creates linked OpenSpec proposals in Java and Angular simultaneously'
tools: ['search/codebase', 'editFiles']
---

# Cross-Repo Propose

## Task
The user describes a feature. Create linked OpenSpec proposals in both repos.

## Steps
1. Extract a change-id (kebab-case, verb-led)
2. Scan both codebases for conventions
3. Create Java proposal: proposal.md, specs/<domain>/spec.md, design.md, tasks.md
4. Create Angular proposal: same artifacts, linked to Java proposal
5. Update contract spec with proposed entries
6. Report and suggest next steps
