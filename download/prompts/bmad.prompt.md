---
mode: 'agent'
description: 'Full BMAD pipeline with incremental Architect approval and propose → approve → apply gate'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---
# BMAD Full Pipeline

## Phase A: Propose

1. **Analyst (Alex)** → scan repos, brief → `docs/briefs/<id>.md`
2. **PM (Penny)** → PRD → `docs/prd.md`
3. **Architect (Archie)** → INCREMENTAL:
   - Investigate → present → **WAIT for ack**
   - Propose approach → **WAIT for ack**
   - Cross-repo impact → **WAIT for ack**
   - Architecture doc → `docs/architecture.md`
   - ASK proactive questions at each stage (entitlements, security, patterns)
4. **Scrum Master (Sam)** → stories → `docs/stories/S-*.md`

Present proposal summary. **STOP for approval.**

## Phase B: Apply (only after "approved")

5. **Developer (Dev)** → implement each story (Java first, Angular second)
6. **QA (Quinn)** → review each story, cross-repo quality gate

Read each agent persona from `.bmad/agents/` before acting. Use terminal commands for file writes.
