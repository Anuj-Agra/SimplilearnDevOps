# Skill: KYC External Services

> Inject this file into agents working with integrations, connector rules, or external data sources in the KYC system.

---

## External service categories

### 1. Sanctions screening providers

**Purpose**: Check customer, UBOs, directors, and counterparties against global sanctions lists (OFAC, UN, EU, HMT, and others).

| Data sent | Data returned |
|----------|--------------|
| Full name, DOB, nationality, address | Hit flag (Y/N), match score (0–100), hit details (list name, entry, match reason), reference ID |

**Key vendors** (examples — confirm with client): Refinitiv World-Check, LexisNexis WorldCompliance, Dow Jones Risk & Compliance, ComplyAdvantage, ACAMS, Accuity (now Fircosoft)

**Protocol**: REST/JSON (modern providers); SOAP/XML (legacy)

**KYC flow integration point**: Immediately after CDD data entry; repeated at periodic review; re-screened when lists update

**Error handling requirements**: Timeout → manual queue; confirmed hit → Sanctions Review workbasket; near-hit → flag for manual review

---

### 2. PEP screening providers

**Purpose**: Identify Politically Exposed Persons and their close associates and family members.

| Data sent | Data returned |
|----------|--------------|
| Full name, DOB, nationality, country of residence | PEP flag (Y/N), PEP category, position, country, relationship type (self/associate/family), source |

**Note**: PEP screening is often bundled with sanctions screening (same provider, same API call). Confirm whether client uses combined or separate providers.

**Key vendors**: Same as sanctions providers — World-Check, WorldCompliance, ComplyAdvantage

---

### 3. Identity verification providers

**Purpose**: Verify that a customer's claimed identity matches authoritative records.

| Verification type | Data sent | Data returned |
|-----------------|----------|--------------|
| Document verification | ID document image (passport/licence), selfie | Document authenticity score, MRZ data extracted, face match score, liveness check result |
| Database verification | Name, DOB, address, national ID | Match confidence score, matched records count, data source |
| Address verification | Name, address | Address validated (Y/N), formatted address, geo-coordinates |

**Key vendors**: Jumio, Onfido, Mitek, Experian Identity, GBG, LexisNexis Risk Solutions, Trulioo

**Protocol**: REST/JSON with multipart/form-data for document images

**KYC flow integration point**: Document upload step; identity check step during CDD initiation

---

### 4. Credit bureaus

**Purpose**: Verify identity using credit history and financial records; assess creditworthiness (if in scope).

| Data sent | Data returned |
|----------|--------------|
| Name, DOB, address, national ID (e.g. SSN, NIN) | Identity match score, address history, credit summary (if in scope), fraud indicators |

**Key vendors**: Experian, Equifax, TransUnion, Dun & Bradstreet (for corporates)

**Protocol**: REST/JSON or SOAP/XML depending on provider and product

---

### 5. Company registry services

**Purpose**: Verify corporate customers' registration details and identify directors and shareholders (for UBO identification).

| Data sent | Data returned |
|----------|--------------|
| Company name, registration number, country | Registered name, status (active/dissolved), registered address, director list, shareholder list, filing history |

**Key vendors**: Companies House (UK), OpenCorporates, Bureau van Dijk (Orbis), Dun & Bradstreet, Refinitiv

**Protocol**: REST/JSON (modern); some national registries provide only web scraping or batch file

---

### 6. Document OCR / classification providers

**Purpose**: Extract data from uploaded KYC documents (passport, utility bill, bank statement).

| Data sent | Data returned |
|----------|--------------|
| Document image (JPEG/PNG/PDF) | Document type classification, extracted fields (name, DOB, document number, expiry, address), quality score, tampering indicators |

**Key vendors**: ABBYY, AWS Textract, Google Document AI, Microsoft Azure Form Recognizer, Jumio (bundled with ID verification)

**Protocol**: REST/JSON with Base64-encoded image or multipart/form-data

**Performance note**: OCR processing typically takes 2–30 seconds → use async pattern (Spinoff)

---

### 7. Core banking / CRM system

**Purpose**: Retrieve and update customer master data; link KYC case to account.

| Direction | Data |
|----------|------|
| Inbound (CRM → PEGA) | Customer ID, name, relationship history, account details, existing KYC status |
| Outbound (PEGA → CRM) | KYC completion status, risk rating, next review date, EDD flag |

**Protocol**: Varies by client — REST/JSON (modern), SOAP/XML, MQ, or database direct (via PEGA Data Page)

---

### 8. Regulatory reporting / FIU

**Purpose**: File Suspicious Activity Reports (SARs) or Suspicious Transaction Reports (STRs) with the Financial Intelligence Unit.

| Data sent | Channel |
|----------|---------|
| SAR form data: subject details, suspicion description, transaction data, narrative | Regulator's reporting portal (GoAML, FinCEN BSA E-Filing, NCA SARS) — typically file-based or web portal submission |

**Note**: In most jurisdictions, SAR filing is NOT an API — it is a secure web portal submission or secure file upload. PEGA generates the SAR report; submission may be manual or semi-automated.

---

## Integration non-negotiables (apply to all KYC external services)

| Requirement | Detail |
|------------|--------|
| Timeout configuration | Every connector must have a timeout (recommended: 5s for synchronous; 30s for async) |
| Error routing | `pyServiceFailed = true` must always route to a defined fallback (manual queue or alert) |
| Audit logging | Every service call must be logged: timestamp, request summary, response summary, outcome |
| PII in transit | All calls must use TLS 1.3 minimum; no PII in URL parameters (use POST body) |
| Credential management | All API keys and OAuth credentials stored in PEGA Auth Profile + Keystore — never hardcoded |
| Retry policy | Transient failures (timeout, 5xx): retry up to 3× with exponential backoff |
| Data residency | Confirm whether external service processes data outside the permitted jurisdiction; if so, GDPR Art. 46 safeguards required |
| Vendor SLA | Document the vendor's uptime SLA and compare to the fallback tolerance |
| Mock / stub for testing | All external services must have a mock/stub available for DEV and TEST environments — never call production APIs from non-prod |
