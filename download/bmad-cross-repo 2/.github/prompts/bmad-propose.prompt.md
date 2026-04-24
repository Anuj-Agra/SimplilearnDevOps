---
mode: 'agent'
description: 'Propose a change: Analyst → PM → Architect (incremental) → Scrum Master. Stops for approval at each major boundary.'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---
# BMAD Propose (Planning Phase)

Run planning agents. **The Architect phase uses incremental approval** — it will stop multiple times for user confirmation.

## Phase 1: Analyst (Alex)
Read `.bmad/agents/analyst.md`. Scan both repos. Produce brief → `docs/briefs/<id>.md`.
--- Phase 1 complete ---

## Phase 2: PM (Penny)
Read `.bmad/agents/pm.md`. Create PRD → `docs/prd.md`.
--- Phase 2 complete ---

## Phase 3: Architect (Archie) — INCREMENTAL
Read `.bmad/agents/architect.md`. **Follow the incremental flow exactly:**
1. Investigate within the user's stated boundary → present findings → **STOP, wait for ack**
2. Propose approach → **STOP, wait for ack**
3. Cross-repo impact → **STOP, wait for ack**
4. Full architecture doc → `docs/architecture.md`

If the Architect detects implications (entitlements, security, pattern concerns), ASK the user before proceeding.

If the user referenced a pattern ("like the accounts module"), the Architect must scan that module first and present the pattern before proposing.

--- Phase 3 complete (after all acks) ---

## Phase 4: Scrum Master (Sam)
Read `.bmad/agents/scrum-master.md`. Create stories → `docs/stories/S-*.md`.
--- Phase 4 complete ---

## Final: Proposal Summary
Present summary and stop:
```
📋 Proposal ready. <N> stories, <M> files across both repos.
Review docs/. When approved, run /bmad-apply.
```

Use terminal commands for all file writes.
