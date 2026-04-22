---
mode: 'agent'
description: 'Reverse-engineer OpenSpec technical specs from existing Java + Angular code'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---

# Technical Spec Generator

## Task
Scan both codebases and generate openspec/specs/<domain>/spec.md files.

## Steps
1. Scan Java: controllers, endpoints, DTOs, entities, enums, services, security, scheduled tasks, error handlers
2. Scan Angular: routes, services, models, components, forms, state management, guards, interceptors
3. Group into domains matching code's package/folder structure
4. Generate specs in OpenSpec format (Requirements with Given/When/Then Scenarios)
   - Java specs: API contracts, validation, business logic, data integrity
   - Angular specs: user interactions, service integration, data display
5. Update contract spec with all discovered endpoints
6. Report: domains discovered, files generated, requirement/scenario counts, ambiguities

## Rules
- Never invent requirements — only document what the code does
- Flag ambiguous code with <!-- REVIEW: ... --> comments
- One spec file per domain, not per endpoint
- **Every spec must include an `## NFR Requirements` section** — see the NFR risk matrix in copilot-instructions.md. Scan for security patterns (authn/authz, input validation, rate limiting, audit) and performance patterns (caching, pagination, async, timeouts, N+1 protection). Cite code evidence. Flag missing controls with REVIEW markers.
