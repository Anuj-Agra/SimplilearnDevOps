---
name: refactoring-advisor
description: >
  Given a specific class or module, identify the exact refactoring moves with
  before/after pseudocode. Use when asked: 'refactor this', 'how to improve',
  'extract method', 'simplify this class', 'clean up this code', 'reduce
  complexity', 'split this class', 'refactoring plan', 'how to restructure',
  'design patterns', 'replace conditional', 'extract service'. Produces a
  sequenced refactoring plan safe to execute incrementally without breaking
  existing behaviour. Works for Java Spring and Angular TypeScript.
---
# Refactoring Advisor

Produce a safe, sequenced refactoring plan with concrete before/after for each move.

---

## The Refactoring Prime Directive

> Every refactoring step must leave the external behaviour unchanged.
> Tests must pass before AND after each step.
> Never refactor and add features in the same commit.

---

## Step 0 — Read the Target
```bash
# Read the class/file in full
cat <target_file>

# Understand its callers (what would break if the API changes)
grep -rn "$(basename <target_file> .java)\|new $(basename <target_file> .java)" \
  <java_path> --include="*.java" | grep -v "//\|test\|import" | head -20

# Check existing test coverage
find <java_path> -name "*Test*" -o -name "*Spec*" | \
  xargs grep -l "$(basename <target_file> .java)" 2>/dev/null | head -10
```

---

## Step 1 — Identify Applicable Moves

Evaluate each refactoring pattern against the target:

### Extract Method
**Trigger**: Method > 30 lines, or a block of code with a comment above it explaining what it does.
```java
// BEFORE
public void processOrder(Order order) {
    // validate
    if (order.getItems().isEmpty()) throw new BusinessException("No items");
    if (order.getCustomerId() == null) throw new BusinessException("No customer");
    if (order.getTotal().compareTo(BigDecimal.ZERO) <= 0) throw new BusinessException("Zero total");
    // calculate discount
    BigDecimal discount = BigDecimal.ZERO;
    if (order.getCustomer().isVip()) discount = order.getTotal().multiply(new BigDecimal("0.1"));
    // save
    order.setDiscount(discount);
    orderRepository.save(order);
}

// AFTER
public void processOrder(Order order) {
    validateOrder(order);
    applyDiscount(order);
    orderRepository.save(order);
}

private void validateOrder(Order order) { ... }
private void applyDiscount(Order order) { ... }
```

### Extract Class (Split God Class)
**Trigger**: Class handles more than one responsibility. Look for field groups that only interact with each other.
```java
// BEFORE: CustomerService handles profile, addresses, AND notifications
public class CustomerService { ... 800 lines ... }

// AFTER: Three cohesive classes
public class CustomerProfileService { ... }   // profile CRUD
public class CustomerAddressService { ... }   // address management
public class CustomerNotificationService { ... } // notification preferences
// CustomerService becomes a facade delegating to the three
```

### Replace Conditional with Polymorphism
**Trigger**: `if/switch` on a type field that keeps growing.
```java
// BEFORE
public BigDecimal calculateFee(Transaction t) {
    if (t.getType().equals("WIRE"))    return t.getAmount().multiply(new BigDecimal("0.002"));
    if (t.getType().equals("SWIFT"))   return t.getAmount().multiply(new BigDecimal("0.005"));
    if (t.getType().equals("SEPA"))    return new BigDecimal("0.50");
    throw new IllegalArgumentException("Unknown type: " + t.getType());
}

// AFTER
public interface TransactionType {
    BigDecimal calculateFee(BigDecimal amount);
}
public enum TransactionTypeEnum implements TransactionType {
    WIRE  { public BigDecimal calculateFee(BigDecimal a) { return a.multiply(new BigDecimal("0.002")); } },
    SWIFT { public BigDecimal calculateFee(BigDecimal a) { return a.multiply(new BigDecimal("0.005")); } },
    SEPA  { public BigDecimal calculateFee(BigDecimal a) { return new BigDecimal("0.50"); } }
}
// Adding a new type = add an enum constant. No if/switch changes.
```

### Introduce Parameter Object
**Trigger**: Method with 4+ parameters that often travel together.
```java
// BEFORE
public void createAccount(String firstName, String lastName,
    String email, String phone, String addressLine1,
    String city, String postcode, String country) { ... }

// AFTER
public record CustomerDetails(String firstName, String lastName,
    String email, String phone, Address address) {}

public void createAccount(CustomerDetails details) { ... }
```

### Replace Magic Number with Named Constant
**Trigger**: Raw numeric literals in logic.
```java
// BEFORE
if (order.getTotal().compareTo(new BigDecimal("10000")) > 0) requireApproval();
if (failedAttempts > 5) lockAccount();

// AFTER
private static final BigDecimal APPROVAL_THRESHOLD = new BigDecimal("10000");
private static final int MAX_LOGIN_ATTEMPTS = 5;

if (order.getTotal().compareTo(APPROVAL_THRESHOLD) > 0) requireApproval();
if (failedAttempts > MAX_LOGIN_ATTEMPTS) lockAccount();
```

### Decompose Conditional (Guard Clauses)
**Trigger**: Deeply nested if/else. Invert conditions to return early.
```java
// BEFORE (arrow anti-pattern)
public Result process(Request req) {
    if (req != null) {
        if (req.isValid()) {
            if (req.getUser() != null) {
                if (req.getUser().isActive()) {
                    return doProcess(req);
                }
            }
        }
    }
    return Result.error();
}

// AFTER (guard clauses)
public Result process(Request req) {
    if (req == null)              return Result.error("Null request");
    if (!req.isValid())           return Result.error("Invalid request");
    if (req.getUser() == null)    return Result.error("No user");
    if (!req.getUser().isActive()) return Result.error("User inactive");
    return doProcess(req);
}
```

### Angular: Extract Service from Component
**Trigger**: Component contains business logic or HTTP calls.
```typescript
// BEFORE: Component doing everything
@Component(...)
export class OrderComponent {
  orders: Order[] = [];
  ngOnInit() {
    this.http.get<Order[]>('/api/orders').subscribe(o => this.orders = o);
  }
  calculateTotal(order: Order): number { return order.items.reduce(...); }
}

// AFTER: Component delegates to service
@Injectable({ providedIn: 'root' })
export class OrderService {
  constructor(private http: HttpClient) {}
  getOrders(): Observable<Order[]> { return this.http.get<Order[]>('/api/orders'); }
  calculateTotal(order: Order): number { return order.items.reduce(...); }
}

@Component(...)
export class OrderComponent {
  orders$ = this.orderService.getOrders();
  constructor(private orderService: OrderService) {}
}
```

---

## Step 2 — Sequenced Refactoring Plan

Order moves from safest to riskiest. Each step must be independently committable.

```
REFACTORING PLAN: [ClassName]
Total estimated effort: [N] hours
Prerequisite: All existing tests pass before starting

Step 1 (30 min) — Replace magic numbers with named constants
  Risk: Zero — pure rename, no logic change
  Test: All existing tests still pass

Step 2 (2 hours) — Extract guard clauses from processOrder()
  Risk: Very low — same logic, different structure
  Test: All existing tests still pass + add edge case tests for each guard

Step 3 (4 hours) — Extract validateOrder() and applyDiscount()
  Risk: Low — internal restructure only
  Test: All existing tests still pass

Step 4 (1 day) — Extract CustomerAddressService from CustomerService
  Risk: Medium — new class, callers unchanged (CustomerService still delegates)
  Test: Add unit tests for CustomerAddressService before starting

Step 5 (2 days) — Replace type-switch with polymorphism
  Risk: Medium — schema change, update callers
  Test: Contract tests for each TransactionType before switching

DO NOT DO IN ONE COMMIT: Steps 4+5 together — too much change at once
```
