---
name: graph-intelligence-suite
description: >
  Three specialised agents that consume a repo-graph.json (produced by the
  repo-graph-architect skill) to power downstream intelligence without re-scanning code.
  Use this skill whenever the user wants to: (1) ask questions about their codebase
  using natural language Q&A — 'what depends on X', 'trace this call', 'blast radius',
  'which module owns Y', 'explain this service'; (2) generate a Functional Requirements
  Document (FRD) or functional spec from the graph — 'create FRD', 'write requirements',
  'document the system', 'generate specs', 'what does module X do functionally';
  (3) analyse or improve API performance — 'optimise my APIs', 'find slow paths',
  'which APIs are bottlenecks', 'latency hotspots', 'API coupling issues',
  'chattiness between services', 'over-fetching', 'fan-out calls'. Works with any
  repo-graph.json produced by repo-graph-architect. Triggers on: 'use the graph',
  'from the graph', 'based on my repo', 'analyse my architecture', 'FRD', 'functional
  requirements', 'API performance', 'service coupling'.
---

# Graph Intelligence Suite

Three agents, one shared graph. All agents load a **sparse projection** of
`repo-graph.json` — never the full file — to stay token-efficient.

---

## Agent Routing

Detect intent from the user's message and route immediately:

| User intent | Agent |
|---|---|
| Question about what X does, who uses X, dependencies, traces, impacts | → **[AGENT: GRAPH-QA]** |
| Generate FRD / functional spec / requirements doc / system documentation | → **[AGENT: FRD]** |
| API performance, latency, coupling, chattiness, fan-out, optimisation | → **[AGENT: API-PERF]** |
| Multiple intents in one message | Run agents in sequence, share context |

If unclear, ask: *"Should I (1) answer a graph question, (2) generate an FRD, or (3) analyse API performance?"*

---

## Shared Step — Token-Efficient Graph Loading

**CRITICAL: Never load the full `repo-graph.json` into context.**
Use the sparse projection engine instead.

Read `references/graph-projection-engine.md` before loading any graph data.

The projection engine extracts only the slice of the graph relevant to the current
query — typically 5–30 nodes instead of hundreds, saving 80–95% of tokens.

---

## [AGENT: GRAPH-QA]

**Purpose**: Answer any natural-language question about the codebase using the graph.

Read → `references/agents/graph-qa-agent.md`

---

## [AGENT: FRD]

**Purpose**: Generate a professional Functional Requirements Document from the graph,
enriched with targeted source-code reads.

Read → `references/agents/frd-agent.md`

---

## [AGENT: API-PERF]

**Purpose**: Identify API performance risks, coupling issues, and optimisation
opportunities by analysing graph structure and code patterns.

Read → `references/agents/api-perf-agent.md`

---

## Shared Context Object

When running multiple agents in sequence, pass this context forward so nothing is
re-computed:

```json
{
  "graphPath": "/path/to/repo-graph.json",
  "graphMeta": { "totalModules": 42, "buildSystem": "maven", ... },
  "loadedProjections": {
    "shared-lib": { "node": {...}, "edges": [...], "impactSet": [...] }
  },
  "sessionFindings": []
}
```

Append each agent's findings to `sessionFindings` so later agents can reference them
without re-querying.
