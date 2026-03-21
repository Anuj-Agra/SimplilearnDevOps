# Agent Catalogue

All agents live under `agents/`. Each agent has a `system-prompt.md` (copy into Claude or inject via API) and a `config.json` (API parameters and skill dependencies).

---

## Agent map

| ID | Agent | Invocation | Input | Output | Skills injected |
|----|-------|-----------|-------|--------|----------------|
| 00 | Orchestrator | Manual | Any PEGA artefact | Routing recommendation | All |
| 01 | Flow Narrator | Manual | JSON / BIN / description | 9-section plain-English flow narrative | pega-knowledge, kyc-domain, role-adapters |
| 02 | BRD Writer | Manual | Flow narrative / process description | 14-section Business Requirements Document | kyc-domain, document-templates/brd, role-adapters |
| 03 | FRD Writer | Manual | BRD / flow details / PEGA rule JSON | Numbered FR Functional Requirements Document | pega-knowledge, kyc-domain, document-templates/frd, role-adapters |
| 04 | Jira Breakdown | Manual | FRD / feature description | Epic → Story → Task hierarchy with estimates | document-templates/jira, kyc-domain |
| 05 | Acceptance Criteria | Manual | Story / flow / rule description | Gherkin Given/When/Then scenario set | document-templates/ac, kyc-domain, role-adapters |
| 06 | PEGA Expert | Manual | Any PEGA question or artefact | Expert technical explanation | pega-knowledge (all), kyc-domain |
| 07 | UI Reader | Manual | Screenshot description / HTML / screen spec | Flow reconstruction + field inventory | pega-knowledge, kyc-domain, role-adapters |
| 08 | Integration Mapper | Manual | Connector JSON / REST spec / flow with service calls | Integration catalogue with data contracts | pega-knowledge/integration-patterns, kyc-domain/external-services |
| **09** | **Recursive Analyser** | **Automated** | **Single rule JSON + context bundle** | **Narrative + FRD fragment per rule** | **All rule schemas, pega-knowledge (all), kyc-domain** |

---

## Agent 09 — Recursive Analyser (automated)

Agent 09 is called automatically by `tools/run.py` in a checkpoint loop — once per rule, in dependency order.

### How it works

```
tools/run.py analyse --workspace ./workspaces/kyc-v1
    │
    ├── Phase 1: Build rule graph (no LLM)
    │     Parse all rule files → extract references → build directed graph
    │     Save: rule_graph.json, manifest.json, queue.json
    │
    ├── Phase 2: Analyse rules (LLM — Agent 09 called per rule)
    │     For each pending rule in queue:
    │       1. Assemble bounded context (rule + dep summaries + skills)
    │       2. Call Agent 09 via API
    │       3. Save output to workspaces/{name}/analysis/{rule_id}.narrative.md
    │       4. Mark done in checkpoint
    │     Safe to interrupt — resumes from last checkpoint on re-run
    │
    └── Phase 3: Aggregate (no LLM)
          Concatenate all narratives → full_flow_narrative.md
          Concatenate FRD fragments → frd_fragments.md
```

### Rule types handled

| Rule type | pxObjClass | Agent 09 produces |
|-----------|-----------|------------------|
| Case Type | `Rule-Obj-CaseType` | Lifecycle, stage map, process inventory, status map |
| Flow | `Rule-Obj-Flow` | Step narrative, decision inventory, assignment/SLA/connector tables |
| Activity | `Rule-Obj-Activity` | Step walkthrough, parameter map, called activity chain |
| Flow Action | `Rule-Obj-Flowsection` | Screen description, button map, pre/post activity analysis |
| Section | `Rule-HTML-Section` | Field inventory, embedded section tree, conditional display logic |
| When Condition | `Rule-Obj-When` | Expression translation, property inventory, edge cases |

### Token window management

For each rule, the engine assembles a **bounded context bundle** (default: 6,000 tokens):

| Tier | Content | Priority |
|------|---------|---------|
| 1 | The rule's own JSON | Always included — never truncated |
| 2 | CaseType overview (orientation) | Always included — capped at 30% of budget |
| 3 | Dependency summaries (completed analyses of referenced rules) | Priority order — last to be truncated |
| 4 | PEGA knowledge skills + KYC domain skills | Capped at 25% of budget |

### Checkpoint and resume

The checkpoint survives LLM token exhaustion, network errors, process crashes, and manual interruption.
On resume, the engine resets any `in_progress` rules and continues from the next `pending` rule.

---

## How to read a system prompt

Each `system-prompt.md` starts with a YAML front-matter block:

```yaml
---
agent: "09-recursive-analyser"
version: "1.0.0"
skills: [list of skill files to inject]
model: claude-sonnet-4-20250514
max_tokens: 4000
---
```

Followed by: Role & Identity, Output format templates, PEGA knowledge, KYC domain knowledge.

## Skill injection pattern

Build the system prompt by concatenating:

```
[Agent system-prompt.md content]
+
[Relevant skills/*.md content]
+
[hierarchy/L<n>-<tier>/context.md  if scoped to a tier]
+
[skills/role-adapters/<role>.md]
```
