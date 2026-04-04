# AGENTS.md

Prompt-driven deep search agents for Copilot Chat. Uses your existing Sourcegraph MCP directly — no setup.

## Core Agents

| Invoke | Does |
|--------|------|
| `#file:.github/copilot/orchestrator.prompt.md` | Routes to right agent(s), synthesizes |
| `#file:.github/copilot/deep-search.prompt.md` | 3-pass semantic code search |
| `#file:.github/copilot/recursive-analyzer.prompt.md` | Investigation trees (L0→L5) |
| `#file:.github/copilot/context-engine.prompt.md` | Dependency graphs, architecture maps |
| `#file:.github/copilot/impact-assessor.prompt.md` | Change blast radius |
| `#file:.github/copilot/code-reviewer.prompt.md` | 5-pass review + pattern scanning |

## Workflow Agents

| Invoke | Does |
|--------|------|
| `#file:.github/copilot/debug.prompt.md` | Root cause analysis |
| `#file:.github/copilot/trace.prompt.md` | End-to-end flow tracing |
| `#file:.github/copilot/explain.prompt.md` | Feature/module understanding |
| `#file:.github/copilot/refactor.prompt.md` | Safe refactor planning |
| `#file:.github/copilot/architecture.prompt.md` | Codebase architecture review |
| `#file:.github/copilot/migration.prompt.md` | Library/framework migration |
| `#file:.github/copilot/security.prompt.md` | Security vulnerability scan |
| `#file:.github/copilot/performance.prompt.md` | Performance bottleneck hunting |
| `#file:.github/copilot/dead-code.prompt.md` | Dead code and tech debt scan |

## Extended Workflows (via @workspace)

```
Follow @workspace workflows/debug-investigation.md for: {bug}
Follow @workspace workflows/trace-execution.md for: {flow}
Follow @workspace workflows/refactor-planning.md for: {refactor}
Follow @workspace workflows/architecture-review.md for: {understanding}
Follow @workspace workflows/migration-analysis.md for: {migration}
Follow @workspace workflows/security-audit.md for: {audit}
Follow @workspace workflows/performance-investigation.md for: {perf}
Follow @workspace workflows/dead-code-scan.md for: {cleanup}
```

## Sub-Agents (composable via @workspace)

Reference within any prompt for focused analysis:

| Sub-Agent | File |
|-----------|------|
| Symbol Resolver | `agents/sub-agents/symbol-resolver.md` |
| Test Coverage Scanner | `agents/sub-agents/test-coverage-scanner.md` |
| Change History Tracer | `agents/sub-agents/change-history-tracer.md` |
| Error Path Tracer | `agents/sub-agents/error-path-tracer.md` |
| Cross-Repo Linker | `agents/sub-agents/cross-repo-linker.md` |
| Librarian | `agents/sub-agents/librarian.md` |
| API Surface Mapper | `agents/sub-agents/api-surface-mapper.md` |
| Config & Env Mapper | `agents/sub-agents/config-mapper.md` |
