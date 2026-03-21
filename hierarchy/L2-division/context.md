# L2 — Division Hierarchy Context

> Fill in your client's actual values. Delete placeholder rows that do not apply.

## Division class details

| Field | Value |
|-------|-------|
| **Division class name** | `Div-RetailBanking` ← replace with client value |
| **Parent class** | `Org-KYC` |
| **RuleSet name** | `KYCRetailBanking` ← replace |
| **RuleSet version** | `01-01-01` ← replace |
| **Business division** | `[e.g. Retail Banking / Wealth Management / Corporate Banking]` |

## Division-level rule overrides (fill in)

Rules at this level override the enterprise-level rule of the same name for this division only.

| Rule type | Rule name | Overrides | Reason for override |
|-----------|-----------|-----------|-------------------|
| Decision Table | `[name]` | `[enterprise rule name]` | [e.g. Different risk thresholds for retail vs corporate] |
| Correspondence | `[name]` | `[enterprise rule name]` | [e.g. Division-specific branding] |

## Division-level policy rules (fill in)

| Rule | Value | Regulatory basis |
|------|-------|----------------|
| Risk score — LOW threshold | `[e.g. 39]` | Internal policy |
| Risk score — HIGH threshold | `[e.g. 70]` | Internal policy |
| Auto-approve enabled? | `[Yes / No]` | Internal policy + regulatory |
| EDD approval level | `[e.g. Head of Compliance]` | Internal policy |

## Notes for agents

Division-level rules apply to all applications within this division. They override enterprise defaults but are themselves overridden by application-level rules.
