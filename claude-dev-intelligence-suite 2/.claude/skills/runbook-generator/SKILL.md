---
name: runbook-generator
description: >
  Generate operational runbooks per service: how to deploy, rollback, what health
  checks mean, what to do when each alert fires, how to diagnose the top failure
  modes, and who to escalate to. Use when asked: 'runbook', 'operational guide',
  'ops playbook', 'how to deploy', 'what to do when alert fires', 'on-call guide',
  'incident response', 'deployment runbook', 'rollback steps', 'production runbook',
  'escalation path'. Reads CI/CD pipelines, health endpoints, alerting rules, SLO
  documents, and source code. Produces what your on-call engineer needs at 2am.
---
# Runbook Generator

Produce the operational runbook an on-call engineer needs at 2am.

---

## Step 0 — Gather Context

```bash
# Service entry points
python3 scripts/project_graph.py --graph repo-graph.json --mode entry-points 2>/dev/null

# Health + actuator endpoints
grep -rn "management\.endpoints\|health\|readiness\|liveness\|actuator" \
  <java_path>/src/main/resources --include="*.yml" --include="*.properties" | head -20

# Alert rules (from SLO generator output or prometheus config)
find . -name "*.yml" -o -name "*.yaml" | \
  xargs grep -l "alert\|PrometheusRule\|alerting" 2>/dev/null | head -5

# CI/CD pipeline
find . -name "Jenkinsfile*" -o -name "*.github/workflows/*.yml" | head -5

# External dependencies
grep -rn "spring.datasource\|spring.data.redis\|spring.kafka\|spring.rabbitmq" \
  <java_path>/src/main/resources --include="*.yml" | head -20

# Log pattern for errors
grep -rn "logger\.error\|log\.error\|LOG\.error" \
  <java_path> --include="*.java" | head -20
```

---

## Step 1 — Generate the Runbook

Produce one runbook file per service. Follow this template exactly:

```markdown
# RUNBOOK: [Service Name]
Version: 1.0 | Last updated: [date] | Owner team: [team]

---

## 1. SERVICE OVERVIEW

**What it does**: [2-3 sentences from FRD — what users experience]
**Criticality**: [Critical / High / Standard]
**SLA**: [availability %] | P95 latency: [N]ms | Error rate: <[N]%
**On-call contact**: [team name / PagerDuty rotation]
**Escalation path**: On-call → [Tech Lead] → [Engineering Manager] → [VP Eng]

---

## 2. QUICK REFERENCE

| Resource | URL / Command |
|---|---|
| Service URL (prod) | https://[service].yourorg.com |
| Health check | GET /actuator/health |
| Metrics | https://grafana.yourorg.com/d/[dashboard] |
| Logs | https://kibana.yourorg.com/app/[service] |
| Alerts | https://pagerduty.com/services/[id] |
| Deployment | [CI/CD URL] |
| Git repo | [repo URL] |

---

## 3. DEPLOYMENT

### Deploy a new version
```bash
# Trigger via CI/CD (preferred)
# Go to [CI/CD URL] → select branch → click Deploy

# Manual deploy (emergency only)
kubectl set image deployment/[service] \
  [service]=[registry]/[service]:[version] -n [namespace]

# Verify deployment
kubectl rollout status deployment/[service] -n [namespace]
curl https://[service].yourorg.com/actuator/health | jq .status
```

### Rollback
```bash
# Immediate rollback to previous version
kubectl rollout undo deployment/[service] -n [namespace]

# Rollback to specific version
kubectl rollout undo deployment/[service] --to-revision=[N] -n [namespace]

# Verify rollback
kubectl rollout status deployment/[service] -n [namespace]
# Check health → confirm status: UP
```

### Database migrations
- Migrations run **automatically before app startup** via Flyway
- If migration fails: app will not start — check logs for `FlywayException`
- **NEVER run migrations manually in production** — use the CI/CD pipeline

---

## 4. HEALTH CHECKS

| Endpoint | What it checks | Healthy response |
|---|---|---|
| /actuator/health | Overall status | `{"status":"UP"}` |
| /actuator/health/db | Database connection | `{"status":"UP"}` |
| /actuator/health/redis | Redis connection | `{"status":"UP"}` |
| /actuator/health/[kafka] | Kafka connectivity | `{"status":"UP"}` |

```bash
# Quick health check
curl -s https://[service].yourorg.com/actuator/health | jq .

# Check individual component
curl -s https://[service].yourorg.com/actuator/health/db | jq .

# Check all metrics
curl -s https://[service].yourorg.com/actuator/metrics | jq .names
```

---

## 5. ALERT RESPONSE PLAYBOOKS

### Alert: HighErrorRate_[Service] (>1% errors over 5 min)

**Severity**: Critical | **SLO impact**: Yes

**Immediate actions (first 5 minutes)**:
1. Open Grafana dashboard → check error rate trend (rising or plateau?)
2. Open Kibana → filter: `service:[service-name] AND level:ERROR` → last 15 min
3. Check if a deployment happened in the last 30 minutes

**Diagnosis tree**:
```
Error rate > 1%?
├── YES → Check logs for error pattern
│   ├── NullPointerException → likely data issue, check recent input
│   ├── ConnectionRefused → check DB / Redis / downstream service health
│   ├── 401/403 errors → auth service issue, check /actuator/health
│   └── BusinessException → likely bad input data — not a code bug
└── NO → Alert may be flapping — check Grafana for spike vs sustained
```

**If DB connectivity is the issue**:
```bash
kubectl exec -it [pod] -n [namespace] -- curl localhost:8080/actuator/health/db
# If DOWN: check DB server status, connection pool metrics
kubectl exec -it [pod] -n [namespace] -- curl localhost:8080/actuator/metrics/hikaricp.connections.active
```

**Resolution options**:
- Bad deployment → rollback (see Section 3)
- DB overloaded → scale DB read replicas or enable maintenance mode
- Downstream service down → circuit breaker should engage automatically
- Data issue → identify affected records, fix data, replay events

**Post-incident**: Create incident ticket, update this runbook with the root cause

---

### Alert: HighLatency_P95_[Service] (P95 > 500ms for 5 min)

**Immediate actions**:
1. Check `http_request_duration_seconds` in Grafana — which endpoints are slow?
2. Check DB query times: `jdbc.query.time` metric
3. Check downstream service latency: `http.client.requests` metric
4. Check thread pool saturation: `executor.active` metric

**Diagnosis tree**:
```
Latency high?
├── DB queries slow → check slow query log, add index
├── Downstream service slow → check circuit breaker status, consider fallback
├── Thread pool saturated → scale pods or increase pool size
└── GC pause → check JVM GC metrics, consider memory increase
```

---

### Alert: PodCrashLooping

```bash
# Check why pod is crashing
kubectl logs [pod-name] -n [namespace] --previous

# Common causes and fixes:
# OOMKilled → increase memory limit in deployment spec
# ExitCode 137 → OOM or killed by OS → increase memory
# ExitCode 1 → application exception on startup → check logs for root cause
# Failed health check → check /actuator/health manually
```

---

## 6. TOP 5 FAILURE MODES

Based on historical incidents and code analysis:

**Failure 1: DB connection pool exhaustion**
- Symptom: All requests timeout, health/db shows DOWN
- Cause: Slow queries holding connections + pool size too small
- Fix: `kubectl exec` → check `/actuator/metrics/hikaricp.connections.pending`
- Resolution: Restart pod (clears connections) + investigate slow query

**Failure 2: [Downstream service] unavailable**
- Symptom: Specific endpoint errors, circuit breaker opens
- Cause: [Service] outage or network issue
- Fix: Circuit breaker returns fallback — check fallback quality
- Resolution: Wait for [service] recovery — circuit breaker auto-closes

**Failure 3: Memory leak under load**
- Symptom: Gradual latency increase, eventual OOMKilled
- Cause: Unreleased subscriptions or large in-memory collections
- Fix: Rolling restart buys time: `kubectl rollout restart deployment/[service]`
- Resolution: Heap dump analysis, fix the leak

**Failure 4: Kafka consumer lag growing**
- Symptom: Events delayed, consumer lag metric rising
- Fix: Check consumer group: `kafka-consumer-groups --describe --group [group]`
- Resolution: Scale consumer pods or investigate slow processing

**Failure 5: Configuration missing in environment**
- Symptom: Service won't start, `IllegalStateException` in logs
- Cause: Missing env var or secret
- Fix: Check `kubectl describe pod [pod]` for env var issues
- Resolution: Add missing config to ConfigMap/Secret

---

## 7. USEFUL COMMANDS CHEAT SHEET

```bash
# Pod status
kubectl get pods -n [namespace] -l app=[service]

# Live logs
kubectl logs -f deployment/[service] -n [namespace]

# Recent errors only
kubectl logs deployment/[service] -n [namespace] --since=30m | grep ERROR

# Scale up
kubectl scale deployment/[service] --replicas=5 -n [namespace]

# Get env vars (check for missing config)
kubectl exec [pod] -n [namespace] -- env | sort

# Thread dump (diagnose deadlock / thread exhaustion)
kubectl exec [pod] -n [namespace] -- kill -3 1

# Heap dump (diagnose OOM)
kubectl exec [pod] -n [namespace] -- \
  jmap -dump:format=b,file=/tmp/heap.hprof 1
kubectl cp [pod]:/tmp/heap.hprof ./heap.hprof -n [namespace]
```

---

## 8. CONTACTS & ESCALATION

| Situation | Contact | Via |
|---|---|---|
| Service down < 15 min | On-call engineer | PagerDuty |
| Service down > 15 min | Tech Lead + On-call | PagerDuty + Slack #incidents |
| Data corruption | Tech Lead + Data team | Immediate call |
| Security incident | Security team + CISO | Security hotline |
| Regulatory impact | Compliance team | Immediate notification |

---

## 9. MAINTENANCE WINDOWS

| Task | Frequency | Duration | Impact |
|---|---|---|---|
| Database vacuum/reindex | Weekly (Sun 2am) | 30 min | Read-only mode |
| Certificate renewal | 90 days | 0 | Zero downtime |
| Dependency upgrade deploy | Bi-weekly | 10 min | Rolling restart |
```
