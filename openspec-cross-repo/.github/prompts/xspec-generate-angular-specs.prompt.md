---
mode: 'agent'
description: 'Scan the Angular app codebase and generate OpenSpec specs for all discovered domains'
tools: ['search/codebase', 'editFiles', 'terminalCommand']
---

# Generate Angular Technical Specs

## Task
Scan the Angular app and generate openspec/specs/<domain>/spec.md for every domain.

## Scan
1. Find all routes (grep path:, Routes, canActivate, loadComponent)
2. Find all services with HTTP calls (grep @Injectable, this.http)
3. Find all models/interfaces (grep export interface, export type, export enum)
4. Find form definitions (grep FormGroup, FormBuilder, Validators)
5. Find components with templates (grep @Component, form interactions)
6. Find state management (grep signal, computed, Store, createAction)
7. Find guards and interceptors

## Generate
Match Angular domains to Java domains where possible. For each domain create spec with:
- Requirements for screens/pages (user interactions, navigation)
- Requirements for service integration (HTTP calls, response handling)
- Requirements for forms (validation, submission, error display)
- **`## NFR Requirements` section** — scan for CanActivate guards, HttpInterceptor, DomSanitizer, ChangeDetectionStrategy.OnPush, trackBy, loadChildren, @defer, debounceTime, shareReplay. Add requirements with `**Evidence:**` citations. Flag missing controls (routes without guards, forms without validators, large tables without virtual scroll, search inputs without debouncing, tokens in localStorage) with `<!-- REVIEW: ... -->` markers.
