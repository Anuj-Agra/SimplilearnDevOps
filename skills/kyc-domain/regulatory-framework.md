# Skill: KYC Regulatory Framework

> Inject this file into agents that need to reference regulatory obligations, map requirements to process steps, or flag compliance gaps.

---

## Core regulatory frameworks

### FATF Recommendations (global standard)

| Rec | Topic | KYC obligation |
|-----|-------|---------------|
| Rec 10 | Customer due diligence | Identify and verify customer identity before/during account opening. Verify beneficial owners. Understand the nature and purpose of the business relationship. Conduct ongoing monitoring. |
| Rec 11 | Record keeping | Retain transaction records and CDD data for at least 5 years. Must be retrievable for competent authorities. |
| Rec 12 | PEPs | Apply enhanced CDD to domestic and foreign PEPs. Obtain senior management approval. Determine source of wealth and funds. Conduct enhanced ongoing monitoring. |
| Rec 13 | Correspondent banking | Conduct enhanced due diligence for correspondent banking relationships. Obtain senior management approval. Assess AML/CFT controls of correspondent. Do not open accounts for shell banks. |
| Rec 15 | New technologies | Assess ML/TF risks of new products, business practices, and technologies before launch. |
| Rec 16 | Wire transfers | Include originator and beneficiary information in wire transfers. Screen against sanctions lists. |
| Rec 17 | Reliance on third parties | Due diligence can be performed by a third party but responsibility remains with the regulated entity. |
| Rec 18 | Internal controls | Implement AML/CFT programmes including CDD policies, independent audit, employee training. |
| Rec 19 | Higher-risk countries | Apply enhanced due diligence for business relationships and transactions from FATF-identified high-risk countries. |
| Rec 20 | Reporting of suspicious transactions | Report suspicious transactions to the FIU. File Suspicious Activity Reports (SARs). |
| Rec 21 | Tipping off | Prohibited from disclosing that a SAR has been filed or that an investigation is underway. |
| Rec 22 | DNFBPs | CDD obligations apply to designated non-financial businesses and professions. |

---

### EU Anti-Money Laundering Directives

| Directive | Key obligations |
|----------|----------------|
| **4th AMLD (2015)** | Risk-based approach mandatory; UBO registers; enhanced CDD for PEPs and high-risk countries; 5-year retention |
| **5th AMLD (2018)** | Public UBO registers; crypto-asset providers included; enhanced due diligence for high-risk third countries; lower thresholds for prepaid cards |
| **6th AMLD (2018)** | Criminal liability harmonised across EU; 22 predicate offences defined; tougher penalties; aiding and abetting AML is an offence |

---

### Key regulatory requirements by KYC process area

#### Customer identification (CDD)
- Obtain: full name, date of birth, nationality, address, tax ID / national ID number
- Verify via: government-issued photo ID (passport, national ID card, driving licence)
- Verify address via: utility bill, bank statement (issued within 3 months)
- For legal entities: company registration, articles of incorporation, UBO information, authorised signatory identification
- Cannot open account / activate service until identification AND verification is complete

#### Enhanced Due Diligence (EDD) triggers
Mandatory EDD (not discretionary) when any of the following apply:
- Customer is a PEP (domestic or foreign)
- Customer's country of residence or nationality is on FATF grey/black list
- Customer is from an EU-designated high-risk third country (per 5th AMLD)
- Transaction patterns inconsistent with the stated business purpose
- Source of funds / source of wealth is unclear
- Correspondent banking relationship
- Non-face-to-face customer onboarding (some jurisdictions)
- Complex, unusually large, or unusual transaction patterns (Rec 20)

#### EDD additional requirements
- Obtain senior management approval (Director-level minimum)
- Document the source of wealth and source of funds
- Conduct enhanced ongoing monitoring
- Increase frequency of periodic review

#### Beneficial ownership (UBO)
- Identify all individuals owning > 25% of a legal entity (some jurisdictions: 10%)
- If no individual owns > threshold, identify the senior managing official
- Record UBO information in PEGA case
- Verify UBO identity (same standards as individual CDD)
- Flag UBOs who are PEPs

#### Sanctions screening
- Screen against: OFAC SDN list, UN Consolidated list, EU Consolidated list, HM Treasury (UK), domestic lists
- Screen: customer, beneficial owners, directors, authorised signatories, counterparties
- Screen at: onboarding AND on an ongoing basis AND on trigger events
- On hit: do not proceed without Compliance review; file SAR if required
- Match score threshold must be defined and agreed with Compliance

#### PEP screening
- Screen at: onboarding, periodic review, trigger events
- PEP categories: current or former heads of state, senior politicians, senior government officials, judicial officials, senior military officials, senior executives of state-owned enterprises, senior officials of international organisations
- Close associates and family members of PEPs are also treated as PEPs
- PEP status does not automatically prevent onboarding — requires EDD and senior approval

#### Ongoing monitoring
- Review KYC data on a risk-based periodic schedule:
  - HIGH risk: annual review
  - MEDIUM risk: every 2–3 years
  - LOW risk: every 5 years
- Trigger ad-hoc review on: change of circumstances, suspicious activity, sanctions alert, PEP identification
- Monitor transactions for patterns inconsistent with the customer's profile

#### Suspicious Activity Reporting (SAR / STR)
- File a SAR with the Financial Intelligence Unit (FIU) when there is knowledge or reasonable grounds to suspect money laundering or terrorist financing
- Do NOT alert the customer that a SAR has been filed (tipping off offence)
- PEGA SAR case must: capture the suspicion, document evidence, route for authorised approval, submit via regulatory channel
- Retain SAR and supporting documentation for minimum 5 years

---

## Data retention requirements

| Data type | Minimum retention | Regulatory basis | Clock starts |
|-----------|-----------------|-----------------|-------------|
| CDD records (identity + verification) | 5 years | FATF Rec 11, AMLD Art. 40 | Account closure |
| Transaction records | 5 years | FATF Rec 11 | Transaction date |
| KYC case documentation | 5 years | FATF Rec 11 | Case closure |
| SAR records | 5 years | FATF Rec 11 | SAR filing date |
| EDD records | 5 years (some jurisdictions: 7 years) | FATF Rec 11 | Account closure |

---

## GDPR overlap with KYC (EU)

| Tension | Resolution |
|---------|-----------|
| GDPR right to erasure vs KYC retention obligation | KYC retention obligation (legal obligation) overrides erasure right for the retention period |
| GDPR data minimisation vs KYC thoroughness | Collect only data necessary for the KYC obligation — no gold-plating |
| GDPR consent vs KYC obligation | KYC processing is based on legal obligation (Art. 6(1)(c)), not consent — consent not required |
| GDPR data subject access request | KYC data must be producible but SAR-related data may be exempt (law enforcement exemption) |
| Cross-border data transfer for screening | Sanctions screening providers outside EEA require Art. 46 safeguards (SCCs, adequacy decision) |
