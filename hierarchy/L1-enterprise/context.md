# L1 — Enterprise Hierarchy Context

> Fill in your client's actual values. Delete placeholder rows that do not apply.

## Enterprise class details

| Field | Value |
|-------|-------|
| **Enterprise class name** | `Org-KYC` ← replace with client value |
| **RuleSet name** | `KYCEnterprise` ← replace |
| **RuleSet version** | `01-01-01` ← replace |
| **PEGA version** | `[e.g. Pega Infinity 23.1]` |
| **Architecture type** | `[Constellation / Classic / Mixed]` |

## Enterprise-level rule inventory (fill in)

| Rule type | Rule name | Purpose |
|-----------|-----------|---------|
| Class | `Org-KYC` | Root enterprise class |
| Class | `Org-Party` | Customer/party master data model |
| Class | `Org-Document` | Document management |
| Data Transform | `[name]` | [purpose] |
| Decision Table | `[name]` | [purpose] |
| Correspondence | `[name]` | [purpose] |

## Enterprise-level data model (fill in)

| Property | Class | Type | Description |
|----------|-------|------|-------------|
| `CustomerID` | `Org-Party` | Text | Unique customer identifier |
| `CustomerFullName` | `Org-Party` | Text | |
| `CustomerDOB` | `Org-Party` | Date | |
| `CustomerNationality` | `Org-Party` | Text | ISO 3166-1 alpha-2 |

## Notes for agents

Rules at this level are inherited by ALL applications and divisions. Changes here affect the entire enterprise. Flag any modifications to enterprise-level rules for senior architect review.
