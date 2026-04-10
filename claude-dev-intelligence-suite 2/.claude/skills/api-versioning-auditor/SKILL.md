---
name: api-versioning-auditor
description: >
  Scan REST controllers for versioning strategy gaps and unversioned breaking changes.
  Use when asked: 'API versioning', 'breaking changes', 'API compatibility', 'version
  strategy', 'backward compatibility', 'contract stability', 'API evolution', 'version
  audit', 'deprecation strategy', 'client compatibility'. Unversioned API changes
  in a parallel-connection system with multiple clients are a deployment hazard.
---
# API Versioning Auditor

Detect versioning gaps and breaking change risks across all REST endpoints.

## Step 1 — Detect Current Versioning Strategy
```bash
# URL versioning (/v1/, /api/v2/)
grep -rn "@RequestMapping\|@GetMapping\|@PostMapping" \
  <java_path> --include="*.java" | grep -o '"[^"]*"' | \
  grep "/v[0-9]\|/api/v" | sort -u | head -20

# Header versioning
grep -rn "Accept.*version\|X-API-Version\|api-version\|@RequestHeader.*version" \
  <java_path> --include="*.java" | head -10

# No versioning (paths without /v[N]/)
grep -rn "@RequestMapping\|@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping" \
  <java_path> --include="*.java" | grep '"[^"]*"' | \
  grep -v "/v[0-9]\|test\|actuator\|health\|swagger" | head -30
```

## Step 2 — Detect Breaking Change Risk
```bash
# @Deprecated on controller methods (good — should be present for old versions)
grep -rn "@Deprecated" <java_path> --include="*.java" | \
  grep -i "controller\|mapping\|endpoint" | head -20

# Shared DTOs used by multiple versions (risky — changes break all versions)
find <java_path> -name "*Request*.java" -o -name "*Response*.java" -o -name "*Dto.java" | \
  xargs grep -l "." 2>/dev/null | head -20
```

## Step 3 — Output

```
API VERSIONING AUDIT: [System]

VERSIONING STRATEGY DETECTED: [URL versioning / Header versioning / None]

UNVERSIONED ENDPOINTS (breaking change risk):
  AV-001 [HIGH]: [N] endpoints have no version in path
    Endpoints: [list]
    Risk: Any signature change breaks existing clients with no warning
    Fix: Add /v1/ prefix and deprecation headers (see below)

VERSIONING GAPS:
  AV-002 [MEDIUM]: v1 DTOs are shared with v2 endpoints
    Risk: Adding a required field to the DTO breaks v1 clients
    Fix: Create separate v1/v2 DTO classes; use mappers between them

DEPRECATION STRATEGY MISSING:
  AV-003: No @Deprecated endpoints found — no evidence of graceful sunset process
    Fix: Implement deprecation headers:
      Deprecation: Sat, 01 Jan 2025 00:00:00 GMT
      Sunset: Sat, 01 Jul 2025 00:00:00 GMT
      Link: <https://api.docs.yourorg.com/migration>; rel="successor-version"

RECOMMENDED VERSIONING CONFIG:
  Strategy: URL versioning (/api/v1/, /api/v2/)
  Compatibility: v1 supported for 12 months after v2 GA
  Deprecation notice: 3 months before sunset

  @RestController
  @RequestMapping("/api/v1/[resource]")
  @Deprecated  // Sunset: 2025-07-01
  public class [Resource]V1Controller { ... }

  @RestController
  @RequestMapping("/api/v2/[resource]")
  public class [Resource]V2Controller { ... }
```
