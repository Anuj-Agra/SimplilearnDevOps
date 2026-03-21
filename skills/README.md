# Skills

Skills are **reusable knowledge modules** injected into agent system prompts at runtime. They allow agents to share a common knowledge base without duplicating content across every prompt.

---

## How skills are injected

When calling the Anthropic API, build the system prompt by concatenating:

```
[Agent system-prompt.md]

---
# Injected Skills

[skill file 1 content]

---

[skill file 2 content]

---

# Hierarchy Context

[hierarchy/L<n>-<tier>/context.md content]

---

# Role Adapter

[skills/role-adapters/<role>.md content]
```

In Claude.ai (manual use): paste the agent system prompt, then paste the relevant skill file(s) beneath it in the same message.

---

## Skill index

| Skill file | Purpose | Injected into agents |
|-----------|---------|---------------------|
| `pega-knowledge/rule-types.md` | All PEGA rule types with definitions | 00, 01, 03, 04, 06, 07, 08 |
| `pega-knowledge/json-bin-structure.md` | JSON/BIN field reference for all rule types | 00, 01, 06, 08 |
| `pega-knowledge/class-hierarchy.md` | 4-tier PEGA class hierarchy and inheritance | 00, 01, 06 |
| `pega-knowledge/integration-patterns.md` | PEGA integration patterns (REST, SOAP, MQ, file) | 01, 06, 08 |
| `kyc-domain/regulatory-framework.md` | KYC regulatory obligations (FATF, AMLD, GDPR) | All |
| `kyc-domain/risk-scoring.md` | Risk scoring models, thresholds, EDD triggers | 01, 02, 03, 05, 06 |
| `kyc-domain/approval-flows.md` | KYC approval hierarchies, maker-checker, SLAs | 01, 02, 03, 04, 05 |
| `kyc-domain/external-services.md` | Catalogue of KYC external service types | 01, 06, 08 |
| `document-templates/brd-template.md` | BRD structure and writing standards | 02 |
| `document-templates/frd-template.md` | FRD structure and FR format | 03 |
| `document-templates/jira-ticket-template.md` | Jira hierarchy and ticket format | 04 |
| `document-templates/acceptance-criteria-template.md` | Gherkin AC format and scenario types | 05 |
| `role-adapters/business-analyst.md` | Tone and depth for BA audience | All (conditional) |
| `role-adapters/product-owner.md` | Tone and depth for PO audience | All (conditional) |
| `role-adapters/pega-developer.md` | Tone and depth for Dev audience | All (conditional) |
| `role-adapters/qa-tester.md` | Tone and depth for QA audience | All (conditional) |
| `shared-context/kyc-glossary.md` | Definitions of all KYC and PEGA terms | 00, 06 |
| `shared-context/pega-kyc-integration-map.md` | Visual map of PEGA KYC system integrations | 08 |

---

## Updating skills

When your client's PEGA hierarchy, class names, or integration endpoints are known, update:
- `hierarchy/L<n>-<tier>/context.md` with actual class names
- `skills/kyc-domain/external-services.md` with actual vendor names and endpoints
- `skills/kyc-domain/risk-scoring.md` with actual scoring thresholds

This ensures all agents use client-specific context without modifying individual agent prompts.
