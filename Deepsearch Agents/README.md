# Cody Deep Search Agents

Prompt-driven agents for Copilot Chat that replicate Sourcegraph Cody's deep search and recursive analysis. Pure prompts, no code — uses your existing Sourcegraph MCP tools directly.

## Quick Start

Copy `.github/` into your repo. Open Copilot Chat. Go:

```
#file:.github/copilot/deep-search.prompt.md Where is the payment processing logic?
```

```
#file:.github/copilot/debug.prompt.md Users get 500 errors on checkout with large discounts
```

```
#file:.github/copilot/explain.prompt.md How does the permission system decide who can edit a document?
```

Nothing to configure — your Sourcegraph MCP tools are used automatically.

---

## What's Included

### 15 Prompt Files (`.github/copilot/`)

Directly invocable in Copilot Chat via `#file:`:

**Core Agents:**
| Prompt | Purpose |
|--------|---------|
| `orchestrator.prompt.md` | Routes to right agent(s), multi-agent synthesis |
| `deep-search.prompt.md` | 3-pass semantic code search |
| `recursive-analyzer.prompt.md` | Investigation trees — L0 through L5 depth |
| `context-engine.prompt.md` | Dependency graphs, call chains, architecture |
| `impact-assessor.prompt.md` | Change blast radius across codebase |
| `code-reviewer.prompt.md` | 5-pass review + codebase-wide pattern scanning |

**Workflow Agents:**
| Prompt | Purpose |
|--------|---------|
| `debug.prompt.md` | Root cause analysis for bugs/errors |
| `trace.prompt.md` | End-to-end execution flow tracing |
| `explain.prompt.md` | Understand how a feature/module works |
| `refactor.prompt.md` | Safe refactor planning with impact analysis |
| `architecture.prompt.md` | Codebase architecture review and tour |
| `migration.prompt.md` | Library/framework migration planning |
| `security.prompt.md` | Security vulnerability audit |
| `performance.prompt.md` | Performance bottleneck investigation |
| `dead-code.prompt.md` | Dead code and tech debt scan |

### 8 Sub-Agents (`agents/sub-agents/`)

Composable helpers you reference within any investigation:

| Sub-Agent | Purpose |
|-----------|---------|
| Symbol Resolver | Resolve any symbol → definition, signature, docs, usage |
| Test Coverage Scanner | Find tests, assess quality, identify gaps |
| Change History Tracer | Git history — who, when, why, frequency |
| Error Path Tracer | Trace throw → catch → propagate → user error |
| Cross-Repo Linker | Shared contracts, API boundaries, version alignment |
| Librarian | Research conventions and patterns across codebase |
| API Surface Mapper | Map every endpoint with auth, validation, handler |
| Config Mapper | Map all env vars, config values, feature flags |

### 8 Extended Workflows (`workflows/`)

Step-by-step playbooks with deeper instructions (reference via `@workspace`).

### 3 Guides (`guides/`)

Setup, agent composition patterns, and a quick-reference cheat sheet.

---

## Project Structure

```
.github/
  copilot-instructions.md           ← Auto-loaded by Copilot Chat
  copilot/
    orchestrator.prompt.md           ← 6 core agents
    deep-search.prompt.md
    recursive-analyzer.prompt.md
    context-engine.prompt.md
    impact-assessor.prompt.md
    code-reviewer.prompt.md
    debug.prompt.md                  ← 9 workflow agents
    trace.prompt.md
    explain.prompt.md
    refactor.prompt.md
    architecture.prompt.md
    migration.prompt.md
    security.prompt.md
    performance.prompt.md
    dead-code.prompt.md

agents/
  sub-agents/                        ← 8 composable sub-agents

workflows/                           ← 8 extended step-by-step workflows

guides/
  setup.md
  agent-composition.md
  quick-reference.md
```

---

## Configuration (Optional)

Edit CONFIG in `.github/copilot-instructions.md`:

| Setting | Default |
|---------|---------|
| `MAX_RECURSION_DEPTH` | 5 |
| `MAX_FILES_PER_SEARCH` | 30 |
| `ANALYSIS_STYLE` | thorough |
| `SHOW_REASONING` | true |
