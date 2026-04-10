---
name: migration-planner
description: >
  Plan a phased migration (mainframe to distributed, monolith to microservices, legacy
  to cloud) using repo-graph.json as the sequencing engine. Use when asked: 'migration
  plan', 'modernisation roadmap', 'how to migrate', 'module migration order',
  'decommission plan', 'phased migration', 'strangler fig', 'mainframe migration'.
  Produces a dependency-ordered migration roadmap with risk scores, rollback checkpoints,
  and effort estimates per phase. Essential for multi-year modernisation programmes.
---
# Migration Planner

Produce a phased, dependency-ordered migration roadmap from graph analysis.

## Step 0 — Load Graph Context
```bash
python3 scripts/project_graph.py --graph repo-graph.json --mode index
python3 scripts/project_graph.py --graph repo-graph.json --mode critical --top 20
python3 scripts/project_graph.py --graph repo-graph.json --mode cycles
python3 scripts/project_graph.py --graph repo-graph.json --mode dead
python3 scripts/project_graph.py --graph repo-graph.json --mode entry-points
```

## Step 1 — Classify Every Module
For each node, assign:
- **Migration complexity**: Low (leaf, no dependents) / Medium / High (high fan-in, circular dep)
- **Migration risk**: Low / Medium / High (based on instability score and blast radius)
- **Migration type**: Rehost / Replatform / Refactor / Replace / Retire
- **Phase eligibility**: Can it move before its dependencies move?

## Step 2 — Build Dependency-Ordered Phases
**Rule**: A module can only migrate in phase N if ALL modules it depends on have migrated in phase N-1 or earlier.

Topological sort the dependency graph → phases emerge naturally.
Flag circular deps — these require a "strangler fig" or interface extraction before migration.

## Step 3 — Output: Migration Roadmap

```
MIGRATION ROADMAP: [System Name]
Strategy: [Strangler Fig / Big Bang / Phased Lift-and-Shift]

Phase 1 — Foundation (Months 1-3)
  Modules: [leaf nodes with no dependents — lowest risk, highest value as proof of concept]
  Risk: Low | Effort: [LOC-based estimate]
  Rollback: [how to revert if phase fails]
  Validation gate: [what must be true before Phase 2 starts]

Phase 2 — Core Services (Months 4-9)
  ...

MIGRATION RISK REGISTER
| Module | Blast Radius | Circular Deps | Complexity | Risk Score |
|--------|-------------|---------------|------------|------------|

CRITICAL PATH: [The longest chain that determines overall timeline]

ROLLBACK CHECKPOINTS: [One per phase — what "undo" looks like]

DECOMMISSION CANDIDATES: [Dead modules — retire immediately, save effort]
```

## Phase Risk Scoring
`riskScore = (fanIn × 2) + (instability × 10) + (inCircularDep ? 5 : 0)`
Sort descending — highest risk modules migrate last.
