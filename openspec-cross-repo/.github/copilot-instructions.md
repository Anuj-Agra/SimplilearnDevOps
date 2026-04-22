# Cross-Repo OpenSpec — Copilot Instructions

## Context

This workspace links two repositories that share an API boundary:

- **Java Service** (`java-service/`) — Spring Boot backend with OpenSpec initialized
- **Angular App** (`angular-app/`) — Angular 17+ frontend with OpenSpec initialized
- **Cross-Repo Workspace** (`cross-repo/`) — Shared contract spec + linking prompts

Each repo has its own `openspec/` folder with independent specs, changes, and archive. The cross-repo workspace holds the **contract spec** (`openspec/specs/contract/spec.md`) which defines the API surface both repos must agree on.

## Cross-Repo Linking Model

When a change in one repo modifies the API surface (new endpoint, changed schema, removed field), a **linked proposal** should be created in the other repo using the same `change-id`.

## Linking Rules

1. **Same change-id**: If Java proposes `add-kyc-endpoint`, Angular's linked proposal also uses `add-kyc-endpoint`
2. **Cross-reference**: Each linked proposal's `proposal.md` references the source proposal
3. **Contract update**: The shared contract spec is updated when either repo archives a change
4. **Breaking change detection**: Removing endpoints, removing required fields, or changing types must be flagged

## Java Service Conventions

- Scan existing controllers/services/DTOs for naming and style patterns
- Use Lombok if already present (`@Data`, `@Builder`, `@RequiredArgsConstructor`)
- Use Jakarta Validation (`@NotNull`, `@Size`, `@Valid`)
- `ResponseEntity<T>` for controller return types
- Constructor injection only
- Interface + Impl pattern for services
- Package structure: `*.controller`, `*.service`, `*.service.impl`, `*.dto`

## Angular App Conventions

- Scan existing services/models/components for naming and style patterns
- Standalone components (Angular 17+)
- Strict TypeScript — no `any`
- `Observable<T>` return types on service methods
- `@Injectable({ providedIn: 'root' })` for services
- File naming: kebab-case (`account-detail.service.ts`)
- Models in `models/`, services in `services/`

## Type Mapping (Java ↔ TypeScript)

| Java Type | TypeScript Type | OpenSpec Schema |
|-----------|-----------------|-----------------|
| `String` | `string` | `type: string` |
| `Integer`, `int` | `number` | `type: integer` |
| `Long` | `number` | `type: int64` |
| `Double`, `Float` | `number` | `type: number` |
| `Boolean` | `boolean` | `type: boolean` |
| `List<T>` | `T[]` | `type: array` |
| `LocalDate` | `string` | `format: date` |
| `LocalDateTime` | `string` | `format: date-time` |
| `UUID` | `string` | `format: uuid` |
| Custom DTO | Named interface | `$ref: SchemaName` |

## Delta Spec Markers

- `## ADDED Requirements` — new capability
- `## MODIFIED Requirements` — changed existing capability
- `## REMOVED Requirements` — deleted capability
- `## RENAMED Requirements` — renamed (preserves content)

## NFR Requirements (Always Include)

Every domain spec must have an `## NFR Requirements` section covering performance and security. When generating or updating specs, scan the code for:

**Security indicators**:
- Java: `@PreAuthorize`, `@Secured`, `@RolesAllowed`, `@Valid`, `@Pattern`, `@JsonIgnore`, `SecurityFilterChain`, `BCrypt`, `@CrossOrigin`, rate limiters (`Bucket4j`, `Resilience4j`), audit loggers
- Angular: `CanActivate`, `AuthGuard`, `HttpInterceptor`, `DomSanitizer`, token storage patterns, `Validators`

**Performance indicators**:
- Java: `@Cacheable`, `@Async`, `@Transactional(timeout=...)`, `Pageable`, `@EntityGraph`, `JOIN FETCH`, `CircuitBreaker`, `@Retry`, `@Timed`
- Angular: `ChangeDetectionStrategy.OnPush`, `trackBy`, `loadChildren`, `@defer`, `debounceTime`, `shareReplay`, `cdk-virtual-scroll`

**For each NFR detected**, add a requirement with an `**Evidence:**` line citing the actual code pattern.

**For each NFR missing** that the risk matrix suggests should exist, add a `<!-- REVIEW: ... -->` marker with a specific recommendation.

**Risk matrix** (patterns that require NFR protection):
- Admin endpoints → role-based authorization
- Write endpoints (POST/PUT/PATCH) → input validation + rate limiting
- List endpoints → pagination
- File uploads → size limits
- Endpoints accepting user IDs → ownership checks
- DB-heavy endpoints → transaction timeouts
- External API calls → circuit breaker + timeout
- PII-returning endpoints → `@JsonIgnore` on sensitive fields
- Angular routes with sensitive data → route guards
- Angular forms with user input → validators + XSS protection
- Auth tokens → httpOnly cookies (not localStorage)
- Large tables in Angular → virtual scroll or pagination
- Angular search inputs → debouncing

Never invent SLAs (response times, throughput numbers) unless the code contains explicit timeouts or SLA annotations. Mark them as REVIEW items instead.
