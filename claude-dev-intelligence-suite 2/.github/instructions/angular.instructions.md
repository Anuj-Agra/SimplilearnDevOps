---
applyTo: "**/*.component.ts,**/*.component.html,**/*.service.ts,**/*.module.ts,**/*.spec.ts,**/angular.json"
description: "Automatically triggered when working with Angular files or when user asks about Angular performance, memory leaks, change detection, or bundle size"
---

# Angular Skills

When working with Angular files or user mentions Angular-specific concerns:

- **angular-memory-leak-detector** (`.claude/skills/angular-memory-leak-detector/SKILL.md`)
  Triggers: "memory leak", "unsubscribed observable", "subscribe without unsubscribe",
  "ngOnDestroy", "takeUntil", "memory growing"

- **angular-change-detection-optimiser** (`.claude/skills/angular-change-detection-optimiser/SKILL.md`)
  Triggers: "slow UI", "change detection", "OnPush", "trackBy", "ngFor performance",
  "function in template", "ExpressionChangedAfterItHasBeenChecked"

- **angular-bundle-analyser** (`.claude/skills/angular-bundle-analyser/SKILL.md`)
  Triggers: "bundle size", "large bundle", "lodash", "moment.js", "tree shaking",
  "lazy loading modules", "bundle analysis"

- **playwright-test-generator** (`.claude/skills/playwright-test-generator/SKILL.md`)
  UI test suite triggers: "write UI tests", "E2E tests", "Playwright", "test this component"

Load the relevant SKILL.md before generating Angular code or analysis.
Generate components with `ChangeDetectionStrategy.OnPush` by default.
Always use `takeUntilDestroyed()` for subscriptions. Always use `trackBy` on `*ngFor`.
