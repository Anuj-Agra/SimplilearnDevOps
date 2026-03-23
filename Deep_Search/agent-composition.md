# Agent Composition Guide

How to combine agents for complex investigations. Each agent is a self-contained prompt that can be referenced individually or chained together.

---

## Composition Methods

### Method 1 — Let the Orchestrator Route

The simplest approach. Ask `@cody` your question and it will invoke the right agents:

```
Use the instructions in @workspace .github/copilot/orchestrator.prompt.md

Why are users seeing stale data after updating their profile?
```

The orchestrator will:
1. Route to Deep Search to find profile update code
2. Route to Recursive Analyzer to trace the cache/data flow
3. Route to Impact Assessor if it suspects a caching issue
4. Synthesize a root cause and fix recommendation

### Method 2 — Explicit Agent Selection

Call a specific agent directly when you know what you need:

```
Use the instructions in @workspace .github/copilot/deep-search.prompt.md

Find all places where we serialize user data for API responses
```

```
Use the instructions in @workspace .github/copilot/recursive-analyzer.prompt.md

Why does the payment webhook sometimes process the same event twice?
```

### Method 3 — Sequential Chaining (Multi-Turn)

Chain agents across multiple messages in the same chat session. Each agent builds on the previous one's output:

**Turn 1 — Search:**
```
Use the instructions in @workspace .github/copilot/deep-search.prompt.md

Find the notification service and all its event handlers
```

**Turn 2 — Analyze (building on search results):**
```
Now use the instructions in @workspace .github/copilot/recursive-analyzer.prompt.md

Based on what we found, trace how a new-order event flows through the notification 
service. Why would some notifications be delayed by 30+ seconds?
```

**Turn 3 — Impact (building on analysis):**
```
Now use the instructions in @workspace .github/copilot/impact-assessor.prompt.md

If I refactor the notification queue to use batching (processing every 5 seconds 
instead of per-event), what would be affected?
```

### Method 4 — Workflow Templates

Use pre-built multi-step workflows that internally combine multiple agent behaviors:

```
Follow the workflow in @workspace workflows/debug-investigation.md for:

Intermittent 502 errors on the /api/checkout endpoint during peak hours
```

The workflow template guides the model through a structured sequence of search → trace → root cause → blast radius → fix recommendation.

### Method 5 — Sub-Agent Composition

Reference sub-agents within a larger investigation to get focused analysis on a specific aspect:

```
Use the instructions in @workspace .github/copilot/recursive-analyzer.prompt.md

Investigate why order totals sometimes calculate incorrectly.

For each function you find in the calculation chain, also apply the 
sub-agent in @workspace agents/sub-agents/error-path-tracer.md to 
check how errors in that function are handled.
```

---

## Composition Patterns by Use Case

### "I have a bug"
```
Turn 1: @workspace .github/copilot/orchestrator.prompt.md + describe the bug
   OR
Turn 1: @workspace workflows/debug-investigation.md + describe the bug
```

### "I want to understand this codebase"
```
Turn 1: @workspace workflows/architecture-review.md + what you want to understand
   Then for specific areas:
Turn 2: @workspace .github/copilot/context-engine.prompt.md + specific module
Turn 3: @workspace .github/copilot/recursive-analyzer.prompt.md + specific flow
```

### "I want to make a change safely"
```
Turn 1: @workspace .github/copilot/impact-assessor.prompt.md + describe the change
Turn 2: @workspace .github/copilot/deep-search.prompt.md + find tests that need updating
Turn 3: @workspace workflows/refactor-planning.md (if change is large)
```

### "I want a security review"
```
Turn 1: @workspace workflows/security-audit.md + scope of audit
   Then for specific findings:
Turn 2: @workspace .github/copilot/recursive-analyzer.prompt.md + trace specific vulnerability
```

### "I want a code review"
```
Turn 1: @workspace .github/copilot/code-reviewer.prompt.md + file or module to review
   Then for systemic issues found:
Turn 2: @workspace .github/copilot/deep-search.prompt.md + search for pattern across codebase
Turn 3: @workspace .github/copilot/impact-assessor.prompt.md + assess fix impact
```

### "I need to migrate a library"
```
Turn 1: @workspace workflows/migration-analysis.md + what you're migrating
```

### "Why is this slow?"
```
Turn 1: @workspace workflows/performance-investigation.md + what's slow
```

---

## Tips for Effective Composition

1. **Start broad, then narrow.** Use the orchestrator or a workflow first. Then drill into specifics with individual agents.

2. **Build on context.** Each turn in the same chat session carries forward context. The second agent can reference what the first found.

3. **Be specific about scope.** "Analyze the auth module" is better than "analyze the codebase." Narrow scope = better results.

4. **Reference findings.** In Turn 2, say "Based on the `validateToken()` function you found in the previous analysis..." to keep the model focused.

5. **Use sub-agents for depth.** When the main agent finds something interesting, invoke a sub-agent for a focused deep-dive on that specific aspect.

6. **Break large tasks into workflows.** If your question has 5+ parts, use a workflow template instead of trying to get it all in one prompt.

7. **Iterate, don't restart.** If an agent's first pass misses something, ask it to dig deeper in the same chat rather than starting a new one. The accumulated context helps.

---

## Creating Custom Workflows

You can create your own workflow templates. Follow this structure:

```markdown
# Workflow: {Name}

Use this workflow when {trigger description}.

## Step-by-Step Protocol

### Step 1 — {Name}
  TASK: {what to do}
  Search for: {what to search}
  Record: {what to capture}

### Step 2 — {Name}
  ...

### Step N — Synthesize
  OUTPUT: {how to present results}

## Example Prompt
  Follow the workflow in @workspace workflows/{name}.md for:
  {example question}
```

Save it in the `workflows/` directory and reference it with `@workspace workflows/your-workflow.md`.

---

## Creating Custom Sub-Agents

For focused, reusable analysis tasks:

```markdown
# Sub-Agent: {Name}

## When to invoke
{describe the trigger}

## Protocol
{step-by-step instructions}

## Output
{expected output format}
```

Save in `agents/sub-agents/` and reference in your prompts.
