# Workflow: Performance Investigation

Use this workflow to find and diagnose performance bottlenecks in a code path, feature, or service.

## Step-by-Step Protocol

### Step 1 — Identify the Slow Path
```
TASK: Find the code path that's slow

Search for:
- The route/handler/function reported as slow
- Timing/metrics code around it (if any)
- Performance-related comments or TODOs

Record:
- Entry point file:line
- What the user experiences (slow page load, timeout, etc.)
- Any existing metrics or timing data in the code
```

### Step 2 — Trace the Hot Path
```
TASK: Follow the execution path and identify I/O and computation

For each function in the call chain, classify:
- 🔵 CPU: Pure computation (transforms, loops, regex, JSON parse)
- 🟠 I/O-DB: Database queries (SELECT, INSERT, UPDATE)
- 🔴 I/O-NET: External API calls (fetch, HTTP client)
- 🟡 I/O-FS: File system operations (read, write)
- 🟣 I/O-QUEUE: Message queue publish/consume

Record the call chain with timing classifications:
```
handleRequest()           🔵 CPU (trivial)
├── validateInput()       🔵 CPU (trivial)
├── fetchUserProfile()    🟠 I/O-DB ← potential bottleneck
├── checkPermissions()    🟠 I/O-DB ← potential bottleneck
├── processOrder()        🔵 CPU
│   ├── calculateTax()    🔴 I/O-NET (external tax API) ← likely bottleneck
│   └── applyDiscount()   🟠 I/O-DB
├── saveOrder()           🟠 I/O-DB
└── sendConfirmation()    🔴 I/O-NET (email service)
```

### Step 3 — Analyze Database Queries
```
TASK: Find problematic query patterns

Search for:
- N+1 patterns (query in a loop)
- Missing WHERE clauses on large tables
- SELECT * instead of specific columns
- Queries without LIMIT on potentially large result sets
- Missing JOINs (separate queries that could be one)
- Transactions holding locks too long

For each query found:
- What table(s) does it hit?
- Is there an index for the WHERE/JOIN conditions?
- Is it called once or in a loop?
- How much data does it return?
```

### Step 4 — Analyze External Calls
```
TASK: Find slow or unnecessary external calls

Search for:
- External API calls on the hot path
- Are responses cached? (search for cache logic)
- Are calls parallelized or sequential?
- What's the timeout configuration?
- Is there a circuit breaker?
- Are there retries that compound latency?

Check:
- Can any external calls be moved to background processing?
- Can any external calls be batched?
- Can any external calls be eliminated with caching?
```

### Step 5 — Find Algorithmic Issues
```
TASK: Identify computation that doesn't scale

Search for:
- Nested loops (O(n²) or worse)
- Sorting or filtering large collections in memory
- Regex on large strings without anchoring
- JSON serialization of large objects
- String concatenation in loops
- Repeated computation that could be memoized

Check:
- How large is the input data? Does it grow over time?
- Are there pagination/limit mechanisms?
- Is there caching for expensive computations?
```

### Step 6 — Check for Concurrency Issues
```
TASK: Find parallelism opportunities and concurrency bottlenecks

Search for:
- Sequential awaits that could be Promise.all / asyncio.gather
- Global locks or mutexes on the hot path
- Connection pool exhaustion patterns
- Thread pool saturation
- Synchronous I/O blocking async code

Check:
- Are independent I/O operations parallelized?
- Are connection pools sized appropriately?
- Is there backpressure handling?
```

### Step 7 — Synthesize Findings
```
OUTPUT: Performance analysis report

## ⚡ Performance Investigation: {target}

### Hot Path
{call chain with timing classifications}

### Bottlenecks Found (ranked by estimated impact)

1. **{description}** — Estimated impact: HIGH
   - Location: `{file:line}`
   - Type: {N+1 query / sequential I/O / missing cache / O(n²) / etc.}
   - Evidence: {code snippet}
   - Fix: {recommendation}
   - Effort: {easy / medium / hard}

2. **{description}** — Estimated impact: MEDIUM
   ...

### Quick Wins (low effort, high impact)
- {fix 1}: {estimated improvement}
- {fix 2}: {estimated improvement}

### Deeper Fixes (higher effort)
- {fix 1}: {estimated improvement}

### Missing Observability
- {what metrics/tracing should be added to diagnose further}
```

## Example Prompt

```
Follow the workflow in @workspace workflows/performance-investigation.md for:

The /api/dashboard endpoint takes 4-8 seconds to respond. 
It aggregates data from orders, users, and analytics.
```
