---
mode: 'agent'
description: 'Scan an existing module/feature as a reference pattern, then propose how to apply it to new work'
tools: ['search/codebase']
---
# BMAD Pattern Reference

The user wants to replicate an existing pattern from the codebase for new work.

## Steps

### 1. Identify the Reference
The user will specify a module, feature, or area to use as a pattern. Examples:
- "Use the same pattern as the accounts module"
- "Follow how KYC was built"
- "Look at how the client search works and replicate it for reports"

### 2. Deep Scan the Reference
Read **every significant file** in the referenced module across both repos:

**Java side:**
- Controller: class structure, annotations, error handling, auth
- Service: interface + impl pattern, method signatures, exception handling
- DTOs: Lombok/records, validation annotations, field naming
- Repository: query methods, custom queries
- Tests: testing patterns, mocks, assertions
- File & package structure

**Angular side:**
- Component: standalone?, signals?, change detection, template patterns
- Service: HttpClient usage, error handling, caching
- Model/interface: field types, optional markers
- Tests: testing patterns
- File & folder structure

### 3. Present the Pattern
```markdown
## Reference Pattern: <Module Name>

### Java Pattern
```
<package>.controller/<Name>Controller.java
  ├── @RestController + @RequestMapping("/api/<resource>")
  ├── Constructor injection of <Name>Service
  ├── Methods: CRUD with @Valid, ResponseEntity<T>
  └── @PreAuthorize("hasRole('...')")

<package>.service/<Name>Service.java (interface)
<package>.service.impl/<Name>ServiceImpl.java
  ├── @Service + @Transactional
  └── Business logic pattern: validate → process → persist

<package>.dto/<Name>RequestDto.java — Lombok @Data, Jakarta validation
<package>.dto/<Name>ResponseDto.java — Lombok @Data
```

### Angular Pattern
```
<feature>/
  ├── <name>.component.ts — standalone, OnPush, signals
  ├── <name>.service.ts — HttpClient, Observable<T>, error handling
  ├── models/<name>.model.ts — interface with typed fields
  └── index.ts — barrel export
```

### Key Conventions
- <naming patterns>
- <error handling approach>
- <auth/entitlement pattern>
- <test coverage pattern>
```

### 4. Propose Application
```markdown
## Proposed Application to <New Feature>

### Following the Pattern
- <what will be replicated exactly>

### Necessary Deviations
- <what must differ and why>

### Questions
1. <any unclear aspects>
```

**STOP and wait for user confirmation before producing architecture.**

### 5. Hand Off
After confirmation, the pattern becomes the "Reference Pattern" section in the architecture doc. Suggest running `/bmad-architect` or `/bmad-propose` next.
