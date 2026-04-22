---
mode: 'agent'
description: 'Update the shared contract spec from both repos actual code and OpenSpec specs'
tools: ['search/codebase', 'editFiles']
---

# Sync Contract Spec

## Task
Scan both codebases and update cross-repo/openspec/specs/contract/spec.md.

## Steps
1. Scan Java: find all controllers, endpoints, DTOs, their fields and types
2. Scan Angular: find all services, HTTP methods, models, their fields and types
3. Detect drift: endpoints in Java not consumed by Angular, type mismatches, missing fields
4. Rewrite contract spec with current truth
5. Report drift findings with action items
