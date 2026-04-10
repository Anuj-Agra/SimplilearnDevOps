---
description: "Quick reference for all 61 Dev Intelligence Suite skills — shows what to type in agent mode to trigger each skill automatically"
---

# Dev Intelligence Suite — Quick Reference

Type any of these in GitHub Copilot agent mode. The right skill loads automatically.

## Architecture & Graph
- "Scan my repo and build a dependency graph"
- "What modules does the payments area contain?"
- "What depends on shared-lib?"
- "What is the blast radius of changing order-service?"
- "Are there circular dependencies?"
- "Which modules are dead and can be deleted?"

## Requirements & Documentation
- "Write an FRD for the orders module"
- "Generate an OpenAPI spec from the order controller"
- "What does the system do from a user perspective?"
- "Create Jira tickets from this FRD section"
- "Generate a runbook for the payment service"
- "Write release notes from the last 10 commits"
- "Convert these requirements to Gherkin scenarios"

## Code Quality & Refactoring
- "Find code smells in the order service"
- "How much technical debt do we have in the payments module?"
- "Refactor OrderService step by step" ← interactive mode with priority menu
- "Extract the validation logic from CustomerService"

## Security & Compliance
- "Run a security audit on the authentication module"
- "Find all places where PII is stored or logged"
- "Trace where customerId flows through the system"
- "Check our dependencies for known CVEs"
- "GDPR compliance review"

## Java Spring Specific
- "Are there race conditions in my services?"
- "Find places where @Transactional will silently fail"
- "Detect N+1 queries including ones hidden in serialisers"
- "Check my connection pool configuration"
- "Plan migration to Spring WebFlux"

## Angular Specific
- "Find memory leaks in Angular components"
- "Which components should use OnPush change detection?"
- "Why is my bundle so large?"

## Testing
- "Write Playwright tests for the checkout feature"
- "Generate test data builders for all my entities"
- "Find flaky tests in my test suite"
- "Set up mutation testing with PITest"
- "Create BDD scenarios from the FRD"

## Resilience & Performance
- "Which external calls have no circuit breaker?"
- "Find missing timeouts and bulkhead isolation"
- "Is my retry configuration safe?"
- "Design a caching strategy for reference data"
- "Generate k6 load tests for the orders API"
- "Decompose the checkout latency budget"

## Observability
- "What observability gaps do I have?"
- "Check correlation ID propagation across services"
- "Generate SLO definitions and Prometheus alerts"

## Production Readiness
- "What functional gaps are there?"
- "What edge cases will break production?"
- "Find performance bottlenecks before release"
- "Full gap analysis on the payments module"

## DevOps & Operations
- "Audit my CI/CD pipeline for missing safety checks"
- "Generate a deployment runbook"
- "Upgrade all my dependencies safely"
- "Find stale feature flags"

## OpenSpec / Spec-Driven Development
- "Why did the AI build the wrong thing from my OpenSpec proposal?"
- "How do I improve my OpenSpec tasks to get better output?"
- "My spec-driven development output is off — diagnose what's wrong"
