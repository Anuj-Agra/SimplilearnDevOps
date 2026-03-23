# Quick Reference — Cody Deep Search Agents

## One-Liner Prompts

### Search
```
Use #file:.github/copilot/deep-search.prompt.md — Find all database query builders
```
```
Use #file:.github/copilot/deep-search.prompt.md — Where is rate limiting configured?
```
```
Use #file:.github/copilot/deep-search.prompt.md — Show me all event listeners for "orderCreated"
```

### Deep Analysis
```
Use #file:.github/copilot/recursive-analyzer.prompt.md — Why does logout not invalidate all sessions?
```
```
Use #file:.github/copilot/recursive-analyzer.prompt.md — How does a file upload go from browser to S3?
```
```
Use #file:.github/copilot/recursive-analyzer.prompt.md — Root cause: users see old email after changing it
```

### Context Building
```
Use #file:.github/copilot/context-engine.prompt.md — Build the dependency graph for the payment module
```
```
Use #file:.github/copilot/context-engine.prompt.md — Map the architecture of the notification system
```
```
Use #file:.github/copilot/context-engine.prompt.md — What is the data flow for user registration?
```

### Impact Assessment
```
Use #file:.github/copilot/impact-assessor.prompt.md — What breaks if I split User.name into firstName/lastName?
```
```
Use #file:.github/copilot/impact-assessor.prompt.md — Is it safe to delete the /legacy directory?
```
```
Use #file:.github/copilot/impact-assessor.prompt.md — Impact of upgrading Express 4 to Express 5
```

### Code Review
```
Use #file:.github/copilot/code-reviewer.prompt.md — Deep review of the order processing service
```
```
Use #file:.github/copilot/code-reviewer.prompt.md — Security review of all route handlers
```
```
Use #file:.github/copilot/code-reviewer.prompt.md — Find performance anti-patterns in the API layer
```

### Orchestrator (multi-agent)
```
Use #file:.github/copilot/orchestrator.prompt.md — Debug: intermittent 500 errors on checkout
```
```
Use #file:.github/copilot/orchestrator.prompt.md — Explain how this repo works, give me a guided tour
```
```
Use #file:.github/copilot/orchestrator.prompt.md — Plan a refactor to extract auth into a shared library
```

### Workflows
```
Follow @workspace workflows/debug-investigation.md — Memory leak in WebSocket handler
```
```
Follow @workspace workflows/trace-execution.md — What happens when a user places an order?
```
```
Follow @workspace workflows/refactor-planning.md — Extract config into a centralized service
```
```
Follow @workspace workflows/architecture-review.md — I just joined, explain this codebase
```
```
Follow @workspace workflows/migration-analysis.md — Migrate from Mongoose to Prisma
```
```
Follow @workspace workflows/security-audit.md — Audit the authentication flow
```
```
Follow @workspace workflows/performance-investigation.md — Dashboard API takes 5+ seconds
```

---

## Prompt Modifiers

Add these to any prompt to adjust behavior:

| Modifier | Effect |
|----------|--------|
| "Be thorough" | More depth, more files examined |
| "Be quick" | Shorter analysis, top results only |
| "Focus on {module}" | Limits search scope |
| "Include tests" | Also searches test files |
| "Cross-repo" | Explicitly searches all connected repos |
| "Show your reasoning" | Displays the investigation tree |
| "Just the answer" | Skips the tree, gives conclusion only |
| "Go deeper on {finding}" | Recurse further on a specific branch |

---

## Shorthand Syntax

If your Copilot Chat supports `#file:` references, you can use compact syntax:

```
#file:.github/copilot/deep-search.prompt.md Where is the auth middleware?
```

```
#file:.github/copilot/recursive-analyzer.prompt.md Why do webhook retries fail silently?
```

These are equivalent to the longer "Use the instructions in..." phrasing.
