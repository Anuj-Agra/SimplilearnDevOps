---
applyTo: "**/*.md,**/docs/**,**/openspec/**,**/.github/**"
description: "Automatically triggered when working with documentation files or when user asks about FRD, requirements, Jira tickets, runbooks, release notes, or OpenSpec"
---

# Documentation & Delivery Skills

When documentation or delivery planning is needed:

- **functional-spec-generator** (`.claude/skills/functional-spec-generator/SKILL.md`)
  Triggers: "FRD", "functional spec", "document the system", "user stories",
  "business rules", "what does this do", "generate requirements"

- **jira-ticket-generator** (`.claude/skills/jira-ticket-generator/SKILL.md`)
  Triggers: "Jira tickets", "backlog items", "create stories", "epics",
  "acceptance criteria", "story points", "sprint backlog"

- **runbook-generator** (`.claude/skills/runbook-generator/SKILL.md`)
  Triggers: "runbook", "ops playbook", "how to deploy", "on-call guide",
  "what to do when alert fires", "deployment guide", "rollback steps"

- **release-notes-generator** (`.claude/skills/release-notes-generator/SKILL.md`)
  Triggers: "release notes", "changelog", "what changed", "sprint summary",
  "user-facing changes", "release announcement"

- **openspec-output-coach** (`.claude/skills/openspec-output-coach/SKILL.md`)
  Triggers: "improve my OpenSpec", "spec is wrong", "AI built wrong thing",
  "tasks too vague", "proposal too broad", "better spec output",
  "spec-driven development quality", "/opsx output feedback"

- **api-contract-generator** (`.claude/skills/api-contract-generator/SKILL.md`)
  Triggers: "OpenAPI spec", "swagger", "API contract", "openapi.yaml",
  "document my API", "REST spec"

Load the relevant SKILL.md before generating documentation.
