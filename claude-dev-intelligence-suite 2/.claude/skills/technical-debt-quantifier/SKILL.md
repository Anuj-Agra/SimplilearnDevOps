---
name: technical-debt-quantifier
description: >
  Produce a board-level technical debt register with financial cost estimates,
  compound interest modelling, and a ROI-ordered payback roadmap. Use when asked:
  'technical debt', 'debt register', 'cost of debt', 'debt report', 'how much
  debt do we have', 'debt quantification', 'debt interest', 'cost of not fixing',
  'debt payback plan', 'debt vs value'. Feeds directly into executive reporting
  and sprint planning. Works with code-smell-detector and gap-detector output.
---
# Technical Debt Quantifier

Turn code quality findings into a financial model that executives and PMs can act on.

---

## Input Sources

Consume output from (run these first if available):
1. `code-smell-detector` findings + scores
2. `gap-detector` findings
3. `security-audit` findings
4. `dependency-risk-tracker` findings
5. Direct codebase scan (if no prior analysis exists)

---

## Step 1 — Classify Debt by Type

| Debt type | Definition | Interest rate |
|---|---|---|
| **Code debt** | Smells, complexity, duplication | 2% / month (slows every feature) |
| **Test debt** | Missing tests, low coverage | 3% / month (bugs cost more to fix) |
| **Architecture debt** | Wrong patterns, wrong boundaries | 4% / month (exponentially harder to change) |
| **Security debt** | Vulnerabilities, misconfigs | 5% / month (risk of incident grows) |
| **Dependency debt** | Outdated/vulnerable libraries | 3% / month |
| **Documentation debt** | Missing FRD, ADRs, runbooks | 1% / month |
| **Infrastructure debt** | Manual processes, no CI/CD gates | 2% / month |

*Interest = cost increases by this % each month if not fixed*

---

## Step 2 — Estimate Fix Cost Per Item

Use these industry benchmarks (adjust to your team's day rate):

| Smell / Finding | Fix effort |
|---|---|
| Extract method (long method) | 2–4 hours |
| Split God class | 2–5 days |
| Reduce cyclomatic complexity | 4–8 hours |
| Add missing unit tests (per class) | 4–8 hours |
| Fix circular dependency | 1–3 days |
| Upgrade one major library version | 1–2 days |
| Add missing @Transactional boundary | 1–2 hours |
| Implement circuit breaker | 4–8 hours |
| Add structured logging | 2–4 hours |
| Document one module (FRD section) | 4–8 hours |

---

## Step 3 — Compound Interest Model

For each debt item:
```
monthlyInterestRate = debtType.interestRate / 100
currentCost        = fixCostNow
costIn6Months      = fixCostNow × (1 + monthlyInterestRate)^6
costIn12Months     = fixCostNow × (1 + monthlyInterestRate)^12
interestAccrued6m  = costIn6Months - fixCostNow
interestAccrued12m = costIn12Months - fixCostNow
```

---

## Step 4 — Output: Executive Debt Register

```
TECHNICAL DEBT REGISTER: [System Name]
Report date: [date] | Team day rate: £[N] | Review cycle: Quarterly

═══════════════════════════════════════════════════════════════
EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════
Total debt (fix today):        £[N]
Cost if fixed in 6 months:     £[N]  (+[N]% interest)
Cost if fixed in 12 months:    £[N]  (+[N]% interest)
Monthly interest accumulating: £[N]/month

Debt breakdown by type:
  Code debt:          £[N]  ([N]%)
  Test debt:          £[N]  ([N]%)
  Architecture debt:  £[N]  ([N]%)
  Security debt:      £[N]  ([N]%)  ← Highest interest rate
  Dependency debt:    £[N]  ([N]%)

═══════════════════════════════════════════════════════════════
DEBT REGISTER (ordered by ROI — fix these first)
═══════════════════════════════════════════════════════════════
┌────┬─────────────────────────┬──────┬──────────┬─────────┬────────┬────────────┐
│ ID │ Item                    │ Type │ Fix Cost │ 6m Cost │ 12m$   │ ROI Score  │
├────┼─────────────────────────┼──────┼──────────┼─────────┼────────┼────────────┤
│ D1 │ OrderService God class  │ Code │  £2,400  │ £2,688  │ £3,014 │ 84 (HIGH)  │
│ D2 │ Missing circuit breakers│ Arch │  £4,000  │ £4,816  │ £5,812 │ 79 (HIGH)  │
│ D3 │ CVE in spring-security  │ Sec  │  £1,600  │ £1,984  │ £2,461 │ 94 (CRIT)  │
│ D4 │ 60% test coverage gap   │ Test │  £8,000  │ £9,442  │ £11.15K│ 72 (HIGH)  │
│ D5 │ No FRD for 3 modules    │ Doc  │  £3,200  │ £3,392  │ £3,597 │ 31 (MED)   │
└────┴─────────────────────────┴──────┴──────────┴─────────┴────────┴────────────┘

ROI Score = (costIn12m - fixToday) / fixToday × 100
Higher score = fix sooner

═══════════════════════════════════════════════════════════════
PAYBACK ROADMAP (ordered by ROI)
═══════════════════════════════════════════════════════════════
Sprint 1 (this sprint — Critical):
  D3: Upgrade spring-security → saves £861 in 12 months on £1,600 fix
  Total investment: £1,600 | Total saved: £861 | Sprint ROI: 54%

Sprint 2-3 (next month — High ROI):
  D1: Refactor OrderService → saves £614 in 12 months
  D2: Add circuit breakers → saves £1,812 in 12 months

Quarter 2 (planned — Medium ROI):
  D4: Increase test coverage to 80%
  D5: Document missing modules

═══════════════════════════════════════════════════════════════
DEBT FREE DATE (if roadmap followed): [date]
TOTAL INTEREST SAVED vs doing nothing: £[N]
═══════════════════════════════════════════════════════════════
```
