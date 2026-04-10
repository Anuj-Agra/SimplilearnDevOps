---
name: circuit-breaker-auditor
description: >
  Map every outbound integration point and verify circuit breaker protection exists.
  Unprotected calls to external systems cause cascading failures under parallel load.
  Use when asked: 'circuit breaker', 'cascading failure', 'resilience', 'fallback',
  'Resilience4j', 'protect downstream calls', 'service resilience', 'failover',
  'circuit breaker missing', 'fault tolerance'. Produces @CircuitBreaker scaffold
  for every unprotected call found via graph + code analysis.
---
# Circuit Breaker Coverage Auditor

Map every integration point and generate Resilience4j circuit breaker configuration.

## Step 1 — Find All Integration Points
```bash
# From graph — modules with outbound edges to external-looking nodes
python3 scripts/project_graph.py --graph repo-graph.json --mode entry-points 2>/dev/null

# From code — every outbound HTTP, messaging, DB call
grep -rn "@FeignClient\|RestTemplate\|WebClient\|HttpClient" \
  <java_path> --include="*.java" -l | head -20

grep -rn "rabbitTemplate\|kafkaTemplate\|sqsClient\|snsClient" \
  <java_path> --include="*.java" -l | head -10
```

## Step 2 — Check Circuit Breaker Coverage
```bash
# Existing circuit breakers
grep -rn "@CircuitBreaker\|@HystrixCommand\|CircuitBreakerFactory\|\
  CircuitBreaker\.decorateSupplier\|@Bulkhead" \
  <java_path> --include="*.java" | head -40

# Methods calling external services — cross-reference with above
grep -rn "\.exchange\(\|\.get\(\|\.post\(\|\.getForObject\|\.postForObject" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -40
```

## Step 3 — Generate Circuit Breaker Scaffold

For each unprotected external call, generate:

```java
// Generated @CircuitBreaker scaffold for [ServiceName]
@Service
public class [ServiceName]Client {

    private final CircuitBreaker circuitBreaker;
    private final WebClient webClient;

    public [ServiceName]Client(CircuitBreakerRegistry registry, WebClient.Builder builder) {
        this.circuitBreaker = registry.circuitBreaker("[service-name]");
        this.webClient = builder.baseUrl("${[service].base-url}").build();
    }

    public [ReturnType] call[Operation]([params]) {
        Supplier<[ReturnType]> supplier = CircuitBreaker
            .decorateSupplier(circuitBreaker, () -> doCall([params]));
        return Try.ofSupplier(supplier)
            .recover(CallNotPermittedException.class, ex -> fallback([params]))
            .recover(Exception.class, ex -> fallback([params]))
            .get();
    }

    private [ReturnType] fallback([params]) {
        // Return cached data, default value, or throw BusinessException
        log.warn("Circuit breaker open for [service-name] — returning fallback");
        return [fallback value];
    }
}
```

## Step 4 — Output Report

```
CIRCUIT BREAKER AUDIT: [System]

UNPROTECTED INTEGRATION POINTS:
  CB-001 [CRITICAL]: [ServiceName].call[X]() → [External Service]
    Risk: If [External Service] is slow, thread pool exhausted in [N] seconds
    Fallback strategy: [cached data / default / graceful error]
    Generated config: (see application.yml below)

  CB-002 [CRITICAL]: [FeignClient] → [Payment Processor]
    Risk: Payment processor timeout cascades to order service
    Fallback: Return "Payment Pending" status, retry asynchronously

PROTECTED (correctly configured):
  ✅ [ServiceName] — circuit breaker with 50% failure threshold, 10s wait

GENERATED application.yml:
resilience4j.circuitbreaker.instances:
  [service-name]:
    slidingWindowType: COUNT_BASED
    slidingWindowSize: 20
    failureRateThreshold: 50
    slowCallRateThreshold: 80
    slowCallDurationThreshold: 3s
    waitDurationInOpenState: 30s
    permittedNumberOfCallsInHalfOpenState: 5
    automaticTransitionFromOpenToHalfOpenEnabled: true
```
