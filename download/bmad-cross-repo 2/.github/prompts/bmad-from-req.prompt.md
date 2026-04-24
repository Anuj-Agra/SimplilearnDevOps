---
mode: 'agent'
description: 'Start from existing requirements: capture reqs, then Architect (incremental) → Stories → approval'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---
# BMAD From Existing Requirements

Skip Analyst and PM. Start with Architect.

## Phase 1: Capture Requirements
Absorb the user's requirements (pasted text, Jira ticket, doc reference). Save a lightweight PRD to `docs/prd.md`.

## Phase 2: Architect (Archie) — INCREMENTAL
Read `.bmad/agents/architect.md`. **Follow the incremental flow exactly:**
1. Investigate within the user's stated boundary → present → **STOP, wait for ack**
2. Propose approach → **STOP, wait for ack**
3. Cross-repo impact → **STOP, wait for ack**
4. Full architecture → `docs/architecture.md`

Ask proactive questions when you detect entitlement, security, pattern, or validation implications.

## Phase 3: Scrum Master (Sam)
Read `.bmad/agents/scrum-master.md`. Create stories → `docs/stories/S-*.md`.

## Phase 4: Proposal Summary
Stop for approval.

Use terminal commands for all file writes. Do NOT question the requirements — they're already decided. DO flag technical impossibilities.
