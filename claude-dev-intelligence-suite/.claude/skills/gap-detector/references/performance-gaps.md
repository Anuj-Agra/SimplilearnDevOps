# Performance Gap Detector — Full Checklist

## Anti-Pattern Detection Queries

### N+1 Query Pattern (most common production killer)
```bash
# Find loops containing database or service calls
grep -rn -B2 -A8 "for.*:\|\.forEach\|\.stream()" \
  <java_path>/src --include="*.java" \
  | grep -B5 "\.findBy\|repository\.\|\.get(\|\.save(\|restTemplate\." \
  | grep -v "test\|Test"
```
**Risk**: 100 records → 101 DB calls. 10,000 records → 10,001 DB calls.
**Fix**: Batch query `findAllById(ids)`, `@EntityGraph`, or `JOIN FETCH`.

### Missing Pagination
```bash
grep -rn "findAll()\b\|List<.*> getAll\b\|Collection<.*> list\b" \
  <java_path>/src --include="*.java" | grep -v "test\|Test"
```
**Risk**: Returns ALL records in memory. At scale → OutOfMemoryError.
**Fix**: Replace with `findAll(Pageable)`, add `?page=&size=` parameters.

### Missing Cache on Hot Reads
```bash
# Find methods that read frequently-stable data without caching
grep -rn "findByCode\|findByType\|getReferenceData\|getConfig\|getLookup" \
  <java_path>/src --include="*.java" -l \
  | xargs grep -L "@Cacheable" 2>/dev/null
```
**Risk**: Every request re-fetches data that barely changes.
**Fix**: Add `@Cacheable` with appropriate TTL. Use Caffeine for in-process, Redis for shared.

### Synchronous Fan-out (chatty services)
Identified from graph: modules with fan-out > 5 making sequential calls.
```bash
# Count HTTP client calls in a single service method
grep -rn -A2 "@GetMapping\|@PostMapping" <java_path>/src --include="*.java" \
  | grep "restTemplate\.\|feignClient\.\|webClient\." | head -30
```
**Risk**: User waits for sum of all downstream latencies.
**Fix**: Parallelise with `CompletableFuture.allOf()` or reactive streams.

### Blocking in Reactive Chain
```bash
grep -rn "\.block()\|\.blockFirst()\|\.blockLast()\|Thread\.sleep" \
  <java_path>/src --include="*.java"
```
**Risk**: Blocks a thread in a non-blocking context. Under load → thread pool exhaustion.
**Fix**: Remove `.block()` entirely; use proper reactive operators.

### Unbounded In-Memory Collections
```bash
grep -rn "new ArrayList<>\|new HashMap<>\|new HashSet<>" <java_path>/src --include="*.java" \
  | grep -v "final.*=.*\[\]\|Collections\." | head -20
```
Flag any collection that is populated from a DB result without a limit.

### Missing Database Indexes (from query patterns)
```bash
# Find queries that filter by non-obvious fields
grep -rn "findBy[A-Z][a-zA-Z]*And\|findBy[A-Z][a-zA-Z]*Or\|@Query.*WHERE" \
  <java_path>/src --include="*.java" | head -30
```
Flag any `findByX` where X is not the primary key — needs an index.

### Large Payload Transfers
```bash
# Find @ResponseBody returning full entities rather than projections
grep -rn "@GetMapping\|@PostMapping" <java_path>/src --include="*.java" -A3 \
  | grep "List<.*Entity\|List<.*Domain\b" | head -20
```
**Risk**: Returns full objects with all fields when only 3 fields are needed.
**Fix**: Create projection DTOs with only required fields.

### Missing Connection Pool Tuning
```bash
grep -rn "spring.datasource\|HikariConfig\|maximum-pool-size\|connection-timeout" \
  <java_path>/src/main/resources --include="*.yml" --include="*.properties"
```
Flag if `maximum-pool-size` is not explicitly set (default = 10, usually too low).

---

## Angular Frontend Performance Patterns

```bash
# Missing trackBy in ngFor (causes full DOM re-render on every change)
grep -rn "*ngFor" <angular_path>/src --include="*.html" \
  | grep -v "trackBy" | head -20

# Deeply nested subscriptions (memory leak risk)
grep -rn "\.subscribe(" <angular_path>/src --include="*.ts" \
  | grep -v "unsubscribe\|takeUntil\|takeUntilDestroyed\|async pipe" | head -30

# HTTP calls in ngOnInit without caching (fetches on every navigation)
grep -rn "ngOnInit\b" <angular_path>/src --include="*.ts" -A10 \
  | grep "http\.\|\.get(\|\.post(\|service\." | head -20

# Large bundle indicators
find <angular_path>/src -name "*.ts" | xargs wc -l | sort -rn | head -10
```

---

## Performance Risk by Graph Metrics

| Graph Metric | Threshold | Performance Risk |
|---|---|---|
| Module fan-out | > 6 | Chatty client — many sync calls per request |
| Longest chain | > 5 hops | High latency under sequential calls |
| Coupling risk (fanIn × fanOut) | > 20 | Bottleneck module — changes affect latency everywhere |
| Circular dependency | Any | Unpredictable latency / deadlock under load |
| Dead module | Any with LOC > 1000 | Wasted memory and startup time |

---

## Load Test Scenarios to Recommend

For each performance gap found, recommend a load test scenario:

| Gap type | Load test scenario |
|---|---|
| N+1 query | Ramp from 100 to 10,000 records; observe DB query count |
| Missing pagination | Request the "list all" endpoint; observe memory and response time |
| Chatty service | 50 concurrent users; observe P95 latency |
| Missing cache | Repeatedly fetch reference data; observe DB call rate |
| Blocking in reactive | 100 concurrent requests; observe thread pool saturation |

Recommended tool: **Gatling** (JVM, integrates with Spring) or **k6** (JS-based, easy to write).
