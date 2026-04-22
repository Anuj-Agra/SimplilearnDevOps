---
mode: 'agent'
description: 'Analyze code for performance and security concerns, then add missing NFR requirements to OpenSpec specs'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---

# NFR Gap Analyzer — Performance & Security

## Purpose

Functional requirements describe *what* the system does. NFRs (Non-Functional Requirements) describe *how well* and *how safely*. This command scans both repos for performance and security indicators, compares against the specs, and **adds missing NFR requirements** to the relevant domain specs.

## Two-Stage Approach

### Stage 1: Detect NFRs Present in Code (implicit specs)
Find evidence in the code of performance/security concerns that exist but aren't specified.

### Stage 2: Detect NFRs Missing From Code (uncovered risks)
Flag code patterns that *should* have NFR protections but don't — these become REVIEW items.

---

## Stage 1a: Security Detection in Java

Scan for security patterns and extract the implicit requirements:

```
# Authentication & Authorization
grep -rn "@PreAuthorize\|@Secured\|@RolesAllowed\|hasRole\|hasAuthority\|@AuthenticationPrincipal" <java-path> --include="*.java"

# Security config
grep -rn "SecurityFilterChain\|WebSecurityConfigurerAdapter\|@EnableWebSecurity\|authorizeRequests\|authorizeHttpRequests" <java-path> --include="*.java"

# Input validation beyond @Valid
grep -rn "@Pattern\|@Email\|@Size\|Pattern.compile\|String.replaceAll\|HtmlUtils" <java-path> --include="*.java"

# SQL injection protections
grep -rn "PreparedStatement\|@Query\|EntityManager\|createQuery\|createNativeQuery" <java-path> --include="*.java"

# Crypto and secrets
grep -rn "MessageDigest\|BCrypt\|PasswordEncoder\|@Value.*\${\|KeyStore\|Cipher\|SecretKey" <java-path> --include="*.java"

# CORS and CSRF
grep -rn "@CrossOrigin\|CorsConfiguration\|csrf()\|CsrfFilter\|SameSite" <java-path> --include="*.java"

# Rate limiting
grep -rn "Bucket4j\|RateLimiter\|@RateLimited\|Resilience4j" <java-path> --include="*.java"

# Audit logging
grep -rn "AuditEventRepository\|@Auditable\|audit.log\|SecurityEvent" <java-path> --include="*.java"

# Sensitive data handling
grep -rn "@JsonIgnore\|@ToString.Exclude\|mask\|redact\|PII" <java-path> --include="*.java"
```

For each finding, record:
- **Endpoint** affected (if applicable)
- **Control type** (authn, authz, input-validation, rate-limit, audit, crypto, etc.)
- **Evidence** (the actual annotation or code pattern)

## Stage 1b: Security Detection in Angular

```
# Route guards
grep -rn "CanActivate\|CanDeactivate\|CanLoad\|AuthGuard\|RoleGuard" <angular-path> --include="*.ts"

# HTTP interceptors (auth tokens, security headers)
grep -rn "HttpInterceptor\|Authorization\|Bearer\|X-CSRF\|withCredentials" <angular-path> --include="*.ts"

# Content Security Policy, XSS protection
grep -rn "DomSanitizer\|bypassSecurityTrust\|innerHTML\|\[innerHTML\]" <angular-path> --include="*.ts"

# Storage of sensitive data
grep -rn "localStorage\|sessionStorage\|document.cookie" <angular-path> --include="*.ts"

# OAuth/OIDC flows
grep -rn "angular-oauth2\|msal\|OAuthService\|MsalService\|AuthService" <angular-path> --include="*.ts"

# Form validation
grep -rn "Validators\.\|customValidator\|asyncValidator" <angular-path> --include="*.ts"
```

## Stage 1c: Performance Detection in Java

```
# Caching
grep -rn "@Cacheable\|@CacheEvict\|@CachePut\|Cache\|Redis\|Caffeine\|Ehcache" <java-path> --include="*.java"

# Async and threading
grep -rn "@Async\|CompletableFuture\|ExecutorService\|@EnableAsync\|ThreadPoolTaskExecutor" <java-path> --include="*.java"

# Database performance
grep -rn "@Transactional\|FetchType\.\|@BatchSize\|@EntityGraph\|Pageable\|Page<\|Slice<" <java-path> --include="*.java"

# N+1 protection
grep -rn "JOIN FETCH\|@EntityGraph\|@Fetch\|FetchMode" <java-path> --include="*.java"

# Timeouts
grep -rn "connectTimeout\|readTimeout\|@Timeout\|\.timeout(\|CircuitBreaker\|@Retry" <java-path> --include="*.java"

# Bulk operations
grep -rn "saveAll\|batchSize\|BulkRequest\|hibernate\.jdbc\.batch_size" <java-path> --include="*.java"

# Connection pooling
grep -rn "HikariCP\|maximum-pool-size\|DataSourceBuilder\|connection-pool" <java-path> --include="*.java"

# Monitoring and metrics
grep -rn "@Timed\|MeterRegistry\|Micrometer\|@Counted\|Prometheus" <java-path> --include="*.java"
```

## Stage 1d: Performance Detection in Angular

```
# Change detection optimization
grep -rn "ChangeDetectionStrategy\.OnPush\|trackBy\|markForCheck\|detectChanges" <angular-path> --include="*.ts"

# Lazy loading
grep -rn "loadChildren\|loadComponent\|@defer\|PreloadingStrategy" <angular-path> --include="*.ts"

# Debouncing user input
grep -rn "debounceTime\|throttleTime\|distinctUntilChanged" <angular-path> --include="*.ts"

# HTTP caching
grep -rn "shareReplay\|cache\|HttpCache" <angular-path> --include="*.ts"

# Virtual scrolling
grep -rn "cdk-virtual-scroll\|VirtualScrollStrategy" <angular-path> --include="*.ts"

# Bundle optimization
grep -rn "budgets\|optimization\|sourceMap" <angular-path> --include="*.json"
```

---

## Stage 2: Detect MISSING NFRs (Uncovered Risks)

For each endpoint and user-facing component, check against this risk matrix:

### Java Endpoint Risk Checklist

| Endpoint Pattern | Required Controls | Check |
|---|---|---|
| Any endpoint under `/api/admin/*` or similar | Role-based auth | Has `@PreAuthorize` or `hasRole`? |
| POST/PUT/PATCH endpoints | Input validation | Has `@Valid` on request body? |
| Search/list endpoints | Pagination | Uses `Pageable`? |
| File upload endpoints | Size limits | Has `@Size` or `MultipartConfig`? |
| Endpoints returning large collections | Pagination + fetch strategy | Uses `Page<>` or has `@EntityGraph`? |
| Endpoints accepting user-provided IDs | Ownership/access check | Validates user can access that entity? |
| Endpoints with sensitive operations | Audit logging | Logs the action? |
| Database-heavy endpoints | Timeout + transaction scope | Has `@Transactional(timeout=...)`? |
| External API calls | Circuit breaker + timeout | Uses `Resilience4j` or similar? |
| Token/auth endpoints | Rate limiting | Has rate limit annotation? |
| PII-returning endpoints | `@JsonIgnore` on sensitive fields, HTTPS enforcement | Masks/filters sensitive data? |

### Angular Component Risk Checklist

| Component Pattern | Required Controls | Check |
|---|---|---|
| Forms accepting user input | Input sanitization | Uses Validators, avoids `[innerHTML]` with user data? |
| Routes with sensitive data | Route guard | Has `canActivate: [AuthGuard]`? |
| Components making HTTP calls | Error handling | Has `catchError` in service? |
| Components with tables/lists | Pagination or virtual scroll | For large datasets? |
| Components with search inputs | Debouncing | Has `debounceTime`? |
| Token storage | Secure storage | Uses httpOnly cookies, not localStorage for tokens? |
| Dynamic content rendering | XSS protection | Uses `DomSanitizer` when accepting HTML? |

---

## Stage 3: Generate NFR Spec Entries

For each domain spec in both repos, add/update an `## NFR Requirements` section.

### Example Output — Java `openspec/specs/accounts/spec.md`

```markdown
## NFR Requirements

### Requirement: Account endpoints require authentication
All `/api/accounts/*` endpoints shall reject unauthenticated requests.

#### Scenario: Unauthenticated request
- Given no valid auth token is provided
- When any `/api/accounts/*` endpoint is called
- Then the system returns HTTP 401 Unauthorized
- And no account data is exposed

**Evidence**: `@PreAuthorize("isAuthenticated()")` on `AccountsController`

### Requirement: Account listing supports pagination
The `GET /api/accounts` endpoint shall limit response size via pagination.

#### Scenario: Request without page parameters
- Given no pagination parameters are provided
- When the endpoint is called
- Then the system returns the first 20 accounts
- And includes pagination metadata (total, pageSize, pageNumber)

**Evidence**: `Pageable pageable` parameter in `AccountsController.listAccounts()`

### Requirement: Account creation rate-limited
The `POST /api/accounts` endpoint shall limit creation rate per authenticated user.

<!-- REVIEW: No rate limiting detected in code. Recommend adding Bucket4j or Resilience4j. -->

### Requirement: Account search response time
The `GET /api/accounts/search` endpoint shall respond within an acceptable time budget.

<!-- REVIEW: No timeout or performance SLA defined. Recommend @Transactional(timeout=5) or explicit SLA in spec. -->
```

### Example Output — Angular `openspec/specs/accounts/spec.md`

```markdown
## NFR Requirements

### Requirement: Account pages require authentication
All routes under `/accounts` shall require a valid session.

#### Scenario: Unauthenticated access attempt
- Given the user is not authenticated
- When the user navigates to `/accounts`
- Then the router redirects to the login page
- And the intended URL is preserved for post-login redirect

**Evidence**: `canActivate: [AuthGuard]` on accounts route

### Requirement: Account list uses OnPush change detection
The accounts list component shall use OnPush for performance.

**Evidence**: `changeDetection: ChangeDetectionStrategy.OnPush` on `AccountsListComponent`

### Requirement: Account search input is debounced
User input in the search field shall not trigger an API call on every keystroke.

#### Scenario: Rapid typing
- Given the user types in the search input
- When characters are entered rapidly
- Then API calls are debounced with a 300ms delay
- And only the final query is sent

**Evidence**: `debounceTime(300)` in search pipe

### Requirement: Auth tokens stored securely
Authentication tokens shall not be accessible to client-side JavaScript.

<!-- REVIEW: Token currently stored in localStorage — consider httpOnly cookie for XSS protection. -->
```

---

## Stage 4: Update Contract Spec

Add a **Cross-Cutting NFRs** section to `cross-repo/openspec/specs/contract/spec.md`:

```markdown
## Cross-Cutting NFRs

### Authentication
- Mechanism: <detected from code: JWT / OAuth / session>
- Token location: <Authorization header / cookie>
- Token refresh: <if detected>

### Rate Limits
- Default: <if detected>
- Per-endpoint overrides: <list>

### Performance Budgets
- API response time: <if defined>
- Angular bundle size: <if defined in budgets>
- Database query timeout: <if @Transactional timeout detected>

### Audit & Compliance
- Logged events: <list of @Auditable or equivalent>
- PII handling: <fields marked @JsonIgnore or equivalent>
```

---

## Stage 5: Final Report

```
## NFR Analysis Complete

### 🔒 Security Coverage
| Domain | Authn | Authz | Input Validation | Rate Limit | Audit |
|--------|-------|-------|------------------|-----------|-------|
| accounts | ✅ | ✅ | ✅ | ⚠️ Missing | ⚠️ Missing |
| kyc | ✅ | ✅ | ✅ | ✅ | ✅ |
| reports | ✅ | ⚠️ | ✅ | ⚠️ Missing | ⚠️ Missing |

### ⚡ Performance Coverage
| Domain | Pagination | Caching | Async | Timeout | Monitoring |
|--------|-----------|---------|-------|---------|------------|
| accounts | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| kyc | ✅ | ⚠️ | ⚠️ | ✅ | ✅ |
| reports | ⚠️ | ✅ | ✅ | ⚠️ | ✅ |

### 📝 NFR Requirements Added
- Java specs: N new NFR requirements across M domains
- Angular specs: N new NFR requirements across M domains

### 🚨 Uncovered Risks (REVIEW items)
1. **accounts/create endpoint** — no rate limiting (recommend Bucket4j)
2. **reports/export endpoint** — no pagination on potentially large datasets
3. **Angular auth token** — stored in localStorage (XSS risk)
4. **reports/download endpoint** — no role check, any authenticated user can access

### 📋 Contract Updated
- Cross-cutting NFRs section added with N entries

### 🔧 Suggested Remediations
1. Add rate limiting to write endpoints (POST/PUT/PATCH)
2. Move auth tokens to httpOnly cookies
3. Add pagination to `reports/export`
4. Add role-based access to `reports/download`
```

---

## Rules

- **Evidence first**: For every NFR requirement added, cite the actual code annotation or pattern that enforces it
- **Mark gaps honestly**: If a control is missing, use `<!-- REVIEW: ... -->` with a specific recommendation
- **Don't invent SLAs**: Don't write "shall respond in 200ms" unless the code has an explicit timeout. Instead, mark it as REVIEW and suggest.
- **Separate positive and negative findings**: Implicit-specs (derived from code) vs uncovered-risks (missing from code) are different categories
- **Be domain-specific**: Group NFRs by domain spec, not one giant NFR file
