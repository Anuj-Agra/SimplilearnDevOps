---
mode: 'agent'
description: 'Auto-orchestrate all cross-repo OpenSpec work: detect changes, generate missing specs, propagate proposals, apply code, verify alignment'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---

# Auto-Sync Orchestrator

You are an autonomous orchestrator agent. Run a full analysis of both repos and execute every required action without further prompting. Work through phases in order. Skip any phase where nothing needs to be done.

## Phase 1: Discover State
Read both repos' OpenSpec directories silently. For each repo: list specs/ domains, list active changes/, read tasks.md progress, scan codebase for controllers/endpoints/services/models.

## Phase 2: Generate Missing Specs
If either repo's openspec/specs/ is empty or has fewer domains than the codebase suggests, scan the codebase and generate openspec/specs/<domain>/spec.md files using OpenSpec format (Requirements with Given/When/Then Scenarios). Java specs: API contracts, validation, business logic. Angular specs: user interactions, service integration, data display.

## Phase 2.5: NFR Analysis (Performance & Security)
For every domain spec (whether newly generated or pre-existing), analyze the code for non-functional requirements and **add/update an `## NFR Requirements` section** in each spec:

**Security scans** (Java):
- Authentication & authorization: @PreAuthorize, @Secured, @RolesAllowed, SecurityFilterChain
- Input validation: @Valid, @Pattern, @Email, @Size beyond basic types
- SQL injection protection: PreparedStatement, @Query, parameterized queries
- Crypto & secrets: MessageDigest, BCrypt, PasswordEncoder, KeyStore usage
- CORS, CSRF, rate limiting: @CrossOrigin, csrf(), Bucket4j, Resilience4j
- Audit logging: @Auditable, AuditEventRepository, security event logging
- Sensitive data handling: @JsonIgnore, @ToString.Exclude, PII masking

**Security scans** (Angular):
- Route guards: CanActivate, CanDeactivate, AuthGuard, RoleGuard
- HTTP interceptors: Authorization headers, Bearer tokens, CSRF headers
- XSS protection: DomSanitizer, bypassSecurityTrust, [innerHTML] usage
- Token storage: localStorage/sessionStorage/cookie patterns
- Form validation: Validators, custom validators, async validators

**Performance scans** (Java):
- Caching: @Cacheable, @CacheEvict, Redis/Caffeine/Ehcache
- Async: @Async, CompletableFuture, ExecutorService, @EnableAsync
- DB performance: @Transactional with timeout, FetchType, @EntityGraph, Pageable
- N+1 protection: JOIN FETCH, @BatchSize, @EntityGraph
- Timeouts & resilience: connectTimeout, @Timeout, CircuitBreaker, @Retry
- Bulk operations: saveAll, batchSize, hibernate.jdbc.batch_size
- Monitoring: @Timed, MeterRegistry, Micrometer, @Counted

**Performance scans** (Angular):
- Change detection: ChangeDetectionStrategy.OnPush, trackBy
- Lazy loading: loadChildren, loadComponent, @defer, PreloadingStrategy
- Input debouncing: debounceTime, throttleTime, distinctUntilChanged
- HTTP caching: shareReplay, HttpCache patterns
- Virtual scrolling: cdk-virtual-scroll for large lists
- Bundle optimization: budgets config in angular.json

**For each NFR detected in code**, add an entry to the relevant domain spec with:
- The requirement statement
- Given/When/Then scenario describing the behavior
- An **Evidence** line citing the actual code annotation or pattern

**For each NFR that SHOULD exist but is MISSING**, add a `<!-- REVIEW: ... -->` marker using this risk matrix:

| Endpoint/Component Pattern | Expected Control |
|---|---|
| Admin endpoints (`/api/admin/*`) | Role-based authorization |
| POST/PUT/PATCH endpoints | @Valid on request body |
| Search/list endpoints | Pagination (Pageable) |
| File upload endpoints | Size limits |
| Endpoints accepting user IDs | Ownership/access check |
| Sensitive operations | Audit logging |
| DB-heavy endpoints | @Transactional timeout |
| External API calls | Circuit breaker + timeout |
| Auth/token endpoints | Rate limiting |
| PII-returning endpoints | @JsonIgnore on sensitive fields |
| Angular forms with user input | Validators, XSS protection |
| Angular routes with sensitive data | Route guard |
| Angular tables with large datasets | Pagination or virtual scroll |
| Angular search inputs | Debouncing |
| Auth token storage | httpOnly cookie (not localStorage) |

Do NOT invent performance SLAs (e.g., "shall respond within 200ms") unless the code contains an explicit timeout. For gaps, write the REVIEW marker with a specific recommendation instead.

Update `cross-repo/openspec/specs/contract/spec.md` with a `## Cross-Cutting NFRs` section covering authentication mechanism, rate limits, performance budgets, and audit policies — whatever is consistently applied across endpoints.

## Phase 3: Detect Unlinked Changes
For each active change in repo A, read its proposal.md and delta specs. If it affects the API surface (endpoints, schemas, data contracts), check if repo B has a matching change with the same change-id. Collect all unlinked API-surface changes.

## Phase 4: Propagate Unlinked Changes
For each unlinked change: read ALL source artifacts, scan target repo conventions, create a linked proposal in the target repo with the same change-id (proposal.md with "Linked From" reference, delta specs, design.md, tasks.md).

## Phase 5: Apply Java Tasks
For each linked change with unchecked tasks in Java: scan existing code for conventions, generate/modify controllers, services, DTOs with ALL imports and annotations, check off tasks in tasks.md.

## Phase 6: Apply Angular Tasks
For each linked change with unchecked tasks in Angular: ensure TypeScript types match Java DTOs, generate/modify services, models, components, check off tasks in tasks.md.

## Phase 7: Verify Type Alignment
For each linked change where both sides are applied: verify every field matches (name, type, required/optional), verify endpoint paths match, verify request/response shapes match. Fix any mismatches.

## Phase 8: Update Contract Spec
Update cross-repo/openspec/specs/contract/spec.md with any new/changed endpoints and schemas.

## Phase 9: Gap Detection
Compare specs against code one final time. Flag undocumented endpoints, stale specs, and type mismatches.

## Final Report
Present a comprehensive summary covering:
- Specs generated (functional)
- **NFR coverage per domain** (security: authn/authz/input-validation/rate-limit/audit; performance: pagination/caching/async/timeout/monitoring)
- **Uncovered risks** from Phase 2.5 REVIEW markers, with specific remediation suggestions
- Changes propagated
- Code generated
- Type alignment status
- Contract updates (including cross-cutting NFRs)
- Items needing human review
- Next steps

## Rules
- Be autonomous — don't ask for confirmation between phases
- Be thorough — don't skip files or leave partial work
- Be safe — never overwrite existing code without showing what changed in the report
- Be precise — generated code must have ALL imports, proper types, no placeholders
- Breaking changes pause the chain and get flagged prominently, but non-breaking work continues
