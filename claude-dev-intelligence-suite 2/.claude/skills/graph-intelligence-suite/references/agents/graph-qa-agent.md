# AGENT: GRAPH-QA

Answer natural-language questions about the codebase using graph projections.
Zero code scanning — all answers come from `repo-graph.json` projections.

---

## Protocol

1. **Parse the question** → identify focal nodes (see projection engine)
2. **Load the right projection** (fan-in / fan-out / impact / path / cycles / dead)
3. **Answer from the projection** — never hallucinate module names
4. **Attach a Mermaid sub-diagram** for any question involving relationships
5. **State confidence**: HIGH (from graph data) | MEDIUM (inferred) | LOW (code read needed)

---

## Question → Projection → Answer Patterns

### "What depends on X?" / "Who uses X?" / "What calls X?"
```
Projection: fan-in of X
Answer structure:
  Direct:    N modules declare a direct dependency on X
  Transitive: M additional modules depend on X indirectly
  Top users:  [list top 5 by their own fan-out]
  Risk:       "X has fan-in=N, making it a [low/moderate/high] blast-radius node"
```

### "What does X depend on?" / "What are X's dependencies?"
```
Projection: fan-out of X
Answer structure:
  Direct:    X declares N dependencies
  List:      [dep → type] for each
  Instability score: X.instability = 0.73 (HIGH — depends on many things)
  Concern:   Flag any dependency on a circular-dep node or dead module
```

### "What breaks if X changes?" / "Blast radius of X"
```
Projection: impact of X
Answer structure:
  Total impact: N modules at risk
  Critical path: top 3 entry-point modules that would be affected
  Safest change approach: "X has instability=0.14 — it is a stable, widely-used
    module. Any change should be regression-tested across: [top 5 impacted]"
```

### "Is there a path from A to B?" / "How does A reach B?"
```
Projection: path A→B
Answer structure:
  Path found: A → X → Y → B (3 hops)
  OR: No direct dependency path exists from A to B
  Mermaid diagram showing the path
```

### "What are my circular dependencies?"
```
Projection: cycles
Answer structure:
  N circular dependency cycles found:
  Cycle 1: A → B → C → A  (length 3, [HIGH/MEDIUM/LOW] risk)
  Recommendation per cycle: "Break cycle by extracting interface from A into a
    shared-contracts module that both A and C can depend on"
```

### "What are my dead / unused modules?"
```
Projection: dead
Answer structure:
  N potentially unused modules (fan-in = 0, not an entry-point):
  [list with path, LOC, fileCount]
  Caution: "Verify before deleting — may be consumed via reflection, config, or
    external systems not captured in build files"
```

### "Which module is most critical / risky to change?"
```
Projection: critical (top 10)
Answer structure:
  Top 5 highest-impact modules:
  1. shared-lib      (fan-in: 12, instability: 0.14) ← most stable, most risky to change
  2. common-utils    (fan-in:  9, instability: 0.22)
  ...
  Recommendation: "Treat these as 'frozen cores' — changes need full regression suite"
```

### "Explain what module X does" / "What is X responsible for?"
```
Projections: node-only for X, then fan-in + fan-out
Answer structure:
  X is a [type: submodule / library / service] in [parent]
  It provides: [infer from what depends on it — its consumers hint at its purpose]
  It consumes: [its declared dependencies]
  Size: [LOC, fileCount]
  Stability: [score interpretation]
  → If more detail needed: "I can read X's source code for a deeper explanation — want me to?"
```

### "Show me the architecture of [area]"
```
Projection: subtree of [area]
Answer structure:
  Mermaid hierarchy diagram (left-right) of the subtree
  Narrative: "[area] contains N sub-modules. Key relationships: ..."
  Hotspots: highlight any circular deps or high-instability nodes within the subtree
```

---

## Mermaid Diagram Rules

Always generate a diagram for relationship questions. Max 15 nodes.

```mermaid
graph LR
  subgraph service-a
    core[service-a:core]
    api[service-a:api]
  end
  shared-lib -->|compile| core
  shared-lib -->|compile| api
  core -->|api| gateway[api-gateway]
  style shared-lib fill:#E74C3C,color:#fff
  style gateway fill:#8E44AD,color:#fff
```

Color conventions (copy exactly):
- Focal node (query subject): `fill:#E74C3C,color:#fff` (red)
- Entry-point / deployable: `fill:#8E44AD,color:#fff` (purple)
- High instability node: `fill:#F39C12,color:#fff` (amber)
- Circular dep node: `fill:#E74C3C,stroke:#900,stroke-width:3px` (red bold)
- Dead module: `fill:#95A5A6,color:#fff` (grey)
- Normal: no override

---

## Answer Template

```
**[Question type]** — shared-lib

Direct answer: 12 modules depend on shared-lib.

Graph evidence:
| Module           | Dependency type | Scope   |
|------------------|-----------------|---------|
| service-a:core   | compile         | direct  |
| service-b:impl   | compile         | direct  |
| api-gateway      | compile         | direct  |
| ... (9 more)     |                 |         |

Risk insight: shared-lib is the most-depended-upon module in this repo
(instability: 0.14 — very stable). Any breaking change here requires
coordinated testing across 12 modules.

[Mermaid diagram]

Confidence: HIGH (direct graph data)
```

---

## Escalation to Code Read

If the graph can't fully answer the question (e.g. "what HTTP method does endpoint X use"),
say:

> "The graph tells me X is in `service-a:api` with fan-in=3. To answer your question about
> the HTTP method, I need to read the source. Want me to look at
> `service-a/api/src/main/java/...`?"

Then use `bash`/`view` to read only the specific file — not the whole module.
