---
name: data-lineage-mapper
description: >
  Trace how a specific data field (e.g. customerId, accountNumber, orderId) flows
  through the entire system — where it enters, every service that reads or transforms
  it, and where it exits. Use when asked: 'data lineage', 'trace this field', 'where
  does customerId go', 'data flow', 'field tracing', 'how does data move', 'impact
  of changing this field', 'data journey'. Essential for KYC/CRD data governance,
  GDPR data mapping, and understanding field-level blast radius.
---
# Data Lineage Mapper

Trace a specific field or entity through the entire system.

## Step 0 — Identify the Target Field
Ask user: which field to trace? (e.g. `customerId`, `accountNumber`, `email`)

## Step 1 — Entry Points
```bash
FIELD="customerId"  # substitute with target

# Where the field first enters the system
grep -rn "@RequestBody\|@RequestParam\|@PathVariable" \
  <java_path> --include="*.java" -A5 | grep -i "$FIELD" | head -30

# Angular form fields where user inputs this value
grep -rn "formControlName.*$FIELD\|$FIELD.*formControl\|\[$FIELD\]" \
  <angular_path> --include="*.html" --include="*.ts" | head -20
```

## Step 2 — Transformations
```bash
# Service methods that read/write/transform the field
grep -rn "$FIELD" <java_path>/src/main/java --include="*.java" | \
  grep -v "import\|//\|test\|Test\|@Column\|@JsonProperty" | head -80

# Mappings and conversions
grep -rn "map\|convert\|transform\|toDto\|toEntity\|mapper" \
  <java_path> --include="*.java" -A3 | grep -i "$FIELD" | head -30
```

## Step 3 — Storage Points
```bash
# Database persistence
grep -rn "@Column.*$FIELD\|$FIELD.*@Column\|\"$FIELD\"" \
  <java_path> --include="*.java" | head -20

# Cache storage
grep -rn "@Cacheable.*$FIELD\|@CacheKey.*$FIELD\|cacheKey.*$FIELD" \
  <java_path> --include="*.java" | head -10
```

## Step 4 — Exit Points (where field leaves the system)
```bash
# Sent to external systems
grep -rn "restTemplate\.\|WebClient\.\|feign\." \
  <java_path> --include="*.java" -A5 | grep -i "$FIELD" | head -30

# Logged (PII risk)
grep -rn "log\." <java_path> --include="*.java" | grep -i "$FIELD" | head -20

# Included in exports/reports
grep -rn "export\|report\|csv\|excel\|pdf" <java_path> --include="*.java" -A3 | \
  grep -i "$FIELD" | head -20
```

## Step 5 — Output: Lineage Diagram

```
DATA LINEAGE: [fieldName]

ENTRY:
  → Angular Form: [screen name, field label]
  → API: [endpoint — plain English]

JOURNEY:
  [Service A] reads → [transforms to X] → passes to [Service B]
  [Service B] validates → stores in [Entity name]
  [Service B] → sends to [External System] via [integration name]

STORAGE:
  Primary store: [entity name — not table name]
  Cache: [yes/no, TTL if yes]

EXIT POINTS:
  → External system: [name]
  → Logs: [masked/unmasked — GDPR flag if unmasked]
  → Reports: [which reports include this field]

GDPR CLASSIFICATION: [Personal Data / Sensitive Personal Data / Anonymous]
CHANGE IMPACT: Changing this field affects [N] components
```
