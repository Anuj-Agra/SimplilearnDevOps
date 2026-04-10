---
name: reactive-migration-advisor
description: >
  Analyse a Spring MVC codebase and produce a phased plan to migrate to reactive
  Spring WebFlux/Project Reactor for handling high parallel connection counts. Use
  when asked: 'migrate to reactive', 'WebFlux migration', 'reactive Spring',
  'handle more connections', 'non-blocking', 'Project Reactor', 'Mono Flux migration',
  'async reactive', 'blocking vs reactive', 'thread per request bottleneck'.
  Identifies safe vs dangerous migration candidates and blocking code that must change.
---
# Reactive Migration Advisor

Plan a safe migration from Spring MVC (blocking) to WebFlux (reactive/non-blocking).

## Step 1 — Detect Current Stack
```bash
grep -rn "spring-boot-starter-web\b\|spring-webmvc\|DispatcherServlet" \
  . --include="*.xml" --include="*.gradle" --include="*.gradle.kts" | head -10
grep -rn "spring-boot-starter-webflux\|WebFlux\|RouterFunction" \
  . --include="*.xml" --include="*.gradle" | head -10
```

## Step 2 — Identify Blocking Code (MUST fix before going reactive)
```bash
# JDBC / JPA (blocking — requires R2DBC to go reactive)
grep -rn "JpaRepository\|EntityManager\|@Repository.*JPA\|jdbcTemplate\|@Transactional" \
  <java_path> --include="*.java" -l | head -20

# Thread.sleep (hard block)
grep -rn "Thread\.sleep\|Object\.wait\|CountDownLatch\.await\|Future\.get()" \
  <java_path> --include="*.java" | head -20

# Synchronised blocks
grep -rn "synchronized\b" <java_path> --include="*.java" | head -20

# RestTemplate (blocking HTTP client — replace with WebClient)
grep -rn "RestTemplate\|new RestTemplate\|restTemplate\." \
  <java_path> --include="*.java" -l | head -20

# Feign clients (blocking — use reactive Feign or WebClient)
grep -rn "@FeignClient" <java_path> --include="*.java" | head -20
```

## Step 3 — Classify Each Module
```
SAFE to migrate (stateless, no blocking IO):
  → Simple REST endpoints returning DTOs
  → Validation-only services
  → Mapping/transformation logic

NEEDS WORK before migration:
  → JPA repositories → migrate to R2DBC first
  → RestTemplate calls → replace with WebClient
  → Synchronised blocks → redesign as reactive operators

HARD to migrate (may stay blocking):
  → Legacy integrations with blocking SDKs
  → Bulk file processing
  → Complex transaction management
```

## Step 4 — Migration Pattern Guide
For each blocking pattern, provide the reactive equivalent:

```java
// BEFORE (blocking)
public Customer getCustomer(String id) {
  return customerRepository.findById(id)
    .orElseThrow(() -> new NotFoundException(id));
}

// AFTER (reactive)
public Mono<Customer> getCustomer(String id) {
  return customerRepository.findById(id)
    .switchIfEmpty(Mono.error(new NotFoundException(id)));
}
```

Common patterns:
- `Optional<T>` → `Mono<T>`
- `List<T>` → `Flux<T>`
- `void` → `Mono<Void>`
- `try/catch` → `.onErrorMap()` / `.onErrorReturn()`
- `if/else` → `.flatMap()` + `.switchIfEmpty()`

## Step 5 — Migration Roadmap

```
REACTIVE MIGRATION PLAN: [System]
Target: Handle [N]K concurrent connections with [N] threads (instead of 1 thread/request)

Phase 0 — Prerequisites (no user impact):
  → Replace RestTemplate with WebClient in: [list]
  → Replace Feign clients with WebClient in: [list]
  → Add spring-boot-starter-webflux to pom.xml alongside spring-web (coexistence)

Phase 1 — Leaf services (lowest risk):
  → Migrate [stateless services] to return Mono<>/Flux<>
  → Run MVC and WebFlux side-by-side (both supported)

Phase 2 — Repository layer:
  → Migrate JPA to R2DBC for: [list of repositories]
  → Replace @Transactional with reactive transaction operators

Phase 3 — Controllers:
  → Convert @RestController methods to return Mono<>/Flux<>
  → Remove spring-web, keep only spring-webflux

PERFORMANCE PROJECTION:
  Before: [N] threads → max [N] concurrent requests
  After:  [N] event-loop threads → [10-100x] concurrent requests
```
