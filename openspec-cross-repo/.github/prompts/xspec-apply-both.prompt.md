---
mode: 'agent'
description: 'Apply a linked OpenSpec change across both repos — implements tasks in Java and Angular'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---

# Apply Linked Change in Both Repos

## Task
Given a change-id that exists in both repos, implement the tasks in both repos sequentially.

## Steps
1. Verify change exists in both repos' openspec/changes/
2. Read both proposals, designs, and task lists
3. Implement Java tasks first: scan conventions, generate complete files, check off tasks
4. Implement Angular tasks second: ensure types match Java DTOs, generate files, check off tasks
5. Verify type alignment: every Java DTO field has matching TS interface field, paths match, request/response shapes match
6. Report all files created/modified and alignment status
