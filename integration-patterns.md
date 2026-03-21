# Skill: PEGA Integration Patterns

> Inject this file into agents working with PEGA external service calls, connector rules, or data exchange patterns.

---

## Integration pattern catalogue

### Pattern 1 — Synchronous REST (real-time)

**Use when**: Response needed immediately to continue the flow (e.g. sanctions check result determines next step).

```
Flow step (Connector type)
    │
    ├─► DT: Build request payload (maps PEGA properties → JSON/XML)
    │
    ├─► [Connector and Metadata rule] POST → External API
    │
    ├─► DT: Parse response (maps JSON/XML → PEGA properties)
    │
    └─► Next flow step reads mapped properties
```

**PEGA rules involved**: Connector and Metadata rule, 2× Data Transform rules (request + response), When rule (error condition check)

**Error handling**: `pyServiceFailed` Boolean is set to `true` on failure. Flow connector checks this and branches to error path.

**KYC examples**: Sanctions API, PEP check, identity verification, credit bureau, OCR (fast), address validation

---

### Pattern 2 — Asynchronous (Spinoff)

**Use when**: External service is slow (> 5s) or response is needed later, not immediately.

```
Main flow step (Spinoff)
    │
    ├─► Spawns a child case or sub-flow (runs independently)
    │       │
    │       ├─► DT: Build request
    │       ├─► Connector: call external service
    │       ├─► DT: Parse response
    │       └─► Update parent case via savable Data Page
    │
    └─► Main flow continues without waiting
    ...
    [Later] Parent case checks for child completion via Await step
```

**PEGA rules involved**: Spinoff step in main flow, child Flow rule, Connector, Data Transforms, Savable Data Page

**KYC examples**: Document OCR (slow), external risk model batch scoring, async PEP enrichment

---

### Pattern 3 — Data Page (cached lookup)

**Use when**: Data changes infrequently and can be cached (e.g. country risk list, document type list).

```
Data Page rule (D_CountryList)
    │
    ├─► Source: Connector call OR Report Definition OR Data Transform
    │
    ├─► Cached at: Page / Thread / Requestor / Node level
    │
    └─► Referenced anywhere on clipboard as .D_CountryList
```

**PEGA rules involved**: Data Page rule, Connector or Report Definition as source

**KYC examples**: `D_CountryRiskList`, `D_DocumentTypeList`, `D_SanctionsListMetadata`, `D_ExchangeRates`

**Cache invalidation**: Set `pyExpireAfter` on the Data Page; or call `.ReloadDataPage` from a flow when a refresh is needed.

---

### Pattern 4 — Declare Expression (reactive calculation)

**Use when**: A property value must always reflect a calculated result, recalculated whenever source properties change.

```
Property: OverallRiskScore
    │
    └─► Declare Expression rule: KYC_CalcOverallRisk
            Source: CountryRiskScore * 0.4 + CustomerTypeScore * 0.3 + PEPScore * 0.3
            When: [always] or [condition]
            Chain type: Forward (recalculate when sources change)
```

**KYC examples**: `OverallRiskScore` (composite of multiple risk factors), `IsEDDRequired` (Boolean derived from PEP + country + score), `DaysToSLABreach`

---

### Pattern 5 — File-based integration (batch)

**Use when**: Large volumes of data are exchanged periodically (daily/weekly) rather than in real-time.

```
File Listener rule (monitors SFTP / filesystem)
    │
    ├─► Detects new file
    │
    ├─► Activity or Queue Processor reads file rows
    │
    └─► For each row: creates/updates PEGA case or data record
```

**KYC examples**: Nightly sanctions list refresh (OFAC, UN, EU), customer risk rating batch update, regulatory reporting export, CRM data sync

---

### Pattern 6 — Inbound service (PEGA as receiver)

**Use when**: An external system calls PEGA (rather than PEGA calling out).

```
External system → POST → PEGA Service REST rule (KYC_ReceiveCDDRequest)
                                │
                                ├─► Authenticate caller (Auth Profile)
                                ├─► Validate payload
                                ├─► Create/update case
                                └─► Return response (case ID, status)
```

**KYC examples**: Customer portal submitting an onboarding request, core banking system triggering a KYC refresh, risk engine pushing updated scores

---

## Common error handling properties

| Property | Type | Meaning |
|---------|------|---------|
| `pyServiceFailed` | Boolean | Set to `true` when a connector call fails |
| `pyServiceFailureCode` | String | HTTP status code or error type |
| `pyServiceFailureMessage` | String | Error message from the service |
| `pyStatusCode` | Integer | HTTP response code |
| `pxObjClass` | String | Response page class |

**Standard error flow pattern**:
```
Connector step
    │
    ├─► [pyServiceFailed = false] → Continue normal flow
    └─► [pyServiceFailed = true]  → Route to error handling step
            │
            ├─► Log error to audit trail
            ├─► Set case note
            ├─► Route to manual workbasket
            └─► Optionally: raise alert / send notification
```

---

## Authentication patterns

| Pattern | PEGA implementation | KYC use |
|---------|-------------------|---------|
| API Key | Auth Profile rule — key in header or query param | Simple API key authentication |
| OAuth 2.0 Client Credentials | Auth Profile rule — client ID + secret → token endpoint | Most modern KYC APIs |
| Mutual TLS (mTLS) | Keystore rule + SSL Profile | High-security financial APIs |
| Basic Auth | Auth Profile rule — username + password (Base64) | Legacy services only |
| Bearer Token | Auth Profile rule — static token in Authorization header | Internal services |

---

## Integration anti-patterns to flag

| Anti-pattern | Risk | Better approach |
|-------------|------|----------------|
| Hardcoded endpoint URL in connector | Cannot change env without code change | Use Dynamic System Settings or Data Page for URL |
| No timeout set on connector | Connector hangs indefinitely | Always set `pyTimeout` (recommended: 5000ms = 5s) |
| No error handling after connector step | Flow fails silently | Always check `pyServiceFailed` after every connector step |
| Calling external service in Declare Expression | Called on every property access — potential performance issue | Use Flow step connector pattern instead |
| Synchronous call to slow service | Blocks user's session | Use Spinoff / async pattern for services > 3s |
| Credentials in connector URL | Security vulnerability | Use Auth Profile rule + Keystore |
| No retry logic | Transient failures not recovered | Implement retry loop (3× with backoff) |
