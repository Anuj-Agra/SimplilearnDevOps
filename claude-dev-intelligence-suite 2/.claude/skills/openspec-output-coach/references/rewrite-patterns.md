# OpenSpec Artifact Rewrite Patterns

Full before/after rewrites for every artifact type.
Read this when prescribing improvements to the user.

---

## proposal.md Rewrites

### Rewrite: Tighten a vague "What's changing" section

```markdown
# BEFORE (too vague — AI will invent scope)
## What's changing
Improve the checkout experience for customers.

# AFTER (precise — AI knows exactly what to build)
## What's changing
Add real-time stock availability check to the Order Form screen.

When a customer enters a quantity, the form SHALL immediately (within 500ms)
display stock availability beneath the quantity field:
- "In stock (23 available)" — shown in green
- "Low stock (2 remaining)" — shown in amber
- "Out of stock" — shown in red, quantity field disabled

The check calls the existing InventoryService.checkStock(skuId, quantity)
method. No new API endpoints are created. No changes to the checkout flow
itself — this is display-only.
```

---

### Rewrite: Add missing out-of-scope section

```markdown
# ADD this section to every proposal.md

## Explicitly out of scope
- [ ] Reserving stock (locking inventory) — tracked in INV-042
- [ ] Backorder functionality — Q3 roadmap
- [ ] Supplier notification when stock drops below threshold — INV-031
- [ ] Any changes to the InventoryService implementation — read-only calls only
- [ ] Mobile-specific layout changes — responsive already handled by existing CSS
- [ ] Performance optimisation of the stock check — use existing implementation as-is
```

---

### Rewrite: Add success criteria

```markdown
# ADD this section to every proposal.md

## Success looks like
Given a product with SKU="WIDGET-001" having 5 units in stock:
1. User opens Order Form, enters SKU="WIDGET-001"
2. Within 500ms, "In stock (5 available)" appears in green below quantity field
3. User enters quantity=5 — message stays green
4. User changes to quantity=6 — message changes to "Out of stock", field disabled
5. User changes back to quantity=5 — message returns to green, field enabled
6. All existing checkout tests pass (no regressions)
7. New integration test covers all three stock states (in-stock, low, out-of-stock)
```

---

## tasks.md Rewrites

### Rewrite: Break down a large task

```markdown
# BEFORE (too large)
- [ ] 1. Implement stock availability feature

# AFTER (atomic — each ~1 hour)
- [ ] 1.1 Add checkStock(skuId: string, quantity: number): Observable<StockStatus>
           to InventoryService (Angular)
           Done when: method compiles, calls GET /api/inventory/:skuId
           with quantity param, maps response to StockStatus enum

- [ ] 1.2 Add StockStatus enum: IN_STOCK | LOW_STOCK | OUT_OF_STOCK
           Add StockStatusComponent with @Input() status: StockStatus
           Done when: component renders correct colour/message per status
           Test: StockStatusComponentSpec covers all three states

- [ ] 1.3 Wire StockStatusComponent into OrderFormComponent
           Listen to quantityControl.valueChanges with debounceTime(300)
           Call inventoryService.checkStock() and set stockStatus
           Done when: manual test shows message updates on quantity change
           Test: OrderFormComponentSpec verifies valueChanges triggers service call

- [ ] 1.4 Disable quantity field when status is OUT_OF_STOCK
           Done when: field has [disabled]="stockStatus === 'OUT_OF_STOCK'"
           Re-enables when status changes
           Test: spec verifies disabled state when OUT_OF_STOCK

- [ ] 1.5 Handle loading and error states
           Show "Checking availability..." while call is in flight
           Show "Could not check stock" on error (do not block checkout)
           Done when: spec verifies loading and error states independently
```

---

### Rewrite: Add "Done when" to every task

Template for "Done when" per task type:

```markdown
# New class / service
Done when: class exists, compiles with no warnings, all injected dependencies
           provided via constructor, no method implementations yet (throws NotImplementedException)

# New method with logic
Done when: [ClassName]Test.[methodName]_[scenario]_[outcome] tests pass, covering:
           happy path + [N] failure cases

# New API endpoint
Done when: curl or Postman call returns expected HTTP status code and response body shape.
           [Test class] integration test passes.

# UI component
Done when: component renders without console errors in the browser.
           [ComponentSpec] covers: renders correctly + primary interaction + error state.

# Database / persistence
Done when: [Test class] integration test with H2 verifies record exists in DB after call
           with correct field values.

# Wiring / integration
Done when: end-to-end test (or manual test documented in task comment) verifies
           data flows from [source] to [destination] with correct transformation.
```

---

## specs/ Rewrites

### Rewrite: Convert weak requirements to SHALL statements

```markdown
# BEFORE (weak — AI treats as optional)
- The system should validate the order
- Errors should be helpful
- The API should be fast

# AFTER (strong — AI treats as mandatory)
REQUIREMENTS:

REQ-001: Order Validation
The system SHALL reject an order submission and return HTTP 422 if:
  - items array is empty (message: "Order must contain at least one item")
  - customerId is null or blank (message: "Customer is required")
  - any item has quantity <= 0 (message: "Quantity must be greater than zero for item: {sku}")
  - total is <= 0 (message: "Order total must be greater than zero")

REQ-002: Error Response Shape
All validation errors SHALL return:
  HTTP 422 with body: { "errors": [{ "field": "string", "message": "string" }] }
  Multiple validation failures SHALL return all errors in a single response.

REQ-003: Response Time
The POST /api/orders endpoint SHALL respond within 2000ms under normal load.
```

---

### Rewrite: Add a scenarios file

Create `openspec/changes/[name]/specs/scenarios.md`:

```markdown
# Scenarios

## HAPPY PATH

Scenario: Customer successfully submits a valid order
  Given:  authenticated customer with valid account
  And:    cart contains 2 items with sufficient stock
  When:   customer submits the order form with all required fields
  Then:   order is saved with status=PENDING
  And:    HTTP 201 returned with order ID and status
  And:    customer receives confirmation email within 30 seconds
  And:    stock is reserved for each item

## VALIDATION FAILURES

Scenario: Cannot submit order with empty cart
  Given:  customer on Order Form
  When:   customer submits with no items added
  Then:   form shows "Order must contain at least one item"
  And:    form is NOT submitted (stays on the page)

Scenario: Cannot submit order with zero quantity
  Given:  customer on Order Form with item added
  When:   customer sets quantity to 0 and submits
  Then:   form shows "Quantity must be greater than zero"

## BUSINESS RULE BOUNDARIES

Scenario: Order at £10,000 does NOT require approval
  Given:  order total = £10,000.00 exactly
  When:   customer submits
  Then:   order status = PROCESSING (not PENDING_APPROVAL)

Scenario: Order above £10,000 requires manager approval
  Given:  order total = £10,000.01
  When:   customer submits
  Then:   order status = PENDING_APPROVAL
  And:    manager receives approval request notification

## EDGE CASES

Scenario: Double-submit prevented
  Given:  customer clicks Submit
  When:   customer clicks Submit again before response
  Then:   only one order is created
  And:    Submit button is disabled after first click

Scenario: Stock depleted between page load and submit
  Given:  item showed "In stock" when customer opened the form
  And:    stock reaches 0 before customer submits
  When:   customer submits the order
  Then:   order is rejected with "Item [sku] is no longer available"
  And:    customer remains on the form (not navigated away)
```

---

## project.md Additions

### Add: Tech Stack Constraints section

```markdown
## Tech Stack Constraints
The AI MUST use these technology choices. Do not introduce alternatives.

Backend (Java/Spring):
  HTTP Client:      RestTemplate (bean in HttpConfig.java) — NOT Feign, NOT WebClient
  ORM:              Spring Data JPA with Hibernate — NOT JOOQ, NOT JDBC template
  Validation:       Jakarta Bean Validation (@NotNull, @Size etc.) — NOT manual validation
  Async:            @Async with ThreadPoolTaskExecutor — NOT CompletableFuture.runAsync()
  Testing:          JUnit 5 + Mockito + AssertJ — NOT JUnit 4, NOT Hamcrest
  Mocking HTTP:     WireMock — NOT MockRestServiceServer
  Test containers:  Testcontainers (see TestConfig.java) — NOT H2 for integration tests

Frontend (Angular):
  State:            NgRx for shared state, component state for local — NOT Akita, NOT BehaviorSubject in services
  HTTP:             Angular HttpClient via services — NEVER directly in components
  Forms:            Reactive forms (FormGroup/FormControl) — NOT template-driven
  Styling:          SCSS with variables from _variables.scss — NOT inline styles
  Testing:          Karma + Jasmine — NOT Jest
  Change detection: OnPush on all new components
```

### Add: Existing Infrastructure section

```markdown
## Existing Infrastructure — Use These, Don't Re-create

| Need | Use this | Location |
|---|---|---|
| Send email | EmailNotificationService.sendEmail() | notification/EmailNotificationService.java |
| Audit log | AuditService.log(action, entityId, userId) | audit/AuditService.java |
| Get current user | SecurityContextHelper.getCurrentUser() | security/SecurityContextHelper.java |
| External HTTP | HttpClientFactory.getClient(serviceName) | config/HttpClientFactory.java |
| Validate input | Extend AbstractValidator | validation/AbstractValidator.java |
| Publish event | ApplicationEventPublisher.publishEvent() | (Spring built-in) |
| Cache data | @Cacheable (CaffeineCacheManager configured) | config/CacheConfig.java |

Before writing new infrastructure, run:
grep -r "[what you need]" src/main/java/
```
