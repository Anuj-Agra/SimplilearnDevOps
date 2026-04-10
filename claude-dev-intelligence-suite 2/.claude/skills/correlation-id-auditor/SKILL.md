---
name: correlation-id-auditor
description: >
  Verify that correlation IDs are generated at entry points and propagated through
  every downstream call, async thread handoff, Kafka message, and log statement.
  Use when asked: 'correlation ID', 'trace propagation', 'request tracing', 'MDC
  propagation', 'traceId missing', 'requestId not propagated', 'logs not correlated',
  'distributed tracing gaps', 'async context loss', 'MDC cleared in async'. Missing
  propagation makes debugging parallel-connection production issues impossible.
---
# Correlation ID & Trace Propagation Auditor

Ensure every request can be traced end-to-end through logs and services.

## Step 1 — Entry Point Generation
```bash
# Servlet filter / interceptor generating the ID
grep -rn "X-Correlation-ID\|correlationId\|requestId\|traceId\|MDC\.put\|MDC.put" \
  <java_path> --include="*.java" | grep -i "filter\|interceptor\|OncePerRequest" | head -20

# WebFlux equivalent
grep -rn "ServerWebExchangeUtils\|ExchangeFilterFunction\|WebFilter" \
  <java_path> --include="*.java" | head -10
```

## Step 2 — HTTP Propagation (outbound calls)
```bash
# Correlation ID passed in outbound HTTP headers
grep -rn "HttpHeaders\|header\|setHeader\|exchange\|getHeaders" \
  <java_path> --include="*.java" | \
  grep -i "correlation\|trace\|request.id\|X-Request\|X-B3" | head -20

# RestTemplate / WebClient interceptors that add headers
grep -rn "ClientHttpRequestInterceptor\|ExchangeFilterFunction\|\
  defaultHeader\|header.*MDC\|MDC.*header" \
  <java_path> --include="*.java" | head -20
```

## Step 3 — Async Thread Propagation
```bash
# @Async methods — MDC not automatically propagated across thread boundaries
grep -rn "@Async" <java_path> --include="*.java" -l | \
  xargs grep -L "MDCContext\|TaskDecorator\|MDCAdapter\|ContextSnapshot" 2>/dev/null

# CompletableFuture.runAsync — bare thread executor loses MDC
grep -rn "CompletableFuture\.runAsync\|CompletableFuture\.supplyAsync" \
  <java_path> --include="*.java" | \
  grep -v "executor\|Executor\|MDC" | head -20

# @Scheduled jobs — no request context
grep -rn "@Scheduled" <java_path> --include="*.java" -A5 | \
  grep -v "MDC\|correlationId\|UUID\|requestId" | head -20
```

## Step 4 — Kafka/Messaging Propagation
```bash
# Correlation ID in Kafka headers
grep -rn "ProducerRecord\|ConsumerRecord\|MessageBuilder\|@Header" \
  <java_path> --include="*.java" | \
  grep -i "correlation\|trace\|header" | head -20
```

## Step 5 — Log Statement Coverage
```bash
# Log statements that include correlationId
grep -rn "log\.\(info\|warn\|error\|debug\)" <java_path> --include="*.java" | \
  grep "correlationId\|requestId\|traceId\|MDC" | wc -l

# Log statements WITHOUT (could be missing it)
grep -rn "log\.\(info\|warn\|error\)" <java_path> --include="*.java" | wc -l
```

## Output + Generated Fix

```
CORRELATION ID AUDIT: [System]

ENTRY POINT: [OK / MISSING]
  CORR-001: No MDC filter found — correlation ID never generated
    Fix: Add CorrelationIdFilter (generated in observability-gap-detector)

PROPAGATION GAPS:
  CORR-002 [CRITICAL]: @Async methods in [Class] lose MDC context
    Risk: Async log entries have no correlationId — cannot link to parent request
    Fix: Configure TaskDecorator:

    @Bean
    public TaskExecutor asyncExecutor() {
      ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
      executor.setTaskDecorator(runnable -> {
        Map<String, String> mdc = MDC.getCopyOfContextMap();
        return () -> {
          MDC.setContextMap(mdc != null ? mdc : Collections.emptyMap());
          try { runnable.run(); } finally { MDC.clear(); }
        };
      });
      return executor;
    }

  CORR-003 [HIGH]: Kafka producer does not include correlationId in headers
    Fix: Add header in KafkaTemplate send:
    record.headers().add("X-Correlation-ID",
      MDC.get("correlationId").getBytes(StandardCharsets.UTF_8));

HTTP OUTBOUND: [OK / MISSING]
  CORR-004 [HIGH]: RestTemplate does not propagate X-Correlation-ID
    Fix: Add ClientHttpRequestInterceptor to inject MDC value into request header
```
