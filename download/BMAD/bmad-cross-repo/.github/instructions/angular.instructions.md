---
applyTo: "**/angular-app/**/*.ts,**/angular-app/**/*.html"
---
## Angular/TypeScript Code Rules (BMAD Cross-Repo)
- Never use `any` — always explicit types
- `readonly` on injected deps, `Observable<T>` returns
- kebab-case files, one class/interface per file
- Standalone components, OnPush change detection
- Interface field names must match Java DTO fields (camelCase)
- Required fields (Java `@NotNull`) → no `?` in TypeScript
- Use terminal commands (`cat >`) if `editFiles` fails
