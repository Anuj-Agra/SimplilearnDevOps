# Cody Deep Search Agents

A set of **prompt-driven, model-agnostic agents** for Copilot Chat that replicate Sourcegraph Cody's deep search and recursive analysis capabilities. No code, no extensions — pure prompts.

## How It Works

Drop this folder into your repo. Copilot Chat auto-loads the instructions and gains deep search, recursive analysis, dependency tracing, impact assessment, and multi-repo awareness — all powered by your existing Sourcegraph MCP connection.

### Prerequisites

- Copilot Chat (with any models you prefer)
- Sourcegraph MCP server connected (for code search)
- VS Code with `chat.promptFiles` enabled

---

## Quick Start

### 1. Copy into your repo
```bash
cp -r cody-agents/.github your-repo/.github
cp -r cody-agents/.vscode your-repo/.vscode
cp -r cody-agents/agents your-repo/agents
cp -r cody-agents/workflows your-repo/workflows
cp -r cody-agents/guides your-repo/guides
```

### 2. Start using in Copilot Chat

**Search for code:**
```
#file:.github/copilot/deep-search.prompt.md Where is the payment processing logic?
```

**Deep investigation:**
```
#file:.github/copilot/recursive-analyzer.prompt.md Why are webhook deliveries failing silently?
```

**Full orchestration:**
```
#file:.github/copilot/orchestrator.prompt.md Debug: users see stale data after profile update
```

**Run a workflow:**
```
Follow @workspace workflows/debug-investigation.md for:
Intermittent 500 errors on the checkout page
```

See `guides/quick-reference.md` for the full prompt cheat sheet.

---

## Agents

| Agent | Prompt File | What It Does |
|-------|-------------|-------------|
| **Orchestrator** | `orchestrator.prompt.md` | Routes complex questions to the right agent(s), synthesizes results |
| **Deep Search** | `deep-search.prompt.md` | 3-pass semantic search via Sourcegraph MCP |
| **Recursive Analyzer** | `recursive-analyzer.prompt.md` | Breaks questions into investigation trees (L0→L5) |
| **Context Engine** | `context-engine.prompt.md` | Builds dependency graphs, call chains, architecture maps |
| **Impact Assessor** | `impact-assessor.prompt.md` | Traces change blast radius across all repos |
| **Code Reviewer** | `code-reviewer.prompt.md` | 5-pass review with codebase-wide pattern scanning |

### Sub-Agents (composable helpers)

| Sub-Agent | What It Does |
|-----------|-------------|
| Symbol Resolver | Resolves a symbol to definition, signature, docs, usage |
| Test Coverage Scanner | Finds all tests for a piece of code, assesses coverage quality |
| Change History Tracer | Investigates git history — who, when, why code was changed |
| Error Path Tracer | Traces all error/exception paths, finds swallowed errors |
| Cross-Repo Linker | Finds connections between repos — shared contracts, API boundaries |

---

## Workflows

Step-by-step playbooks for structured multi-agent analysis:

| Workflow | When to Use |
|----------|------------|
| `debug-investigation.md` | Finding the root cause of a bug |
| `trace-execution.md` | Understanding an end-to-end flow |
| `refactor-planning.md` | Planning a safe refactor with impact analysis |
| `architecture-review.md` | Understanding a codebase you're new to |
| `migration-analysis.md` | Planning a library/framework migration |
| `security-audit.md` | Comprehensive security review |
| `performance-investigation.md` | Finding performance bottlenecks |
| `dead-code-scan.md` | Finding unused code and tech debt |

---

## Project Structure

```
.github/
  copilot-instructions.md          ← Main brain (auto-loaded by Copilot)
  copilot/
    orchestrator.prompt.md         ← Multi-agent orchestrator
    deep-search.prompt.md          ← Semantic code search
    recursive-analyzer.prompt.md   ← Recursive investigation trees
    context-engine.prompt.md       ← Dependency/architecture graphs
    impact-assessor.prompt.md      ← Change blast radius analysis
    code-reviewer.prompt.md        ← Multi-pass code review

.vscode/
  settings.json                    ← Optimized workspace settings

agents/
  orchestrator.md                  ← Full orchestrator reference
  deep-search.md                   ← Full search agent reference
  recursive-analyzer.md            ← Full recursive analysis reference
  context-engine.md                ← Full context engine reference
  impact-assessor.md               ← Full impact assessment reference
  code-reviewer.md                 ← Full code review reference
  sub-agents/
    symbol-resolver.md             ← Resolve any symbol to full context
    test-coverage-scanner.md       ← Find and assess test coverage
    change-history-tracer.md       ← Git history investigation
    error-path-tracer.md           ← Error propagation analysis
    cross-repo-linker.md           ← Cross-repository connections

workflows/
  debug-investigation.md           ← 6-step bug root cause analysis
  trace-execution.md               ← End-to-end flow tracing
  refactor-planning.md             ← Safe refactor planning
  architecture-review.md           ← Codebase architecture tour
  migration-analysis.md            ← Library/framework migration
  security-audit.md                ← Security vulnerability scan
  performance-investigation.md     ← Performance bottleneck hunting
  dead-code-scan.md                ← Dead code and tech debt scan

guides/
  setup.md                         ← MCP setup and configuration guide
  agent-composition.md             ← How to chain and combine agents
  quick-reference.md               ← Prompt cheat sheet

examples/
  example-deep-search.md           ← Example: deep search session
  example-recursive.md             ← Example: recursive analysis session
  example-impact.md                ← Example: impact assessment session
```

---

## Configuration

Edit the CONFIG block at the top of `.github/copilot-instructions.md`:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_RECURSION_DEPTH` | 5 | How deep recursive analysis goes |
| `MAX_FILES_PER_SEARCH` | 30 | Files to examine per search pass |
| `ANALYSIS_STYLE` | thorough | `thorough` / `balanced` / `quick` |
| `MULTI_REPO` | true | Enable cross-repo analysis |
| `SHOW_REASONING` | true | Show investigation tree in output |

---

## Guides

- **[Setup Guide](guides/setup.md)** — MCP configuration, workspace setup, verification
- **[Agent Composition](guides/agent-composition.md)** — How to chain agents, composition patterns, creating custom workflows
- **[Quick Reference](guides/quick-reference.md)** — Copy-paste prompt cheat sheet

---

## How It Compares to Sourcegraph Cody/Amp

| Capability | Sourcegraph Cody | Amp Deep Mode | This Project |
|-----------|------------------|---------------|--------------|
| Codebase search | Built-in | Built-in | Via Sourcegraph MCP |
| Chat interface | IDE extension | CLI + IDE | Copilot Chat |
| Recursive analysis | Single-pass | Sub-agents | Investigation trees (L0-L5) |
| Multi-repo | Enterprise | Via MCP | Via MCP |
| Model agnostic | Partial | Partial | Fully — any model |
| Customizable agents | No | Via skills | Edit any .md file |
| Workflow templates | No | No | 8 built-in |
| No code required | Extension | CLI tool | Pure prompts |
