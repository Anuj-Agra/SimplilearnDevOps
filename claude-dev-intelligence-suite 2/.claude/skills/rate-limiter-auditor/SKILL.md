---
name: rate-limiter-auditor
description: >
  Check every public-facing endpoint for rate limiting configuration. Without rate
  limits, a single misbehaving client can saturate thread pools under parallel load.
  Use when asked: 'rate limiting', 'rate limit audit', 'throttling', 'API throttle',
  'request quota', 'DDoS protection', 'client abuse', 'Bucket4j', 'rate limit config',
  'too many requests', 'request rate', '429 response'. Produces Bucket4j and Spring
  Cloud Gateway rate limit configuration for each endpoint tier.
---
# Rate Limiter Coverage Auditor

Find unprotected endpoints and generate tiered rate limit configuration.

## Step 1 — Detect Existing Rate Limits
```bash
# Bucket4j
grep -rn "Bucket4j\|Bucket\.\|@RateLimit\|BucketConfiguration\|bandwidth\|Refill" \
  <java_path> --include="*.java" | head -20

# Spring Cloud Gateway rate limiter
grep -rn "RequestRateLimiter\|RedisRateLimiter\|spring.cloud.gateway" \
  . --include="*.yml" --include="*.properties" | head -20

# Nginx / reverse proxy (outside Java)
find . -name "nginx.conf" -o -name "*.conf" | \
  xargs grep -l "limit_req\|limit_conn" 2>/dev/null | head -5

# Resilience4j rate limiter
grep -rn "@RateLimiter\|RateLimiterConfig\|RateLimiterRegistry" \
  <java_path> --include="*.java" | head -10
```

## Step 2 — Classify Endpoints by Rate Limit Tier

```
TIER 1 — Strict (auth, payment, sensitive operations):
  Limit: 10 requests/minute per IP
  Applies to: /login, /register, /password-reset, /payment

TIER 2 — Standard (standard user operations):
  Limit: 100 requests/minute per authenticated user
  Applies to: most CRUD endpoints

TIER 3 — Relaxed (read-only, public data):
  Limit: 1000 requests/minute per IP
  Applies to: GET /api/products, /api/search, public listings

TIER 4 — Bulk (export, report generation):
  Limit: 5 requests/hour per user
  Applies to: /api/export, /api/report
```

## Step 3 — Output + Generated Config

```
RATE LIMITER AUDIT: [System]

UNPROTECTED ENDPOINTS:
  RL-001 [CRITICAL]: POST /api/auth/login — no rate limit
    Risk: Brute force attack exhausts CPU and locks accounts en masse
    Limit: 5 attempts/minute per IP → temporary block on breach

  RL-002 [HIGH]: GET /api/[resource] — no rate limit
    Risk: Single client polling every 100ms consumes 600 req/min
    Limit: 100 req/min per authenticated user

  RL-003 [MEDIUM]: POST /api/export — no rate limit
    Risk: Large export triggered 10× simultaneously → OOM
    Limit: 5 requests/hour per user

GENERATED BUCKET4J CONFIG (application.yml):
bucket4j:
  enabled: true
  filters:
    - cache-name: rate-limit-buckets
      url: /api/auth/login
      rate-limits:
        - bandwidths:
          - capacity: 5
            time: 1
            unit: minutes
            refill-speed: intervally
      http-response-body: '{"error":"Too many login attempts. Try again in 1 minute."}'

    - cache-name: rate-limit-buckets
      url: /api/.*
      rate-limits:
        - execute-condition: "getAuthentication() != null"
          expression: "getAuthentication().getName()"
          bandwidths:
          - capacity: 100
            time: 1
            unit: minutes

SPRING CLOUD GATEWAY ALTERNATIVE:
spring.cloud.gateway.routes:
  - id: rate-limited-api
    uri: lb://api-service
    filters:
      - name: RequestRateLimiter
        args:
          redis-rate-limiter.replenishRate: 100
          redis-rate-limiter.burstCapacity: 200
          redis-rate-limiter.requestedTokens: 1
          key-resolver: "#{@userKeyResolver}"
```
