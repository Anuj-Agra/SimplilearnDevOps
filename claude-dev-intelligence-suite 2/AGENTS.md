# Dev Intelligence Suite — Agent Orchestrator

This file is read automatically by GitHub Copilot (agent mode), Claude Code,
Cursor, Windsurf, and all AI coding assistants that respect AGENTS.md.

You are operating inside a project equipped with 61 specialised intelligence
skills. **You never need to be told which skill to use.** Read the user's
message, match their intent to the skill routing table below, read the
corresponding SKILL.md, and execute it.

---

## How to Route Automatically

1. Read the user's message carefully.
2. Match their intent to the TRIGGER PHRASES in the routing table.
3. Load the matching skill file from `.claude/skills/[skill-name]/SKILL.md`.
4. Follow the skill instructions exactly — they contain all scanning commands,
   output formats, and code patterns.
5. If multiple skills match, run them in the RECOMMENDED ORDER shown below.
6. If no skill matches, answer directly using your own knowledge.

You do not need to announce which skill you are using unless the user asks.
Just execute it. The user expects seamless routing.

---

## Skill Routing Table

### Say anything about the codebase structure or dependencies →
`repo-graph-architect` — scan repo, build dependency graph
`graph-intelligence-suite` — Q&A, performance analysis from existing graph

### Say anything about what the system does, requirements, or specs →
`functional-spec-generator` — generate FRD document
`api-contract-generator` — generate OpenAPI 3.0 YAML
`db-schema-reverse-engineer` — produce logical data model / ER diagram
`bdd-scenario-generator` — produce Gherkin feature files from requirements

### Say anything about who uses the system or what roles can do →
`functional-spec-generator` (Section 3 — User Roles & Personas)
`persona-suite` — review from PO / BA / Architect / Developer / Test Architect perspective

### Say anything about security, vulnerabilities, or compliance →
`security-audit` — OWASP Top 10 scan
`gdpr-compliance-scanner` — PII mapping, GDPR Article 30
`data-lineage-mapper` — trace a field through the system
`dependency-risk-tracker` — CVE scan, licence check

### Say anything about architecture, migration, or dead code →
`migration-planner` — phased migration roadmap
`dead-code-eliminator` — safe decommission runbook
`change-impact-analyser` — blast radius of a change

### Say anything about concurrency, thread safety, or parallel connections →
`concurrency-hazard-scanner` — find race conditions and shared mutable state
`reactive-migration-advisor` — plan migration to Spring WebFlux
`distributed-lock-auditor` — find multi-instance unsafe operations

### Say anything about resilience, fallback, or timeouts →
`circuit-breaker-auditor` — unprotected downstream calls
`timeout-bulkhead-auditor` — missing timeouts and thread pool isolation
`retry-storm-detector` — bad retry configurations
`graceful-degradation-planner` — explicit fallback strategies per endpoint

### Say anything about connections, pools, or queues →
`connection-pool-analyser` — HikariCP and HTTP pool sizing
`backpressure-queue-analyser` — Kafka/RabbitMQ consumer lag, DLQ gaps

### Say anything about observability, logging, or monitoring →
`observability-gap-detector` — missing metrics, tracing, structured logging
`correlation-id-auditor` — trace propagation across async boundaries
`slo-sla-generator` — SLO definitions and Prometheus alert rules

### Say anything about API design, versioning, or safety →
`api-versioning-auditor` — breaking changes, deprecation strategy
`idempotency-scanner` — duplicate request risks
`rate-limiter-auditor` — unprotected endpoints

### Say anything about performance, caching, or load →
`cache-strategy-generator` — what to cache, TTL, warming strategy
`latency-budget-decomposer` — per-hop latency allocation
`load-test-generator` — Gatling / k6 load test scripts

### Say anything about testing →
`playwright-test-generator` — Playwright UI + API test suites
`test-data-builder-generator` — fluent builder pattern for all entities
`flaky-test-detector` — find non-deterministic tests
`mutation-testing-reporter` — PITest / Stryker configuration and analysis
`bdd-scenario-generator` — Gherkin feature files

### Say anything about production risks, gaps, or edge cases →
`gap-detector` — functional, technical, scenario, and performance gaps

### Say anything about CI/CD, pipeline, or deployment →
`cicd-pipeline-auditor` — missing pipeline gates and safety checks
`runbook-generator` — operational runbooks per service
`release-notes-generator` — user-facing changelog from git log

### Say anything about Jira, tickets, or backlog →
`jira-ticket-generator` — epics, stories, bugs with acceptance criteria

### Say anything about code quality, smells, or debt →
`code-smell-detector` — God classes, long methods, complexity hotspots
`technical-debt-quantifier` — financial cost model of the debt
`refactoring-advisor` — specific refactoring moves with before/after code

### Say anything about refactoring interactively or step by step →
`interactive-refactoring-agent` — analyse class → present menu → write code per selection

### Say anything about library upgrades or migration →
`dependency-upgrade-automator` — updated pom.xml/package.json + migration guide

### Say anything about feature flags →
`feature-flag-auditor` — stale flags, nested flags, retirement backlog

### Say anything about mocking external APIs or test stubs →
`external-api-mock-generator` — WireMock stubs for all external integrations

### Say anything about architecture decisions or onboarding →
`adr-generator` — Architecture Decision Records
`onboarding-guide-generator` — developer onboarding guide per module

### Say anything about Spring, Hibernate, or transaction issues →
`spring-transaction-analyser` — 9 ways @Transactional silently fails
`spring-bean-lifecycle-auditor` — scoping bugs, proxy failures
`hibernate-n1-deep-scanner` — N+1 in serialisers, toString, stream operations

### Say anything about Angular, memory leaks, or bundle size →
`angular-memory-leak-detector` — unsubscribed observables, setInterval leaks
`angular-change-detection-optimiser` — OnPush, trackBy, template functions
`angular-bundle-analyser` — bundle bloat from lodash, moment, icon libraries

### Say anything about contract testing →
`pact-contract-test-generator` — consumer-driven contract tests

### Say anything about OpenSpec or spec-driven development quality →
`openspec-output-coach` — diagnose why AI built wrong thing, prescribe spec fixes

---

## Multi-Skill Workflows

When the user's request spans multiple skills, run them in sequence:

**"Analyse my codebase" / "Full discovery"**
→ repo-graph-architect → functional-spec-generator → security-audit → gap-detector

**"Review this before release" / "Pre-release check"**
→ change-impact-analyser → gap-detector → concurrency-hazard-scanner → cicd-pipeline-auditor

**"Set up tests for this module"**
→ functional-spec-generator → bdd-scenario-generator → test-data-builder-generator → playwright-test-generator

**"Is this ready for production scale?"**
→ concurrency-hazard-scanner → connection-pool-analyser → circuit-breaker-auditor
  → timeout-bulkhead-auditor → observability-gap-detector → load-test-generator

**"Help me refactor this class"**
→ interactive-refactoring-agent (handles analysis → menu → code writing in one session)

**"Compliance review" (for financial services)**
→ gdpr-compliance-scanner → data-lineage-mapper → security-audit → dependency-risk-tracker

---

## Key Paths

Skills location:   `.claude/skills/[skill-name]/SKILL.md`
Graph output:      `graph/repo-graph.json`
Graph projection:  `.claude/skills/graph-intelligence-suite/scripts/project_graph.py`
FRD output:        `docs/frd/`
Test output:       `tests/`
Gap reports:       `docs/gap-reports/`

---

## Behaviour Rules

- Load the skill BEFORE responding — skills contain the detection patterns,
  output formats, and code templates. Do not improvise these from memory.
- Use `graph/repo-graph.json` if it exists — it is faster and more accurate
  than rescanning the codebase.
- When generating code (refactoring, test generation), produce COMPLETE,
  compilable files — never pseudocode, never "..." placeholders.
- When a skill prescribes a specific output format (report, YAML, .docx),
  follow it exactly — consistency matters for team tooling.
- If the user says "skip the skill" or "just answer directly", comply.
