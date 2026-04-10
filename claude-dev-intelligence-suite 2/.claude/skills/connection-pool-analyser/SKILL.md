---
name: connection-pool-analyser
description: >
  Examine every connection pool in the system — database (HikariCP), HTTP clients,
  Redis, Kafka, message brokers — and verify sizing is correct relative to thread
  pools and expected concurrency. Use when asked: 'connection pool', 'pool sizing',
  'HikariCP config', 'database connections', 'pool exhaustion', 'too many connections',
  'connection timeout', 'pool configuration', 'connection leak', 'concurrent connections'.
  A misconfigured pool is the most common cause of production failure at scale.
---
# Connection Pool Analyser

Audit every connection pool and detect mismatches that cause production failures.

## Step 1 — Discover All Pools
```bash
# HikariCP (Spring datasource)
grep -rn "spring.datasource\|hikari\|maximum-pool-size\|minimumIdle\|connectionTimeout\|\
  maxLifetime\|idleTimeout" . --include="*.yml" --include="*.properties" | head -40

# HTTP Client pools
grep -rn "maxConnections\|maxConnectionsPerRoute\|connectionRequestTimeout\|\
  PoolingHttpClientConnectionManager\|connectionPool\|maxTotal" \
  <java_path> --include="*.java" | head -30

# Redis connection pool
grep -rn "spring.redis\|jedis.pool\|lettuce.pool\|maxActive\|maxIdle\|spring.data.redis" \
  . --include="*.yml" --include="*.properties" | head -20

# Kafka consumer threads
grep -rn "concurrency\|consumer.threads\|num.partitions\|@KafkaListener.*concurrency" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -20
```

## Step 2 — Detect Mismatches

### The Critical Pool Mismatch
If using a thread pool with N threads, your DB pool needs ≥ N connections.
If using reactive (WebFlux), you only need ~2× CPU cores for the event loop,
but your DB pool must NOT exceed what your DB can handle.

Formula: `safe_pool_size = min(thread_count, db_max_connections / num_instances)`

### Detect the "Reactive + Blocking DB" Deadlock Pattern
If WebFlux is detected AND JPA/JDBC is used:
→ **CRITICAL**: Blocking DB call on a non-blocking thread will exhaust the event loop.
→ Each blocking call holds an event-loop thread, defeating reactive entirely.

```bash
# Detect this combination
grep -rn "spring-boot-starter-webflux" . --include="*.xml" --include="*.gradle" | head -5
grep -rn "JpaRepository\|EntityManager\|jdbcTemplate" <java_path> --include="*.java" | head -5
```

## Step 3 — Output: Pool Configuration Report

```
CONNECTION POOL ANALYSIS: [System]

DATABASE POOL (HikariCP):
  Current config:
    maximum-pool-size: [value or "NOT SET — default 10"]
    minimumIdle:       [value]
    connectionTimeout: [value or "NOT SET — default 30s"]
    maxLifetime:       [value or "NOT SET — default 30min"]

  Assessment:
    Thread pool size:          [N]
    DB pool size:              [N]
    Match:                     [OK / MISMATCH — pool too small/large]
    Expected max DB load:      [pool × instances] connections to DB server

  Recommendation:
    maximum-pool-size: [calculated value]
    minimumIdle: [calculated value]
    connectionTimeout: 5000  # Fail fast — 30s default hides pool exhaustion
    maxLifetime: 600000      # 10 min — less than DB's wait_timeout

CRITICAL ISSUES:
  POOL-001: [issue] — Risk: [what fails] — Fix: [config change]

HTTP CLIENT POOL:
  [same structure]

REDIS POOL:
  [same structure]

COMPLETE CONFIG RECOMMENDATION:
  [Ready-to-paste application.yml snippet]
```
