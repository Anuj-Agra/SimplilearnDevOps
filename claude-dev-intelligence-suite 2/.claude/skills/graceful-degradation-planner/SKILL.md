---
name: graceful-degradation-planner
description: >
  For each API endpoint, design an explicit degradation strategy for when downstream
  dependencies fail. Use when asked: 'graceful degradation', 'fallback strategy',
  'what if dependency goes down', 'stale cache fallback', 'partial response',
  'degraded mode', 'service unavailable handling', 'fallback design', 'resilience
  planning', 'what happens when X is down'. Documents degradation decisions as
  explicit non-functional requirements feeding into FRD and test suites.
---
# Graceful Degradation Planner

Design explicit fallback behaviour for every API endpoint and dependency.

## Step 1 — Map Dependencies per Endpoint
```bash
# From graph: what each entry-point module depends on
python3 scripts/project_graph.py --graph repo-graph.json --mode entry-points
python3 scripts/project_graph.py --graph repo-graph.json --mode fan-out --node <service>

# From code: actual outbound calls per controller method
grep -rn "@GetMapping\|@PostMapping" <java_path> --include="*.java" -A20 | \
  grep "restTemplate\.\|webClient\.\|service\.\|repository\." | head -40
```

## Step 2 — Classify Each Dependency

| Dependency type | Suggested degradation strategy |
|---|---|
| Read-only reference data | Return stale cache (with `Cache-Control: stale-while-revalidate`) |
| Read-only user data | Return last-known value + staleness indicator |
| Write operations (create/update) | Queue the operation, return 202 Accepted |
| Payment/financial | Fail safe — return explicit error, do NOT guess |
| Search/filtering | Return empty results with "Search temporarily unavailable" |
| Notification service | Continue without notification, log for retry |
| Auth service | Use local token validation if possible, else 503 |

## Step 3 — Generate Degradation Specification

For each endpoint:

```
ENDPOINT: [Plain English name — e.g. "Get Customer Profile"]
Depends on: [list of downstream services]

DEPENDENCY FAILURE SCENARIOS:

If [Customer Data Service] is unavailable:
  Strategy: Return cached customer record (max staleness: 5 minutes)
  User sees: Normal response (transparent if within staleness window)
  User sees: "Profile data may be slightly out of date" banner if stale > 5 min
  Fallback code pattern: .onErrorReturn(customerCache.get(id))

If [Auth Service] is unavailable:
  Strategy: Validate JWT locally using cached public key
  Fails after: Public key expires (rotate every 24h) → return 503
  User sees: Normal experience for up to 24 hours

If [Pricing Service] is unavailable:
  Strategy: Use last-known prices from local cache
  Degraded mode indicator: Price shown with "(prices may vary)" note
  Maximum staleness: 15 minutes

WRITE ENDPOINT: [Place Order]
If [Inventory Service] is unavailable:
  Strategy: Accept order with "Pending Inventory Check" status
  Process: Background job retries inventory check every 5 minutes
  User sees: "Your order is received and being confirmed"
  SLA: Full confirmation within 30 minutes
```

## Step 4 — Non-Functional Requirements (feeds back to FRD Section 10)

```
NFR-DEGRAD-001: The system shall serve Customer Profile requests using cached data
  for up to 5 minutes when the Customer Data Service is unavailable.

NFR-DEGRAD-002: The system shall accept Order submissions when Inventory Service
  is unavailable, placing them in Pending status, and shall confirm or reject
  within 30 minutes via email notification.

NFR-DEGRAD-003: The system shall never silently discard a failed write operation.
  All failed writes shall be queued for retry or explicitly surfaced to the user.
```
