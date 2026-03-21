# L4 — Module / Work Type Hierarchy Context

> Fill in your client's actual values. This is the most specific tier — rules here apply only to the named work type.

## Work types in scope (fill in one block per work type)

---

### Work Type: KYC-Work-CDD (Standard Customer Due Diligence)

| Field | Value |
|-------|-------|
| **Work type class** | `KYC-Work-CDD` ← replace |
| **Parent class** | `KYCOnboarding` |
| **RuleSet** | `KYCOnboarding:01-02-03` ← replace |
| **Case stages** | `Initiation → Document Verification → Risk Assessment → Approval → Complete` ← replace |
| **SLA** | `KYC-SLA-CDDReview` ← replace |

#### CDD-specific flows

| Flow name | Purpose | Key steps |
|-----------|---------|-----------|
| `KYC_CDDOnboarding` | Main CDD process flow | CollectDetails → SanctionsCheck → RiskScore → Route |
| `KYC_CDDDocumentVerification` | Document review sub-flow | ReceiveDocs → ReviewDocs → Approve/Reject |
| `KYC_CDDApproval` | Approval routing flow | RM review → Compliance review → Decision |
| `[add your flows]` | | |

#### CDD-specific data transforms

| Data Transform | Purpose |
|---------------|---------|
| `KYC_InitialiseCDDCase` | Sets default values on case creation |
| `KYC_MapSanctionsResponse` | Maps sanctions API response to case properties |
| `KYC_CalculateCDDRiskScore` | Computes composite risk score |
| `[add your data transforms]` | |

#### CDD-specific UI rules

| Rule name | Type | Purpose | Screen in flow |
|-----------|------|---------|---------------|
| `CDDInitiation` | Section | Capture customer details | Step 1 |
| `CDDDocumentUpload` | Section | Upload identity documents | Step 2 |
| `CDDRiskReview` | Section | RM risk review panel | Step 3 |
| `CDDComplianceApproval` | Section | Compliance decision screen | Step 4 |
| `[add your UI rules]` | | | |

#### CDD case statuses

| Status | Meaning |
|--------|---------|
| `Open-CDDInitiation` | Case created, awaiting customer details |
| `Open-DocumentReview` | Documents uploaded, awaiting review |
| `Open-RiskAssessment` | Risk scoring in progress |
| `Open-RMReview` | Assigned to Relationship Manager |
| `Open-ComplianceReview` | Assigned to Compliance Officer |
| `Open-EDDRequired` | EDD sub-flow triggered |
| `Open-SanctionsReview` | Sanctions hit under review |
| `Open-ManualScreening` | Automated screening failed; manual review |
| `Resolved-Approved` | Case approved |
| `Resolved-Rejected` | Case rejected |
| `Resolved-Withdrawn` | Customer withdrew application |

---

### Work Type: KYC-Work-EDD (Enhanced Due Diligence)

| Field | Value |
|-------|-------|
| **Work type class** | `KYC-Work-EDD` ← replace |
| **Parent class** | `KYCOnboarding` |
| **Trigger** | Spawned as a sub-case from `KYC-Work-CDD` when EDD conditions are met |
| **SLA** | `KYC-SLA-EDDCompletion` (10 business days) ← replace |

#### EDD-specific flows

| Flow name | Purpose |
|-----------|---------|
| `KYC_EDDProcess` | Main EDD flow |
| `KYC_EDDSourceOfWealth` | Source of wealth collection sub-flow |
| `KYC_EDDSeniorApproval` | Senior management approval sub-flow |
| `[add your flows]` | |

---

### Work Type: KYC-Work-SAR (Suspicious Activity Report)

| Field | Value |
|-------|-------|
| **Work type class** | `KYC-Work-SAR` ← replace |
| **Trigger** | Manual flag by Compliance Officer or MLRO |
| **SLA** | `KYC-SLA-SARFiling` (5 business days) ← replace |

---

### Work Type: KYC-Work-PeriodicReview

| Field | Value |
|-------|-------|
| **Work type class** | `KYC-Work-PeriodicReview` ← replace |
| **Trigger** | Scheduled — created automatically based on last review date + risk rating |
| **SLA** | Varies by risk rating ← replace |

---

## Module-level property reference (fill in for each work type)

| Property | Work type class | Type | Description |
|----------|----------------|------|-------------|
| `RiskRating` | `KYC-Work-CDD` | Text | LOW / MEDIUM / HIGH |
| `OverallRiskScore` | `KYC-Work-CDD` | Decimal | Composite score 0–100 |
| `CountryRiskScore` | `KYC-Work-CDD` | Decimal | Country risk factor |
| `PEPFlag` | `KYC-Work-CDD` | Boolean | True if customer is PEP |
| `SanctionsHitFlag` | `KYC-Work-CDD` | Boolean | True if confirmed sanctions hit |
| `SanctionsMatchScore` | `KYC-Work-CDD` | Decimal | Match score from sanctions API |
| `DocumentVerificationStatus` | `KYC-Work-CDD` | Text | Pending / Verified / Rejected |
| `EDDRequired` | `KYC-Work-CDD` | Boolean | True if EDD is mandatory |
| `EDDCaseID` | `KYC-Work-CDD` | Text | ID of spawned EDD sub-case |
| `ApprovalDecision` | `KYC-Work-CDD` | Text | Approved / Rejected / EDD-Required |
| `ApprovalRationale` | `KYC-Work-CDD` | Text | Free text decision rationale |
| `NextReviewDate` | `KYC-Work-CDD` | Date | Calculated from risk rating |
| `[add your properties]` | | | |

## Notes for agents

Work-type level rules are the most specific. They only apply to the named case type. When a rule is not found here, PEGA inherits from the application class (L3), then division (L2), then enterprise (L1). Always specify the work type class when naming rules in outputs.
