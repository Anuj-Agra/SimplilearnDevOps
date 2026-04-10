---
name: slo-sla-generator
description: >
  Generate Service Level Objective (SLO) and Service Level Agreement (SLA) definitions
  for each API endpoint, with latency targets (P50/P95/P99), error rate budgets,
  availability targets, and alerting rules. Use when asked: 'SLO', 'SLA', 'service
  level', 'latency target', 'P95 latency', 'error budget', 'availability target',
  'alerting rules', 'uptime SLA', 'performance baseline', 'response time target',
  'service objectives'. Produces Prometheus alerting rules and runbook stubs.
---
# SLO/SLA Definition Generator

Generate measurable SLOs for every API endpoint extracted from the codebase.

## Step 1 — Identify All User-Facing Endpoints
```bash
python3 scripts/project_graph.py --graph repo-graph.json --mode entry-points 2>/dev/null

grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@PatchMapping" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -60
```

## Step 2 — Classify Endpoints by Criticality
- **Critical** (payment, auth, core workflow) → tightest SLOs
- **Standard** (CRUD, search) → normal SLOs
- **Background** (reporting, export, batch) → relaxed SLOs

## Step 3 — SLO Targets by Classification

| Classification | Availability | P50 | P95 | P99 | Error Rate |
|---|---|---|---|---|---|
| Critical | 99.95% | 100ms | 500ms | 1s | < 0.1% |
| Standard | 99.9% | 200ms | 1s | 2s | < 1% |
| Background | 99.5% | 2s | 10s | 30s | < 5% |

## Step 4 — Output: SLO Document + Alert Rules

```
SLO DOCUMENT: [System Name]
Review date: [quarterly]

ENDPOINT SLOS:
┌─────────────────────────────────────────────────────────────────┐
│ Endpoint: [Plain English name]                                   │
│ Classification: Critical                                         │
│ Availability SLO:  99.95% (4.38 hours downtime/year budget)     │
│ Latency SLOs:      P50 ≤ 100ms | P95 ≤ 500ms | P99 ≤ 1s        │
│ Error Rate SLO:    < 0.1% of requests over 5-minute window      │
│ Error Budget:      0.05% of requests/month = [N] errors/month   │
└─────────────────────────────────────────────────────────────────┘

PROMETHEUS ALERT RULES (generated):

groups:
  - name: slo-alerts
    rules:
      - alert: HighErrorRate_[EndpointName]
        expr: |
          rate(http_requests_total{endpoint="[path]",status=~"5.."}[5m])
          / rate(http_requests_total{endpoint="[path]"}[5m]) > 0.001
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate exceeds SLO for [endpoint]"
          runbook: "https://runbook.yourorg.com/[endpoint]-errors"

      - alert: HighLatency_P95_[EndpointName]
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket{endpoint="[path]"}[5m])
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency exceeds 500ms SLO for [endpoint]"

RUNBOOK STUBS (fill in per incident):
  On HighErrorRate alert:
    1. Check [downstream service] health
    2. Check DB connection pool utilisation
    3. Check recent deployments
    4. If > 1% error rate: enable circuit breaker fallback
```
