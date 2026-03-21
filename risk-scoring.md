# Skill: KYC Risk Scoring

> Inject this file into agents that need to explain, document, or generate acceptance criteria for risk scoring logic.

---

## Standard KYC risk scoring model

### Composite risk score formula (typical)

```
OverallRiskScore = (CountryRisk × W1) + (CustomerTypeRisk × W2) + (PEPRisk × W3) + (ProductRisk × W4)

Typical weights:
  W1 (Country)       = 0.40
  W2 (Customer type) = 0.30
  W3 (PEP status)    = 0.20
  W4 (Product/channel) = 0.10
```

### Risk rating thresholds (confirm with client Compliance team)

| Score range | Risk rating | Routing |
|------------|------------|---------|
| 0 – 39 | LOW | Auto-approve (if no hits, no PEP, docs verified) |
| 40 – 69 | MEDIUM | Relationship Manager review |
| 70 – 100 | HIGH | Compliance Officer review + EDD mandatory |

---

## Risk factor reference tables

### Country risk scoring

| Country risk category | Score | Examples |
|----------------------|-------|---------|
| FATF member — low risk | 10–20 | US, UK, Germany, France, Australia, Canada, Japan |
| FATF member — standard | 25–40 | Brazil, South Africa, India, Mexico |
| FATF grey list (Increased Monitoring) | 60–75 | [Current FATF grey list — updated periodically] |
| FATF black list (Call for Action) | 90–100 | Currently: Iran, North Korea, Myanmar |
| EU high-risk third country (5th AMLD) | 80–90 | [Per EC delegated regulation — updated periodically] |
| Domestic high-risk jurisdiction | 70–85 | Per client's internal country risk policy |
| Offshore / secrecy jurisdiction | 50–70 | Cayman Islands, BVI, etc. (context-dependent) |

**Important**: Country risk lists are updated regularly. The PEGA Decision Table `KYC_CountryRiskTable` must be updated whenever FATF or the EC publishes updates. Build a scheduled review process into the renovation plan.

### Customer type risk scoring

| Customer type | Score | Notes |
|-------------|-------|-------|
| Individual — standard | 20 | Employed, verified identity |
| Individual — self-employed | 35 | Higher source-of-funds risk |
| Individual — high net worth | 40 | Complex wealth structures |
| Corporate — private company | 35 | UBO identification required |
| Corporate — listed company | 15 | Regulated; UBO via exchange records |
| Trust | 60 | Complex beneficial ownership |
| Foundation / NGO | 65 | Potential sanctions risk |
| Shell company / SPV | 80 | High opacity — enhanced scrutiny |
| Charity | 55 | Potential terrorist financing risk |
| Sole trader | 30 | |
| Partnership | 45 | UBO identification required |

### PEP risk scoring

| PEP status | Score | Handling |
|-----------|-------|---------|
| No PEP connection | 0 | No special handling |
| Close associate of PEP | 40 | Enhanced scrutiny; document relationship |
| Family member of PEP | 50 | Enhanced scrutiny; EDD recommended |
| Domestic PEP (current) | 80 | EDD mandatory; senior approval required |
| Foreign PEP (current) | 90 | EDD mandatory; senior approval required |
| Former PEP (< 12 months) | 70 | EDD mandatory; review at 12 months |
| Former PEP (12–24 months) | 40 | Enhanced scrutiny; document risk assessment |
| Former PEP (> 24 months) | 10 | Risk-based assessment |

### Product / channel risk scoring

| Product / channel | Score | Notes |
|------------------|-------|-------|
| Standard deposit account (branch) | 10 | Face-to-face; lower risk |
| Standard deposit account (online) | 20 | Non-face-to-face; slightly higher |
| Corporate current account | 30 | Business purpose monitoring |
| Trade finance | 50 | Complex, multi-party, documentation risk |
| Wealth / investment product | 40 | Source of funds scrutiny |
| Cryptocurrency exchange | 70 | High ML/TF risk (5th AMLD scope) |
| Correspondent banking | 80 | Rec 13 obligations |
| Private banking | 50 | HNW clients; complex structures |

---

## EDD mandatory triggers (non-score-based)

The following conditions trigger EDD **regardless of the composite score**. They cannot be overridden by a LOW score:

1. `PEPFlag = true` (any PEP status)
2. `CustomerNationality` or `CustomerCountryOfResidence` is on FATF Call for Action list
3. `CustomerNationality` or `CustomerCountryOfResidence` is on EU high-risk third country list
4. `CustomerType` = Trust, Foundation, Shell Company, or SPV
5. `UBOIdentified = false` (UBO not yet identified for a legal entity)
6. `SanctionsNearHit = true` (match score above near-hit threshold but below confirmed hit)
7. Correspondent banking relationship
8. Compliance officer manual EDD flag

---

## Auto-approval conditions

A case can be auto-approved (no human review) ONLY when ALL of the following are true:

- `OverallRiskScore` < LOW threshold (e.g. < 40)
- `PEPFlag = false`
- `SanctionsHitFlag = false`
- `SanctionsNearHitFlag = false`
- `DocumentVerificationStatus = "Verified"`
- `UBOIdentified = true` (for legal entities)
- `CountryRisk` < HIGH threshold (not on grey or black list)
- No override flag set by a Compliance officer
- Customer type is not on the mandatory-EDD list

---

## Periodic review schedule

| Risk rating | Review frequency | Trigger |
|------------|----------------|--------|
| LOW | Every 5 years | Scheduled; ad-hoc on trigger event |
| MEDIUM | Every 3 years | Scheduled; ad-hoc on trigger event |
| HIGH | Annually | Scheduled; ad-hoc on trigger event |
| PEP | Annually (minimum) | Scheduled; ad-hoc on status change |
| EDD | Annually | Scheduled; ad-hoc on trigger event |

Ad-hoc review triggers:
- Change of country of residence or nationality
- Sanctions list update that produces a new hit
- PEP status change
- Suspicious transaction alert
- Material change to UBO structure
- Internal compliance flag
