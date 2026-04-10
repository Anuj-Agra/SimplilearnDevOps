---
name: load-test-generator
description: >
  Generate complete Gatling (Scala/Java) and k6 (JavaScript) load test scripts from
  Spring REST controllers. Produces ramp-up, sustained load, spike, and soak test
  scenarios. Use when asked: 'load tests', 'performance tests', 'Gatling', 'k6',
  'stress test', 'ramp up test', 'spike test', 'soak test', 'load testing script',
  'concurrent users test', 'throughput test', 'performance baseline'. Prioritises
  endpoints by graph fan-in (most-used = most important to test under load).
---
# Load Test Generator (Gatling + k6)

Generate complete load test suites prioritised by endpoint criticality.

## Step 1 — Identify & Prioritise Endpoints
```bash
python3 scripts/project_graph.py --graph repo-graph.json --mode critical --top 10
grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test"
```

## Step 2 — Extract Auth Flow
```bash
grep -rn "@PostMapping.*login\|@PostMapping.*auth\|@PostMapping.*token\|/oauth/token" \
  <java_path> --include="*.java" | head -10
```

## Step 3 — Generate Four Scenario Types

### k6 Script (recommended — simpler syntax)

```javascript
// tests/load/[feature]-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const responseTime = new Trend('response_time', true);

const BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8080';

// ── Scenario Definitions ──────────────────────────────────────────────────
export const options = {
  scenarios: {
    // 1. Ramp-up: find breaking point
    ramp_up: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },   // ramp to 50 users
        { duration: '5m', target: 50 },   // hold
        { duration: '2m', target: 100 },  // ramp to 100
        { duration: '5m', target: 100 },  // hold
        { duration: '2m', target: 0 },    // ramp down
      ],
      exec: 'standardFlow',
    },
    // 2. Spike: sudden traffic burst
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 5 },
        { duration: '10s', target: 200 },  // spike!
        { duration: '1m',  target: 200 },
        { duration: '30s', target: 5 },
      ],
      exec: 'standardFlow',
    },
  },
  thresholds: {
    // SLO enforcement — test fails if these are breached
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    errors: ['rate<0.01'],
    http_req_failed: ['rate<0.01'],
  },
};

// ── Auth Setup ────────────────────────────────────────────────────────────
function getToken() {
  const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    username: __ENV.TEST_USER || 'loadtest@yourorg.com',
    password: __ENV.TEST_PASS,
  }), { headers: { 'Content-Type': 'application/json' } });
  return res.json('token') || res.json('access_token');
}

// ── Main Scenario ─────────────────────────────────────────────────────────
export function standardFlow() {
  const token = getToken();
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'X-Correlation-ID': `load-test-${Date.now()}-${Math.random()}`,
  };

  // [Endpoint 1 — highest fan-in from graph]
  const listRes = http.get(`${BASE_URL}/api/[resource]?page=0&size=20`, { headers });
  check(listRes, {
    'list status 200':    r => r.status === 200,
    'list has content':   r => r.json('content') !== undefined,
    'list response < 1s': r => r.timings.duration < 1000,
  });
  errorRate.add(listRes.status !== 200);
  responseTime.add(listRes.timings.duration);

  sleep(1);  // Think time between requests

  // [Endpoint 2 — create resource]
  const createRes = http.post(`${BASE_URL}/api/[resource]`, JSON.stringify({
    [field1]: `load-test-${Date.now()}`,
    [field2]: 'test-value',
  }), { headers });
  check(createRes, {
    'create status 201': r => r.status === 201,
    'create has id':     r => r.json('id') !== undefined,
  });
  errorRate.add(createRes.status !== 201);

  sleep(2);
}
```

### Gatling Script (Java — integrates with Maven)

```java
// src/test/java/gatling/[Feature]LoadTest.java
public class [Feature]LoadTest extends Simulation {

  private final HttpProtocolBuilder protocol = http
    .baseUrl(System.getProperty("baseUrl", "http://localhost:8080"))
    .acceptHeader("application/json")
    .contentTypeHeader("application/json");

  private final ScenarioBuilder scenario = scenario("[Feature] Load Test")
    .exec(session -> session.set("correlationId",
        "gatling-" + UUID.randomUUID()))
    .exec(http("Authenticate")
        .post("/api/auth/login")
        .body(StringBody("{\"username\":\"${user}\",\"password\":\"${pass}\"}"))
        .check(jmesPath("token").saveAs("token")))
    .pause(1)
    .exec(http("List [Resource]")
        .get("/api/[resource]?page=0&size=20")
        .header("Authorization", "Bearer ${token}")
        .header("X-Correlation-ID", "${correlationId}")
        .check(status().is(200))
        .check(jsonPath("$.content").exists())
        .check(responseTimeInMillis().lt(1000)));

  // Ramp-up scenario
  { setUp(scenario.injectOpen(
      nothingFor(5),
      atOnceUsers(10),
      rampUsers(50).during(120),
      constantUsersPerSec(20).during(300)
    )).protocols(protocol)
    .assertions(
      global().responseTime().percentile(95).lt(500),
      global().failedRequests().percent().lt(1)
    );
  }
}
```

## Step 4 — Output: Test Suite Structure

```
tests/load/
├── k6/
│   ├── [feature]-load-test.js        ← Main scenario
│   ├── [feature]-spike-test.js       ← Spike variant
│   ├── [feature]-soak-test.js        ← 24h soak
│   └── shared/
│       ├── auth.js                   ← Auth helpers
│       └── helpers.js                ← Common checks
├── gatling/
│   └── [Feature]LoadTest.java
└── run-tests.sh                      ← One-command runner

RUN INSTRUCTIONS:
  k6: k6 run --env API_BASE_URL=http://localhost:8080 \
              --env TEST_USER=load@test.com \
              --env TEST_PASS=password \
              k6/[feature]-load-test.js

  Gatling: mvn gatling:test -DbaseUrl=http://localhost:8080

THRESHOLDS ALIGNED TO SLOS:
  P95 < 500ms (from SLO document)
  Error rate < 1%
  P99 < 1000ms
```
