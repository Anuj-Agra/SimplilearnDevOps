---
name: test-data-builder-generator
description: >
  Generate the Builder pattern for every entity and DTO, making test setup
  readable: anOrder().withStatus(PENDING).withItems(3).build(). Use when asked:
  'test data builders', 'test fixtures', 'builder pattern tests', 'test data
  factory', 'test data setup', 'readable test data', 'object mother pattern',
  'test builder generation', 'test data helpers', 'fixture factory'. Generates
  consistent builders across all test classes, eliminates duplication, and makes
  tests self-documenting. Works for Java entities/DTOs and Angular TypeScript models.
---
# Test Data Builder Generator

Generate fluent builders for every entity and DTO so tests read like specifications.

---

## Why Builders Beat Direct Construction

```java
// Without builders — hard to understand test intent
Order order = new Order();
order.setId(UUID.randomUUID());
order.setCustomerId("CUST-001");
order.setStatus(OrderStatus.PENDING);
order.setTotal(new BigDecimal("150.00"));
order.setItems(List.of(new OrderItem("SKU-1", 2, new BigDecimal("75.00"))));
order.setCreatedAt(LocalDateTime.now());
// 6 lines of noise before the test even starts

// With builders — reads like a business specification
Order order = anOrder()
    .withStatus(PENDING)
    .withItems(2)
    .withTotal("150.00")
    .build();
// Intent is immediately clear
```

---

## Step 1 — Discover All Entities and DTOs

```bash
# Java entities
find <java_path> -name "*.java" | \
  xargs grep -l "@Entity\|@Document\|@Table" 2>/dev/null | head -30

# Java DTOs / Request / Response classes
find <java_path> -name "*Dto.java" -o -name "*DTO.java" \
  -o -name "*Request.java" -o -name "*Response.java" | head -30

# Read fields of each
grep -rn "private " <entity_file> | \
  grep -v "static\|final\|Logger\|log\b\|@" | head -30

# Angular models
find <angular_path> -name "*.model.ts" -o -name "*.interface.ts" | head -20
grep -rn "export interface\|export class\|export type" \
  <angular_path> --include="*.model.ts" --include="*.ts" | head -30
```

---

## Step 2 — Generate Java Builders

Generate one builder class per entity/DTO. Save to `src/test/java/[package]/builders/`.

### Pattern: Fluent Builder with Sensible Defaults

```java
// Generated: src/test/java/com/yourorg/builders/OrderBuilder.java
package com.yourorg.builders;

import com.yourorg.domain.Order;
import com.yourorg.domain.OrderStatus;
import com.yourorg.domain.OrderItem;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Test data builder for Order.
 * Usage: anOrder().withStatus(PENDING).withItems(2).build()
 */
public class OrderBuilder {

    // Sensible defaults — tests only override what matters for THEIR scenario
    private String id              = "ORDER-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    private String customerId      = "CUST-TEST-001";
    private OrderStatus status     = OrderStatus.PENDING;
    private BigDecimal total       = new BigDecimal("100.00");
    private List<OrderItem> items  = defaultItems(1);
    private LocalDateTime createdAt = LocalDateTime.of(2024, 1, 15, 10, 0, 0); // fixed — not now()
    private String reference       = "REF-TEST-001";

    // Static factory — readable entry point
    public static OrderBuilder anOrder() { return new OrderBuilder(); }

    // Domain-language methods — name after business concepts, not fields
    public OrderBuilder withStatus(OrderStatus status) {
        this.status = status; return this;
    }

    public OrderBuilder withItems(int count) {
        this.items = defaultItems(count); return this;
    }

    public OrderBuilder withItem(OrderItemBuilder itemBuilder) {
        this.items = new ArrayList<>(this.items);
        this.items.add(itemBuilder.build()); return this;
    }

    public OrderBuilder withTotal(String amount) {
        this.total = new BigDecimal(amount); return this;
    }

    public OrderBuilder withTotal(BigDecimal amount) {
        this.total = amount; return this;
    }

    public OrderBuilder forCustomer(String customerId) {
        this.customerId = customerId; return this;
    }

    public OrderBuilder withReference(String reference) {
        this.reference = reference; return this;
    }

    public OrderBuilder createdAt(LocalDateTime time) {
        this.createdAt = time; return this;
    }

    // Convenience methods for common test scenarios
    public OrderBuilder pending()   { return withStatus(OrderStatus.PENDING); }
    public OrderBuilder approved()  { return withStatus(OrderStatus.APPROVED); }
    public OrderBuilder cancelled() { return withStatus(OrderStatus.CANCELLED); }
    public OrderBuilder forVipCustomer() { return forCustomer("VIP-CUST-001"); }
    public OrderBuilder empty()     { this.items = List.of(); return this; }

    public OrderBuilder aboveApprovalThreshold() {
        return withTotal("10001.00"); // just above the £10,000 threshold
    }

    public OrderBuilder belowApprovalThreshold() {
        return withTotal("9999.00");
    }

    public Order build() {
        Order order = new Order();
        order.setId(id);
        order.setCustomerId(customerId);
        order.setStatus(status);
        order.setTotal(total);
        order.setItems(new ArrayList<>(items));
        order.setCreatedAt(createdAt);
        order.setReference(reference);
        return order;
    }

    // Build list of N orders
    public static List<Order> buildList(int count) {
        return java.util.stream.IntStream.rangeClosed(1, count)
            .mapToObj(i -> anOrder()
                .withReference("REF-TEST-" + String.format("%03d", i))
                .forCustomer("CUST-TEST-" + String.format("%03d", i))
                .build())
            .collect(java.util.stream.Collectors.toList());
    }

    private static List<OrderItem> defaultItems(int count) {
        return java.util.stream.IntStream.rangeClosed(1, count)
            .mapToObj(i -> anOrderItem()
                .withSku("SKU-TEST-" + String.format("%03d", i))
                .withQuantity(1)
                .withPrice("50.00")
                .build())
            .collect(java.util.stream.Collectors.toList());
    }
}
```

### Generate the companion import class

```java
// src/test/java/com/yourorg/builders/Builders.java
// One-stop import for all builders
package com.yourorg.builders;

public class Builders {
    // Static imports — use in tests: import static Builders.*
    public static OrderBuilder anOrder()        { return new OrderBuilder(); }
    public static CustomerBuilder aCustomer()   { return new CustomerBuilder(); }
    public static OrderItemBuilder anOrderItem(){ return new OrderItemBuilder(); }
    public static PaymentBuilder aPayment()     { return new PaymentBuilder(); }
    // Add one line per entity
}
```

### How tests use builders

```java
// BEFORE: verbose, noisy setup
@Test
void order_above_threshold_requires_approval() {
    Order order = new Order();
    order.setCustomerId("CUST-001");
    order.setStatus(OrderStatus.PENDING);
    order.setTotal(new BigDecimal("10001.00"));
    order.setItems(List.of(new OrderItem(...)));
    // ... 8 more setup lines ...

    // AFTER: intent-revealing
    Order order = anOrder().aboveApprovalThreshold().pending().build();

    OrderResult result = orderService.process(order);

    assertThat(result.requiresApproval()).isTrue();
}

// Complex scenario — still readable
@Test
void vip_customer_gets_discount_applied_before_persistence() {
    Order order = anOrder()
        .forVipCustomer()
        .withItems(3)
        .withTotal("500.00")
        .build();
    // ...
}
```

---

## Step 3 — Generate Angular TypeScript Builders

```typescript
// src/test/builders/order.builder.ts
import { Order, OrderStatus, OrderItem } from '../../app/models/order.model';

export class OrderBuilder {
  private order: Partial<Order> = {
    id:         'ORDER-TEST-001',
    customerId: 'CUST-TEST-001',
    status:      OrderStatus.PENDING,
    total:       100,
    items:       [defaultItem()],
    createdAt:   new Date('2024-01-15T10:00:00Z'), // fixed — not new Date()
    reference:   'REF-TEST-001',
  };

  static anOrder(): OrderBuilder { return new OrderBuilder(); }

  withStatus(status: OrderStatus):  OrderBuilder { this.order.status = status; return this; }
  withTotal(amount: number):        OrderBuilder { this.order.total  = amount; return this; }
  withItems(count: number):         OrderBuilder { this.order.items  = defaultItems(count); return this; }
  forCustomer(id: string):          OrderBuilder { this.order.customerId = id; return this; }

  // Scenario shortcuts
  pending():   OrderBuilder { return this.withStatus(OrderStatus.PENDING); }
  approved():  OrderBuilder { return this.withStatus(OrderStatus.APPROVED); }
  cancelled(): OrderBuilder { return this.withStatus(OrderStatus.CANCELLED); }
  empty():     OrderBuilder { this.order.items = []; return this; }
  aboveApprovalThreshold(): OrderBuilder { return this.withTotal(10001); }

  build(): Order { return { ...this.order } as Order; }
}

// Helper — used in component specs
export function anOrder(): OrderBuilder { return new OrderBuilder(); }

function defaultItem(): OrderItem {
  return { sku: 'SKU-001', quantity: 1, price: 100, description: 'Test Item' };
}

function defaultItems(count: number): OrderItem[] {
  return Array.from({ length: count }, (_, i) => ({
    sku: `SKU-${String(i+1).padStart(3,'0')}`,
    quantity: 1, price: 50,
    description: `Test Item ${i+1}`
  }));
}
```

---

## Step 4 — Output: Builder Coverage Report

```
TEST DATA BUILDERS GENERATED: [System]

BUILDERS CREATED ([N] files):
  Java (src/test/java/[package]/builders/):
    ✅ OrderBuilder.java           (22 methods, 8 scenario shortcuts)
    ✅ CustomerBuilder.java        (15 methods, 5 scenario shortcuts)
    ✅ OrderItemBuilder.java       (10 methods)
    ✅ PaymentBuilder.java         (12 methods, 4 scenario shortcuts)
    ✅ Builders.java               (central import hub)

  Angular (src/test/builders/):
    ✅ order.builder.ts
    ✅ customer.builder.ts
    ✅ payment.builder.ts

SCENARIO SHORTCUTS GENERATED:
  Domain thresholds:   aboveApprovalThreshold(), belowApprovalThreshold()
  Status shortcuts:    pending(), approved(), cancelled(), rejected()
  Role shortcuts:      forVipCustomer(), forGuestCustomer()
  Data shortcuts:      empty(), withMaxLength(), withMinLength()

USAGE:
  import static com.yourorg.builders.Builders.*;

  anOrder().aboveApprovalThreshold().forVipCustomer().build()
  aCustomer().vip().withAddress("London").build()
  buildList(10)  // generate 10 distinct test orders
```
