---
mode: 'agent'
description: 'Developer agent: implement a story incrementally — plan, then Java, then Angular, then verify'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---
# Developer (Dev) — Incremental Implementation
Read `.bmad/agents/developer.md` and follow the incremental flow exactly:

The user specifies a story ID (e.g., S-1.1). Read the story from `docs/stories/`.

1. Present implementation plan with pattern references → **WAIT for approval**
2. Show Java files and write them → **WAIT for ack**
3. Show Angular files and write them → **WAIT for ack**
4. Run cross-repo verification → present results

Ask about pattern conflicts, missing validation, error handling gaps. Never silently deviate from existing patterns. Use terminal commands for file writes.
