# Flow Narrative: KYC_CDDOnboarding

**PEGA Class:** KYC-Work-CDD
**Hierarchy Level:** L4 — Module / Work Type
**Prepared for:** Business Analyst
**Source:** Flow rule JSON export

---

## 1. Purpose

This flow manages the end-to-end process of onboarding a new individual customer through the standard Customer Due Diligence (CDD) process. It collects the customer's identity information, screens them against global sanctions and PEP lists, scores their risk profile, and routes the case to the appropriate approval path based on that risk rating. It directly fulfils the firm's obligations under FATF Recommendation 10 (Customer Due Diligence).

---

## 2. Trigger & Entry Conditions

- **Triggered by:** A KYC Operator initiating a new CDD case from the KYC Operator Portal, or an inbound API call from the Customer Portal when a customer submits a self-service onboarding request.
- **Entry data required:** Customer's full name, date of birth, nationality. Tax ID is required for applicable jurisdictions.
- **Preconditions:** The initiating user must hold the `KYC-Operator` access group. The customer must not have an active CDD case already open in the system.

---

## 3. Actors & Roles

| Actor | Type | Responsibility in this flow |
|-------|------|-----------------------------|
| KYC Operator | Human | Initiates case; collects customer details; uploads documents |
| Relationship Manager | Human | Reviews and decides on MEDIUM risk cases |
| Compliance Officer | Human | Reviews and decides on HIGH risk and PEP cases |
| Sanctions Screening API | External system | Screens customer against OFAC, UN, EU, and HMT sanctions lists; identifies PEP status |
| KYC Platform (PEGA) | System | Calculates risk score; routes case; enforces SLAs; logs audit trail |

---

## 4. Step-by-Step Narrative

**Step 1 — Collect Customer Details**
A KYC Operator receives the case in the `KYC-Initiation-WB` workbasket. They open the CDD Initiation screen and enter the customer's full name, date of birth, nationality, and tax identification number. The system validates that all mandatory fields are complete and correctly formatted. A 4-hour SLA applies to this step. If not actioned within the SLA, the case escalates to the KYC Team Lead.

**Step 2 — Upload Identity Documents**
The operator uploads the customer's government-issued photo ID (passport or national ID card) and proof of address (utility bill or bank statement issued within the last 3 months). The system records the document type, upload timestamp, and uploading operator in the audit trail. A document submission SLA applies.

**Step 3 — Sanctions & PEP Screening**
The system automatically calls the ACME Sanctions Screening API (a REST/JSON service). It submits the customer's full name, date of birth, and nationality. The API screens against the OFAC SDN list, UN Consolidated list, EU Consolidated list, and HM Treasury list. It also checks whether the customer is a Politically Exposed Person (PEP). The call must return within 5 seconds. All request and response details are logged in the audit trail.

**Step 4 — Interpret Screening Result**
The system maps the API response to the case record. It sets the `SanctionsHitFlag` (confirmed hit: yes/no), `SanctionsMatchScore` (0–100), and `PEPFlag` (yes/no). If a confirmed sanctions hit is returned (hit flag = true), the case is immediately routed to the Sanctions Review team — the flow does not continue to risk scoring.

**Step 5 — Calculate Risk Score**
For cases with no confirmed sanctions hit, the system runs the risk scoring Data Transform. This calculates a composite `OverallRiskScore` based on: country risk (40% weight), customer type risk (30%), PEP status (20%), and product/channel risk (10%). The score is used to determine the risk rating.

**Step 6 — Route by Risk Rating**
The system applies the risk threshold Decision Table to translate the numeric score into a risk rating (LOW, MEDIUM, or HIGH) and routes the case accordingly:

| Rating | Score range | Routing |
|--------|------------|---------|
| LOW | 0–39 | Auto-approve (if no PEP flag, no near-hit) |
| MEDIUM | 40–69 | Assigned to Relationship Manager |
| HIGH | 70–100 | Assigned to Compliance Officer |

> Note: A PEP flag overrides the risk score — any customer identified as a PEP is routed to Compliance regardless of their score.

**Step 7a — Auto-Approve (LOW risk)**
Where the risk rating is LOW and the PEP flag is false and document verification is complete, the system automatically approves the case without human intervention. The case status is set to `Resolved-Approved`. An audit log entry records the auto-approval decision, timestamp, and risk score.

**Step 7b — Relationship Manager Review (MEDIUM risk)**
The case is assigned to the customer's Relationship Manager via the `KYC-RMReview-WB` workbasket. A 48-hour business SLA applies. The RM can: Approve (case moves to `Resolved-Approved`), Reject (case moves to `Resolved-Rejected`), or Escalate to Compliance (case routes to Compliance review). If the 48-hour SLA is breached, the case auto-escalates to the Compliance team workbasket.

**Step 7c — Compliance Review (HIGH risk / PEP / RM escalation)**
The case is assigned to a Compliance Officer via the `KYC-Compliance-WB` workbasket. A 5-business-day SLA applies. The Compliance Officer can: Approve, Reject, or determine that Enhanced Due Diligence (EDD) is required. If EDD is required, the system spawns an EDD sub-case (`KYC-Work-EDD`) and links it to this CDD case. The CDD case waits for EDD completion before resolving.

---

## 5. Decision Points & Branching Logic

| Decision point | Condition | Branch A | Branch B |
|---------------|-----------|----------|----------|
| Sanctions hit check | `SanctionsHitFlag == true` | Route to Sanctions Review | Continue to risk scoring |
| Risk rating routing | `RiskRating == "HIGH"` | Compliance review | → next row |
| Risk rating routing | `RiskRating == "MEDIUM"` | RM review | → next row |
| Risk rating routing | `RiskRating == "LOW"` and no PEP | Auto-approve | — |
| PEP override | `PEPFlag == true` | Force Compliance review (overrides LOW/MEDIUM routing) | — |
| EDD required | `EDDRequired == true` | Spawn EDD sub-case | Approve directly |
| RM decision | `ApprovalDecision == "Escalate"` | Route to Compliance | — |

---

## 6. External Service Interactions

| Service | Protocol | Data sent | Data returned | Error handling |
|---------|----------|-----------|---------------|----------------|
| ACME Sanctions Screening API | REST/JSON | CustomerFirstName, CustomerLastName, CustomerDOB, CustomerNationality, pzInsKey | SanctionsHitFlag, SanctionsMatchScore, PEPFlag, HitDetails[] | Timeout (> 5s) → route to Manual Screening workbasket; HTTP 500 → retry ×3, then manual queue |

---

## 7. Data Created or Modified (CRUD)

| Property / Page | Operation | Set when |
|----------------|-----------|----------|
| `CustomerFirstName`, `CustomerLastName`, `CustomerDOB`, `CustomerNationality` | Write | Step 1 — operator entry |
| `DocumentType`, `DocumentUploadTimestamp` | Write | Step 2 — document upload |
| `SanctionsHitFlag`, `SanctionsMatchScore`, `PEPFlag`, `SanctionsHitDetails` | Write | Step 4 — API response parsed |
| `CountryRiskScore`, `CustomerTypeScore`, `OverallRiskScore` | Write | Step 5 — risk scoring |
| `RiskRating` | Write | Step 6 — threshold applied |
| `ApprovalDecision`, `ApprovalRationale`, `ApprovedByOperatorID` | Write | Step 7 — human decision |
| `pyStatusWork` | Write | Multiple transitions |

---

## 8. Completion & Exit Conditions

- **Approved:** Case status = `Resolved-Approved`. Triggered by auto-approval, RM approval, or Compliance approval.
- **Rejected:** Case status = `Resolved-Rejected`. Triggered by RM or Compliance rejection.
- **EDD spawned:** Case status = `Open-EDDRequired`. CDD case remains open pending EDD sub-case completion.
- **Sanctions review:** Case status = `Open-SanctionsReview`. Flow paused pending Sanctions team decision.

---

## 9. Compliance & Audit Notes

This flow directly implements: FATF Recommendation 10 (CDD), FATF Recommendation 12 (PEP identification and EDD), EU AMLD 5 Art. 13 (EDD for high-risk third countries).

Every step transition, decision outcome, external service call, and document upload is recorded in PEGA's case audit trail with timestamp, operator ID, and before/after values. Audit records are retained for 5 years from case closure per FATF Recommendation 11.
