# Quick Reference

## Core Agents

```
#file:.github/copilot/deep-search.prompt.md Find all database query builders
#file:.github/copilot/recursive-analyzer.prompt.md Why does logout not invalidate sessions?
#file:.github/copilot/context-engine.prompt.md Dependency graph for the payment module
#file:.github/copilot/impact-assessor.prompt.md What breaks if I rename UserService?
#file:.github/copilot/code-reviewer.prompt.md Deep review of order processing
#file:.github/copilot/orchestrator.prompt.md Debug: intermittent 500s on checkout
```

## Workflow Agents

```
#file:.github/copilot/debug.prompt.md Users get Payment Failed with 50%+ discounts
#file:.github/copilot/trace.prompt.md What happens when a user submits an order?
#file:.github/copilot/explain.prompt.md How does the permission system work?
#file:.github/copilot/refactor.prompt.md Extract auth into a shared service
#file:.github/copilot/architecture.prompt.md Give me a tour of this backend
#file:.github/copilot/migration.prompt.md Migrate from Express to Fastify
#file:.github/copilot/security.prompt.md Audit the auth and session flow
#file:.github/copilot/performance.prompt.md Dashboard API takes 5+ seconds
#file:.github/copilot/dead-code.prompt.md Find unused code in the backend
```

## Extended Workflows (via @workspace)

```
Follow @workspace workflows/debug-investigation.md for: {bug}
Follow @workspace workflows/trace-execution.md for: {flow}
Follow @workspace workflows/refactor-planning.md for: {refactor}
Follow @workspace workflows/architecture-review.md for: {understanding}
Follow @workspace workflows/migration-analysis.md for: {migration}
Follow @workspace workflows/security-audit.md for: {security}
Follow @workspace workflows/performance-investigation.md for: {perf}
Follow @workspace workflows/dead-code-scan.md for: {cleanup}
```

## Sub-Agent Composition

Reference sub-agents within any prompt:
```
#file:.github/copilot/recursive-analyzer.prompt.md Investigate order total bugs.
Also apply @workspace agents/sub-agents/error-path-tracer.md for each function found.
Also apply @workspace agents/sub-agents/test-coverage-scanner.md for each finding.
```

## Modifiers

| Add to any prompt | Effect |
|-------------------|--------|
| "Be thorough" | More depth, more files |
| "Be quick" | Shorter, top results only |
| "Focus on {module}" | Limits scope |
| "Include tests" | Also searches test files |
| "Show reasoning" | Displays investigation tree |
| "Just the answer" | Conclusion only |
| "Go deeper on {finding}" | Recurse further |
