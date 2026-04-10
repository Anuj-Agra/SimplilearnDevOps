# Code Generation Patterns

Full, production-ready templates for each refactoring move.
Read the relevant section when the user selects a refactoring to implement.

---

## PATTERN A — Extract Class (Split God Class)

Use when: Class has 2+ distinct responsibility groups detected by D1.

### Step 1: Create the new class

```java
package [same.package.as.original];

import [only imports needed by extracted methods];

/**
 * Extracted from [OriginalClassName].
 * Responsibility: [single clear sentence]
 */
@Service  // adjust: @Component / @Repository / plain class as appropriate
@RequiredArgsConstructor
public class [NewClassName] {

    // Only the fields that the extracted methods actually use
    private final [Dependency1] [dep1];
    private final [Dependency2] [dep2];

    // Copy extracted methods VERBATIM first — clean up in a later step
    [extracted method 1 - full signature and body]

    [extracted method 2 - full signature and body]
}
```

### Step 2: Update the original class (facade pattern)

```java
@Service
@RequiredArgsConstructor
public class [OriginalClassName] {

    // ADD: new dependency
    private final [NewClassName] [newClassFieldName];

    // REMOVE: fields that moved to NewClass
    // REMOVE: methods that moved to NewClass

    // KEEP: delegating method so callers don't change
    public [ReturnType] [extractedMethodName]([params]) {
        return [newClassFieldName].[extractedMethodName]([params]);
    }

    // KEEP: all methods that stay in this class (unchanged)
}
```

### Step 3: Test the new class

```java
@ExtendWith(MockitoExtension.class)
class [NewClassName]Test {

    @Mock [Dependency1] dep1Mock;
    @Mock [Dependency2] dep2Mock;

    @InjectMocks [NewClassName] sut; // system under test

    @Test
    void [extracted_method]_[scenario]_[expected_outcome]() {
        // Arrange
        when(dep1Mock.[method]([args])).thenReturn([value]);

        // Act
        [ReturnType] result = sut.[extractedMethodName]([testArgs]);

        // Assert — verify OBSERVABLE result, not internal calls
        assertThat(result).[assertion];
        // Only verify interactions if the test IS about interaction
    }

    // Test for each public method extracted
    // Include: happy path + each validation failure + each business rule
}
```

---

## PATTERN B — Extract Method

Use when: Method > 30 lines, or contains a comment above a block explaining what it does.

```java
// BEFORE: processOrder() doing 3 things
public OrderResult processOrder(Order order) {
    // === VALIDATION BLOCK ===
    if (order.getItems().isEmpty()) throw new InvalidOrderException("No items");
    if (order.getCustomerId() == null) throw new InvalidOrderException("Missing customer");
    order.getItems().forEach(item -> {
        if (item.getQuantity() <= 0) throw new InvalidOrderException("Invalid qty for: " + item.getSku());
    });

    // === DISCOUNT CALCULATION ===
    BigDecimal discount = BigDecimal.ZERO;
    if (order.getCustomer().isVip()) {
        discount = order.getTotal().multiply(VIP_DISCOUNT_RATE);
    } else if (order.getTotal().compareTo(BULK_ORDER_THRESHOLD) > 0) {
        discount = order.getTotal().multiply(BULK_DISCOUNT_RATE);
    }

    // === PERSISTENCE ===
    order.setDiscount(discount);
    order.setStatus(OrderStatus.SUBMITTED);
    Order saved = orderRepository.save(order);
    eventPublisher.publishEvent(new OrderSubmittedEvent(saved.getId()));
    return OrderResult.success(saved);
}

// AFTER: each block becomes a named method
public OrderResult processOrder(Order order) {
    validateOrder(order);
    BigDecimal discount = calculateDiscount(order);
    return persistAndPublish(order, discount);
}

private void validateOrder(Order order) {
    if (order.getItems().isEmpty())
        throw new InvalidOrderException("Order must contain at least one item");
    if (order.getCustomerId() == null)
        throw new InvalidOrderException("Customer is required");
    order.getItems().forEach(item -> {
        if (item.getQuantity() <= 0)
            throw new InvalidOrderException("Invalid quantity for item: " + item.getSku());
    });
}

private BigDecimal calculateDiscount(Order order) {
    if (order.getCustomer().isVip())
        return order.getTotal().multiply(VIP_DISCOUNT_RATE);
    if (order.getTotal().compareTo(BULK_ORDER_THRESHOLD) > 0)
        return order.getTotal().multiply(BULK_DISCOUNT_RATE);
    return BigDecimal.ZERO;
}

private OrderResult persistAndPublish(Order order, BigDecimal discount) {
    order.setDiscount(discount);
    order.setStatus(OrderStatus.SUBMITTED);
    Order saved = orderRepository.save(order);
    eventPublisher.publishEvent(new OrderSubmittedEvent(saved.getId()));
    return OrderResult.success(saved);
}
```

**Tests to add**: one test per extracted private method covering each branch.

---

## PATTERN C — Replace Conditional with Polymorphism

Use when: switch/if-chain on a type field that will grow.

```java
// BEFORE
public BigDecimal calculateFee(Transaction t) {
    switch (t.getType()) {
        case "WIRE":  return t.getAmount().multiply(new BigDecimal("0.002"));
        case "SWIFT": return t.getAmount().multiply(new BigDecimal("0.005"));
        case "SEPA":  return new BigDecimal("0.50");
        default: throw new IllegalArgumentException("Unknown type: " + t.getType());
    }
}

// AFTER — Step 1: Define the strategy interface
public interface FeeStrategy {
    BigDecimal calculateFee(BigDecimal amount);
}

// Step 2: One implementation per type
@Component("wireFeeStrategy")
public class WireFeeStrategy implements FeeStrategy {
    private static final BigDecimal RATE = new BigDecimal("0.002");
    public BigDecimal calculateFee(BigDecimal amount) {
        return amount.multiply(RATE);
    }
}

@Component("swiftFeeStrategy")
public class SwiftFeeStrategy implements FeeStrategy {
    private static final BigDecimal RATE = new BigDecimal("0.005");
    public BigDecimal calculateFee(BigDecimal amount) {
        return amount.multiply(RATE);
    }
}

@Component("sepaFeeStrategy")
public class SepaFeeStrategy implements FeeStrategy {
    private static final BigDecimal FIXED_FEE = new BigDecimal("0.50");
    public BigDecimal calculateFee(BigDecimal amount) {
        return FIXED_FEE;
    }
}

// Step 3: Registry that replaces the switch
@Service
@RequiredArgsConstructor
public class FeeStrategyRegistry {
    private final Map<String, FeeStrategy> strategies; // Spring injects all FeeStrategy beans

    public FeeStrategy get(String transactionType) {
        FeeStrategy strategy = strategies.get(transactionType.toLowerCase() + "FeeStrategy");
        if (strategy == null) throw new IllegalArgumentException("No fee strategy for: " + transactionType);
        return strategy;
    }
}

// Step 4: Updated calling code
// BEFORE: calculateFee(transaction)
// AFTER:  feeStrategyRegistry.get(transaction.getType()).calculateFee(transaction.getAmount())
```

**Tests**: one test class per strategy + one test for the registry.

---

## PATTERN D — Introduce Parameter Object

Use when: 4+ parameters travel together across multiple methods.

```java
// BEFORE
public Customer createCustomer(String firstName, String lastName,
    String email, String phone, String addressLine1,
    String city, String postcode, String country) { ... }

public void updateCustomer(String customerId, String firstName,
    String lastName, String email, String phone) { ... }

// AFTER — Step 1: Create the parameter object
public record PersonalDetails(
    @NotBlank String firstName,
    @NotBlank String lastName,
    @Email   String email,
    @Pattern(regexp = "^[+]?[0-9]{10,15}$") String phone
) {
    // Compact constructor for validation
    public PersonalDetails {
        Objects.requireNonNull(firstName, "First name required");
        Objects.requireNonNull(lastName, "Last name required");
        Objects.requireNonNull(email, "Email required");
    }
}

public record AddressDetails(
    @NotBlank String line1,
    @NotBlank String city,
    @NotBlank String postcode,
    @NotBlank String country
) {}

// Step 2: Updated methods
public Customer createCustomer(PersonalDetails personal, AddressDetails address) { ... }
public void updateCustomer(String customerId, PersonalDetails personal) { ... }

// Step 3: Update callers
// Old: createCustomer("John", "Smith", "j@x.com", "+44...", "1 High St", "London", "EC1", "UK")
// New: createCustomer(new PersonalDetails("John","Smith","j@x.com","+44..."),
//                     new AddressDetails("1 High St","London","EC1","UK"))
```

---

## PATTERN E — Replace Magic Numbers with Constants

```java
// BEFORE
if (failedAttempts > 5) lockAccount(Duration.ofMinutes(30));
if (amount.compareTo(new BigDecimal("10000")) > 0) requireApproval();
if (description.length() > 255) throw new ValidationException("Too long");

// AFTER
private static final int    MAX_LOGIN_ATTEMPTS    = 5;
private static final Duration LOCKOUT_DURATION    = Duration.ofMinutes(30);
private static final BigDecimal APPROVAL_THRESHOLD = new BigDecimal("10_000");
private static final int    MAX_DESCRIPTION_LENGTH = 255;

if (failedAttempts > MAX_LOGIN_ATTEMPTS) lockAccount(LOCKOUT_DURATION);
if (amount.compareTo(APPROVAL_THRESHOLD) > 0) requireApproval();
if (description.length() > MAX_DESCRIPTION_LENGTH)
    throw new ValidationException("Description must not exceed " + MAX_DESCRIPTION_LENGTH + " characters");
```

---

## PATTERN F — Flatten Nesting with Guard Clauses

```java
// BEFORE (arrow anti-pattern — reads like a pyramid)
public ProcessingResult process(Request request) {
    if (request != null) {
        if (request.isValid()) {
            if (securityService.isAuthorised(request.getUserId())) {
                if (inventoryService.isAvailable(request.getItemId())) {
                    return doProcess(request);
                } else {
                    return ProcessingResult.failure("Item unavailable");
                }
            } else {
                return ProcessingResult.failure("Not authorised");
            }
        } else {
            return ProcessingResult.failure("Invalid request");
        }
    }
    return ProcessingResult.failure("Null request");
}

// AFTER (guard clauses — reads top to bottom, happy path last)
public ProcessingResult process(Request request) {
    if (request == null)
        return ProcessingResult.failure("Request must not be null");

    if (!request.isValid())
        return ProcessingResult.failure("Request is invalid: " + request.getValidationMessage());

    if (!securityService.isAuthorised(request.getUserId()))
        return ProcessingResult.failure("User is not authorised for this operation");

    if (!inventoryService.isAvailable(request.getItemId()))
        return ProcessingResult.failure("Item " + request.getItemId() + " is currently unavailable");

    return doProcess(request); // happy path — clear and prominent
}
```

---

## ANGULAR PATTERN G — Extract Service from Component

```typescript
// BEFORE: fat component doing everything
@Component({
  selector: 'app-orders',
  templateUrl: './orders.component.html',
  changeDetection: ChangeDetectionStrategy.Default,  // bad
})
export class OrdersComponent implements OnInit, OnDestroy {
  orders: Order[] = [];
  private subscription = new Subscription();

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    this.subscription.add(
      this.http.get<Order[]>('/api/orders').subscribe(orders => {
        this.orders = orders.filter(o => o.status !== 'CANCELLED')
          .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
      })
    );
  }

  getTotal(order: Order): number {
    return order.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  }

  submitOrder(order: Order) {
    this.http.post('/api/orders', order).subscribe(() => {
      this.router.navigate(['/orders/confirmation']);
    });
  }

  ngOnDestroy() { this.subscription.unsubscribe(); }
}

// AFTER — Step 1: Extract OrderService
@Injectable({ providedIn: 'root' })
export class OrderService {
  constructor(private http: HttpClient) {}

  getActiveOrders(): Observable<Order[]> {
    return this.http.get<Order[]>('/api/orders').pipe(
      map(orders => orders
        .filter(o => o.status !== 'CANCELLED')
        .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
      )
    );
  }

  calculateTotal(order: Order): number {
    return order.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  }

  submitOrder(order: Order): Observable<void> {
    return this.http.post<void>('/api/orders', order);
  }
}

// Step 2: Lean component — presentation only
@Component({
  selector: 'app-orders',
  templateUrl: './orders.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,  // correct now
})
export class OrdersComponent {
  orders$ = this.orderService.getActiveOrders();

  constructor(
    private orderService: OrderService,
    private router: Router
  ) {}

  // Uses async pipe in template — no manual subscription needed
  getTotal(order: Order): number {
    return this.orderService.calculateTotal(order);
  }

  submitOrder(order: Order) {
    this.orderService.submitOrder(order)
      .pipe(takeUntilDestroyed())
      .subscribe(() => this.router.navigate(['/orders/confirmation']));
  }
}
```

**Template update** — use `async` pipe to eliminate manual subscriptions:
```html
<!-- BEFORE -->
<div *ngFor="let order of orders">

<!-- AFTER -->
<div *ngFor="let order of orders$ | async; trackBy: trackById">
```
