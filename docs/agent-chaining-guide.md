# Agent Chaining Guide

## Overview

Agents in this system are designed to be **chained** — each agent's output is the natural input for the next. This produces a complete documentation suite from raw PEGA artefacts.

---

## Full chain: PEGA artefact → complete Jira-ready documentation

```
INPUT: PEGA JSON / BIN file / screenshot description
    │
    ▼
[Agent 06 — PEGA Expert]           ← Use this first if the artefact is unclear
    │   "What is this rule? What does it do?"
    │
    ▼
[Agent 07 — UI Reader]             ← Use if you have screenshots to process
    │   "What fields, buttons, and navigation does this screen have?"
    │
    ▼
[Agent 08 — Integration Mapper]    ← Use if the flow calls external services
    │   "What external services are called? What data is exchanged?"
    │
    ▼
[Agent 01 — Flow Narrator]         ← Always use this before BRD/FRD
    │   Output: 9-section plain-English flow narrative
    │
    ├──► [Agent 02 — BRD Writer]
    │        Input:  Flow narrative (+ any stakeholder context)
    │        Output: 14-section Business Requirements Document
    │
    ▼
[Agent 03 — FRD Writer]
    │   Input:  BRD + flow narrative (+ integration catalogue if available)
    │   Output: 13-section Functional Requirements Document
    │
    ▼
[Agent 04 — Jira Breakdown]
    │   Input:  FRD (full or selected FR blocks)
    │   Output: Epic → Story → Task hierarchy with estimates
    │
    ▼
[Agent 05 — Acceptance Criteria]
    │   Input:  Individual Jira Stories (one at a time for best results)
    │   Output: Gherkin AC set per story
    │
    ▼
OUTPUT: BRD + FRD + Jira tickets + Acceptance Criteria
        (ready for sprint planning, UAT, and regulatory sign-off)
```

---

## Chain variants by scenario

### Scenario A — "We have PEGA JSON/BIN, no documentation exists"

```
[06 PEGA Expert]  →  [01 Flow Narrator]  →  [02 BRD]  →  [03 FRD]  →  [04 Jira]  →  [05 AC]
```

Use Agent 06 first to understand any unclear rules, then 01 to narrate, then the full documentation chain.

### Scenario B — "We have screenshots from a demo / walkthrough"

```
[07 UI Reader]  →  [01 Flow Narrator]  →  [03 FRD]  →  [04 Jira]  →  [05 AC]
```

UI Reader reconstructs the field inventory and navigation. Feed this to Flow Narrator with a note that the source is screenshot-based.

### Scenario C — "We have a description of what the system does, no code access"

```
[01 Flow Narrator]  →  [02 BRD]  →  [03 FRD]  →  [04 Jira]  →  [05 AC]
```

Agent 01 can work from plain-text descriptions — it will flag what it cannot confirm without seeing the actual PEGA rules.

### Scenario D — "We need to document an integration (connector JSON available)"

```
[08 Integration Mapper]  →  [03 FRD] (INT-XXX blocks)  →  [05 AC] (integration failure scenarios)
```

### Scenario E — "A developer has a specific PEGA question"

```
[06 PEGA Expert]  (standalone — no chain needed)
```

### Scenario F — "We need Jira tickets for a specific feature immediately"

```
[04 Jira Breakdown]  (with a plain-text feature description as input)
→  [05 AC]  (for each Story generated)
```

---

## Inter-agent handoff: what to pass

| From agent | To agent | What to pass |
|-----------|---------|-------------|
| 07 UI Reader | 01 Flow Narrator | Full UI analysis output — paste the entire markdown |
| 08 Integration Mapper | 01 Flow Narrator | Integration summary table + data flow section |
| 01 Flow Narrator | 02 BRD Writer | Full 9-section flow narrative — paste entire output |
| 01 Flow Narrator | 03 FRD Writer | Full 9-section flow narrative |
| 02 BRD Writer | 03 FRD Writer | Full BRD — or just the Business Rules (Section 5) + Regulatory Requirements (Section 7) |
| 03 FRD Writer | 04 Jira Breakdown | Full FRD — or individual FR blocks for a specific feature |
| 04 Jira Breakdown | 05 Acceptance Criteria | Individual Story block (STORY [E1.S1]: ...) — run AC generation per story, not per Epic |
| 06 PEGA Expert | 01 Flow Narrator | Expert explanation — paste into Flow Narrator along with original JSON |

---

## Multi-flow analysis

If your KYC codebase has 4 hierarchical levels and multiple flows per level, process systematically:

```
Level 1: Identify all top-level flows (main CDD, main EDD, SAR, Periodic Review)
Level 2: For each top-level flow, identify sub-flows called
Level 3: For each sub-flow, identify utility steps and connectors
Level 4: For each connector, run Integration Mapper

Recommended processing order:
  1. Start with the main flow (KYC_CDDOnboarding or equivalent)
  2. Recurse into each sub-flow as it is referenced
  3. Process connectors in parallel (all can be Integration-Mapped independently)
  4. Aggregate all flow narratives before writing the BRD (one BRD covers the full scope)
  5. Write one FRD per major process area (CDD, EDD, AML, Approval, Reporting)
  6. Break down one Jira Epic per FRD functional area
```

---

## Token management tips

Each agent has a `typical_tokens_output` in its `config.json`. For the API, account for:

- Long BRD/FRD outputs (3,000–3,500 tokens) will approach max_tokens = 4,000
- For very large flows (> 20 steps), summarise the JSON before passing to Flow Narrator: ask Agent 06 to identify and list the key steps first
- For Jira breakdowns of large FRDs, process one functional area at a time rather than the entire FRD in one call
- Acceptance Criteria: always process one Story at a time for maximum scenario coverage
