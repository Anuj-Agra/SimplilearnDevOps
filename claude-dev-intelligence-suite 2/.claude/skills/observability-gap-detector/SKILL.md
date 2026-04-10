---
name: observability-gap-detector
description: >
  Find missing structured logging, metrics instrumentation, distributed tracing,
  and health endpoints. You cannot diagnose production issues under parallel load
  without these. Use when asked: 'observability', 'logging gaps', 'missing metrics',
  'distributed tracing', 'OpenTelemetry', 'Micrometer', 'Prometheus', 'health checks',
  'structured logging', 'correlation ID', 'no monitoring', 'blind in production',
  'missing instrumentation', 'actuator config'. Generates instrumentation boilerplate.
---
# Observability Gap Detector

Find every missing observability instrument and generate the boilerplate to add it.

## Step 1 — Structured Logging
```bash
# Check log format (JSON preferred for parallel systems)
grep -rn "logback\|log4j2\|logging.pattern\|JsonLayout\|LogstashEncoder" \
  . --include="*.xml" --include="*.yml" --include="*.properties" | head -20

# Check for correlation ID in log output
grep -rn "MDC\.\|correlationId\|traceId\|requestId\|X-Correlation-ID" \
  <java_path> --include="*.java" | head -20

# Check for PII in logs (security + GDPR)
grep -rn "log\.\(info\|debug\|warn\)" <java_path> --include="*.java" | \
  grep -i "password\|email\|phone\|ssn\|card" | head -20
```

## Step 2 — Metrics
```bash
# Micrometer / Prometheus
grep -rn "MeterRegistry\|@Timed\|Counter\|Gauge\|Timer\|DistributionSummary\|\
  spring.boot.actuator\|management.metrics\|prometheus" \
  . --include="*.java" --include="*.yml" --include="*.properties" | head -30

# Custom business metrics (not just technical)
grep -rn "meterRegistry\.counter\|meterRegistry\.timer\|meterRegistry\.gauge" \
  <java_path> --include="*.java" | head -20
```

## Step 3 — Distributed Tracing
```bash
# OpenTelemetry / Sleuth / Zipkin
grep -rn "opentelemetry\|spring-cloud-sleuth\|brave\|zipkin\|jaeger\|\
  @WithSpan\|Tracer\|Span\|SpanContext\|OTEL_" \
  . --include="*.xml" --include="*.gradle" --include="*.yml" --include="*.java" | head -30
```

## Step 4 — Health & Readiness
```bash
# Actuator endpoints
grep -rn "management.endpoints\|actuator\|health\|readiness\|liveness\|\
  HealthIndicator\|@HealthEndpoint" \
  . --include="*.yml" --include="*.properties" --include="*.java" | head -20
```

## Step 5 — Output + Generated Boilerplate

```
OBSERVABILITY GAP REPORT: [System]

STRUCTURED LOGGING:
  OBS-001 [HIGH]: Logs are not in JSON format — hard to parse in log aggregators
    Fix: Add logback-spring.xml with LogstashEncoder (generated below)

  OBS-002 [CRITICAL]: No correlation ID in logs — cannot trace a request
    Fix: Add MDCFilter to inject X-Correlation-ID into MDC on every request

METRICS:
  OBS-003 [HIGH]: No custom business metrics defined
    Missing: Order submission rate, processing time, failure rate
    Fix: Add @Timed annotations + custom counters (generated below)

  OBS-004 [MEDIUM]: No SLO-aligned latency histograms
    Fix: Add histogram buckets at 100ms, 250ms, 500ms, 1s, 2s, 5s

DISTRIBUTED TRACING:
  OBS-005 [HIGH]: No distributed tracing configured
    Impact: Cannot correlate logs across services for a single user request
    Fix: Add spring-boot-starter-actuator + micrometer-tracing-bridge-otel

HEALTH CHECKS:
  OBS-006 [MEDIUM]: Liveness and readiness probes not differentiated
    Fix: Configure separate /actuator/health/liveness and /actuator/health/readiness

GENERATED CODE:

// MDC Correlation Filter (add to filter chain)
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorrelationIdFilter extends OncePerRequestFilter {
  @Override
  protected void doFilterInternal(HttpServletRequest req,
      HttpServletResponse res, FilterChain chain) throws ... {
    String correlationId = Optional.ofNullable(
      req.getHeader("X-Correlation-ID")).orElse(UUID.randomUUID().toString());
    MDC.put("correlationId", correlationId);
    res.setHeader("X-Correlation-ID", correlationId);
    try { chain.doFilter(req, res); }
    finally { MDC.clear(); }
  }
}
```
