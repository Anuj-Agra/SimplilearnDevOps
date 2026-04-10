---
name: security-audit
description: >
  Scan for OWASP Top 10 vulnerabilities and security misconfigurations in Java/Angular
  codebases. Use when asked: 'security audit', 'security review', 'OWASP', 'security
  scan', 'vulnerabilities', 'security gaps', 'pen test prep', 'security checklist',
  'injection risk', 'XSS', 'CSRF', 'authentication issues', 'authorisation gaps',
  'hardcoded secrets', 'sensitive data exposure'. Produces a CVSS-scored security
  report with remediation steps. Critical for KYC, AML, financial services systems.
---
# Security Audit Skill

Scan Java/Angular codebases for OWASP Top 10 vulnerabilities.

## Scan Categories & Commands

### A01: Broken Access Control
```bash
# Endpoints missing @PreAuthorize (unprotected)
grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping" \
  <java_path> --include="*.java" -l | \
  xargs grep -L "@PreAuthorize\|@Secured\|@RolesAllowed"

# Angular routes missing canActivate guard
grep -rn "path:" <angular_path> --include="*.ts" | grep -v "canActivate\|children\|\[\]"
```

### A02: Cryptographic Failures (Sensitive Data Exposure)
```bash
# PII in logs
grep -rn "log\.\|logger\." <java_path> --include="*.java" | \
  grep -i "password\|ssn\|dob\|credit\|card\|secret\|token\|key" | head -30

# Weak hashing
grep -rn "MD5\|SHA1\|DES\b\|new MessageDigest\|getInstance.*MD5\|getInstance.*SHA-1" \
  <java_path> --include="*.java"

# HTTP (not HTTPS) in config
grep -rn "http://\|requiresHttps.*false\|http\.requiresChannel" \
  <java_path> --include="*.yml" --include="*.properties"
```

### A03: Injection
```bash
# SQL injection risk (string concatenation in queries)
grep -rn "createQuery\|nativeQuery\|createNativeQuery\|jdbcTemplate" \
  <java_path> --include="*.java" -A2 | grep '"+\|+ "' | head -20

# JPQL string concat
grep -rn '"SELECT.*" +\|"FROM.*" +\|"WHERE.*" +' <java_path> --include="*.java"
```

### A05: Security Misconfiguration
```bash
# CORS wildcard
grep -rn "allowedOrigins.*\*\|cors.*\*\|CorsConfiguration\|@CrossOrigin" \
  <java_path> --include="*.java" | head -20

# Actuator endpoints exposed without auth
grep -rn "management\.endpoints\.web\.exposure\|include=\*\|include: '\*'" \
  <java_path> --include="*.yml" --include="*.properties"

# Stack traces exposed to client
grep -rn "printStackTrace\|getStackTrace\|@ExceptionHandler" \
  <java_path> --include="*.java" | grep -v "log\." | head -20
```

### A07: Identification and Authentication Failures
```bash
# No account lockout
grep -rn "BadCredentialsException\|failedAttempts\|lockAccount\|accountNonLocked" \
  <java_path> --include="*.java" | head -20

# Hardcoded credentials
grep -rn "password.*=.*\"[^${\"]" <java_path> \
  --include="*.java" --include="*.yml" --include="*.properties" | \
  grep -v "//\|test\|Test\|#\|placeholder" | head -20
```

### A09: Security Logging Failures
```bash
# Missing security event logging
grep -rn "AuthenticationSuccessHandler\|AuthenticationFailureHandler\|@PostAuthorize" \
  <java_path> --include="*.java" | head -20
grep -rn "ACCESS_DENIED\|AUTHENTICATION_FAILURE\|audit\|AuditLog" \
  <java_path> --include="*.java" | head -20
```

## Output: Security Report

```
SECURITY AUDIT REPORT: [System]
Date: [date] | Severity Scale: CVSS 3.1

CRITICAL FINDINGS ([N])
  SEC-001 [CVSS 9.x]: [Finding]
    Location: [file/module]
    Risk:     [What an attacker can do]
    Fix:      [Specific remediation]

HIGH FINDINGS ([N]) ...
MEDIUM FINDINGS ([N]) ...

COMPLIANCE NOTES (for financial services):
  - PCI DSS: [relevant findings]
  - GDPR: [relevant findings]
  - Regulatory: [KYC/AML implications]
```
