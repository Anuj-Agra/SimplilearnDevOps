---
mode: 'agent'
description: 'Apply approved proposal: implement stories (Developer) then review (QA). Run after /bmad-propose has been approved.'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---
# BMAD Apply (Implementation Phase)

The planning phase is complete and approved. Now implement the stories.

## Input
- If the user says `/bmad-apply` with no arguments → implement ALL stories in dependency order
- If the user says `/bmad-apply S-1.2` → implement that specific story only
- If the user says `/bmad-apply S-1.1 S-1.2 S-2.1` → implement those stories in order

## Pre-Flight Check
1. Verify `docs/architecture.md` exists — refuse to proceed without it
2. Verify `docs/stories/` has story files — refuse to proceed without them
3. Read `docs/architecture.md` for API contracts
4. List all stories and their dependency order

If no architecture or stories exist, tell the user:
```
No approved proposal found. Run /bmad-propose first to create the planning artifacts.
```

## Implementation Pipeline

For each story (in dependency order):

### Step 1: Developer (Dev)
Read `.bmad/agents/developer.md` and adopt that persona.

1. Read the story from `docs/stories/<story-id>.md`
2. Read `docs/architecture.md` for contracts and implementation order
3. Read "Existing Code to Reference" files from the story
4. Scan 1-2 similar existing files for conventions
5. **Implement Java tasks first** (API must exist before consumer):
   - Write complete files using terminal commands
   - Check off each task: `sed -i 's/- \[ \] J1:/- [x] J1:/' docs/stories/<id>.md`
6. **Implement Angular tasks second**:
   - Ensure TypeScript types match Java DTOs exactly
   - Write complete files using terminal commands
   - Check off each task
7. **Run verification tasks**:
   - Verify type alignment (Java DTO fields ↔ TypeScript interface fields)
   - Verify endpoint paths match
   - Check off verification tasks

Show progress between each task:
```
[Dev] Implementing S-1.1...
  [x] J1: Created java-service/src/.../KycStatusDto.java
  [x] J2: Created java-service/src/.../KycController.java
  [x] A1: Created angular-app/src/.../kyc-status.model.ts
  [x] A2: Created angular-app/src/.../kyc.service.ts
  [x] V1: Type alignment verified ✅
```

### Step 2: QA (Quinn)
Read `.bmad/agents/qa.md` and adopt that persona.

1. Read the story
2. Read ALL files just created/modified
3. Run `.bmad/checklists/cross-repo-quality-gate.md`
4. Produce a review report
5. Verdict: ✅ APPROVED / ❌ NEEDS CHANGES / ⚠️ APPROVED WITH NOTES

If NEEDS CHANGES:
- List specific issues with file paths
- Switch back to Developer persona
- Fix each issue
- Re-run QA

### After all stories:

```
╔══════════════════════════════════════════════════════════╗
║                  BMAD APPLY COMPLETE                     ║
╚══════════════════════════════════════════════════════════╝

✅ Stories Implemented: <N>/<total>

### Files Created/Modified
☕ Java Service:
  [CREATE] java-service/src/.../KycStatusDto.java
  [CREATE] java-service/src/.../KycController.java
  [CREATE] java-service/src/.../KycService.java

🅰️ Angular App:
  [CREATE] angular-app/src/.../kyc-status.model.ts
  [CREATE] angular-app/src/.../kyc.service.ts

### QA Results
  S-1.1: ✅ APPROVED
  S-1.2: ✅ APPROVED
  S-2.1: ⚠️ APPROVED WITH NOTES — minor naming inconsistency

### Cross-Repo Alignment: ✅ Verified
  All DTO↔interface fields match
  All endpoint paths match

═══════════════════════════════════════════════════════════
👉 Run tests in both repos
👉 Review generated code
👉 Commit when satisfied
═══════════════════════════════════════════════════════════
```

## Rules
- Never implement without existing architecture and story artifacts
- Java first, Angular second — always
- Every story gets a QA review — no exceptions
- Use terminal commands for all file writes in both repos
- If QA finds issues, fix them before moving to the next story
