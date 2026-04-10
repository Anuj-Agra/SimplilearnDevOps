---
name: flaky-test-detector
description: >
  Find tests that pass sometimes and fail other times — without any code change.
  Analyses code patterns to identify flakiness before it poisons your CI pipeline.
  Use when asked: 'flaky tests', 'intermittent failures', 'unreliable tests',
  'test sometimes fails', 'flaky test detection', 'fix flaky tests', 'non-deterministic
  tests', 'test ordering dependency', 'time-dependent tests', 'Thread.sleep in tests',
  'shared test state', 'CI randomly fails'. Produces a prioritised flakiness register
  with specific fixes for each pattern.
---
# Flaky Test Detector

Find tests that will randomly fail and poison CI — before they do it in production builds.

---

## The 8 Flakiness Patterns

### Pattern 1 — Time Dependency (most common)
Tests that depend on `System.currentTimeMillis()`, real dates, or `Thread.sleep`.

```bash
# Java
grep -rn "Thread\.sleep\|System\.currentTimeMillis\|new Date()\|LocalDate\.now()\|\
  LocalDateTime\.now()\|Instant\.now()\|Calendar\.getInstance()" \
  <test_path> --include="*Test*.java" --include="*Spec*.java" | head -30

# Angular
grep -rn "new Date()\|Date\.now()\|setTimeout\|setInterval\|jasmine\.clock\|\
  fakeAsync\|tick(" <angular_path> --include="*.spec.ts" | head -30
```

**Fix**: Inject a `Clock` or `TimeProvider` and mock it in tests.

### Pattern 2 — Ordering Dependency (tests rely on execution order)
Tests that pass only when run after another specific test.

```bash
# Java — shared mutable static state between tests
grep -rn "private static\|static.*List\|static.*Map\|static.*Set\|@BeforeAll.*static" \
  <test_path> --include="*Test*.java" | \
  grep -v "final\|Logger\|log\b\|INSTANCE\|lock" | head -20

# Tests that don't clean up after themselves
grep -rn "@AfterEach\|@After\b\|tearDown\|cleanup\|@AfterAll" \
  <test_path> --include="*Test*.java" | head -10
# Low count relative to @BeforeEach count = missing cleanup

# Missing @DirtiesContext on Spring tests that modify context state
grep -rn "@SpringBootTest\|@SpringRunner" \
  <test_path> --include="*Test*.java" -l | \
  xargs grep -L "@DirtiesContext\|@Transactional" 2>/dev/null | head -15
```

**Fix**: Use `@Transactional` on tests (auto-rollback), or `@DirtiesContext`, or reset state in `@AfterEach`.

### Pattern 3 — Async / Concurrency Race Conditions

```bash
# Java — tests not properly waiting for async completion
grep -rn "CompletableFuture\|@Async\|ExecutorService\|new Thread\|Executors\." \
  <test_path> --include="*Test*.java" | \
  grep -v "\.get()\|\.join()\|await\|CountDownLatch\|awaitTermination" | head -20

# Angular — async tests not properly using done() or async/await
grep -rn "it('.*',\s*function\|it('.*',\s*async" \
  <angular_path> --include="*.spec.ts" | \
  grep -v "async\|done\|fakeAsync\|waitForAsync" | head -20
```

**Fix**: Use `CompletableFuture.get(timeout)`, `CountDownLatch.await(timeout)`, or `@Async` test utilities.

### Pattern 4 — External Resource Dependency

```bash
# Tests hitting real HTTP endpoints
grep -rn "http://\|https://\|new URL(" \
  <test_path> --include="*Test*.java" | \
  grep -v "localhost\|127\.0\.0\.1\|wiremock\|mockserver\|//\|@" | head -20

# Tests hitting real databases (no @DataJpaTest or @Transactional)
grep -rn "@SpringBootTest" <test_path> --include="*Test*.java" -l | \
  xargs grep -L "H2\|TestContainers\|@DataJpaTest\|EmbeddedDatabase\|H2Console" \
  2>/dev/null | head -10

# Real file system access
grep -rn "new File(\|Files\.write\|FileOutputStream\|new FileWriter" \
  <test_path> --include="*Test*.java" | \
  grep -v "//\|TempDir\|tmp\|temp\|@TempDir" | head -20
```

**Fix**: Use `WireMock`, `@DataJpaTest` with H2, Testcontainers, or `@TempDir`.

### Pattern 5 — Port / Resource Contention

```bash
# Tests that bind to fixed ports
grep -rn "new ServerSocket(\|server\.start.*808\|port.*=.*[0-9]\{4\}\|@LocalServerPort" \
  <test_path> --include="*Test*.java" | \
  grep "[0-9]\{4\}" | grep -v "0\b\|random\|0L" | head -10

# Multiple test classes starting embedded servers on same port
grep -rn "@SpringBootTest(webEnvironment\|RANDOM_PORT\|DEFINED_PORT" \
  <test_path> --include="*Test*.java" | head -10
```

**Fix**: Use `webEnvironment = RANDOM_PORT` + `@LocalServerPort` injection.

### Pattern 6 — Non-Deterministic Data (random, UUIDs)

```bash
# Tests using UUID.randomUUID() or Math.random() without seeding
grep -rn "UUID\.randomUUID()\|Math\.random()\|new Random()" \
  <test_path> --include="*Test*.java" | head -20

# Tests asserting on collections without order guarantee
grep -rn "assertEquals.*List\|assertThat.*containsExactly\|\.equals.*list\b" \
  <test_path> --include="*Test*.java" | head -20
```

**Fix**: Use fixed test data (not random), or use `containsExactlyInAnyOrder` for unordered assertions.

### Pattern 7 — Mockito / Spy State Leakage

```bash
# @Mock fields without @ExtendWith(MockitoExtension.class) — stale mocks
grep -rn "@Mock\|@Spy\|@InjectMocks" \
  <test_path> --include="*Test*.java" -l | \
  xargs grep -L "@ExtendWith(MockitoExtension.class)\|MockitoAnnotations.openMocks\|\
  @RunWith(MockitoJUnitRunner" 2>/dev/null | head -10

# verify() without reset between tests — counts accumulate
grep -rn "verify(\|Mockito\.verify(" <test_path> --include="*Test*.java" | \
  grep -v "@BeforeEach\|reset(" | head -20
```

**Fix**: Always use `@ExtendWith(MockitoExtension.class)` — it resets mocks between tests.

### Pattern 8 — Angular: Zone / Change Detection Issues

```bash
# Missing TestBed.flushEffects() or fixture.detectChanges()
grep -rn "fixture\.detectChanges()" \
  <angular_path> --include="*.spec.ts" | wc -l
# Very low count relative to test count = missing change detection calls

# Unresolved promises in tests
grep -rn "Promise\.\|async.*void\|\.then(" \
  <angular_path> --include="*.spec.ts" | \
  grep -v "await\|fakeAsync\|done(" | head -20
```

---

## Step 2 — Score Each Finding

| Pattern | Flakiness rate | Detection confidence | Priority |
|---|---|---|---|
| P1 Thread.sleep / real dates | Very high | High | CRITICAL |
| P2 Static shared state | High | High | CRITICAL |
| P3 Unwaited async | High | Medium | HIGH |
| P4 External HTTP/DB | High | High | HIGH |
| P5 Fixed port binding | Medium | High | HIGH |
| P6 Random data | Medium | Medium | MEDIUM |
| P7 Mockito leakage | Medium | High | MEDIUM |
| P8 Angular zone issues | Low-Med | Medium | MEDIUM |

---

## Step 3 — Output: Flakiness Register

```
FLAKY TEST ANALYSIS: [System]
Tests scanned: [N] | Flakiness risks found: [N]

CRITICAL — Will cause CI failures:
  FT-001 [Thread.sleep in 12 tests]
    Files: OrderServiceTest:142, PaymentTest:89, CustomerTest:203 ...
    Pattern: Tests pause for real time — fail when server is slow
    Fix template:
      // BEFORE
      Thread.sleep(500); // wait for async

      // AFTER (Java)
      Awaitility.await()
        .atMost(5, SECONDS)
        .until(() -> result.isDone());

      // AFTER (Angular)
      fakeAsync(() => {
        component.triggerAsync();
        tick(500);
        expect(component.result).toBeDefined();
      });

  FT-002 [Shared static list in BaseTest]
    File: BaseTest.java:23 — static List<String> processedIds
    Pattern: Tests add to list, later tests see previous test's data
    Fix:
      @AfterEach
      void cleanup() { processedIds.clear(); }
      // Or: make field non-static, instantiate in @BeforeEach

HIGH — Will cause intermittent failures:
  FT-003 [3 tests hit real HTTP endpoint]
    Files: [list]
    Fix: Add WireMock for these endpoints (see external-api-mock-generator skill)

MEDIUM:
  FT-004 [Fixed port 8080 in 5 test classes]
    Fix: Replace with @SpringBootTest(webEnvironment = RANDOM_PORT)

SUMMARY:
  Estimated CI failure rate (current):  ~[N]% of builds
  Estimated CI failure rate (after fix): < 1%
  Fix priority: FT-001 → FT-002 → FT-003 → FT-004
```
