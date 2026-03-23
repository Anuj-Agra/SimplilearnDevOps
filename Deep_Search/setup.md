# Setup Guide

## Prerequisites

1. **VS Code** with GitHub Copilot Chat extension
2. **Copilot Chat** with access to any model (GPT-4o, Claude, etc.)
3. **Sourcegraph MCP** server connected for code search

---

## Step 1 — Install the Agent Files

Copy the `cody-agents/` folder into your repository root:

```
your-repo/
├── .github/
│   ├── copilot-instructions.md    ← Auto-loaded by Copilot Chat
│   └── copilot/
│       ├── orchestrator.prompt.md
│       ├── deep-search.prompt.md
│       ├── recursive-analyzer.prompt.md
│       ├── context-engine.prompt.md
│       ├── impact-assessor.prompt.md
│       └── code-reviewer.prompt.md
├── .vscode/
│   └── settings.json              ← Workspace settings
├── agents/                        ← Full agent definitions (reference)
├── workflows/                     ← Step-by-step workflow templates
├── examples/                      ← Example conversations
├── AGENTS.md                      ← Quick reference
└── ... your code ...
```

The key file is `.github/copilot-instructions.md` — Copilot Chat reads this automatically for every conversation in the workspace.

---

## Step 2 — Connect Sourcegraph MCP

The agents rely on Sourcegraph MCP for code search. Configure it in your VS Code MCP settings.

### Option A: Sourcegraph Cloud

In your VS Code `settings.json` (user-level) or your MCP configuration file:

```json
{
  "mcpServers": {
    "sourcegraph": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-sourcegraph"],
      "env": {
        "SOURCEGRAPH_ACCESS_TOKEN": "your-token-here",
        "SOURCEGRAPH_ENDPOINT": "https://sourcegraph.com"
      }
    }
  }
}
```

### Option B: Sourcegraph Self-Hosted

```json
{
  "mcpServers": {
    "sourcegraph": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-sourcegraph"],
      "env": {
        "SOURCEGRAPH_ACCESS_TOKEN": "your-token-here",
        "SOURCEGRAPH_ENDPOINT": "https://sourcegraph.your-company.com"
      }
    }
  }
}
```

### Option C: Sourcegraph Cody Gateway

If you use Cody's gateway, configure the MCP server to use it as the backend. Refer to Sourcegraph's MCP documentation for your specific setup.

### Verify Connection

In Copilot Chat, test the connection:
```
Search for "main" in my codebase using Sourcegraph
```

If it returns results, MCP is connected.

---

## Step 3 — Configure Agent Behavior

Edit the CONFIG block at the top of `.github/copilot-instructions.md`:

```markdown
<!-- CONFIG -->
<!--
MAX_RECURSION_DEPTH: 5        # How deep recursive analysis goes (1-10)
MAX_FILES_PER_SEARCH: 30      # Files to examine per search pass
ANALYSIS_STYLE: thorough       # thorough | balanced | quick
MULTI_REPO: true               # Enable cross-repo analysis
SHOW_REASONING: true           # Show investigation tree (set false for concise answers)
-->
```

| Setting | Options | Recommendation |
|---------|---------|----------------|
| MAX_RECURSION_DEPTH | 1-10 | 5 for most codebases, 3 for quick iterations, 7-10 for deep investigations |
| MAX_FILES_PER_SEARCH | 10-100 | 30 balances thoroughness and speed |
| ANALYSIS_STYLE | thorough / balanced / quick | `thorough` for debugging, `quick` for simple lookups |
| MULTI_REPO | true / false | `true` if workspace has multiple repos |
| SHOW_REASONING | true / false | `true` to see the investigation tree, `false` for just the answer |

---

## Step 4 — Multi-Repo Setup

For multi-repo analysis, ensure all repos are accessible:

### VS Code Multi-Root Workspace

Create a `.code-workspace` file:

```json
{
  "folders": [
    { "path": "../frontend-repo" },
    { "path": "../backend-repo" },
    { "path": "../shared-libs" },
    { "path": "../worker-repo" }
  ],
  "settings": {
    "codyAgents.multiRepo": true
  }
}
```

### Sourcegraph Multi-Repo

Ensure all repos are indexed in your Sourcegraph instance. The MCP server will search across all indexed repos automatically.

---

## Step 5 — Verify Setup

Run these test prompts in Copilot Chat to verify everything works:

**Test 1 — Basic search:**
```
Search for all API route definitions in this workspace
```
Expected: Returns files with route definitions, with file paths and code snippets.

**Test 2 — Recursive analysis:**
```
How does authentication work in this codebase? Trace it from the middleware to the token validation.
```
Expected: Shows an investigation tree with multiple depth levels.

**Test 3 — Workflow reference:**
```
Follow the workflow in @workspace workflows/architecture-review.md to review this codebase
```
Expected: Executes the 6-step architecture review workflow.

---

## Troubleshooting

**Copilot Chat doesn't follow the agent instructions:**
- Verify `.github/copilot-instructions.md` exists at the repo root
- Restart VS Code after adding the file
- Check that `chat.promptFiles` is enabled in VS Code settings

**Sourcegraph MCP returns no results:**
- Check your access token is valid
- Verify the endpoint URL
- Ensure repos are indexed in Sourcegraph
- Test with a simple search directly

**Agent goes off-topic or fabricates code:**
- This usually means MCP isn't connected — the agent falls back to guessing
- Verify MCP connection, then retry

**Agent stops recursing too early:**
- Increase `MAX_RECURSION_DEPTH` in the CONFIG block
- Use explicit prompt: "Go deeper — investigate why {specific finding}"

**Too much output / too slow:**
- Set `ANALYSIS_STYLE: quick` for simpler questions
- Reduce `MAX_FILES_PER_SEARCH` to 15-20
- Use targeted prompts: specify which files or modules to focus on
