---
mode: 'agent'
description: 'Scan the Java service codebase and generate OpenSpec specs for all discovered domains'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---

# Generate Java Technical Specs

## Task
Scan the Java service and generate openspec/specs/<domain>/spec.md for every domain.

## Scan
1. Find all controllers and endpoints (grep @RestController, @GetMapping, etc.)
2. Find all DTOs, entities, enums (grep class.*Dto, @Entity, public enum)
3. Find security config (grep @PreAuthorize, @Secured, hasRole)
4. Find business logic in services (grep @Service, conditional logic, state transitions)
5. Find validation rules (grep @NotNull, @Size, @Pattern)
6. Find error handlers (grep @ControllerAdvice, @ExceptionHandler)
7. Find scheduled tasks (grep @Scheduled)

## Generate
Group into domains by package structure. For each domain create spec with:
- Requirements for each endpoint (with security, validation scenarios)
- Requirements for data contracts (field types, constraints)
- Requirements for business rules (state transitions, calculations)
- **`## NFR Requirements` section** — scan for @PreAuthorize, @Valid, @Cacheable, @Transactional(timeout), Pageable, @Async, rate limiters, audit loggers. Add requirements with `**Evidence:**` citations. Flag missing controls (write endpoints without rate limiting, admin endpoints without role checks, DB-heavy endpoints without timeouts, list endpoints without pagination) with `<!-- REVIEW: ... -->` markers.
