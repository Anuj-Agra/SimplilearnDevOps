---
mode: 'agent'
description: 'Compare existing OpenSpec specs against actual code to find gaps, drift, and undocumented capabilities'
tools: ['search/codebase']
---

# Spec Gap Detection

## Task
Compare specs in openspec/specs/ against actual code in both repos.

## Steps
1. Inventory existing specs: list every Requirement in every spec file (including NFR Requirements)
2. Inventory actual code: list all endpoints, services, models, forms in both repos
3. Inventory NFR controls in code: auth annotations, caching, pagination, guards, validators, rate limiters
4. Cross-reference:
   - Code without specs = undocumented
   - Specs without code = stale
   - Partial matches = drift
   - **NFR-expected patterns without controls = risk gap** (e.g., write endpoint without rate limiting, admin endpoint without role check, large list without pagination, sensitive Angular route without guard)
5. Report with coverage %, categorized findings, and recommended actions

## Severity
- 🔴 Undocumented code (exists in code, missing from specs)
- 🔴 **Missing security control** (risk exposure)
- 🟠 Drift (specs partially match but details differ)
- 🟠 **Missing performance control** (scalability concern)
- 🟡 Stale specs (in specs, no matching code)
