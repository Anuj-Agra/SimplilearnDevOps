---
name: mutation-testing-reporter
description: >
  Configure and run PIT (PITest) for Java and Stryker for Angular, interpret the
  mutation score per module, and produce a test quality improvement backlog. Use
  when asked: 'mutation testing', 'PITest', 'Stryker', 'mutation score', 'test
  quality', 'are my tests good', 'superficial tests', 'test effectiveness',
  'surviving mutants', 'killed mutants', 'test coverage vs mutation score'.
  Code coverage shows lines executed; mutation testing proves lines are actually
  verified. A module with 80% coverage and 30% mutation score has untested logic.
---
# Mutation Testing Reporter

Prove your tests actually verify the logic — not just execute it.

---

## Background: Why Mutation Testing?

Code coverage = "the test ran this line"
Mutation score = "the test would FAIL if this line had a bug"

A test that calls `processOrder()` but never asserts the result gives 100%
line coverage and 0% mutation score. Mutation testing catches this.

---

## Step 1 — Configure PIT for Java

```xml
<!-- Add to pom.xml -->
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <version>1.15.0</version>
  <dependencies>
    <!-- JUnit 5 support -->
    <dependency>
      <groupId>org.pitest</groupId>
      <artifactId>pitest-junit5-plugin</artifactId>
      <version>1.2.1</version>
    </dependency>
  </dependencies>
  <configuration>
    <!-- Target only business logic — not Spring config, DTOs, controllers -->
    <targetClasses>
      <param>com.yourorg.*.service.*</param>
      <param>com.yourorg.*.domain.*</param>
      <param>com.yourorg.*.validator.*</param>
    </targetClasses>
    <targetTests>
      <param>com.yourorg.*Test</param>
      <param>com.yourorg.*Spec</param>
    </targetTests>
    <!-- Mutation operators to apply -->
    <mutators>
      <mutator>STRONGER</mutator>  <!-- includes boundary, null returns, etc. -->
    </mutators>
    <!-- Thresholds — build fails if below these -->
    <mutationThreshold>70</mutationThreshold>
    <coverageThreshold>80</coverageThreshold>
    <outputFormats>
      <outputFormat>HTML</outputFormat>
      <outputFormat>XML</outputFormat>
    </outputFormats>
    <!-- Exclude generated code and config -->
    <excludedClasses>
      <param>*Config</param>
      <param>*Configuration</param>
      <param>*Application</param>
      <param>*Dto</param>
      <param>*DTO</param>
    </excludedClasses>
    <threads>4</threads>
    <timeoutConstant>8000</timeoutConstant>
  </configuration>
</plugin>
```

```bash
# Run mutation tests
mvn org.pitest:pitest-maven:mutationCoverage

# Run for a specific module only (faster for large codebases)
mvn org.pitest:pitest-maven:mutationCoverage \
  -DtargetClasses="com.yourorg.orders.service.*" \
  -DtargetTests="com.yourorg.orders.*Test"

# View report
open target/pit-reports/[timestamp]/index.html
```

---

## Step 2 — Configure Stryker for Angular

```json
// stryker.config.json
{
  "$schema": "./node_modules/@stryker-mutator/core/schema/stryker-schema.json",
  "packageManager": "npm",
  "reporters": ["html", "clear-text", "progress", "json"],
  "testRunner": "karma",
  "coverageAnalysis": "perTest",
  "karma": {
    "projectType": "angular-cli",
    "configFile": "karma.conf.js",
    "config": {
      "browsers": ["ChromeHeadless"]
    }
  },
  "mutate": [
    "src/app/**/*.ts",
    "!src/app/**/*.spec.ts",
    "!src/app/**/*.module.ts",
    "!src/app/**/*.routing.ts",
    "!src/environments/**"
  ],
  "thresholds": {
    "high": 80,
    "low": 70,
    "break": 60
  },
  "ignorePatterns": ["node_modules", "dist", "coverage"],
  "timeoutMS": 10000,
  "concurrency": 4
}
```

```bash
# Install Stryker
npm install --save-dev @stryker-mutator/core @stryker-mutator/karma-runner

# Run mutation tests
npx stryker run

# Run on specific directory (faster)
npx stryker run --mutate "src/app/orders/**/*.ts"

# View HTML report
open reports/mutation/mutation.html
```

---

## Step 3 — Interpret Results

### Mutation Score by Level

| Score | Meaning | Action |
|---|---|---|
| 90–100% | Excellent — tests are thorough | Maintain, review quarterly |
| 70–90% | Good — most logic verified | Fix surviving mutants in weak areas |
| 50–70% | Moderate — significant gaps | Dedicated test improvement sprint |
| < 50% | Poor — tests are superficial | Treat as untested code |

### Types of Surviving Mutants

**Conditional Boundary** (`>` changed to `>=`)
```java
// Original
if (amount.compareTo(THRESHOLD) > 0) requireApproval();
// Mutant: > changed to >= 
// If test only checks amount=11000 when threshold=10000, mutant survives
// Fix: Add test exactly AT boundary: amount=10000 (boundary value)
```

**Null Return** (method returns null instead of value)
```java
// Original: return customer;
// Mutant:   return null;
// If test doesn't assert the returned object's fields, mutant survives
// Fix: Assert specific fields of returned object
```

**Removed Condition** (entire if block removed)
```java
// Original: if (user.isActive()) throw new UserInactiveException();
// Mutant: condition removed entirely
// If test doesn't test with an inactive user, mutant survives
// Fix: Add test case with inactive user
```

**Negated Condition** (`isValid()` becomes `!isValid()`)
```java
// Fix: Ensure both valid and invalid inputs are tested
```

---

## Step 4 — Output: Mutation Test Report

```
MUTATION TEST REPORT: [System]
Run date: [date] | Tool: PITest [version] / Stryker [version]

═══════════════════════════════════════════════════════════
SUMMARY
═══════════════════════════════════════════════════════════
                    │ Line Coverage │ Mutation Score │ Gap
────────────────────┼───────────────┼────────────────┼──────
order.service       │     91%       │      43%       │ HIGH
payment.service     │     85%       │      71%       │ MED
customer.validator  │     78%       │      82%       │ LOW
pricing.calculator  │     95%       │      38%       │ HIGH ← worst
auth.service        │     88%       │      76%       │ LOW

Overall mutation score: 62%  (target: 70%)

═══════════════════════════════════════════════════════════
CRITICAL — SUPERFICIAL TEST SUITES (high coverage, low mutation)
═══════════════════════════════════════════════════════════
pricing.calculator: 95% coverage, 38% mutation score
  This class has tests that EXECUTE the code but don't VERIFY the results.
  Surviving mutants:
    - ConditionalBoundary in applyTierPricing() (line 67)
    - NullReturn in getBasePrice() (line 34)
    - NegatedConditional in isEligibleForDiscount() (line 89)

  Tests to add:
    1. Test applyTierPricing() at EXACT tier boundary values
    2. Assert getBasePrice() returns non-null AND correct value
    3. Test isEligibleForDiscount() with customer that IS and IS NOT eligible

═══════════════════════════════════════════════════════════
TEST IMPROVEMENT BACKLOG (ordered by risk × effort)
═══════════════════════════════════════════════════════════
1. pricing.calculator — 10 surviving mutants
   Priority: CRITICAL (financial logic with weak tests)
   Estimated effort: 1 day
   Highest value mutants to kill first:
     → Add boundary value tests for ALL threshold comparisons
     → Assert return values, not just "no exception thrown"

2. order.service — 18 surviving mutants
   Priority: HIGH
   Estimated effort: 2 days

═══════════════════════════════════════════════════════════
TREND (if previous reports exist)
═══════════════════════════════════════════════════════════
  3 months ago: 48%  → Today: 62%  → Target: 70%  → On track ✅
```
