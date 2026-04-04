# Skill: Cross-Project Mapper

> **Referenced by**: Agent 12 (Requirement Mapper)
> **Purpose**: Maps PEGA concepts to target technology implementations

---

## CONCEPT MAPPING PATTERNS

When searching for a PEGA concept in a non-PEGA codebase, use these equivalence patterns:

### Process Flows → Target Patterns

| PEGA Flow Concept | React/Next.js | Java/Spring | Node/Express | Angular |
|-------------------|--------------|-------------|--------------|---------|
| Screen Flow | Multi-step form, Wizard, Stepper | @Controller with form steps | Router with sequential routes | MatStepper, Router guards |
| Approval Flow | State machine, workflow engine | Spring State Machine, Activiti | Node workflow lib, Bull queue | NgRx effects, state management |
| Assignment | Form page + submit handler | @PostMapping endpoint | POST route handler | Reactive form + submit |
| Flow Action | Form onSubmit + API call | Form submission handler | Request handler | ngSubmit handler |
| SLA/Timer | setTimeout, cron job | @Scheduled, Quartz | node-cron, agenda | RxJS timer, schedulers |

### Decision Logic → Target Patterns

| PEGA Decision | React/Next.js | Java/Spring | Node/Express | Angular |
|---------------|--------------|-------------|--------------|---------|
| Decision Table | Switch/if-else, lookup map | Strategy pattern, rule engine | Business logic service | Service with conditions |
| Decision Tree | Nested ternary, chain of checks | Decision tree class | Recursive if-else | Service with branching |
| When Rule | Conditional rendering, guard | @Conditional, Predicate | Middleware, guard function | *ngIf, route guard |
| Map Value | Object literal, Map, enum | HashMap, enum lookup | Object/Map lookup | Pipe, Map |
| Declare Expression | useMemo, computed | @Transient getter | Computed property | Pipe, getter |

### Integrations → Target Patterns

| PEGA Integration | React/Next.js | Java/Spring | Node/Express | Angular |
|------------------|--------------|-------------|--------------|---------|
| Connect-REST | fetch/axios call | RestTemplate, WebClient | axios, node-fetch, got | HttpClient |
| Connect-SOAP | soap npm package | Spring-WS, JAX-WS | strong-soap, easy-soap | Custom HttpClient XML |
| Data Page | React Query cache, SWR | @Cacheable | Redis cache, memory cache | HttpClient + RxJS cache |
| Data Transform | DTO mapper function | ModelMapper, MapStruct | Object spread, lodash map | Class-transformer |

### UI → Target Patterns

| PEGA UI | React/Next.js | Java/Spring (Thymeleaf) | Angular |
|---------|--------------|------------------------|---------|
| Harness | Page layout, Shell | Template layout | App shell component |
| Section | Component, Card | th:fragment | Component with template |
| Field (Text) | `<input type="text">` | `<input th:field>` | `<mat-input>`, `<input>` |
| Field (Dropdown) | `<select>`, Combobox | `<select th:each>` | `<mat-select>` |
| Field (Date) | DatePicker component | `<input type="date">` | `<mat-datepicker>` |
| Visibility condition | Conditional render `{x && <Y/>}` | `th:if` | `*ngIf` |
| Validation | Yup/Zod schema | @Valid, @NotNull | Validators.required |

---

# Skill: Coverage Calculator

> **Referenced by**: Agent 13 (Gap Detector), Agent 15 (Report Generator)
> **Purpose**: Calculates implementation coverage percentages

## CALCULATION METHOD

```
Coverage % = (Implemented + 0.5 × Partial) / Total Requirements × 100

Where:
  Implemented = count of ✅ requirements
  Partial = count of 🟡 requirements (weighted at 50%)
  Total = all requirements

Weighted Coverage (accounts for priority):
  Each requirement weighted by priority multiplier:
    Critical: ×3
    High:     ×2
    Medium:   ×1
    Low:      ×0.5

  Weighted Coverage = Σ(status_score × priority_weight) / Σ(priority_weight) × 100
  Where status_score: Implemented=1, Partial=0.5, Missing=0, Divergent=0.25
```

## CATEGORY-LEVEL COVERAGE

Calculate separately for:
- Flow coverage (are process steps built?)
- Decision coverage (are business rules coded?)
- Integration coverage (are API calls implemented?)
- UI coverage (are fields and screens present?)
- End-to-end coverage (can a full workflow execute?)

---

# Skill: Gap Classifier

> **Referenced by**: Agent 13 (Gap Detector)
> **Purpose**: Classifies gaps into standardized types

## GAP TAXONOMY

```
MISSING — No implementation exists
  MISSING_FLOW:        Entire process flow not built
  MISSING_STEP:        Specific step in a flow not built
  MISSING_BRANCH:      Decision branch not handled
  MISSING_INTEGRATION: External API call not implemented
  MISSING_FIELD:       UI field not present
  MISSING_VALIDATION:  Field validation not implemented
  MISSING_ERROR_PATH:  Error handling not implemented

PARTIAL — Implementation started but incomplete
  PARTIAL_CONDITIONS:  Some decision conditions missing
  PARTIAL_FIELDS:      Some fields missing from a screen
  PARTIAL_MAPPING:     Some request/response fields not mapped
  PARTIAL_FLOW:        Flow started but not all steps built
  PARTIAL_ERROR:       Some error scenarios handled, others not

DIVERGENT — Implemented differently from source
  DIVERGENT_LOGIC:     Different conditions or operators used
  DIVERGENT_FLOW:      Process steps in different order or different approach
  DIVERGENT_SCHEMA:    Different data structure or field names
  DIVERGENT_BEHAVIOR:  Works but produces different outcomes

LOGIC_ERROR — Implementation present but incorrect
  WRONG_OPERATOR:      >= instead of >, etc.
  WRONG_THRESHOLD:     Different numeric values
  WRONG_ORDER:         Evaluation order differs
  WRONG_DEFAULT:       Default/else case produces wrong result
```
