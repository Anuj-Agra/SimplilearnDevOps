---
name: idempotency-scanner
description: >
  Find POST/PUT/PATCH/DELETE endpoints where duplicate requests (network retry,
  double-submit) would cause incorrect results. Use when asked: 'idempotency',
  'duplicate requests', 'double submit', 'network retry safety', 'idempotency key',
  'safe to retry', 'payment duplicate', 'order duplicate', 'concurrent submit',
  'retry-safe endpoint'. Parallel connections dramatically increase duplicate
  submission probability. Generates idempotency key implementation patterns.
---
# Idempotency Coverage Scanner

Find non-idempotent endpoints and generate idempotency patterns.

## Step 1 — Find Non-Safe Write Endpoints
```bash
# POST endpoints (create — likely non-idempotent)
grep -rn "@PostMapping\|@RequestMapping.*POST" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test\|login\|auth"

# PUT/PATCH (update — should be idempotent by design, but often isn't)
grep -rn "@PutMapping\|@PatchMapping" <java_path> --include="*.java" | \
  grep -v "//\|test\|Test"

# DELETE (should be idempotent — returning 404 on second call is acceptable)
grep -rn "@DeleteMapping" <java_path> --include="*.java" | grep -v "//\|test\|Test"
```

## Step 2 — Check Idempotency Protections
```bash
# Idempotency key header support
grep -rn "Idempotency-Key\|idempotencyKey\|idempotency.key\|X-Idempotency" \
  <java_path> --include="*.java" | head -20

# Unique constraint enforcement (catches duplicates at DB level)
grep -rn "@UniqueConstraint\|@Column.*unique.*true\|UNIQUE\b\|unique = true" \
  <java_path> --include="*.java" | head -20

# Idempotency token table / cache
grep -rn "IdempotencyKey\|ProcessedRequest\|idempotency_keys\|processedRequests" \
  <java_path> --include="*.java" | head -10
```

## Step 3 — Output + Generated Pattern

```
IDEMPOTENCY AUDIT: [System]

NON-IDEMPOTENT ENDPOINTS:
  IDEM-001 [CRITICAL]: POST /api/[payments/orders] — no idempotency protection
    Risk: Network timeout causes client retry → duplicate [payment/order] created
    Business impact: Customer charged twice / order placed twice
    Fix: Implement Idempotency-Key header pattern (generated below)

  IDEM-002 [HIGH]: POST /api/[resource] — no unique constraint on business key
    Risk: Double-submit creates two identical records
    Fix: Add @UniqueConstraint on business identifier field

SAFE ENDPOINTS (correctly idempotent):
  ✅ PUT /api/[resource]/{id} — full replacement, safe to retry
  ✅ DELETE /api/[resource]/{id} — returns 404 on repeat, acceptable

GENERATED IDEMPOTENCY IMPLEMENTATION:

// 1. Redis-based idempotency key store
@Service
public class IdempotencyService {
  private final RedisTemplate<String, String> redis;
  private static final Duration IDEMPOTENCY_TTL = Duration.ofHours(24);

  public boolean isAlreadyProcessed(String idempotencyKey) {
    return Boolean.TRUE.equals(
      redis.opsForValue().setIfAbsent("idem:" + idempotencyKey, "processing",
        IDEMPOTENCY_TTL));
    // Returns false if key already existed (already processed)
  }

  public void storeResult(String idempotencyKey, String responseBody) {
    redis.opsForValue().set("idem-result:" + idempotencyKey, responseBody,
      IDEMPOTENCY_TTL);
  }
}

// 2. Controller usage
@PostMapping("/api/[resource]")
public ResponseEntity<[Resource]> create(
    @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
    @Valid @RequestBody [Resource]Request request) {

  if (idempotencyKey != null) {
    String cached = idempotencyService.getCachedResult(idempotencyKey);
    if (cached != null) {
      return ResponseEntity.ok(objectMapper.readValue(cached, [Resource].class));
    }
  }

  [Resource] result = service.create(request);

  if (idempotencyKey != null) {
    idempotencyService.storeResult(idempotencyKey, objectMapper.writeValueAsString(result));
  }

  return ResponseEntity.status(201).body(result);
}
```
