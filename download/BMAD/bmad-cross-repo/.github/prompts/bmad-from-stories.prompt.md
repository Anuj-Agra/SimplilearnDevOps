---
mode: 'agent'
description: 'Start from existing stories or tasks: skip to Developer to implement immediately'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---
# BMAD From Existing Stories

The user already has stories, tasks, or a detailed implementation plan. Skip to Developer.

## Input
The user may provide:
- Stories already saved in `docs/stories/`
- Jira tickets with task breakdowns
- A pasted task list with file paths
- An informal "here's what needs to be done" list

## Pipeline

### Phase 1: Capture Stories
If stories aren't already in `docs/stories/`, create them from the user's input. Each story needs at minimum:
- A description
- Implementation tasks with file paths (scan repos to determine paths)
- Which repo each task targets

If the user provides a vague list, scan both repos and enrich each task with:
- Full file paths within the monorepo
- Existing code references for conventions
- Verification tasks for cross-repo items

### Phase 2: Confirm Before Implementing
Show the enriched story list:
```
Ready to implement:
  S-1.1: <title> — J:2 tasks, A:1 task, V:2 checks
  S-1.2: <title> — A:3 tasks, V:1 check
Proceed? (or run /bmad-apply to start)
```

### Phase 3: Developer (Dev) + QA (Quinn)
If user confirms, run the same implementation pipeline as `/bmad-apply`.

## Rules
- Enrich vague tasks with real file paths from scanning the repos
- Maintain Java-first, Angular-second ordering
- Every cross-repo task gets verification
- Use terminal commands for file writes
