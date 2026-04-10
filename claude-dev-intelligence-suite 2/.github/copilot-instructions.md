---
applyTo: "**"
---

# Dev Intelligence Suite — GitHub Copilot Instructions

This workspace contains 61 specialised AI skills in `.claude/skills/`.
GitHub Copilot agent mode automatically loads the relevant skill based on
your prompt. You do not need to name a skill — just describe what you want.

## How it works

When you type a prompt in agent mode, Copilot reads this file and the
`AGENTS.md` routing table, identifies the matching skill, loads its
`SKILL.md`, and executes it. The routing is automatic and invisible.

## Examples — type these exactly as shown

| What you type | Skill invoked automatically |
|---|---|
| "Scan my repo and build a dependency graph" | repo-graph-architect |
| "What depends on the shared-lib module?" | graph-intelligence-suite |
| "Write an FRD for the orders module" | functional-spec-generator |
| "Find security vulnerabilities" | security-audit |
| "Are there race conditions in my code?" | concurrency-hazard-scanner |
| "Size my connection pools correctly" | connection-pool-analyser |
| "Add circuit breakers to my external calls" | circuit-breaker-auditor |
| "What will break in production?" | gap-detector |
| "Write Playwright tests for the checkout feature" | playwright-test-generator |
| "Generate test data builders for my entities" | test-data-builder-generator |
| "Find flaky tests" | flaky-test-detector |
| "Refactor OrderService step by step" | interactive-refactoring-agent |
| "How much technical debt do I have?" | technical-debt-quantifier |
| "Plan my mainframe migration" | migration-planner |
| "Generate Gherkin scenarios from this FRD" | bdd-scenario-generator |
| "Create a runbook for the payment service" | runbook-generator |
| "What should I fix to improve my OpenSpec output?" | openspec-output-coach |

## Project conventions (applied to all code generated)

- Java: constructor injection via `@RequiredArgsConstructor` — never `@Autowired` on fields
- Java: all service exceptions extend `BusinessException` (runtime)
- Java: `@Transactional` on service methods, never on controllers or repositories
- Angular: `ChangeDetectionStrategy.OnPush` on all new components
- Angular: `trackBy` on every `*ngFor`
- Angular: reactive forms (`FormGroup`) — never template-driven
- Tests: JUnit 5 + Mockito + AssertJ — never JUnit 4
- Tests: `@ExtendWith(MockitoExtension.class)` on every test class

## Skill file location

All skills are in `.claude/skills/[skill-name]/SKILL.md`.
Reference files are in `.claude/skills/[skill-name]/references/`.
Scripts are in `.claude/skills/[skill-name]/scripts/`.

The shared dependency graph (when built) is at `graph/repo-graph.json`.
Always check if this file exists before scanning the codebase — it is
significantly faster to load a projection than to rescan.
