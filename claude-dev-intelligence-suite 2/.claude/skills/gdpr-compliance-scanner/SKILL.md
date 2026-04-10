---
name: gdpr-compliance-scanner
description: >
  Find all PII storage, processing, and transmission in Java/Angular codebases and
  map against GDPR, MiFID II, AML, and KYC requirements. Use when asked: 'GDPR scan',
  'compliance audit', 'PII mapping', 'data protection', 'regulatory compliance',
  'Article 30', 'right to erasure', 'data retention', 'MiFID compliance', 'KYC audit',
  'AML review', 'DPIA', 'data flow mapping'. Produces Article 30 records of processing
  and flags retention policy gaps. Essential for financial services systems.
---
# GDPR / Regulatory Compliance Scanner

## Step 1 — PII Field Discovery
```bash
# Find PII field names across entities/DTOs
grep -rn "name\|email\|phone\|address\|dob\|dateOfBirth\|ssn\|nationalId\|passport\|\
  taxId\|salary\|income\|accountNumber\|sortCode\|iban\|creditCard\|ipAddress\|deviceId" \
  <java_path> --include="*.java" | grep "private\|String\|field\|column" | head -100

# Find PII in Angular forms
grep -rn "name.*Control\|email.*Control\|phone.*Control\|address.*Control\|dob\|dateOfBirth" \
  <angular_path> --include="*.ts" | head -40
```

## Step 2 — Data Flow Mapping
```bash
# Where PII is logged (GDPR violation if unmasked)
grep -rn "log\.\(info\|debug\|warn\|error\)" <java_path> --include="*.java" | \
  grep -i "email\|name\|phone\|address\|account\|customer" | head -40

# Where PII is sent externally
grep -rn "restTemplate\.\|webClient\.\|feign\." <java_path> --include="*.java" -A3 | \
  grep -i "email\|name\|phone\|address" | head -30

# Retention / expiry logic
grep -rn "deleteBy\|expiry\|retention\|purge\|archive\|@Scheduled.*delete\|TTL\|expiresAt" \
  <java_path> --include="*.java" | head -30

# Right to erasure implementation
grep -rn "deleteById\|deleteByCustomerId\|anonymise\|anonymize\|erasure\|rightToDelete" \
  <java_path> --include="*.java" | head -20

# Consent management
grep -rn "consent\|optIn\|optOut\|marketing\|gdprConsent" \
  <java_path> --include="*.java" | head -20
```

## Step 3 — Output: Article 30 Record + Compliance Gaps

```
GDPR COMPLIANCE REPORT: [System]

ARTICLE 30 — RECORDS OF PROCESSING ACTIVITIES
| Data Category | Purpose | Legal Basis | Retention Period | Recipients | Risk |
|---|---|---|---|---|---|
| Customer Name + Email | Account management | Contract | Duration of account | Internal only | LOW |
| Payment Details | Transaction processing | Contract | 7 years (regulatory) | Payment processor | MED |

GAPS IDENTIFIED:
  GAP-001 [CRITICAL]: No right-to-erasure endpoint found
    Impact: Cannot comply with GDPR Art.17 requests
    Fix: Implement DELETE /api/customers/{id} that anonymises all PII fields

  GAP-002 [HIGH]: PII found in application logs (email, name)
    Location: [files]
    Fix: Mask PII before logging using @JsonIgnore / custom log filter

  GAP-003 [HIGH]: No data retention policy detected for [entity]
    Fix: Add @Scheduled cleanup job with configurable retention period

KYC / AML SPECIFIC:
  - Customer Due Diligence records: retention found? [Yes/No]
  - Transaction monitoring audit trail: [Yes/No]
  - Suspicious Activity Report logging: [Yes/No]

MiFID II:
  - Trade record retention (7 years): [Yes/No]
  - Best execution recording: [Yes/No]
```
