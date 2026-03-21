# Skill: PEGA Class Hierarchy

> Inject this file into agents that need to reason about PEGA's 4-tier class hierarchy and inheritance model.

---

## The 4-tier PEGA class hierarchy

```
TIER 1 — Enterprise (Org-)
    Shared across ALL applications in the organisation
    └──► e.g. Org-KYC, Org-Party, Org-Document

TIER 2 — Division (Div-)
    Shared across applications within a business division
    └──► e.g. Div-RetailBanking, Div-WealthManagement

TIER 3 — Application
    Application-specific rules; inherits from Division and Enterprise
    └──► e.g. KYCOnboarding, AMLScreening, CustomerPortal

TIER 4 — Work type / Module (Work-, Data-)
    Case type-specific rules — the most specific level
    └──► e.g. KYC-Work-CDD, KYC-Work-EDD, KYC-Work-AMLReview
         KYC-Data-Customer, KYC-Data-RiskAssessment, KYC-Data-Document
```

---

## Inheritance rule

PEGA resolves rules by searching from the **most specific class upward** through the hierarchy:

```
Rule lookup order for KYC-Work-CDD:
  1. KYC-Work-CDD           (most specific — checked first)
  2. KYCOnboarding           (application class)
  3. Div-RetailBanking       (division class)
  4. Org-KYC                 (enterprise class)
  5. @baseclass              (PEGA base — last resort)
```

**Consequence**: A rule defined at `KYC-Work-CDD` level overrides the same-named rule at any higher level. This is how division-level customisations override enterprise defaults without modifying the enterprise rule.

---

## Class types in a KYC system

### Work classes (case types)
These hold the process rules: flows, SLAs, routers, UI rules, data transforms.

| Work class | KYC purpose |
|-----------|------------|
| `KYC-Work-CDD` | Standard Customer Due Diligence case |
| `KYC-Work-EDD` | Enhanced Due Diligence case |
| `KYC-Work-AMLReview` | AML alert review / investigation |
| `KYC-Work-SAR` | Suspicious Activity Report case |
| `KYC-Work-DocumentReview` | Document verification sub-case |
| `KYC-Work-PEPReview` | PEP escalation case |
| `KYC-Work-SanctionsReview` | Sanctions hit review case |
| `KYC-Work-UBODisclosure` | Ultimate Beneficial Owner disclosure |
| `KYC-Work-CorporateKYC` | Corporate / legal entity onboarding |
| `KYC-Work-PeriodicReview` | Periodic KYC refresh case |

### Data classes (data models)
These hold property definitions and data page rules — no process logic.

| Data class | Purpose |
|-----------|---------|
| `KYC-Data-Customer` | Customer entity: name, DOB, nationality, tax ID |
| `KYC-Data-Individual` | Natural person detail (extends Customer) |
| `KYC-Data-LegalEntity` | Corporate / trust entity detail |
| `KYC-Data-RiskAssessment` | Risk scoring results and factors |
| `KYC-Data-Document` | KYC document metadata and status |
| `KYC-Data-SanctionsResult` | Sanctions screening response data |
| `KYC-Data-PEPResult` | PEP screening response data |
| `KYC-Data-CreditCheck` | Credit bureau response data |
| `KYC-Data-UBO` | Ultimate Beneficial Owner record |
| `KYC-Data-Address` | Structured address |
| `KYC-Data-ContactDetail` | Email, phone, preferred communication |

### Shared / Org-level classes
| Class | Purpose |
|-------|---------|
| `Org-KYC` | Enterprise-level shared rules and data model |
| `Org-Party` | Party master data (links to CRM) |
| `Org-Document` | Enterprise document management |
| `Org-Notification` | Shared notification framework |

---

## Where to look for rules by tier

| If you need to find... | Look in class... |
|-----------------------|-----------------|
| A flow that is specific to CDD cases | `KYC-Work-CDD` |
| A flow shared across all KYC case types | `KYCOnboarding` (application class) |
| A decision table shared across divisions | `Org-KYC` or `Div-RetailBanking` |
| The customer data model | `KYC-Data-Customer` |
| The risk scoring logic | `KYC-Work-CDD` or `KYCOnboarding` |
| Integration connectors | Typically `KYCOnboarding` or `KYC-Work-CDD` |
| UI sections | `KYC-Work-CDD` (case-specific) or `KYCOnboarding` (shared) |
| SLA rules | `KYC-Work-CDD`, `KYC-Work-EDD` (case-specific) |
| Access groups and roles | Application-level or Org-level |

---

## RuleSet versioning

Rules belong to a **RuleSet** with a version. Format: `RuleSetName:Major-Minor-Patch`

Example: `KYCOnboarding:01-02-03`

- **Major** version: breaking change — new application version
- **Minor** version: feature addition — backward compatible
- **Patch** version: bug fix

Multiple RuleSet versions can coexist. PEGA resolves which version to use based on the **application stack** configured for each environment (Dev, Test, UAT, Prod).

---

## Key PEGA class inheritance gotchas

1. **Blocked rules**: A rule can be `Blocked` at a lower level to prevent it from being overridden by a higher-level rule. If a rule is not behaving as expected, check if it is Blocked.
2. **Final rules**: A `Final` rule cannot be overridden at any lower level. Enterprise-level compliance rules are often marked Final to prevent divisional overrides.
3. **Circumstance-based rules**: Rules can have circumstances (e.g. `CustomerType = Corporate`) that activate a variant of the rule only when the condition is met. Check for circumstanced variants before assuming a rule is the only one with that name.
4. **Template rules**: Some rules exist as templates at the application class level and are intended to be copied and specialised at the work class level — not overridden in place.
