# PEGA KYC Agent Hub

> A modular AI agent system for analysing, documenting, and renovating a PEGA KYC codebase.
> Built for Business Analysts, Product Owners, PEGA Developers, and QA Engineers.

---

## What this repository contains

| Folder | Purpose |
|--------|---------|
| `agents/` | System prompts for each specialist AI agent |
| `skills/` | Reusable knowledge modules injected into agents |
| `hierarchy/` | PEGA 4-tier class hierarchy context files |
| `app/` | Interactive React/Claude AI–powered web application |
| `examples/` | Sample inputs and expected outputs for each agent |
| `docs/` | Usage guides, chaining patterns, prompt engineering tips |

---

## Repository hierarchy (copy order for GitHub)

```
pega-kyc-agent-hub/                        ← Root
│
├── README.md                               ← Start here
├── AGENTS.md                               ← Agent catalogue & capabilities
├── SKILLS.md                               ← Skill catalogue & injection guide
│
├── .github/
│   ├── workflows/
│   │   └── validate-prompts.yml            ← CI: lint prompt files
│   └── CODEOWNERS                          ← Ownership by domain
│
├── agents/                                 ← LAYER 1: Agent system prompts
│   ├── README.md
│   ├── 00-orchestrator/
│   │   ├── system-prompt.md
│   │   └── config.json
│   ├── 01-flow-narrator/
│   │   ├── system-prompt.md
│   │   └── config.json
│   ├── 02-brd-writer/
│   │   ├── system-prompt.md
│   │   └── config.json
│   ├── 03-frd-writer/
│   │   ├── system-prompt.md
│   │   └── config.json
│   ├── 04-jira-breakdown/
│   │   ├── system-prompt.md
│   │   └── config.json
│   ├── 05-acceptance-criteria/
│   │   ├── system-prompt.md
│   │   └── config.json
│   ├── 06-pega-expert/
│   │   ├── system-prompt.md
│   │   └── config.json
│   ├── 07-ui-reader/
│   │   ├── system-prompt.md
│   │   └── config.json
│   └── 08-integration-mapper/
│       ├── system-prompt.md
│       └── config.json
│
├── skills/                                 ← LAYER 2: Reusable knowledge modules
│   ├── README.md
│   ├── pega-knowledge/
│   │   ├── rule-types.md
│   │   ├── json-bin-structure.md
│   │   ├── class-hierarchy.md
│   │   └── integration-patterns.md
│   ├── kyc-domain/
│   │   ├── regulatory-framework.md
│   │   ├── risk-scoring.md
│   │   ├── approval-flows.md
│   │   └── external-services.md
│   ├── document-templates/
│   │   ├── brd-template.md
│   │   ├── frd-template.md
│   │   ├── jira-ticket-template.md
│   │   └── acceptance-criteria-template.md
│   ├── role-adapters/
│   │   ├── business-analyst.md
│   │   ├── product-owner.md
│   │   ├── pega-developer.md
│   │   └── qa-tester.md
│   └── shared-context/
│       ├── kyc-glossary.md
│       └── pega-kyc-integration-map.md
│
├── hierarchy/                              ← LAYER 3: PEGA 4-tier context
│   ├── README.md
│   ├── L1-enterprise/
│   │   └── context.md
│   ├── L2-division/
│   │   └── context.md
│   ├── L3-application/
│   │   └── context.md
│   └── L4-module/
│       └── context.md
│
├── app/                                    ← LAYER 4: Interactive application
│   ├── README.md
│   └── pega-kyc-agent-hub.jsx
│
├── examples/                               ← LAYER 5: Reference I/O
│   ├── README.md
│   ├── sample-inputs/
│   │   ├── flow-json-example.json
│   │   ├── flow-description-example.md
│   │   └── connector-json-example.json
│   └── sample-outputs/
│       ├── flow-narrative-example.md
│       ├── brd-example.md
│       ├── frd-example.md
│       ├── jira-breakdown-example.md
│       └── acceptance-criteria-example.md
│
└── docs/
    ├── getting-started.md
    ├── agent-chaining-guide.md
    ├── prompt-engineering-guide.md
    └── how-to-read-pega-json.md
```

---

## Quickstart

### Option A — Use the interactive app (recommended for teams)
1. Open `app/pega-kyc-agent-hub.jsx` in [Claude.ai Artifacts](https://claude.ai)
2. Select your agent and role
3. Paste PEGA JSON, BIN content, or a description
4. Generate your deliverable

### Option B — Copy a prompt template (paste into Claude.ai)
1. Open `agents/<agent-name>/system-prompt.md`
2. Copy the full contents
3. In Claude.ai, start a new conversation and paste as a **System Prompt** (Projects feature) or prepend to your message
4. Include the relevant skill files from `skills/` for richer context

### Option C — API integration
1. Read `docs/getting-started.md`
2. Use `agents/<agent-name>/config.json` for model and parameter settings
3. Inject skill files from `skills/` as additional context in the system prompt

---

## Agent chaining (recommended workflow)

```
PEGA JSON / BIN / Screenshots
         │
         ▼
  [01] Flow Narrator  ──────────────────────────────┐
         │                                          │
         ▼                                          ▼
  [02] BRD Writer     [03] FRD Writer       [06] PEGA Expert
                             │
                             ▼
                    [04] Jira Breakdown
                             │
                             ▼
                  [05] Acceptance Criteria
```

See `docs/agent-chaining-guide.md` for the full chaining strategy.

---

## PEGA hierarchy support

This system is aware of PEGA's 4-tier class hierarchy:

| Tier | Level | Typical KYC contents |
|------|-------|----------------------|
| L1 | Enterprise | `Org-` classes, shared data models, master SLAs |
| L2 | Division | `Div-` classes, divisional risk policies |
| L3 | Application | `KYC-` / `AML-` application classes, flows, UI |
| L4 | Module | `KYC-Work-CDD`, `KYC-Work-EDD`, connector rules |

Populate `hierarchy/L<n>-<name>/context.md` with your client's specific class names, then reference that file when prompting any agent.

---

## Regulatory coverage

| Framework | Coverage |
|-----------|----------|
| FATF Recommendations 10, 12, 15–17 | ✓ |
| EU AMLD 5 / 6 | ✓ |
| OFAC / UN / EU sanctions | ✓ |
| PEP screening | ✓ |
| UBO disclosure | ✓ |
| GDPR (data handling) | ✓ |

---

## Contributing

See `.github/CODEOWNERS` for domain ownership.
Prompt files must pass the YAML front-matter lint check in `.github/workflows/validate-prompts.yml`.
