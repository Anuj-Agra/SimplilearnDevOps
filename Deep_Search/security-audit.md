# Workflow: Security Audit

Use this workflow to perform a comprehensive security audit of a codebase, module, or feature.

## Step-by-Step Protocol

### Step 1 — Map Attack Surface
```
TASK: Find every point where external input enters the system

Search for:
- HTTP route handlers (GET, POST, PUT, DELETE, PATCH)
- WebSocket message handlers
- File upload handlers
- Message queue consumers
- CLI argument parsers
- Environment variable readers
- Database query builders that accept parameters

Record:
- Each entry point with file:line
- What input it accepts (body, query params, headers, files)
- Whether input is validated before use
```

### Step 2 — Trace Input to Dangerous Sinks
```
TASK: For each entry point, trace where user input ends up

Dangerous sinks to search for:
- SQL/NoSQL queries (SQL injection)
- HTML rendering (XSS)
- Shell command execution (command injection)
- File system operations with user input (path traversal)
- Deserialization of user input (deserialization attacks)
- Redirect URLs from user input (open redirect)
- Regex with user input (ReDoS)
- Template rendering with user input (SSTI)

For each trace:
- Is input sanitized/validated BEFORE reaching the sink?
- Is parameterized/prepared query used for DB operations?
- Is output encoding applied for HTML rendering?
```

### Step 3 — Authentication & Authorization Review
```
TASK: Verify auth is correctly applied everywhere

Search for:
- Routes/endpoints WITHOUT auth middleware
- Auth bypass patterns (skip auth for certain paths)
- Token validation logic — is it correct?
- Session management — creation, expiry, invalidation
- Role/permission checks — are they consistent?
- CORS configuration — is it restrictive enough?

Check:
- Are admin endpoints properly protected?
- Can a regular user access admin functionality?
- Is auth checked on EVERY request, or can it be skipped?
- Are API keys/tokens rotated and scoped?
```

### Step 4 — Secrets & Configuration
```
TASK: Find secrets, credentials, and insecure configuration

Search for:
- Hardcoded secrets (API keys, passwords, tokens)
- .env files committed to git
- Default credentials that haven't been changed
- Insecure default configurations
- Debug/development mode flags in production config
- Verbose error messages that leak internals

Patterns to search:
- "password" / "secret" / "api_key" / "token" / "credential"
- "BEGIN RSA PRIVATE KEY" / "BEGIN CERTIFICATE"
- "sk_live_" / "pk_live_" (Stripe keys)
- "AKIA" (AWS access keys)
- "mongodb+srv://" / "postgres://" with passwords in URL
```

### Step 5 — Dependency Vulnerabilities
```
TASK: Assess third-party dependency risk

Search for:
- Package manifests and lock files
- Outdated packages with known vulnerabilities
- Packages with low maintenance or suspicious origins
- Dependencies pulled from non-standard registries
- Pinned vs floating version ranges

Check:
- Are lock files committed? (prevents supply chain attacks)
- Are there any deprecated packages still in use?
- Are security-critical packages (crypto, auth, TLS) up to date?
```

### Step 6 — Data Protection
```
TASK: Verify sensitive data is properly handled

Search for:
- PII fields (email, phone, SSN, address) — how are they stored?
- Encryption at rest — are sensitive fields encrypted in DB?
- Encryption in transit — is TLS enforced?
- Logging — are sensitive fields redacted from logs?
- Error responses — do they leak internal state or PII?
- Data retention — is there cleanup for old/deleted user data?
```

### Step 7 — Synthesize Findings
```
OUTPUT: Security audit report

## 🔒 Security Audit: {target}

### Risk Summary
| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Injection | | | | |
| Auth | | | | |
| Secrets | | | | |
| Dependencies | | | | |
| Data Protection | | | | |

### 🔴 Critical Findings
{each with: description, file:line, proof, fix recommendation}

### 🟠 High Findings
{same format}

### 🟡 Medium Findings
{same format}

### Positive Findings
{security practices that are well-implemented}

### Recommended Priorities
1. {most urgent fix}
2. {second priority}
3. {third priority}
```

## Example Prompt

```
Follow the workflow in @workspace workflows/security-audit.md to audit:

Our user authentication and session management flow — 
check for auth bypass, session fixation, and token handling issues.
```
