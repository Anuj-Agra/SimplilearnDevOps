# Shared Context: PEGA KYC Integration Map

> Inject into Agent 08 (Integration Mapper) and Agent 06 (PEGA Expert) when discussing the system-level integration architecture.

## Integration topology

```
                        ┌─────────────────────────────┐
                        │     PEGA KYC Platform        │
                        │                              │
  Customer Portal ─────►│  KYC-Work-CDD                │
  (self-service)        │  KYC-Work-EDD                │
                        │  KYC-Work-SAR                │
  Core Banking  ◄──────►│  KYC-Work-PeriodicReview     │
  (CRM)                 │                              │
                        └────────────┬─────────────────┘
                                     │ Outbound calls
                    ┌────────────────┼────────────────────┐
                    │                │                    │
                    ▼                ▼                    ▼
             Sanctions API    Identity Verify       PEP Screening
             (OFAC/UN/EU)     (Jumio / Onfido)     (World-Check)
                    │
                    ▼
             Credit Bureau         OCR / Document        Company Registry
             (Experian/Equifax)    Classification        (OpenCorporates)
```

## Integration inventory (template — fill in with client's actual vendors)

| INT ID | Direction | Service | Vendor | Protocol | Status |
|--------|-----------|---------|--------|----------|--------|
| INT-001 | Outbound | Sanctions screening | [TBC] | REST/JSON | [Prod/UAT/Dev] |
| INT-002 | Outbound | PEP screening | [TBC — often same as INT-001] | REST/JSON | |
| INT-003 | Outbound | Identity verification | [TBC] | REST/JSON | |
| INT-004 | Outbound | Address verification | [TBC] | REST/JSON | |
| INT-005 | Outbound | Document OCR | [TBC] | REST/JSON | |
| INT-006 | Bidirectional | Core banking / CRM | [TBC] | [TBC] | |
| INT-007 | Outbound | Company registry | [TBC] | REST/JSON | |
| INT-008 | Outbound | Credit bureau | [TBC] | REST/JSON | |
| INT-009 | Outbound | SAR / FIU reporting | [Regulator portal] | File/Web | |

Update this file with the client's actual vendors, endpoints, and statuses once known. All agents referencing integrations will use this map as context.
