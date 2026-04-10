# Graph Projection Engine

## Why Projections?

A large mono-repo graph can have 500+ nodes with 2000+ edges and 500KB+ of JSON.
Loading it all = ~125,000 tokens before you even start answering.

Instead, load a **sparse projection** — only the nodes and edges relevant to the
current query. This cuts token usage by 80–95%.

---

## Step 1 — Load Only the Graph Index (always)

The index is the `meta` block + node IDs + labels only. No edges, no metrics, no
impact sets. This is your "table of contents" — cheap to load, fast to search.

```python
# scripts/project_graph.py --mode index --graph repo-graph.json
```

Index output (flat list, ~3 tokens per module):
```
service-a | service-a:core | service-a:api | service-b | shared-lib | ...
```

**Load the index for every query first.** From it, identify the 1–5 focal nodes
relevant to the question before loading anything else.

---

## Step 2 — Identify Focal Nodes

Parse the user's question and extract module names:
- Direct mention: "what calls `shared-lib`?" → focal = `["shared-lib"]`
- Partial match: "what is in payments?" → search index for nodes where label contains "payment"
- Role mention: "what do my API gateway services depend on?" → search for nodes with "gateway" in label/path

If zero focal nodes found → ask the user to clarify or give the module name.

---

## Step 3 — Load the Right Projection

Choose projection type based on the query:

| Query type | Projection to load | Typical node count |
|---|---|---|
| "What does X do?" | Node-only: just X's metadata | 1 node |
| "What depends on X?" | Fan-in projection: X + all nodes with edge `→ X` | 2–15 nodes |
| "What does X depend on?" | Fan-out projection: X + all nodes X points to | 2–20 nodes |
| "Impact of changing X" | Impact projection: X + impactSet[X] | 5–50 nodes |
| "Path from A to B" | Path projection: BFS subgraph A→B | 3–10 nodes |
| "Circular deps" | Cycle projection: only cycleNodes | 3–20 nodes |
| "Dead modules" | Dead projection: only deadModules list | N dead nodes |
| "Critical nodes" | Top-N criticalNodes from analysis block | 5–10 nodes |
| Full FRD (module scope) | Module subtree: module + all children | 10–40 nodes |
| API perf analysis | High-fanout + entry-point nodes | 10–30 nodes |

---

## Projection Extraction Commands

Use `scripts/project_graph.py` to extract projections without loading the full file:

```bash
# Index only (always run first)
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode index

# Fan-in: who depends on shared-lib?
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode fan-in --node shared-lib

# Fan-out: what does service-a:core depend on?
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode fan-out --node service-a:core

# Impact set: blast radius of shared-lib
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode impact --node shared-lib

# Shortest path between two nodes
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode path --from service-a:core --to api-gateway

# All cycles (for circular dep questions)
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode cycles

# Dead modules
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode dead

# Module subtree (for FRD scoping)
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode subtree --node service-a

# High fan-in nodes (for API perf / critical path)
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode critical --top 10

# Entry-point nodes (Spring Boot apps, Angular main, etc.)
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode entry-points
```

---

## Projection Output Format

Each projection returns a minimal JSON slice:

```json
{
  "projectionType": "fan-in",
  "focalNode": "shared-lib",
  "nodes": [
    { "id": "shared-lib",  "label": "shared-lib", "metrics": { "fanIn": 12, "fanOut": 2, "instability": 0.14 } },
    { "id": "service-a:core", "label": "core", "parent": "service-a" },
    { "id": "service-b:impl", "label": "impl", "parent": "service-b" }
  ],
  "edges": [
    { "from": "service-a:core", "to": "shared-lib", "type": "compile" },
    { "from": "service-b:impl", "to": "shared-lib", "type": "compile" }
  ],
  "summary": "12 modules depend on shared-lib"
}
```

This is what goes into context — not the raw full graph.

---

## Token Budget Guidelines

| Operation | Approximate tokens |
|---|---|
| Full `repo-graph.json` (100 modules) | ~25,000 |
| Full `repo-graph.json` (500 modules) | ~125,000 |
| Index only (500 modules) | ~2,000 |
| Single node projection | ~200 |
| Fan-in/fan-out projection (10 nodes) | ~1,500 |
| Impact projection (30 nodes) | ~4,500 |
| Module subtree (20 nodes, for FRD) | ~3,000 |
| Critical nodes (top 10) | ~800 |

Target: keep loaded graph context under **5,000 tokens** per agent invocation.
If impact set > 50 nodes, summarise instead of listing: "42 modules affected (top 5: ...)"

---

## Caching Within a Session

Once a projection is loaded, add it to `sessionFindings.loadedProjections[nodeId]`.
Before loading a projection, check if it's already cached — never load the same
projection twice in a conversation.
