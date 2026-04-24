---
mode: 'agent'
description: 'Start from existing architecture: skip to Scrum Master to create stories, then stop for approval'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---
# BMAD From Existing Architecture

The user already has architecture or technical design. Skip to Scrum Master.

## Input
The user may provide:
- A reference to `docs/architecture.md` already in the workspace
- Pasted technical design with endpoints, schemas, contracts
- API specs (OpenAPI, Swagger, or informal)
- Data model definitions

## Pipeline

### Phase 1: Capture Architecture
If `docs/architecture.md` doesn't exist, create it from the user's input. Restructure informal designs into the standard architecture format (see `.bmad/agents/architect.md`). Scan both repos to fill in existing code references.

### Phase 2: Scrum Master (Sam)
Read `.bmad/agents/scrum-master.md`. Create stories from the architecture. Save to `docs/stories/S-*.md`.

### Phase 3: Proposal Summary
Stop for approval.

## Rules
- Trust the architecture — don't redesign, just create stories from it
- DO scan repos to add "Existing Code to Reference" to each story
- Use terminal commands for file writes
