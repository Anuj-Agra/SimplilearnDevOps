---
name: gap-detector
description: >
  Detect gaps, missing scenarios, and production risks across four dimensions: functional
  flow gaps (incomplete user journeys), technical flow gaps (broken or missing integration
  contracts), scenario gaps (edge cases that will crash production), and performance gaps
  (bottlenecks and scalability risks). Use this skill whenever a user wants to find
  problems BEFORE they hit production. Triggers include: 'find gaps', 'what's missing',
  'what will break', 'production risks', 'edge cases', 'missing scenarios', 'test gaps',
  'what could go wrong', 'validate requirements', 'review for completeness', 'what are
  we missing', 'performance risks', 'where are the bottlenecks', 'what breaks under
  load', 'scenario analysis', 'risk review', 'gap analysis'. Can work from an FRD doc,
  a repo-graph.json, a codebase, or all three together. Produces a prioritised list of
  gaps with severity, impact, and recommended fixes. Should always be run before sign-off
  on any FRD, before any major release, or when a module has changed significantly.
---

# Gap Detector

Find what's missing, broken, or dangerous — before production does.

Four detection engines. One prioritised risk report.

---

## Detection Mode Routing

Run ALL four engines by default. If the user specifies a focus:

| User phrase | Engine(s) to run |
|---|---|
| "functional gaps", "missing user journeys" | → Engine 1: Functional |
| "technical gaps", "integration issues", "broken contracts" | → Engine 2: Technical |
| "production scenarios", "edge cases", "what will crash" | → Engine 3: Scenario |
| "performance", "load", "bottlenecks", "scalability" | → Engine 4: Performance |
| No specific focus | → Run all four, combine into one report |

---

## Pre-work: Load All Available Context

```bash
# Graph (if available)
ls repo-graph.json && python3 scripts/project_graph.py --graph repo-graph.json --mode index

# FRD or spec doc
ls *.docx *.md | grep -i "frd\|spec\|requirement" | head -5

# Codebase paths
ls <java_path>/src <angular_path>/src 2>/dev/null
```

Load in this priority: graph projections first (cheap), then FRD, then targeted code reads.

---

## ENGINE 1: Functional Gap Detector

Read `references/functional-gaps.md` for the full detection checklist.

**Goal**: Find incomplete user journeys — places where the user gets stuck,
confused, or can't accomplish what they came to do.

### Detection Approach

**From FRD**: Cross-check every use case against this completeness matrix:
- Does every use case have: a start condition, all steps, ALL alternate flows, a postcondition?
- Does every user role appear in at least one use case?
- Are there user roles that can only read but never create? (Is that intentional?)
- Does every data entity have a: create story, read story, edit story, delete/archive story?
- Does every status transition have: a way to enter AND a way to exit?

**From graph + code**: Find features that exist in code but are missing from the FRD:
```bash
# Features in code not in FRD = undocumented features = gap
grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping" \
  <java_path> --include="*.java" | grep -v "test\|Test" | wc -l
# Compare count vs FR count in FRD
```

**Outputs**: List of functional gaps, each with:
- Gap ID: FG-[###]
- Gap type: Missing use case / Incomplete flow / Undocumented feature / Orphaned role
- Severity: 🔴 Critical / 🟠 High / 🟡 Medium
- Description: What is missing
- Impact: What user problem this creates
- Fix: What to add

---

## ENGINE 2: Technical Gap Detector

Read `references/technical-gaps.md` for the full detection checklist.

**Goal**: Find broken integration contracts, missing error handling, and architectural
risks that will cause runtime failures.

### Detection Approach

**From graph**:
```bash
python3 scripts/project_graph.py --graph repo-graph.json --mode cycles
python3 scripts/project_graph.py --graph repo-graph.json --mode dead
python3 scripts/project_graph.py --graph repo-graph.json --mode longest-path
python3 scripts/project_graph.py --graph repo-graph.json --mode critical --top 10
```

Flag:
- Circular dependencies → deadlock risk, initialisation order bugs
- Dead modules referenced in FRD → requirements written for code that doesn't exist
- Long dependency chains (>5 hops) → cascading failure risk
- High fan-in modules with no error handling → single point of failure

**From code**:
```bash
# Missing null checks on external calls
grep -rn "\.get\(\|\.findById\|Optional" <java_path> --include="*.java" \
  | grep -v "isPresent\|ifPresent\|orElse\|orElseThrow" | head -30

# Unhandled exceptions
grep -rn "catch.*Exception\|catch.*Error" <java_path> --include="*.java" \
  | grep -v "log\|throw\|return\|rollback" | head -30

# Missing transaction boundaries
grep -rn "@Service" <java_path> --include="*.java" -l \
  | xargs grep -L "@Transactional" | head -20

# Angular: uncaught HTTP errors
grep -rn "\.subscribe\(" <angular_path> --include="*.ts" \
  | grep -v "error\|catch\|catchError" | head -30
```

**Outputs**: List of technical gaps, each with:
- Gap ID: TG-[###]
- Gap type: Circular dep / Dead code / Missing error handling / Unhandled exception / Missing transaction
- Severity: 🔴 Critical / 🟠 High / 🟡 Medium
- Description: What is missing/broken
- Impact: What runtime failure this causes
- Fix: What to add/change

---

## ENGINE 3: Scenario Gap Detector

Read `references/scenario-gaps.md` for the full detection checklist.

**Goal**: Find the specific scenarios that WILL break production — the edge cases
developers forgot and testers didn't think to check.

### The "Break Production" Checklist

For every significant feature, ask all of these:

**Concurrency scenarios**
- What if two users submit the same record at the exact same time?
- What if a user double-clicks the submit button?
- What if a background job runs while a user is editing?

**Data boundary scenarios**
- What happens with the minimum allowed input? (e.g. quantity = 0)
- What happens at exactly the boundary? (e.g. exactly $10,000 — is that ≥ or >?)
- What happens with the maximum allowed input?
- What happens with Unicode, special characters, SQL-injection-like strings in text fields?
- What happens with very long strings at the exact character limit?
- What if a decimal is entered where a whole number is expected?

**State / lifecycle scenarios**
- Can a user access a record that has been deleted by someone else?
- Can a record be edited while it is in a status that shouldn't allow editing?
- What happens if an approval is submitted after the underlying record changed?
- What if a user bookmarks a URL for a record they no longer have access to?

**Session / auth scenarios**
- What happens if a user's session expires while they are mid-form?
- What if a user's role changes while they are logged in?
- What if a user is deleted while they are logged in?

**Integration / network scenarios**
- What if the downstream system is unavailable?
- What if the downstream call times out after 30 seconds?
- What if the downstream call succeeds but returns partial data?

**Data integrity scenarios**
- What if a required lookup value (e.g. a product in a dropdown) is deleted while the user is mid-order?
- What if a foreign key reference no longer exists?
- What if a bulk import contains one invalid record — does the whole import fail or just that record?

**From graph**: Flag modules with circular deps as likely concurrency/deadlock candidates.
Flag high fan-in modules as likely failure-propagation points.

**Outputs**: List of missing scenarios, each with:
- Gap ID: SG-[###]
- Scenario: [Exact scenario description]
- Severity: 🔴 Production-breaking / 🟠 Data-corrupting / 🟡 User-confusing
- Likelihood: High / Medium / Low
- Affected module: [module name]
- What should happen: [expected correct behaviour]
- Current behaviour: [what the code does, or "Unknown — not handled"]
- Test case to add: [TC-XXX scenario in plain English]

---

## ENGINE 4: Performance Gap Detector

Read `references/performance-gaps.md` for the full detection checklist.

**Goal**: Find the performance and scalability risks that will cause production
degradation under real load.

### Detection Approach

**From graph**:
```bash
# Chatty services (high fan-out = many synchronous calls per request)
python3 scripts/project_graph.py --graph repo-graph.json --mode critical --top 10
python3 scripts/project_graph.py --graph repo-graph.json --mode longest-path

# Entry points = where load originates
python3 scripts/project_graph.py --graph repo-graph.json --mode entry-points
```

**From code**:
```bash
# N+1 query patterns (loop containing a DB/service call)
grep -rn -A5 "for.*:\|\.forEach\|\.stream()" <java_path>/src --include="*.java" \
  | grep -B3 "repository\.\|findBy\|\.get\(\|restTemplate\." | head -40

# Missing pagination on list queries
grep -rn "findAll()\b\|getAll\b\|\.getAll()" <java_path> --include="*.java" | head -20

# Missing cache on stable data
grep -rn "findById\|findByCode\|findByName\|getReferenceData" \
  <java_path> --include="*.java" -l \
  | xargs grep -L "@Cacheable\|CacheManager" 2>/dev/null | head -15

# Synchronous calls that could be async
grep -rn "restTemplate\.\|feign\.\|HttpClient\.\|WebClient\." \
  <java_path> --include="*.java" | grep -v "Mono\|Flux\|CompletableFuture\|async" | head -30

# Blocking calls in reactive chain
grep -rn "\.block()\|\.blockFirst()\|\.blockLast()" \
  <java_path> --include="*.java" | head -20

# Large data loads without streaming
grep -rn "List<.*>\|ArrayList\|Collection<" <java_path> --include="*.java" \
  | grep -v "pageable\|page\|Pageable\|slice" | head -20
```

**From FRD**: For every feature that operates on "all records" or "a list":
- Is a maximum page size defined?
- Is there a search/filter to reduce the result set?
- What happens when there are 100,000 records?

**Outputs**: List of performance gaps, each with:
- Gap ID: PG-[###]
- Pattern: N+1 / Missing pagination / No caching / Chatty service / Blocking call / No timeout
- Severity: 🔴 Critical (will fail at scale) / 🟠 High / 🟡 Medium
- Module: [where the issue is]
- Evidence: [code pattern or graph metric that identified it]
- Impact: [what degrades — response time / memory / throughput]
- Fix: [specific recommendation]

---

## Final Output: Combined Gap Report

Consolidate all four engines into one prioritised report:

```
GAP ANALYSIS REPORT: [System/Module Name]
Generated: [date]
Scope: [what was analysed]

EXECUTIVE SUMMARY
  Total gaps found: [N]
  🔴 Critical: [N]  🟠 High: [N]  🟡 Medium: [N]
  Production-risk scenarios: [N]
  Performance hotspots: [N]

TOP 5 RISKS (things most likely to break production):
  1. [Gap] — [one-line severity + fix]
  ...

FUNCTIONAL GAPS ([N])
  [FG-001 through FG-N]

TECHNICAL GAPS ([N])
  [TG-001 through TG-N]

SCENARIO GAPS ([N]) — production-breaking edge cases
  [SG-001 through SG-N]

PERFORMANCE GAPS ([N])
  [PG-001 through PG-N]

RECOMMENDED ACTIONS (prioritised by risk):
  Phase 1 — Before next release (Critical + High):
    [List]
  Phase 2 — Next sprint (Medium):
    [List]
  Phase 3 — Backlog (Low):
    [List]
```
