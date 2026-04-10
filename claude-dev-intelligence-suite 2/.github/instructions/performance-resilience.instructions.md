---
applyTo: "**/*Service*.java,**/*Client*.java,**/*Repository*.java,**/application.yml"
description: "Automatically triggered when working with service/client/repository files or when user asks about performance, resilience, circuit breakers, caching, or load testing"
---

# Performance & Resilience Skills

When performance or resilience concerns arise:

- **circuit-breaker-auditor** (`.claude/skills/circuit-breaker-auditor/SKILL.md`)
  Triggers: "circuit breaker", "cascading failure", "Resilience4j",
  "fallback", "unprotected calls", "downstream failure"

- **timeout-bulkhead-auditor** (`.claude/skills/timeout-bulkhead-auditor/SKILL.md`)
  Triggers: "missing timeouts", "bulkhead", "thread pool isolation",
  "no timeout", "connection timeout", "read timeout"

- **retry-storm-detector** (`.claude/skills/retry-storm-detector/SKILL.md`)
  Triggers: "retry storm", "retry configuration", "exponential backoff",
  "jitter", "thundering herd retry", "retry loop"

- **cache-strategy-generator** (`.claude/skills/cache-strategy-generator/SKILL.md`)
  Triggers: "caching", "what to cache", "Redis", "Caffeine", "TTL",
  "cache invalidation", "thundering herd cache"

- **latency-budget-decomposer** (`.claude/skills/latency-budget-decomposer/SKILL.md`)
  Triggers: "latency budget", "where is time spent", "call chain latency",
  "which service is slow", "SLA breakdown"

- **load-test-generator** (`.claude/skills/load-test-generator/SKILL.md`)
  Triggers: "load tests", "Gatling", "k6", "stress test", "spike test",
  "concurrent users", "performance test"

Load the relevant SKILL.md before generating resilience patterns or load test scripts.
