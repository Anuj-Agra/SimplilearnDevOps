
INSTRUCTIONS FOR USE
════════════════════════════════════════════════════════════════════
1. Open a NEW conversation at claude.ai (no Project needed)
2. Copy EVERYTHING from the first === line below to the very end
3. Paste it as your message
4. BEFORE sending, scroll to the bottom and fill in the [PASTE HERE] sections
   with content from your actual BIN files and manifest JSONs
5. Send — Claude will produce all 4 updated skill files in one response
════════════════════════════════════════════════════════════════════

HOW TO GET YOUR BIN CONTENT (no software needed)
  Windows: right-click a .bin file → Open with → Notepad
  Mac:     right-click → Open With → TextEdit
  You will see garbled characters mixed with readable English text.
  Copy ONLY the readable parts — rule names, numbers, property names,
  status strings, URLs, field names. Ignore all the garbage characters.

WHICH FILES TO OPEN FIRST (in this order):
  1. Any .bin file whose name contains: Flow, CDD, EDD, Approval, Onboard
  2. Any .bin file whose name contains: Connector, Connect, API, Service, Screen
  3. Any .bin file whose name contains: SLA, Workbasket, Route, Status, Assign
  4. Any .bin file whose name contains: Risk, Score, Rating, Threshold, Country
  5. Your manifest JSON files — search for "pxObjClass" to find rule types
════════════════════════════════════════════════════════════════════

=== START OF PROMPT — COPY FROM HERE ===

You are a PEGA KYC Domain Calibrator. Your job is to read raw evidence
extracted from a real PEGA KYC codebase — manifest JSON entries and
readable strings extracted from native .bin rule files — and produce
4 fully updated KYC domain skill files with client-specific values
replacing all generic placeholders.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYSIS METHOD — apply these 5 lenses to every piece of evidence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LENS 1 — RULE NAMING PATTERNS
PEGA rule names encode business intent directly.
  KYC_CalculateRiskScore   → risk scoring activity exists; look for numbers nearby
  COB_EDDApprovalFlow      → EDD has a named approval flow in the COB application
  MSFW_SanctionsConnector  → connector to a sanctions service exists
  KYC_IsHighRisk           → a When condition defines the HIGH risk boundary
  KYC-SLA-ComplianceReview → an SLA rule governs the Compliance review step
Extract every business concept encoded in rule names.

LENS 2 — PROPERTY NAME PATTERNS
Property names reveal the real data model.
  .pxRiskRating            → the actual risk rating field name
  .CustomerRiskScore       → the actual score property
  .RMApprovalStatus        → approval status field
  .EDDRequired             → EDD flag property
  .pxFlow                  → flow name reference
These replace the generic property names in the skill files.

LENS 3 — DECISION / THRESHOLD FRAGMENTS
Strings like "LOW","MEDIUM","HIGH" near numbers "0","39","40","69","70","100"
reveal actual thresholds. A Decision Table .bin often contains the full
threshold table as readable text. Factor names like "CountryRisk",
"CustomerType", "PEPStatus" reveal the actual risk model inputs.

LENS 4 — CONNECTOR AND SERVICE PATTERNS
Connector rule names (KYC-Conn-SanctionsAPI, MSFW_WorldCheckConnector)
identify the vendor or service. HTTP strings (POST, GET, /api/v1/),
URL fragments (https://api.worldcheck.com), response field names
(hitFlag, matchScore, screeningResult) reveal the data contract.
Auth keywords (OAuth, Bearer, APIKey, ClientId) reveal authentication method.

LENS 5 — STATUS, WORKBASKET AND ROLE PATTERNS
Status strings (Open-KYCReview, Resolved-Approved, Open-EDDRequired),
workbasket names (KYC-ComplianceTeam-WB, COB-RMApproval-WB), and
role references (ComplianceOfficer, RelationshipManager, MLRO) reveal
the real approval hierarchy and case lifecycle.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT RULES — follow these exactly
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ONLY UPDATE WHAT YOU CAN EVIDENCE. If a value is not evidenced in the
   input, keep the generic text and mark it: ⚠ NOT CONFIRMED — verify with PEGA developer

2. MARK EVERY VALUE with one of these confidence tags:
   ✓ CONFIRMED  = found directly in a rule name, BIN string, or manifest field
   ~ INFERRED   = logically deduced from naming patterns, not directly stated
   ⚠ NOT CONFIRMED = generic value kept — not evidenced in this codebase
   ⚠ CONFLICT   = two sources give different values — flag both

3. CITE YOUR SOURCE inline after each changed value, like this:
   <!-- Source: BIN strings from KYC_RiskThresholdDT.bin -->

4. PRODUCE ALL 4 FILES in sequence — complete, full content, no abbreviations.
   Do not summarise or skip sections. Replace values inline.

5. DO NOT INVENT. If a connector name appears but no URL is visible, write:
   [URL not found in BIN evidence — confirm with developer]
   Never fill in a plausible-sounding value.

6. PREPEND THIS HEADER to each file:

   # STATUS: Calibrated from codebase BIN/manifest evidence
   # Applications analysed: [list app names from the evidence]
   # Date: [today]
   # Confirmed values: [count] | Inferred: [count] | Not confirmed: [count]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE 4 GENERIC SKILL FILES — these are what you will update
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

═══ CURRENT FILE 1: skills/kyc-domain/risk-scoring.md ═══

# Skill: KYC Risk Scoring

## Standard KYC risk scoring model

### Composite risk score formula (typical)

```
OverallRiskScore = (CountryRisk × W1) + (CustomerTypeRisk × W2) + (PEPRisk × W3) + (ProductRisk × W4)

Typical weights:
  W1 (Country)         = 0.40
  W2 (Customer type)   = 0.30
  W3 (PEP status)      = 0.20
  W4 (Product/channel) = 0.10
```

### Risk rating thresholds

| Score range | Risk rating | Routing |
|------------|-------------|---------|
| 0 – 39     | LOW         | Auto-approve (if no hits, no PEP, docs verified) |
| 40 – 69    | MEDIUM      | Relationship Manager review |
| 70 – 100   | HIGH        | Compliance Officer review + EDD mandatory |

### EDD mandatory triggers (non-score-based)

Conditions that trigger EDD regardless of composite score:
1. PEPFlag = true
2. CustomerNationality on FATF Call for Action list
3. CustomerType = Trust, Foundation, Shell Company, or SPV
4. UBOIdentified = false
5. SanctionsNearHit = true
6. Correspondent banking relationship

### Auto-approval conditions

ALL of these must be true for system auto-approval:
- OverallRiskScore < LOW threshold (< 40)
- PEPFlag = false
- SanctionsHitFlag = false
- SanctionsNearHitFlag = false
- DocumentVerificationStatus = "Verified"
- UBOIdentified = true (for legal entities)
- CountryRisk not on grey or black list

### Periodic review schedule

| Risk rating | Review frequency |
|-------------|-----------------|
| LOW         | Every 5 years   |
| MEDIUM      | Every 3 years   |
| HIGH        | Annually        |
| PEP         | Annually        |

═══ CURRENT FILE 2: skills/kyc-domain/approval-flows.md ═══

# Skill: KYC Approval Flows

## KYC approval hierarchy

AUTO-APPROVE
    Condition: LOW risk + no hits + all docs verified + no PEP
    Actor: System
    SLA: Immediate

RM REVIEW
    Condition: MEDIUM risk
    Actor: Assigned Relationship Manager
    Workbasket: KYC-RMReview-WB
    SLA: 48 business hours
    Escalation: → Compliance if SLA breached

COMPLIANCE REVIEW
    Condition: HIGH risk OR PEP OR EDD required
    Actor: Compliance Officer
    Workbasket: KYC-Compliance-WB
    SLA: 5 business days
    Escalation: → Head of Compliance if SLA breached

DUAL APPROVAL (Maker-Checker)
    Condition: EDD cases, sanctions near-hits, HIGH risk corporate
    Actor 1 (Maker): Compliance Officer
    Actor 2 (Checker): Senior Compliance Officer
    Constraint: Maker ≠ Checker (enforced by Router rule)

SANCTIONS REVIEW
    Condition: Confirmed sanctions hit
    Actor: Dedicated Sanctions Review team
    Workbasket: KYC-Sanctions-WB
    SLA: 24 business hours

MLRO APPROVAL
    Condition: SAR filing required
    Actor: Money Laundering Reporting Officer
    Workbasket: KYC-MLRO-WB

## SLA reference table

| SLA rule name              | Process              | Goal     | Deadline  |
|---------------------------|----------------------|----------|-----------|
| KYC-SLA-RMReview          | RM review            | 24 hours | 48 hours  |
| KYC-SLA-ComplianceReview  | Compliance review    | 3 days   | 5 days    |
| KYC-SLA-EDDCompletion     | Full EDD case        | 5 days   | 10 days   |
| KYC-SLA-SanctionsReview   | Sanctions hit review | 4 hours  | 24 hours  |

## Workbasket reference

| Workbasket name           | Owner               | Receives                        |
|--------------------------|---------------------|--------------------------------|
| KYC-Initiation-WB        | KYC Operations      | New CDD cases                  |
| KYC-RMReview-WB          | Relationship Mgrs   | MEDIUM risk cases              |
| KYC-Compliance-WB        | Compliance Officers | HIGH risk, PEP, EDD cases      |
| KYC-Sanctions-WB         | Sanctions Team      | Sanctions hit cases            |
| KYC-MLRO-WB              | MLRO                | SAR and escalated cases        |
| KYC-PeriodicReview-WB    | KYC Operations      | Cases due for periodic review  |

## Case status transitions

| Decision                  | Status after               |
|--------------------------|---------------------------|
| Auto-approved             | Resolved-Approved          |
| RM approved               | Resolved-Approved          |
| RM escalated              | Open-ComplianceReview      |
| Compliance approved       | Resolved-Approved          |
| Compliance EDD required   | Open-EDDReview             |
| Compliance rejected       | Resolved-Rejected          |
| Checker approved          | Resolved-Approved          |
| Checker sent back         | Open-ComplianceReview      |
| Sanctions escalated       | Open-MLROReview            |
| MLRO account blocked      | Resolved-Blocked           |

═══ CURRENT FILE 3: skills/kyc-domain/external-services.md ═══

# Skill: KYC External Services

## 1. Sanctions screening

Purpose: Check against OFAC, UN, EU, HMT lists
Vendors: Refinitiv World-Check, LexisNexis, ComplyAdvantage (confirm with client)
PEGA connector rule: [confirm from codebase]
Protocol: REST/JSON
Data sent: Full name, DOB, nationality
Data returned: hitFlag, matchScore, hitDetails
Timeout: 5 seconds (recommended)
On timeout: route to KYC-Manual-Screening-WB

## 2. PEP screening

Often bundled with sanctions — same provider, same API call.
PEP data returned: pepFlag, pepCategory, position, country, relationship type

## 3. Identity / document verification

Vendors: Jumio, Onfido, Mitek, GBG (confirm with client)
PEGA connector rule: [confirm from codebase]
Protocol: REST/JSON + multipart/form-data for images
Data sent: ID document image, selfie image
Data returned: authenticityScore, extractedData, faceMatchScore, livenessResult
Note: async pattern (Spinoff) recommended — processing takes 2–30 seconds

## 4. Credit bureau / database verification

Vendors: Experian, Equifax, TransUnion (confirm with client)
PEGA connector rule: [confirm from codebase]
Data sent: Name, DOB, address, national ID
Data returned: identityMatchScore, addressHistory, fraudIndicators

## 5. Company registry

Vendors: Companies House (UK), OpenCorporates, Bureau van Dijk
PEGA connector rule: [confirm from codebase]
Data sent: Company name, registration number, country
Data returned: Directors list, shareholders list, UBO data

## 6. Core banking / CRM

PEGA connector rule: [confirm from codebase]
Direction inbound (CRM → PEGA): customer ID, account details, existing KYC status
Direction outbound (PEGA → CRM): KYC completion status, risk rating, next review date

## Integration requirements (all services)

- Timeout: every connector must have a configured timeout
- Error routing: pyServiceFailed = true must always route to a fallback
- Audit logging: every call must be logged with timestamp and outcome
- PII in transit: TLS 1.3 minimum; no PII in URL parameters
- Credentials: stored in PEGA Auth Profile + Keystore, never hardcoded

═══ CURRENT FILE 4: skills/kyc-domain/regulatory-framework.md ═══

# Skill: KYC Regulatory Framework

## Core regulatory obligations implemented

| FATF Rec | Obligation              | Implemented by (PEGA process) |
|----------|------------------------|------------------------------|
| Rec 10   | Customer identification | CDD case type + verification flow |
| Rec 11   | Record keeping 5 years  | Data retention policy + audit log |
| Rec 12   | PEP enhanced CDD        | EDD flow + senior approval |
| Rec 20   | Suspicious transaction reporting | SAR case type |

## KYC process → regulatory obligation mapping

| Process step              | Obligation                         | Source               |
|--------------------------|------------------------------------|---------------------|
| Customer identification  | FATF Rec 10; AMLD Art. 13          | CDD initiation flow |
| Document verification    | FATF Rec 10; AMLD Art. 13(1)(a)    | Document review step |
| Sanctions screening      | FATF Rec 10; OFAC / UN / EU lists  | Screening activity  |
| PEP screening            | FATF Rec 12; AMLD Art. 20          | Screening activity  |
| UBO identification       | FATF Rec 10; AMLD Art. 13(1)(b)    | Corporate CDD step  |
| EDD                      | FATF Rec 12, 19; AMLD Art. 18      | EDD flow            |
| SAR filing               | FATF Rec 20; AMLD Art. 33          | SAR case type       |
| Periodic review          | FATF Rec 10; AMLD Art. 14          | Periodic review flow|
| Record keeping           | FATF Rec 11; AMLD Art. 40          | Data retention rule |

## EDD triggers (mandatory, not discretionary)

- PEPFlag = true
- Country on FATF Call for Action list
- Country on EU high-risk third country list (5th AMLD)
- CustomerType = Trust, Foundation, Shell Company, or SPV
- UBO not identified for a legal entity
- Source of funds unclear

## Data retention requirements

| Data type              | Minimum period | Clock starts     |
|-----------------------|----------------|-----------------|
| CDD records            | 5 years        | Account closure  |
| Transaction records    | 5 years        | Transaction date |
| SAR records            | 5 years        | SAR filing date  |
| EDD records            | 5 years        | Account closure  |

## GDPR overlap

- KYC processing basis: Legal obligation — Art. 6(1)(c) — not consent
- Right to erasure: overridden by retention obligation for the retention period
- Cross-border screening transfers: require GDPR Art. 46 safeguards

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR CODEBASE EVIDENCE — paste your real content below each heading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

--- MANIFEST ENTRIES ---
[PASTE HERE: open your manifest .json files in Notepad/TextEdit.
 Find the "pxResults" array. Copy any entries (the { } blocks) whose
 "pyRuleName" contains these words — paste as many as you have:
   Risk, Score, Threshold, EDD, PEP, Approval, Flow, SLA, Route,
   Connector, Connect, API, CaseType, CDD, SAR, Periodic, Compliance

 Each entry looks like this — paste the whole block:
 {
   "pyRuleName": "KYC_CalculateRiskScore",
   "pyClassName": "KYC-Work-CDD",
   "pxObjClass": "Rule-Obj-Activity",
   "pyLabel": "Calculate risk score",
   "pyRuleSetName": "COBRules",
   "pyRuleSetVersion": "01-02-01"
 }
]


--- BIN FILE CONTENT ---
[PASTE HERE: open each relevant .bin file in Notepad/TextEdit.
 Copy only the readable English text — ignore all garbled characters.

 For each file, format your paste like this:

 ==== FILE: KYC_CalculateRiskScore.bin ====
 [paste readable text from this file]

 ==== FILE: KYC_RiskThresholdDecision.bin ====
 [paste readable text from this file]

 ==== FILE: KYC_CDDApprovalFlow.bin ====
 [paste readable text from this file]

 ==== FILE: KYC-Conn-SanctionsAPI.bin ====
 [paste readable text from this file — connector files often contain URLs]

 ==== FILE: KYC-SLA-ComplianceReview.bin ====
 [paste readable text from this file — SLA files contain time numbers]

 Paste as many files as you have. More evidence = more accurate output.
]


--- ADDITIONAL CONTEXT (fill in anything you know) ---

Application hierarchy (e.g. COB → CRDFWApp → MSFWApp → PegaRules):
[your answer]

Root CaseType name (pyRuleName of the main KYC case):
[your answer — e.g. KYC-Work-CDD]

Countries / jurisdictions this system covers:
[your answer — e.g. UK, EU, Singapore]

Risk thresholds (if you know them from Compliance docs or screens):
[your answer — e.g. LOW under 35, HIGH over 75]

SLA durations (if you know them):
[your answer — e.g. RM has 48 hours, Compliance has 5 days]

Workbasket names you have seen on screen:
[your answer]

External service vendors you know are used:
[your answer — e.g. World-Check for sanctions, Jumio for identity]

Does a dual approval / maker-checker pattern exist?
[your answer — yes / no / unsure]

Does a SAR case type exist?
[your answer — yes / no / unsure]

Regulatory frameworks explicitly referenced in project docs:
[your answer — e.g. FATF, EU 5th AMLD, MAS Notice 626, FCA SYSC]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT TO PRODUCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Produce all 4 updated skill files in full, one after the other.

For each file:
  - Replace every generic value with the real value from the evidence
  - Mark each value ✓ CONFIRMED, ~ INFERRED, or ⚠ NOT CONFIRMED
  - Add a <!-- Source: filename or field --> comment for confirmed values
  - Keep ⚠ NOT CONFIRMED for any value not evidenced
  - Do not abbreviate — output the complete file every time

After all 4 files, produce a CALIBRATION SUMMARY with:

  Section A — What was confirmed vs generic (counts per file)
  Section B — Cross-checks: does the risk threshold in risk-scoring.md
               match the routing condition in approval-flows.md?
               Does approval-flows reference a service that is in external-services?
               Does regulatory-framework list an obligation with no implementation?
  Section C — Hidden patterns: anything in your codebase that was NOT
               in the generic skill files — extra case types, extra risk factors,
               extra roles, extra services, extra regulatory obligations
  Section D — Top 5 items to verify with your PEGA developer or Compliance team
  Section E — MASTER CONTEXT BLOCK: a compact 35-line summary of all confirmed
               values from all 4 files, ready to paste into any agent system prompt

=== END OF PROMPT ===
