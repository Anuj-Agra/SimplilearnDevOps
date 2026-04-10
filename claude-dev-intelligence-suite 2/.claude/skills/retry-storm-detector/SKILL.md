---
name: retry-storm-detector
description: >
  Find retry logic that will make a degraded situation catastrophically worse:
  retries without exponential backoff, retries without jitter, retrying non-retryable
  errors, and retry loops exceeding caller timeout. Use when asked: 'retry storm',
  'retry configuration', 'exponential backoff', 'retry jitter', 'retry loops',
  'thundering herd retry', 'retry audit', 'bad retry logic', 'retry on 400',
  'synchronized retries'. Produces corrected retry configurations.
---
# Retry Storm Detector

Find retry configurations that amplify failures rather than recover from them.

## Step 1 — Find All Retry Logic
```bash
# Resilience4j @Retry
grep -rn "@Retry\|RetryConfig\|RetryRegistry\|@Retryable" \
  <java_path> --include="*.java" | head -30

# Spring @Retryable
grep -rn "@Retryable\|@EnableRetry\|RetryTemplate\|BackOffPolicy" \
  <java_path> --include="*.java" | head -30

# Manual retry loops
grep -rn "for.*retry\|while.*retry\|int.*attempt\|retryCount\|maxRetries" \
  <java_path> --include="*.java" | head -30

# Kafka / messaging retries
grep -rn "@RetryableTopic\|attempts\|backoff.*delay\|maxAttempts" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -20
```

## Step 2 — Detect Anti-Patterns

### Anti-pattern 1: No backoff (linear retries)
```bash
grep -rn "maxAttempts\|max-attempts\|maxRetries" \
  . --include="*.yml" --include="*.properties" --include="*.java" | \
  grep -v "backoff\|BackOff\|delay\|waitDuration\|exponential" | head -20
```
**Risk**: 100 clients all retry every 1 second → 100× amplified load on degraded service

### Anti-pattern 2: No jitter
```bash
grep -rn "exponentialBackoff\|ExponentialBackOff\|waitDuration.*exponential" \
  . --include="*.yml" --include="*.properties" --include="*.java" | \
  grep -v "jitter\|randomisedWait\|randomizedWait\|Math.random" | head -20
```
**Risk**: All clients retry at the exact same millisecond — synchronised retry storm

### Anti-pattern 3: Retrying non-retryable errors
```bash
grep -rn "retryExceptions\|retryOn\|include.*Exception\|@Retryable.*value" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -20
```
Check: is `BadRequestException` (400), `ValidationException`, or any 4xx in the retry list?
**Risk**: Retrying a bad request endlessly — it will never succeed

### Anti-pattern 4: Retry timeout exceeds caller timeout
Look for retry configuration where `maxAttempts × waitDuration > caller's timeout`.
E.g. 3 retries × 5s wait = 15s total, but caller times out after 10s.

## Step 3 — Output + Fixed Config

```
RETRY STORM ANALYSIS: [System]

ANTI-PATTERNS FOUND:
  RS-001 [CRITICAL]: [Class] retries with no backoff (fixed 1s interval)
    Risk: Under failure, 50 clients × 3 retries = 150 req/s instead of 50
    Fix: Add exponential backoff with jitter (see config below)

  RS-002 [HIGH]: [Class] retries on BusinessException (400 equivalent)
    Risk: Will retry forever on a request that can never succeed
    Fix: Move BusinessException to ignoreExceptions list

  RS-003 [MEDIUM]: Retry window (3 × 5s = 15s) exceeds caller timeout (10s)
    Risk: Retry completes but caller has already failed — wasted retries
    Fix: Reduce maxAttempts to 2 or increase caller timeout to 20s

CORRECTED RESILIENCE4J CONFIG:
resilience4j.retry.instances:
  [service-name]:
    maxAttempts: 3
    waitDuration: 500ms
    enableExponentialBackoff: true
    exponentialBackoffMultiplier: 2        # 500ms, 1s, 2s
    enableRandomizedWait: true             # ±25% jitter — prevents sync storms
    randomizedWaitFactor: 0.25
    retryExceptions:
      - java.net.ConnectException
      - java.net.SocketTimeoutException
      - org.springframework.web.client.ResourceAccessException
    ignoreExceptions:
      - com.yourorg.BusinessException      # 4xx — never retry
      - com.yourorg.ValidationException    # 4xx — never retry
      - java.lang.IllegalArgumentException
```
