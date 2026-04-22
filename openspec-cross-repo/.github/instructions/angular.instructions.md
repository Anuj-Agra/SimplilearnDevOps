---
applyTo: "**/*.ts,**/*.html"
---

## Angular/TypeScript Code Rules (Cross-Repo Context)

When creating or modifying TypeScript files:

- Never use `any` — always provide explicit types
- `readonly` on constructor-injected dependencies
- `Observable<T>` return types on all service methods
- kebab-case file naming (`account-detail.service.ts`)
- One class/interface per file
- `OnPush` change detection for new components
- Standalone components unless the project uses NgModules

When creating models/interfaces for cross-repo changes:
- Field names must match the Java DTO field names (camelCase in both)
- Required fields (Java `@NotNull`) → no `?` in TypeScript
- Optional fields → use `?` suffix
