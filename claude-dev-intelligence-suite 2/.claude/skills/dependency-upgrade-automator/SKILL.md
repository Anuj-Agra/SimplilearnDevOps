---
name: dependency-upgrade-automator
description: >
  Not just detects outdated dependencies — actually generates the updated pom.xml
  or package.json, identifies which tests to run, and produces a migration guide
  for breaking API changes. Use when asked: 'upgrade dependencies', 'update
  libraries', 'upgrade Spring Boot', 'update Angular', 'dependency upgrade',
  'update pom.xml', 'upgrade npm packages', 'migrate to Spring Boot 3',
  'update to Angular 17', 'library migration guide', 'breaking changes upgrade'.
  Produces ready-to-apply file changes + a migration checklist per upgraded library.
---
# Dependency Upgrade Automator

Generate the actual file changes for dependency upgrades, not just a list of what to update.

---

## Step 0 — Scope Clarification

Ask the user:
1. **Target**: Upgrade everything? A specific library? Spring Boot major version?
2. **Risk appetite**: Conservative (patch/minor only) vs Aggressive (major versions)?
3. **Java version**: Current JDK? Target JDK?

Default: upgrade to latest stable minor versions, flag majors for separate decision.

---

## Step 1 — Inventory Current Dependencies

### Maven
```bash
# Full dependency list with current versions
mvn dependency:tree -DoutputType=text --no-transfer-progress 2>/dev/null | \
  grep "^\[INFO\].*jar$" | head -60

# Check for outdated versions
mvn versions:display-dependency-updates --no-transfer-progress 2>/dev/null | \
  grep "->\\|Available\|The following" | head -40

# Check for outdated plugins
mvn versions:display-plugin-updates --no-transfer-progress 2>/dev/null | \
  grep "->\\|Available" | head -20

# Current parent/BOM
grep -n "parent\|dependencyManagement\|spring-boot\|bom\|platform" \
  pom.xml | head -20
```

### npm / Angular
```bash
# Current versions and available updates
cat package.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
deps = {**d.get('dependencies',{}), **d.get('devDependencies',{})}
for k,v in sorted(deps.items()):
    print(f'{k}: {v}')
"

# Angular-specific update check
npx ng update 2>/dev/null | head -30
npm outdated 2>/dev/null | head -30
```

---

## Step 2 — Categorise Each Upgrade

For each dependency needing upgrade:

| Category | Criteria | Action |
|---|---|---|
| **Patch** | x.y.Z → x.y.Z+1 | Apply automatically — no breaking changes |
| **Minor** | x.Y.z → x.Y+1.z | Apply — check changelog for deprecations |
| **Major** | X.y.z → X+1.y.z | Flag — breaking changes likely, needs migration guide |
| **Security** | Any version with known CVE | Apply immediately regardless of semver jump |

---

## Step 3 — Generate Migration Guides Per Major Upgrade

Read `references/migration-guides.md` for known breaking changes per library.

### Spring Boot 2.x → 3.x
```
BREAKING CHANGES CHECKLIST:
□ Java 17 minimum (was Java 8) — update Dockerfile + CI pipeline
□ javax.* → jakarta.* package rename — find/replace across entire codebase
□ Spring Security config — WebSecurityConfigurerAdapter removed
□ spring.factories → Auto-configuration files moved to META-INF/spring/
□ Actuator endpoints — some paths changed
□ Hibernate 6 — some HQL syntax changed, @GeneratedValue strategies changed
□ Embedded server changes — TomcatServletWebServerFactory API changed

AUTOMATED FIND/REPLACE:
  find src -name "*.java" -exec sed -i \
    's/javax\.persistence/jakarta\.persistence/g;
     s/javax\.validation/jakarta\.validation/g;
     s/javax\.servlet/jakarta\.servlet/g;
     s/javax\.annotation/jakarta\.annotation/g' {} +
```

### Angular 14 → 17
```
BREAKING CHANGES CHECKLIST:
□ Standalone components — NgModule optional but migration required
□ Signals — new reactivity model, replace some RxJS patterns
□ @defer blocks — lazy loading syntax changed
□ Control flow syntax — @if/@for replace *ngIf/*ngFor (new syntax)
□ inject() function — alternative to constructor injection
□ Required inputs — @Input({ required: true })

MIGRATION COMMANDS:
  npx ng update @angular/core@17 @angular/cli@17
  npx ng generate @angular/core:standalone  # optional migration
```

---

## Step 4 — Generate Updated Dependency Files

### Updated pom.xml sections

```xml
<!-- GENERATED pom.xml changes -->

<!-- 1. Update parent/BOM version -->
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>[LATEST_STABLE]</version> <!-- was: [OLD_VERSION] -->
</parent>

<!-- 2. Updated dependencies (only changed ones shown) -->
<dependencies>

  <!-- Security fix: [CVE-XXXX-XXXX] -->
  <dependency>
    <groupId>[groupId]</groupId>
    <artifactId>[artifactId]</artifactId>
    <version>[NEW_VERSION]</version> <!-- was: [OLD_VERSION] -->
  </dependency>

  <!-- Minor upgrade: added [new feature] -->
  <dependency>
    <groupId>[groupId]</groupId>
    <artifactId>[artifactId]</artifactId>
    <version>[NEW_VERSION]</version> <!-- was: [OLD_VERSION] -->
  </dependency>

</dependencies>

<!-- 3. Updated plugin versions -->
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <version>[NEW_VERSION]</version> <!-- was: [OLD_VERSION] -->
      <configuration>
        <source>[JAVA_VERSION]</source>
        <target>[JAVA_VERSION]</target>
      </configuration>
    </plugin>
  </plugins>
</build>
```

### Updated package.json

```json
{
  "dependencies": {
    "@angular/common": "^[NEW_VERSION]",
    "@angular/core": "^[NEW_VERSION]",
    "rxjs": "~[NEW_VERSION]",
    "tslib": "^[NEW_VERSION]",
    "zone.js": "~[NEW_VERSION]"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^[NEW_VERSION]",
    "@angular/cli": "^[NEW_VERSION]",
    "@angular/compiler-cli": "^[NEW_VERSION]",
    "typescript": "~[NEW_VERSION]"
  }
}
```

---

## Step 5 — Generate Test Scope

Produce a targeted regression test plan — not "run everything":

```
UPGRADE TEST PLAN
─────────────────────────────────────────────────────────
Upgraded:           [N] libraries ([N] patch, [N] minor, [N] major)
Security fixes:     [N]

MUST TEST (high risk — API/behaviour changes):
  1. [spring-security upgrade] → Run: AuthenticationTests, SecurityConfigTest
  2. [hibernate upgrade]       → Run: All @Repository tests + data migration tests

SHOULD TEST (medium risk):
  3. [jackson upgrade]         → Run: SerializationTests, JsonControllerTests
  4. [slf4j upgrade]           → Run: LoggingConfigTest

SMOKE TEST ONLY (low risk — patch versions):
  5-[N]. Patch upgrades       → Run: HealthCheckTest, ApplicationContextLoads

SKIP (no functional impact):
  • Documentation-only changes
  • Test-only dependency upgrades (run their own tests)

COMMANDS:
  # Run full regression for major upgrades
  mvn test -pl [affected-modules] -Dtest="*AuthTest,*SecurityTest,*RepositoryTest"

  # Run smoke tests for minor upgrades
  mvn test -Dtest="ApplicationContextLoadsTest,HealthCheckTest"

  # Angular
  npx ng test --include="**/*.spec.ts" --watch=false
```

---

## Step 6 — Output Summary

```
DEPENDENCY UPGRADE REPORT: [System]
Generated: [date]

UPGRADES APPLIED: [N] total
  Patch (safe):    [N] applied automatically
  Minor (low risk):[N] applied — see changelog notes
  Major (risky):   [N] flagged — migration guide required
  Security fixes:  [N] CRITICAL — apply first

FILES CHANGED:
  pom.xml — [N] version bumps
  package.json — [N] version bumps

MIGRATION REQUIRED FOR:
  [library] [old] → [new]: [brief breaking change summary]
  Apply migration guide from references/migration-guides.md

NEXT STEPS:
  1. Apply the generated file changes
  2. Run: [migration commands for major upgrades]
  3. Run: [test commands]
  4. Fix any compilation errors from breaking changes
  5. Commit with message: "chore: dependency upgrades [date]"
```
