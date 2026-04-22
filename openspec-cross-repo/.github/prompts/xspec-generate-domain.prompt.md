---
mode: 'agent'
description: 'Generate OpenSpec specs for a single domain/module across both repos'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---

# Generate Specs for a Single Domain

## Task
The user names a domain. Scan both repos for related code and generate focused specs.

## Steps
1. Search for the domain across both codebases (packages, folders, class names)
2. Deep-read ALL domain-related files in both repos
3. Extract: endpoints, DTOs, services, forms, business rules, validation, error handling
4. Extract NFR indicators: security patterns (authn/authz, input validation, rate limiting, audit) + performance patterns (caching, pagination, async, timeouts, debouncing)
5. Generate openspec/specs/<domain>/spec.md in both repos with functional Requirements AND an `## NFR Requirements` section (with evidence citations and REVIEW markers for gaps)
6. Update contract spec with domain endpoints + cross-cutting NFRs
7. Report code discovered, specs generated, NFR coverage, ambiguities
