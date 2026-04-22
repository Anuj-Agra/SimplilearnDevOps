---
applyTo: "**/*.java"
---

## Java Code Rules (Cross-Repo Context)

When creating or modifying Java files:

- Include the full `package` statement and ALL imports
- Scan existing code first — match naming, annotations, error handling
- Use Lombok only if the project already uses it
- Constructor injection with `private final` fields, never `@Autowired`
- `@Valid` on every `@RequestBody` parameter
- `ResponseEntity<T>` for controller return types with proper HTTP status codes
- Interface + Impl pattern for services
- DTOs must have field names that translate cleanly to camelCase in TypeScript
- Add Javadoc on public methods

When creating DTOs for cross-repo changes:
- Field names must match the TypeScript interface in the Angular repo
- Use `@NotNull` / `@NotBlank` on required fields — these map to non-optional TS fields
