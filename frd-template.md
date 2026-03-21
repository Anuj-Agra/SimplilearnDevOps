# Skill: FRD Template Reference

> Inject into Agent 03 (FRD Writer).

## FR numbering convention

FR-001 sequential. Group by area:
- FR-001–019: Customer identification and CDD
- FR-020–039: Risk scoring
- FR-040–059: Approval and routing
- FR-060–079: External integrations
- FR-080–099: UI and screens
- FR-100–119: Reporting and audit

## FRD section checklist

- [ ] 1. Introduction (1.1 Purpose, 1.2 Audience, 1.3 Related docs, 1.4 PEGA hierarchy scope table)
- [ ] 2. System Overview
- [ ] 3. Functional Requirements (FR-001... grouped, each as a full detail block)
- [ ] 4. Data Requirements (4.1 entities + properties, 4.2 validation rules, 4.3 retention)
- [ ] 5. Integration Requirements (INT-001... full detail per integration)
- [ ] 6. UI/UX Requirements (screen inventory + per-screen field table)
- [ ] 7. Business Logic & Calculation Rules
- [ ] 8. SLA & Performance Requirements
- [ ] 9. Security & Access Control
- [ ] 10. Reporting & Audit Requirements
- [ ] 11. Non-Functional Requirements
- [ ] 12. Traceability Matrix (FR ↔ BR ↔ REG ↔ INT ↔ UI ↔ Test)
- [ ] 13. Open Items & Decisions Required

## MoSCoW guide for KYC

| Priority | KYC examples |
|----------|-------------|
| Must Have | Sanctions screening, CDD data capture, audit trail, SLA enforcement |
| Should Have | Risk dashboard, email notifications, document expiry alerts |
| Could Have | PDF report export, custom branding |
| Won't Have | Mobile app, offline mode (this release) |
