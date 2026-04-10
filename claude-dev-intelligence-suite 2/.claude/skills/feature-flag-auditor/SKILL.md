---
name: feature-flag-auditor
description: >
  Find stale feature flags, flags with no tests, nested flag complexity, and flags
  with no documented owner or removal date. Use when asked: 'feature flags', 'toggle
  audit', 'stale flags', 'flag cleanup', 'feature toggle debt', 'flags to remove',
  'flag explosion', 'nested flags', 'LaunchDarkly audit', 'Unleash audit', 'flag
  retirement', 'flag coverage'. Feature flags accumulate silently and create 2^N
  untestable code paths. Produces a flag retirement backlog.
---
# Feature Flag Auditor

Find flag debt before it creates untestable code paths and production surprises.

---

## Step 1 — Discover All Flags

```bash
# Spring / custom flag checks
grep -rn "featureFlag\|isEnabled\|isActive\|toggles\.\|FeatureToggle\|\
  @ConditionalOnProperty\|Environment.*getProperty.*feature\|\
  featureFlags\.get\|featureService\." \
  <java_path> --include="*.java" | grep -v "//\|test\|Test" | head -60

# LaunchDarkly
grep -rn "ldClient\.\|LDClient\.\|boolVariation\|stringVariation\|jsonValueVariation" \
  <java_path> --include="*.java" | head -30

# Unleash
grep -rn "unleash\.\|isEnabled\|UnleashClient\|FeatureToggle" \
  <java_path> --include="*.java" | head -30

# Angular feature flags
grep -rn "featureFlag\|isFeatureEnabled\|featureToggle\|FeatureFlagService\|\
  environment\.[a-z]*Feature\|environment\.features\." \
  <angular_path> --include="*.ts" | head -30

# Environment-based flags
grep -rn "environment\." <angular_path>/src/environments --include="*.ts" | head -20
grep -rn "feature\.\|toggle\.\|enabled\." \
  <java_path>/src/main/resources --include="*.yml" --include="*.properties" | head -20
```

---

## Step 2 — For Each Flag, Determine Status

### Age Assessment
```bash
# Find when flag was first introduced (git blame)
git log --all --oneline -S "featureFlagName" -- <java_path> 2>/dev/null | tail -1
```

### Coverage Assessment
```bash
# Is there a test that exercises both the flag=ON and flag=OFF path?
grep -rn "<flag_name>" <java_path> --include="*Test*.java" | head -10
```

### Nesting Assessment
```bash
# Flags inside flags (exponential complexity)
grep -rn "isEnabled\|featureFlag" <java_path> --include="*.java" -B2 -A2 | \
  grep -B3 -A3 "isEnabled\|featureFlag" | grep -v "^--$" | head -40
```

---

## Step 3 — Classify Each Flag

| Classification | Criteria | Action |
|---|---|---|
| **Retire NOW** | 100% on for 3+ months in production | Remove flag, make permanent |
| **Retire SOON** | 100% on for 1-3 months | Schedule removal this sprint |
| **Active — needs tests** | In use, but only one path tested | Add missing test before next change |
| **Active — healthy** | In use, both paths tested, owner known | No action |
| **Dead** | Flag value never read in active code | Delete immediately |
| **Nested** | Flag inside another flag | Restructure — 2^N paths untestable |
| **Orphaned** | No documented owner, no removal date | Assign owner this sprint |

---

## Step 4 — Output: Flag Register

```
FEATURE FLAG AUDIT: [System]
Total flags found: [N]

FLAG REGISTER:
┌─────────────────────────────────────────────────────────────────────┐
│ Flag Name           │ Age    │ Status  │ Tests │ Owner  │ Action    │
├─────────────────────┼────────┼─────────┼───────┼────────┼───────────┤
│ new-checkout-flow   │ 8 mths │ 100% ON │ ON ✅ │ @alice │ RETIRE    │
│                     │        │         │ OFF ❌│        │ NOW       │
├─────────────────────┼────────┼─────────┼───────┼────────┼───────────┤
│ enhanced-kyc-check  │ 2 mths │ 50/50   │ Both✅│ @bob   │ HEALTHY   │
├─────────────────────┼────────┼─────────┼───────┼────────┼───────────┤
│ legacy-pricing      │ 18 mth │ 0% ON   │ OFF ✅│ NONE   │ RETIRE    │
│                     │        │ (dead)  │ ON ❌ │        │ DEAD CODE │
├─────────────────────┼────────┼─────────┼───────┼────────┼───────────┤
│ beta-dashboard      │ 1 mth  │ 30% ON  │ None❌│ NONE   │ ADD TESTS │
│                     │        │         │       │        │ + OWNER   │
└─────────────────────┴────────┴─────────┴───────┴────────┴───────────┘

CRITICAL — NESTED FLAGS DETECTED:
  FF-001: [flag-a] checked inside [flag-b] block
    Creates 4 code paths — only 1 is tested
    Risk: 3 untested production combinations
    Fix: Flatten — combine into single flag OR test all combinations

RETIREMENT BACKLOG (ordered by urgency):
  1. Remove 'new-checkout-flow' — permanent ON for 8 months, saves 45 lines
  2. Delete 'legacy-pricing' — dead code, ON=0% for 6 months

CODE TO DELETE when retiring 'new-checkout-flow':
  CheckoutService.java:142 — remove if(!featureFlags.isEnabled("new-checkout-flow"))
  CheckoutController.java:67 — remove else branch
  checkout.component.ts:23 — remove *ngIf="!featureFlags.isEnabled('new-checkout-flow')"
```
