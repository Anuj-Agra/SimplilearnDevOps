---
name: external-api-mock-generator
description: >
  Generate WireMock stub mappings and Testcontainers setup for every external API
  the system calls, including realistic error scenarios. Use when asked: 'mock
  external API', 'WireMock stubs', 'mock server', 'stub external service',
  'test without external dependency', 'mock payment gateway', 'mock third party',
  'contract mock', 'API simulation', 'offline testing', 'Testcontainers WireMock'.
  Enables Angular team and integration tests to run without real external dependencies.
  Covers success, timeout, rate-limit, partial-response, and server-error scenarios.
---
# External API Mock Generator

Generate complete WireMock stubs for every external integration point.

---

## Step 1 — Discover External Integrations

```bash
# External HTTP calls (not to internal modules)
grep -rn "restTemplate\.\|webClient\.\|@FeignClient\|HttpClient\.\|OkHttpClient" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -40

# Base URLs for external systems
grep -rn "base-url\|baseUrl\|BASE_URL\|\.url\|endpoint\." \
  <java_path>/src/main/resources --include="*.yml" --include="*.properties" | \
  grep -v "localhost\|127\.0\.0\|actuator\|swagger" | head -30

# Feign client definitions
grep -rn "@FeignClient" <java_path> --include="*.java" -A5 | head -60

# Angular external calls
grep -rn "http\.\(get\|post\|put\|delete\)" \
  <angular_path>/src --include="*.ts" | \
  grep "http\|https" | grep -v "localhost" | head -20
```

---

## Step 2 — Generate WireMock Stubs Per Integration

For each external service, generate these stub scenarios:

### 2A: Happy Path Stubs

```json
// stubs/[service-name]/[operation]-success.json
{
  "request": {
    "method": "GET",
    "urlPattern": "/api/[resource]/[^/]+"
  },
  "response": {
    "status": 200,
    "headers": {
      "Content-Type": "application/json",
      "X-Request-ID": "{{randomValue type='UUID'}}"
    },
    "jsonBody": {
      "id": "{{request.pathSegments.[1]}}",
      "[field1]": "[realistic example value]",
      "[field2]": "[realistic example value]",
      "status": "ACTIVE",
      "timestamp": "{{now format='yyyy-MM-dd\\'T\\'HH:mm:ss\\'Z\\''}}"
    },
    "transformers": ["response-template"]
  }
}
```

### 2B: Error Scenario Stubs (one per type)

```json
// stubs/[service-name]/timeout.json
{
  "request": { "method": "GET", "urlPattern": "/api/[resource]/timeout-.*" },
  "response": { "status": 200, "fixedDelayMilliseconds": 30000 }
}

// stubs/[service-name]/rate-limited.json
{
  "request": { "method": "GET", "urlPattern": "/api/[resource]/.*",
    "headers": { "X-Test-Scenario": { "equalTo": "rate-limited" } } },
  "response": {
    "status": 429,
    "headers": {
      "Content-Type": "application/json",
      "Retry-After": "60"
    },
    "jsonBody": { "error": "Too Many Requests", "retryAfter": 60 }
  }
}

// stubs/[service-name]/server-error.json
{
  "request": { "urlPattern": "/api/[resource]/error-.*" },
  "response": { "status": 500,
    "jsonBody": { "error": "Internal Server Error", "message": "Unexpected error" }
  }
}

// stubs/[service-name]/partial-response.json
{
  "request": { "urlPattern": "/api/[resource]/partial-.*" },
  "response": { "status": 200,
    "jsonBody": { "id": "partial-123" }
    // Note: required fields missing — tests consumer's null handling
  }
}

// stubs/[service-name]/not-found.json
{
  "request": { "urlPattern": "/api/[resource]/not-found-.*" },
  "response": { "status": 404,
    "jsonBody": { "error": "Not Found", "message": "Resource not found" }
  }
}
```

---

## Step 3 — Generate Testcontainers Setup

```java
// src/test/java/config/WireMockConfig.java
@TestConfiguration
public class WireMockConfig {

    @Bean(initMethod = "start", destroyMethod = "stop")
    public WireMockServer [serviceName]MockServer() {
        WireMockServer server = new WireMockServer(
            WireMockConfiguration.wireMockConfig()
                .port(0) // random port
                .usingFilesUnderDirectory("src/test/resources/stubs/[service-name]")
        );
        return server;
    }

    @Bean
    @Primary
    public [ServiceName]Client [serviceName]Client(
            @Qualifier("[serviceName]MockServer") WireMockServer server) {
        return [ServiceName]Client.create("http://localhost:" + server.port());
    }
}

// Usage in tests
@SpringBootTest
@Import(WireMockConfig.class)
class [Feature]IntegrationTest {

    @Autowired
    private WireMockServer [serviceName]MockServer;

    @Test
    void handles_timeout_from_external_service() {
        // Arrange: configure specific stub for this test
        [serviceName]MockServer.stubFor(
            get(urlPathMatching("/api/[resource]/.*"))
                .willReturn(aResponse().withFixedDelay(30_000))
        );
        // Act + Assert: verify circuit breaker or timeout behaviour
    }
}
```

---

## Step 4 — Angular Mock Service

```typescript
// src/test/mocks/[service-name].mock.ts
import { of, throwError, delay } from 'rxjs';

export const [ServiceName]MockService = {
  // Happy path
  get[Resource]: (id: string) => of({
    id,
    [field1]: '[realistic value]',
    status: 'ACTIVE'
  }).pipe(delay(50)), // realistic latency

  // Simulate timeout
  get[Resource]Timeout: () =>
    of(null).pipe(delay(30000)),

  // Simulate error
  get[Resource]Error: () =>
    throwError(() => ({ status: 500, message: 'Server error' })),

  // Simulate not found
  get[Resource]NotFound: () =>
    throwError(() => ({ status: 404, message: 'Not found' })),
};

// Usage in component specs
TestBed.configureTestingModule({
  providers: [
    { provide: [ServiceName]Service, useValue: [ServiceName]MockService }
  ]
});
```

---

## Step 5 — Mock Coverage Matrix

```
MOCK COVERAGE: [System]

External dependencies mocked:
┌─────────────────────┬───────┬─────────┬────────┬────────┬────────┬──────────┐
│ Service             │ Happy │ Timeout │ 429    │ 500    │ 404    │ Partial  │
├─────────────────────┼───────┼─────────┼────────┼────────┼────────┼──────────┤
│ Payment Gateway     │  ✅   │   ✅    │   ✅   │   ✅   │   ✅   │   ✅     │
│ KYC Provider        │  ✅   │   ✅    │   ✅   │   ✅   │   ✅   │   ⚠️ TODO│
│ Address Validator   │  ✅   │   ❌    │   ❌   │   ✅   │   ✅   │   ❌     │
└─────────────────────┴───────┴─────────┴────────┴────────┴────────┴──────────┘

Run mocked tests:
  mvn test -Dspring.profiles.active=mock
  npx playwright test --project=ui-with-mocks
```
