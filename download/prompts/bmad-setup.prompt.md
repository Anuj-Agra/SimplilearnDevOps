---
mode: 'agent'
description: 'Bootstrap BMAD in this workspace: scan both monorepos and create initial project context'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---
# BMAD Setup / Bootstrap

## Task
Scan both monorepos and create the initial BMAD context files that all agents will reference.

## Steps

### 1. Scan Java Service Monorepo
- List all modules/subprojects with their purpose
- Find all controllers → endpoints
- Find all DTOs/entities → data models
- Find all services → business logic
- Identify package naming convention, build tool, test framework

### 2. Scan Angular App Monorepo
- List all projects/libraries (if using Nx, Angular workspace, or similar)
- Find all routes → screens
- Find all services → API integrations
- Find all models/interfaces → data types
- Identify component architecture, state management, test framework

### 3. Generate Project Context
Save to `docs/project-context.md`:
```markdown
# Project Context

## Java Service Monorepo
- Root: java-service/
- Build: <Maven/Gradle>
- Modules: <list with descriptions>
- Base package: <detected>
- Conventions: <Lombok/Records/Validation/etc>
- Endpoints: <count> across <count> controllers
- DTOs: <count>

## Angular App Monorepo
- Root: angular-app/
- CLI/Nx: <detected>
- Projects: <list>
- Style: <standalone/modules, signals/observables>
- Services: <count>
- Models: <count>
- Routes: <count>

## API Boundary
| Endpoint | Java Controller | Angular Service |
|----------|----------------|-----------------|
| GET /api/... | ....Controller | ....Service |

## Conventions Detected
### Java
<patterns found>
### Angular
<patterns found>
```

This file becomes the reference for all BMAD agents going forward.
