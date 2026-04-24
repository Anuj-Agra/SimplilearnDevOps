# Cross-Repo Quality Gate Checklist

Use this checklist when reviewing any story that spans both repos.

## API Contract Alignment
- [ ] Every Java endpoint has a matching Angular service method
- [ ] HTTP methods match (GET↔get, POST↔post, etc.)
- [ ] URL paths match exactly (including path parameters)
- [ ] Query parameters match in name and type

## Type Alignment
- [ ] Every Java DTO field has a matching TypeScript interface field
- [ ] Field names are identical (camelCase in both)
- [ ] Types map correctly (String↔string, Long↔number, List↔array, etc.)
- [ ] Required fields in Java (`@NotNull`) are non-optional in TypeScript (no `?`)
- [ ] Optional fields in Java are optional in TypeScript (`?`)
- [ ] Enums have matching values in both repos

## Request/Response Shapes
- [ ] Request body DTO matches the TypeScript request model
- [ ] Response DTO matches the TypeScript response model
- [ ] Error response shape is consistent with the error contract
- [ ] Pagination shapes match (if applicable)

## Code Quality — Java
- [ ] All imports resolved
- [ ] `@Valid` on `@RequestBody` parameters
- [ ] `ResponseEntity<T>` return types
- [ ] Javadoc on public methods
- [ ] Matches existing controller/service/DTO conventions
- [ ] Constructor injection (no field `@Autowired`)

## Code Quality — Angular
- [ ] No `any` types
- [ ] `Observable<T>` return types on service methods
- [ ] `readonly` on injected dependencies
- [ ] Matches existing naming and folder conventions
- [ ] Barrel exports updated (if project uses them)
- [ ] Error handling present in services

## Integration
- [ ] Implementation order correct (Java before Angular for new endpoints)
- [ ] Angular service base URL matches Java controller path
- [ ] Auth/role requirements consistent between backend and frontend
