---
name: latency-budget-decomposer
description: >
  For each user-facing API call, trace the full call chain and calculate a latency
  budget per hop. Use when asked: 'latency budget', 'where is time spent', 'call
  chain latency', 'hop latency', 'SLA breakdown', 'latency decomposition', 'which
  service is slow', 'latency allocation', 'response time breakdown'. Uses graph
  path projections to trace chains. Flags chains where sum of p95 latencies already
  exceeds the SLA with no headroom.
---
# Latency Budget Decomposer

Trace call chains and allocate latency budgets per hop.

## Step 1 — Find Call Chains
```bash
python3 scripts/project_graph.py --graph repo-graph.json --mode longest-path
python3 scripts/project_graph.py --graph repo-graph.json --mode entry-points

# For a specific endpoint's chain:
python3 scripts/project_graph.py --graph repo-graph.json \
  --mode path --from <entry-point> --to <leaf-service>
```

## Step 2 — Identify Synchronous Hops
From the code, for each hop in the chain, classify:
- **Network hop** (HTTP/gRPC call): ~1-10ms network + downstream processing
- **Database query**: ~1-100ms depending on complexity + indexes
- **Cache read**: ~0.1-2ms (in-process) or ~1-5ms (Redis)
- **External API**: ~50-500ms (highly variable — must timeout)
- **Computation**: ~0-10ms (usually negligible)

## Step 3 — Budget Allocation Formula

```
Total SLA budget = [SLO P95 target, e.g. 500ms]

For a chain of N hops:
  Network overhead = N × 2ms (round trip per hop)
  Per-hop budget = (Total - network overhead) / N

Flag if any single hop historically uses > 50% of total budget.
```

## Step 4 — Output

```
LATENCY BUDGET: GET /api/checkout [SLA: 500ms P95]

CALL CHAIN (4 hops):
  Client → API Gateway (5ms) → Order Service → Inventory → Pricing → (response)

BUDGET ALLOCATION:
  ┌─────────────────────────────────────────────────────────┐
  │ Hop                  │ Budget   │ Current P95 │ Status  │
  ├──────────────────────┼──────────┼─────────────┼─────────┤
  │ API Gateway          │  20ms    │   8ms       │ ✅ OK   │
  │ Order Service (DB)   │ 150ms    │ 180ms       │ ❌ OVER │
  │ Inventory Service    │ 150ms    │  95ms       │ ✅ OK   │
  │ Pricing Service      │ 150ms    │  45ms       │ ✅ OK   │
  │ Network overhead     │  30ms    │  12ms       │ ✅ OK   │
  ├──────────────────────┼──────────┼─────────────┼─────────┤
  │ TOTAL                │ 500ms    │ 340ms       │ ⚠️  68% │
  └─────────────────────────────────────────────────────────┘

FINDINGS:
  LAT-001 [HIGH]: Order Service DB query exceeds its budget by 30ms
    Likely cause: Missing index on order lookup by customerId
    Fix: Add index on customer_id column; review query plan

  LAT-002 [MEDIUM]: Only 32% headroom to SLA (160ms remaining)
    Risk: Any degradation of any hop will breach the 500ms SLA
    Fix: Introduce caching in Pricing Service (TTL 5 min) → reduces to ~5ms

OPTIMISED PROJECTION (after fixes):
  Order Service: 180ms → 80ms (with index)
  Pricing Service: 45ms → 5ms (with cache)
  New total P95: ~200ms  |  Headroom: 300ms (60%)
```
