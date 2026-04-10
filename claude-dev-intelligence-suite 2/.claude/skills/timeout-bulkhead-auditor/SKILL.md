---
name: timeout-bulkhead-auditor
description: >
  Scan every outbound call for missing read timeouts, connection timeouts, circuit
  breakers, and bulkhead isolation. A single downstream service with no timeout
  can exhaust your thread pool and take down the entire system. Use when asked:
  'timeout configuration', 'bulkhead', 'thread pool isolation', 'missing timeouts',
  'circuit breaker', 'Resilience4j config', 'service isolation', 'timeout audit',
  'downstream timeout', 'connection timeout missing'. Produces Resilience4j config.
---
# Timeout & Bulkhead Auditor

Find every unprotected outbound call and produce Resilience4j configuration.

## Step 1 — Find All Outbound Calls
```bash
# HTTP calls
grep -rn "RestTemplate\.\|webClient\.\|HttpClient\.\|FeignClient\|@FeignClient" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -50

# Database (connection + query timeout)
grep -rn "spring.datasource\|@Query\|entityManager\|hibernate.jdbc.fetch_size" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -30

# External message brokers
grep -rn "@KafkaListener\|rabbitTemplate\.\|sqsClient\." \
  <java_path> --include="*.java" | head -20
```

## Step 2 — Check Each for Timeout Configuration
```bash
# RestTemplate timeout config
grep -rn "SimpleClientHttpRequestFactory\|HttpComponentsClientHttpRequestFactory\|\
  setReadTimeout\|setConnectTimeout\|ReadTimeoutHandler\|responseTimeout\|connectTimeout" \
  <java_path> --include="*.java" | head -30

# WebClient timeout
grep -rn "responseTimeout\|connectTimeout\|ReadTimeoutHandler\|WriteTimeoutHandler\|\
  HttpClient.*responseTimeout" <java_path> --include="*.java" | head -20

# Resilience4j / Hystrix / Sentinel
grep -rn "@CircuitBreaker\|@TimeLimiter\|@Bulkhead\|@RateLimiter\|\
  @Retry\|CircuitBreakerConfig\|BulkheadConfig\|TimeLimiterConfig" \
  <java_path> --include="*.java" | head -30

# Feign timeout
grep -rn "feign.client.config\|connectTimeout\|readTimeout" \
  . --include="*.yml" --include="*.properties" | head -20
```

## Step 3 — Output + Generated Config

```
TIMEOUT & BULKHEAD AUDIT: [System]

UNPROTECTED CALLS (no timeout configured):
  TB-001 [CRITICAL]: RestTemplate call to [service] in [Class]
    Risk: If [service] hangs, ALL threads wait indefinitely → total outage
    Fix: Add timeout config (see below)

  TB-002 [CRITICAL]: Database queries have no query timeout
    Risk: A slow query holds a DB connection and a thread
    Fix: Add spring.datasource.hikari.connection-timeout + @QueryHints

MISSING BULKHEADS:
  TB-003 [HIGH]: [ServiceA] and [ServiceB] share the same thread pool
    Risk: [ServiceB] degradation consumes threads needed for [ServiceA]
    Fix: Isolate with @Bulkhead (thread pool per downstream)

GENERATED RESILIENCE4J CONFIG (application.yml):

resilience4j:
  circuitbreaker:
    instances:
      [service-name]:
        slidingWindowSize: 10
        failureRateThreshold: 50
        waitDurationInOpenState: 10s
        permittedNumberOfCallsInHalfOpenState: 3

  timelimiter:
    instances:
      [service-name]:
        timeoutDuration: 3s        # Fail fast — never wait forever

  bulkhead:
    instances:
      [service-name]:
        maxConcurrentCalls: 20     # Isolate this service's thread usage
        maxWaitDuration: 500ms

  retry:
    instances:
      [service-name]:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
        retryExceptions:
          - java.net.ConnectException
          - java.net.SocketTimeoutException
        ignoreExceptions:
          - com.yourorg.BusinessException  # Don't retry business errors
```
