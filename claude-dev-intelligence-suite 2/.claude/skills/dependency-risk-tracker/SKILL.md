---
name: dependency-risk-tracker
description: >
  Scan third-party library dependencies for known CVEs, end-of-life versions, licence
  incompatibilities, and major version lag. Use when asked: 'dependency audit',
  'library vulnerabilities', 'outdated dependencies', 'CVE scan', 'licence check',
  'dependency risk', 'upgrade plan', 'EOL libraries', 'vulnerable libraries',
  'dependency health'. Produces a prioritised upgrade backlog with CVSS scores.
---
# Dependency Risk Tracker

Audit all third-party dependencies for security, licence, and freshness risks.

## Step 1 — Extract All Dependencies
```bash
# Maven
find . -name "pom.xml" | xargs grep -A3 "<dependency>" | \
  grep "<groupId>\|<artifactId>\|<version>" | head -200

# Gradle
grep -rn "implementation\|api\|testImplementation\|runtimeOnly" \
  . --include="*.gradle" --include="*.gradle.kts" | \
  grep -v "project(" | head -200

# npm (Angular)
cat package.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
deps={**d.get('dependencies',{}),**d.get('devDependencies',{})}
[print(f'{k}: {v}') for k,v in deps.items()]
"
```

## Step 2 — Risk Classification Per Dependency

For each dependency, assess:

**Security Risk** (check known CVE databases — flag for manual check):
- Spring Framework < 6.x → potential CVEs
- Log4j any version → check for Log4Shell variants
- Jackson < 2.14 → deserialization vulnerabilities
- Any library not updated in 2+ years → flag for research

**Licence Risk** (for commercial/financial services systems):
- GPL v2/v3 → INCOMPATIBLE with closed-source commercial products
- AGPL → INCOMPATIBLE unless releasing your source
- LGPL → Conditional — check usage pattern
- Apache 2.0, MIT, BSD → Safe
- Unknown licence → Flag for legal review

**Version Freshness**:
- Major version behind → HIGH risk (breaking changes to upgrade, security backlog)
- 2+ minor versions behind → MEDIUM risk
- Current or 1 minor behind → LOW risk

## Step 3 — Output: Dependency Risk Report

```
DEPENDENCY RISK REPORT: [System]

CRITICAL (upgrade this sprint):
  DEP-001: [library] [current version] → CVE-[XXX] (CVSS [score])
    Risk: [what an attacker can do]
    Upgrade to: [safe version]
    Breaking changes: [yes/no — what to test]

HIGH (upgrade next sprint):
  DEP-002: [library] — End of Life [date]
  DEP-003: [library] — Licence: GPL (incompatible)

MEDIUM (schedule in backlog):
  DEP-004: [library] — 3 major versions behind latest

LOW (monitor):
  [list]

LICENCE SUMMARY:
  Safe: [N libraries]
  Needs review: [N libraries]
  Incompatible: [N libraries] ← URGENT

UPGRADE ROADMAP:
  Week 1: [Critical CVE fixes]
  Sprint N+1: [EOL libraries]
  Backlog: [Major version upgrades]
```
