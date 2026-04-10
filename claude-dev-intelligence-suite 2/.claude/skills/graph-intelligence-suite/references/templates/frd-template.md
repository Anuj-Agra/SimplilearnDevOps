# FRD Document Template

## Document Structure

Use this outline exactly. Section numbers must match.

---

```
FUNCTIONAL REQUIREMENTS DOCUMENT
[System / Repo Name]

Version:      1.0
Date:         [ISO date]
Prepared by:  Graph Intelligence Suite (AI-assisted)
Status:       Draft — requires human review
Scope:        [Module or repo scope]
Graph source: repo-graph.json generated [date]
```

---

## 1. Document Purpose

State: what this document is, who it is for, and what decisions it supports.

Example:
> This FRD describes the functional capabilities and integration contracts of the
> [system name] mono-repo. It is intended for software engineers, architects, and
> technical leads involved in onboarding, migration planning, or feature development.
> It was generated semi-automatically from a structural dependency graph and targeted
> source-code analysis.

---

## 2. Scope & Boundaries

| In Scope | Out of Scope |
|---|---|
| All modules in [scope] | External third-party APIs (documented by integration table only) |
| Internal integration contracts | Infrastructure / deployment configuration |
| Data models managed by in-scope modules | Non-functional requirements (covered in Section 8) |

---

## 3. Module Inventory

Taken directly from graph projection. Columns:

| Module ID | Display Name | Type | Parent | LOC | Files | Fan-in | Fan-out | Instability | Notes |
|---|---|---|---|---|---|---|---|---|---|
| service-a:core | Core | submodule | service-a | 2,400 | 34 | 3 | 5 | 0.63 | |

Instability guide: 0.0–0.3 = stable provider | 0.3–0.7 = balanced | 0.7–1.0 = volatile consumer

---

## 4. Architecture Overview

Include a Mermaid diagram of the top-level module relationships.
Max 20 nodes. Group into `subgraph` blocks by top-level module.

Instructions for rendering:
> Open repo-graph.html for the full interactive version.

---

## 5. Functional Requirements by Module

One subsection per module. Use this repeating block:

---

### 5.X [Module Display Name] (`[module-id]`)

**Purpose**: [1–2 sentences from controller + service method names]

**Stability**: Instability = [score] ([interpretation])

#### 5.X.1 Capabilities

| # | The system... | Trigger | Notes |
|---|---|---|---|
| FR-[module]-001 | retrieves [resource] by ID | GET /api/[resource]/{id} | Returns 404 if not found |
| FR-[module]-002 | creates a new [resource] | POST /api/[resource] | Validates [fields] |
| FR-[module]-003 | updates [resource] | PUT /api/[resource]/{id} | Partial update supported |

#### 5.X.2 Data Managed

| Field | Type | Required | Validation | Business Meaning |
|---|---|---|---|---|
| [field] | [type] | [Yes/No] | [constraint] | [plain English] |

#### 5.X.3 Integration Contracts

| Direction | Module | Contract type | What is exchanged |
|---|---|---|---|
| Consumes | shared-lib | Java compile | Common validation + utility functions |
| Exposes to | api-gateway | REST API | [Resource] CRUD endpoints |
| Publishes | message-bus | Event | [EventName] on state change |

#### 5.X.4 Error States

| Condition | Response | User impact |
|---|---|---|
| Resource not found | 404 Not Found | [explain] |
| Validation failure | 400 Bad Request + field errors | [explain] |
| Downstream timeout | 503 Service Unavailable | [explain] |

#### 5.X.5 Flags

⚠️ Circular dependency with: [list if applicable]
⚠️ Dead module — no consumers detected [if applicable]
⚠️ High instability — volatile consumer of many dependencies [if instability > 0.7]

---

## 6. Cross-Module Integration Map

Table of all internal edges from graph:

| From Module | To Module | Dependency Type | Notes |
|---|---|---|---|
| service-a:core | shared-lib | compile | |
| service-b:impl | shared-lib | compile | |

---

## 7. Data Model Summary

List all major entities across all modules:

| Entity | Owning Module | Key Fields | Related Entities |
|---|---|---|---|
| Customer | service-a:core | customerId, name, email | Order (1:N) |

---

## 8. Stability & Risk Register

| Risk | Module(s) | Severity | Detail |
|---|---|---|---|
| Circular dependency | A, B, C | HIGH | A→B→C→A — risk of init deadlock |
| Dead module | orphan-svc | MEDIUM | No consumers — safe to remove? |
| High instability | order-proc | MEDIUM | Instability 0.81 — fragile consumer |
| High blast radius | shared-lib | HIGH | 12 dependents — change with care |

---

## 9. Open Questions & Assumptions

| # | Question / Assumption | Module | Priority |
|---|---|---|---|
| 1 | Assumed X is the authoritative source for Y — confirm with team | service-a | High |
| 2 | Could not determine business purpose of module Z from code alone — needs clarification | orphan-svc | Medium |

---

## Appendix A — Graph Metadata

```
Generated:      [timestamp]
Graph source:   repo-graph.json
Build system:   [maven/gradle/npm/mixed]
Total modules:  [N]
Total edges:    [N]
Circular deps:  [N cycles]
Dead modules:   [N]
Analysis tool:  repo-graph-architect
```
