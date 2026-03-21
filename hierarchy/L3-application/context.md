# L3 — Application Hierarchy Context

> Fill in your client's actual values. Delete placeholder rows that do not apply.

## Application details

| Field | Value |
|-------|-------|
| **Application name** | `KYCOnboarding` ← replace with client value |
| **Application class** | `KYCOnboarding` ← replace |
| **Parent class** | `Div-RetailBanking` ← replace |
| **RuleSet name** | `KYCOnboarding` ← replace |
| **RuleSet version** | `01-02-03` ← replace |
| **PEGA version** | `[e.g. Pega Infinity 23.1]` |
| **UI framework** | `[Constellation / Classic]` |
| **Environment URLs** | DEV: `[url]` / UAT: `[url]` / PROD: `[url]` |

## Application-level flows (fill in)

These are flows shared across multiple work types within this application.

| Flow name | Class | Purpose | Sub-flows called |
|-----------|-------|---------|-----------------|
| `KYC_CommonDocumentVerification` | `KYCOnboarding` | Shared document check sub-flow | — |
| `KYC_SanctionsScreening` | `KYCOnboarding` | Shared sanctions check sub-flow | — |
| `KYC_PEPScreening` | `KYCOnboarding` | Shared PEP check sub-flow | — |
| `KYC_RiskScoring` | `KYCOnboarding` | Shared risk score sub-flow | — |
| `[add your flows]` | | | |

## Application-level connectors (fill in)

| Connector name | Class | External service | Protocol | Auth method |
|---------------|-------|-----------------|----------|------------|
| `KYC-Conn-SanctionsAPI` | `KYCOnboarding` | [Vendor name] | REST/JSON | OAuth 2.0 |
| `KYC-Conn-PEPCheck` | `KYCOnboarding` | [Vendor name] | REST/JSON | API Key |
| `KYC-Conn-IdentityVerify` | `KYCOnboarding` | [Vendor name] | REST/JSON | OAuth 2.0 |
| `KYC-Conn-CRMSystem` | `KYCOnboarding` | [CRM name] | REST/JSON | mTLS |
| `[add your connectors]` | | | | |

## Application-level data pages (fill in)

| Data Page name | Class | Source | Cached at | Refresh interval |
|----------------|-------|--------|-----------|-----------------|
| `D_CountryRiskList` | `KYCOnboarding` | Decision Table | Node | Daily |
| `D_DocumentTypeList` | `KYCOnboarding` | Report Definition | Thread | Session |
| `D_SanctionsListMeta` | `KYCOnboarding` | Connector | Node | Hourly |
| `[add your data pages]` | | | | |

## Application-level decision tables (fill in)

| Decision Table name | Class | Input | Output | Used in |
|--------------------|-------|-------|--------|---------|
| `KYC_CountryRiskTable` | `KYCOnboarding` | CustomerNationality | CountryRiskScore | Risk scoring flow |
| `KYC_RiskThresholdTable` | `KYCOnboarding` | OverallRiskScore | RiskRating (LOW/MED/HIGH) | Risk scoring flow |
| `KYC_DocumentAcceptanceTable` | `KYCOnboarding` | DocumentType + CustomerType | Accepted (Y/N) | Document verification |
| `[add your decision tables]` | | | | |

## Application-level UI rules (fill in)

| Rule name | Type | Class | Purpose |
|-----------|------|-------|---------|
| `KYCWork_Edit` | Harness | `KYCOnboarding` | Main case workspace (edit mode) |
| `KYCWork_Review` | Harness | `KYCOnboarding` | Main case workspace (review mode) |
| `KYCPortal` | Portal | `KYCOnboarding` | KYC Operator portal shell |
| `[add your UI rules]` | | | |

## Access groups defined at application level (fill in)

| Access Group | Role | Workbasket access | Privileges |
|-------------|------|------------------|-----------|
| `KYC-Operator` | KYC Operations | `KYC-Initiation-WB`, `KYC-DocReview-WB` | CreateCDDCase, SubmitDocReview |
| `KYC-RM` | Relationship Manager | `KYC-RMReview-WB` | ReviewCase, ApproveCase, EscalateCase |
| `KYC-Compliance` | Compliance Officer | `KYC-Compliance-WB`, `KYC-Sanctions-WB` | ApproveEDD, RejectCase, FlagSAR |
| `KYC-MLRO` | MLRO | `KYC-MLRO-WB` | ApproveSAR, BlockAccount |
| `[add your access groups]` | | | |

## Notes for agents

Application-level rules are shared across all case types (work types) in this application. They represent reusable, cross-case logic and should be referenced when a rule is not found at the work-type level.
