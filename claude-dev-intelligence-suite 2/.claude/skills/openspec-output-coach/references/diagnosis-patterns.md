# OpenSpec Diagnosis Patterns

Detailed root cause analysis for every common failure mode.

---

## PROPOSAL.MD Failures

### P1 — Vague Intent ("What's changing" underspecified)

**Symptom**: AI built a feature that sort of matches but misses the actual goal.
**Signal phrase**: "That's not quite what I meant"

**Diagnostic check**:
```bash
# Is the what's changing section more than 3 sentences without specifics?
head -20 openspec/changes/[name]/proposal.md
```

**Bad proposal → AI guesses**:
```markdown
## What's changing
Improve the user management section.
```

**Good proposal → AI executes precisely**:
```markdown
## What's changing
Add a "Suspend Account" button to the User Detail screen (/admin/users/:id).
Clicking it changes the user's status from ACTIVE to SUSPENDED.
A suspended user can still log in but sees a "Your account is suspended" banner
and cannot perform any write operations until reinstated.
This does NOT affect the user's data or permissions — only their active status.
```

**Coaching rule**: One noun (what), one verb (change type), one screen/endpoint,
one visible outcome. If you can't write it in 3 sentences, the scope is too large.

---

### P2 — Missing Out-of-Scope Boundary

**Symptom**: AI built extra features you didn't ask for.
**Signal phrase**: "AI added X which I didn't want"

**Bad**:
```markdown
## What's changing
Add authentication.
(no out-of-scope section)
```

**Good**:
```markdown
## Explicitly out of scope for this change
- Password reset flow (tracked as AUTH-004)
- Email verification (AUTH-005)
- OAuth/social login (Q3 milestone)
- Any changes to the session management code (AUTH-002)
- Registration — admin creates accounts manually
```

**Coaching rule**: OpenSpec AI reads out-of-scope as a hard stop list.
Every obvious extension of your feature that you DON'T want should be listed.
When in doubt, list it as out of scope.

---

### P3 — No Success Definition

**Symptom**: AI said it was done but the feature didn't work end-to-end.
**Signal phrase**: "Tasks all ticked but it's still broken"

**Bad**: No success criteria → AI completes tasks mechanically without verifying intent.

**Good**:
```markdown
## Success looks like
- A user with status=ACTIVE can navigate to /admin/users/123 and see "Suspend" button
- Clicking "Suspend" shows a confirmation dialog ("Are you sure? This will...")
- After confirmation, the button changes to "Reinstate" and user.status = SUSPENDED
- Navigating to any write operation as a suspended user shows the banner
- The suspension is recorded in the audit log with timestamp and admin who actioned it
- Existing tests pass (no regressions)
```

**Coaching rule**: "Success looks like" items become the AI's acceptance test.
Make them observable (visible in UI or verifiable in DB) and specific.

---

## TASKS.MD Failures

### T1 — Tasks Too Large

**Symptom**: AI drifted halfway through a task, or produced a partial implementation.
**Signal**: Single task that takes >2 hours, or contains the word "implement the..."

**Diagnostic**:
Any task containing: "implement the module", "create the full service",
"build the complete...", "handle all the..." is too large.

**Bad tasks**:
```markdown
- [ ] 1.1 Implement the payment service
- [ ] 1.2 Add all the validation
- [ ] 1.3 Wire up the frontend
```

**Good tasks** (1-hour atomic units):
```markdown
- [ ] 1.1 Create PaymentService class (empty, with constructor injection of PaymentRepository)
      Done when: class exists, compiles, has no implementation yet
- [ ] 1.2 Add validatePayment(PaymentRequest) — throws PaymentValidationException if:
          amount <= 0, currency not in [GBP, USD, EUR], or accountId null
      Done when: PaymentServiceTest.validatePayment tests pass (3 failure cases + 1 success)
- [ ] 1.3 Implement processPayment(PaymentRequest) — calls paymentGatewayClient.charge()
          then saves Payment entity via paymentRepository.save()
      Done when: happy path integration test passes with H2
- [ ] 1.4 Add POST /api/payments endpoint to PaymentController
      Done when: curl -X POST localhost:8080/api/payments returns 201 with payment ID
```

**Coaching rule**: Each task = one class, one method, one endpoint, or one test file.
If the task has "and" in it, split it.

---

### T2 — Missing "Done When" Criteria

**Symptom**: AI ticked a task as complete but the work was partial.
**Signal**: "AI said done but the feature is half-built"

**Bad**:
```markdown
- [ ] 2.3 Add discount logic
```

**Good**:
```markdown
- [ ] 2.3 Implement calculateDiscount(Order order) in OrderService
      Done when:
        - Returns order.total × 0.10 when customer.tier == VIP
        - Returns BigDecimal.ZERO for all other customer tiers
        - Discount never exceeds £500 (cap applied inside this method)
        - OrderServiceTest.calculateDiscount covers: VIP below cap, VIP above cap,
          non-VIP, null customer tier
```

**Coaching rule**: "Done when" is a contract. The AI checks it before marking
the task complete. Without it, "done" means "I wrote some code".

---

### T3 — Dependency Order Violated

**Symptom**: AI tried to use a class/method before creating it.
**Signal**: "AI imported something that didn't exist yet"

**Diagnostic**: Check if any task uses output (class, method, DTO) from a later task.

**Fix**: Add dependency comments:
```markdown
- [ ] 1.1 Create CreateOrderRequest record (id, customerId, items, total)
- [ ] 1.2 Create OrderResponse record (id, status, createdAt)
      Depends on: 1.1 complete
- [ ] 1.3 Add POST /api/orders to OrderController
          Request: CreateOrderRequest, Response: 201 + OrderResponse
      Depends on: 1.1 and 1.2 complete
```

---

## SPECS/ Failures

### S1 — "Should" Instead of "SHALL"

**Symptom**: AI implemented the feature but skipped some requirements.
**Signal**: "AI ignored the validation rules"

**Diagnostic**:
```bash
grep -c "should\|may\|might\|could" openspec/changes/[name]/specs/*.md
# High count = weak requirements
grep -c "SHALL\|MUST\|REQUIRED" openspec/changes/[name]/specs/*.md
# Low count = requirements not enforceable
```

**Bad** (AI treats as suggestion):
```
The system should validate the email format.
Errors should be user-friendly.
The response should include the created resource.
```

**Good** (AI treats as hard requirement):
```
The system SHALL reject any email address that does not conform to RFC 5322 format.
The system SHALL return HTTP 400 with body {"field": "email", "message": "Must be a valid email address"}.
The system SHALL return HTTP 201 with the full created resource in the response body.
```

---

### S2 — Missing Edge Case Scenarios

**Symptom**: AI only implemented the happy path.
**Signal**: "Empty list returns null", "Zero quantity accepted", "Works for first user but not second"

Add a `specs/scenarios.md` file if missing. Include these for EVERY feature:
```markdown
# Scenarios

## Happy Path
Given: [valid precondition]
When: [user action with valid data]
Then: [expected result]

## Validation Failures (one per mandatory field)
Given: user on [screen/endpoint]
When: [field] is empty / invalid / too long
Then: error "[exact message]" is shown

## Business Rule Boundaries
Given: order total is £10,000 (AT threshold)
When: submitted
Then: processed without approval (threshold is EXCEEDING not AT)

Given: order total is £10,001 (ABOVE threshold)
When: submitted
Then: status = PENDING_APPROVAL, manager notified

## Edge Cases
Given: list has 0 items
When: GET /api/orders
Then: returns 200 with empty array [], NOT null, NOT 404

Given: same request submitted twice
When: idempotency key matches existing request
Then: returns original response, no duplicate created
```

---

## PROJECT.MD Failures

### PM1 — Domain Language Not Defined

**Symptom**: AI used inconsistent or wrong terminology throughout.
**Signal**: "AI called it 'user' but we call it 'account holder'"

**Fix**: Add a Glossary section to `openspec/project.md`:
```markdown
## Domain Glossary
The AI MUST use these exact terms in all code, comments, and documentation:

| Our term | NOT this |
|---|---|
| Account Holder | user, customer, client, person |
| Account | profile, record |
| Transaction | payment, transfer, movement |
| Suspend | disable, deactivate, block |
| Reinstate | enable, reactivate, unblock |
| Reference | ID, code, number |
```

### PM2 — Architecture Constraints Missing

**Fix**: Add to `openspec/project.md`:
```markdown
## Architecture Rules (MUST follow, no exceptions)
- HTTP clients: Use existing RestTemplate bean from HttpConfig — never add Feign or WebClient
- Dependency injection: Constructor only via @RequiredArgsConstructor — never @Autowired on fields
- Exceptions: All service exceptions extend BusinessException — never catch and swallow
- Transactions: @Transactional on service methods, never on controllers or repositories
- Database: All queries via Spring Data repositories — never EntityManager directly
- Layers: Controller → Service → Repository only. Controllers never call repositories.
- Security: @PreAuthorize on every non-public controller method — no security through obscurity
```

---

## AGENTS.MD / CLAUDE.MD Failures

### A1 — AI Ignored Existing Patterns

**Symptom**: AI created a new implementation of something that already exists.
**Signal**: "AI created a new email service — EmailNotificationService already exists"

**Fix**: Add to `AGENTS.md`:
```markdown
## Before writing new code, always check if it already exists:
- Email/notification: EmailNotificationService in notification/ module
- Validation: Validators in validation/ — extend AbstractValidator
- HTTP clients: HttpClientFactory — get clients from here
- Audit logging: AuditService.log(action, entityId, userId)
- Error handling: GlobalExceptionHandler — add new @ExceptionHandler here
- Auth context: SecurityContextHelper.getCurrentUser()
Run: grep -r "[thing you need]" src/ before implementing it fresh.
```

### A2 — AI Didn't Run Tests

**Fix**: Add to `AGENTS.md`:
```markdown
## After implementing each task:
1. Run: mvn test -pl :[affected-module] --no-transfer-progress
2. Confirm: all tests pass before marking task done
3. If new tests were expected: confirm the new test file exists and tests pass
4. Never mark a task as Done if tests are failing
```
