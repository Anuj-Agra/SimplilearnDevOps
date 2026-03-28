# Bridge Configuration

> **EDIT THIS FIRST** — Tell the bridge where both projects live.

## Project Paths

```
SOURCE PROJECT (PEGA Reverse Engineering):
  Root:     [../pega-reverse-engineering/]
  Findings: [../pega-reverse-engineering/workspace/findings/]
  FRD:      [../pega-reverse-engineering/workspace/findings/FRD-COMPLETE.md]
  Config:   [../pega-reverse-engineering/config/project-config.md]

TARGET PROJECT (New Application):
  Root:     [../new-app/]
  Source:   [../new-app/src/]
  APIs:     [../new-app/src/api/]
  UI:       [../new-app/src/components/]
  Config:   [../new-app/src/config/]
  Tests:    [../new-app/tests/]
  Docs:     [../new-app/docs/]

DEEP SEARCH PROJECT (Your Existing Deep Search Agents):
  Root:     [../deep-search-agents/]
  Agents:   [../deep-search-agents/agents/]
  Config:   [../deep-search-agents/config/]
```

## Target Technology Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Frontend | [React / Angular / Vue / etc.] | [version] |
| Backend | [Node.js / Java / .NET / etc.] | [version] |
| Database | [PostgreSQL / MongoDB / etc.] | [version] |
| API Style | [REST / GraphQL / gRPC] | |
| Auth | [OAuth2 / JWT / SAML] | |
| Hosting | [AWS / Azure / GCP / On-prem] | |

## Mapping Convention

How PEGA concepts translate to the new technology:

| PEGA Concept | Maps To In New App | Location Pattern |
|-------------|-------------------|-----------------|
| Flow (Screen Flow) | [Page route / wizard component] | [src/pages/] |
| Flow (Approval) | [Workflow engine / state machine] | [src/workflows/] |
| Assignment | [Form component + API endpoint] | [src/components/forms/] |
| Decision Table | [Business rule engine / if-else logic] | [src/rules/] |
| Decision Tree | [Strategy pattern / rule chain] | [src/rules/] |
| When Rule | [Middleware / guard / validator] | [src/middleware/] |
| Section (UI) | [React component / Angular template] | [src/components/] |
| Harness | [Page layout / shell component] | [src/layouts/] |
| Connect-REST | [API client / HTTP service] | [src/services/] |
| Connect-SOAP | [SOAP client / adapter] | [src/services/] |
| Data Page | [API cache / state store / query hook] | [src/stores/] |
| Data Transform | [DTO mapper / serializer] | [src/mappers/] |
| Property | [DB column / model field / form field] | [src/models/] |
| Validate rule | [Validation schema / form validator] | [src/validators/] |
| SLA | [Cron job / scheduler / timeout] | [src/jobs/] |
| Correspondence | [Email template / notification service] | [src/notifications/] |

## Deep Search Agent Configuration

How to invoke your deep search agents for scanning the target:

```
SEARCH COMMAND PATTERN: [describe how your deep search agents are invoked]

Example patterns (edit to match YOUR deep search setup):
  - File search:    "Search for files matching [pattern] in [path]"
  - Code search:    "Find code implementing [concept] in [path]"
  - API search:     "Find API endpoints matching [description]"
  - Component search: "Find UI components handling [feature]"
  - Schema search:  "Find database schemas for [entity]"
```

## Gap Severity Definitions

| Severity | Definition | Example |
|----------|-----------|---------|
| CRITICAL | Core business flow completely missing | Entire approval workflow not built |
| HIGH | Major feature missing or fundamentally wrong | Decision table logic missing |
| MEDIUM | Feature partial — key conditions or paths missing | 3 of 8 eligibility conditions implemented |
| LOW | Minor gap — cosmetic or non-functional | Field label different, validation message text |
| INFO | Difference noted but not necessarily a gap | Different UI framework, equivalent result |
