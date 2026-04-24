---
applyTo: "**/java-service/**/*.java"
---
## Java Code Rules (BMAD Cross-Repo)
- Full `package` statement + ALL imports
- Scan existing code first — match conventions exactly
- Lombok only if project uses it, constructor injection only
- `@Valid` on `@RequestBody`, `ResponseEntity<T>` returns, Javadoc on public methods
- DTO field names must match TypeScript interface names (camelCase)
- `@NotNull` on required fields → maps to non-optional TS fields
- Use terminal commands (`cat >`) if `editFiles` fails
