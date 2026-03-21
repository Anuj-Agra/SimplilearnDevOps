# Agent Catalogue

All agents live under `agents/`. Each agent has a `system-prompt.md` (copy into Claude) and a `config.json` (API parameters).

---

## Agent map

| ID | Agent | Input | Output | Skills injected |
|----|-------|-------|--------|----------------|
| 00 | Orchestrator | Any PEGA artefact | Routes to specialist agent | All |
| 01 | Flow Narrator | JSON / BIN / description | Plain-English 8-section flow narrative | pega-knowledge, kyc-domain, role-adapters |
| 02 | BRD Writer | Flow narrative / process description | 12-section Business Requirements Document | kyc-domain, document-templates/brd, role-adapters |
| 03 | FRD Writer | BRD / flow details / PEGA rule JSON | Numbered FR Functional Requirements Document | pega-knowledge, kyc-domain, document-templates/frd, role-adapters |
| 04 | Jira Breakdown | FRD / feature description | Epic → Story → Task hierarchy with estimates | document-templates/jira, kyc-domain |
| 05 | Acceptance Criteria | Story / flow / rule description | Gherkin Given/When/Then scenario set | document-templates/ac, kyc-domain, role-adapters |
| 06 | PEGA Expert | Any PEGA question or artefact | Expert technical explanation | pega-knowledge (all), kyc-domain |
| 07 | UI Reader | Screenshot description / HTML / screen spec | Flow reconstruction + field inventory | pega-knowledge, kyc-domain, role-adapters |
| 08 | Integration Mapper | Connector JSON / REST spec / flow with service calls | Integration catalogue with data contracts | pega-knowledge/integration-patterns, kyc-domain/external-services |

---

## How to read a system prompt

Each `system-prompt.md` contains:

```
---
agent: <name>
version: <semver>
skills: [list of skill files to inject]
model: claude-sonnet-4-20250514
max_tokens: 4000
---

## Role & Identity
## Core responsibilities  
## Output format (exact template)
## PEGA knowledge base
## KYC domain knowledge
## Role adapter (injected at runtime)
## Hierarchy context (injected at runtime)
```

---

## Skill injection pattern

When calling via API, build the system prompt as:

```
[agent system-prompt.md content]
+
[relevant skills/*.md content]
+
[hierarchy/L<n>/context.md if scoped]
+
[role-adapters/<role>.md]
```

See `docs/getting-started.md` for the full assembly pattern.
