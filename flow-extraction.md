# Flow Extraction Reference

Detailed patterns for tracing front-to-back flows and generating
Section 4A (high-level overview) and Section 4B (detailed breakdowns).

---

## What Is a Flow?

A flow is the complete journey of ONE user intention from first click to final
outcome — tracing through every layer of the system.

Unlike a use case (which describes steps from the user's perspective only),
a flow traces what EVERY layer does:

```
User clicks button
  → Angular component handles event
    → Angular service makes HTTP call
      → Java controller receives request
        → Java service applies business rules
          → Repository reads/writes data
            → Event published (if async)
              → Consumer processes event
                → External system notified
                  → Response travels back up
                    → Angular updates UI
                      → User sees result
```

---

## Flow Discovery: What to Look For

### Signal 1: Angular Button Click → Service Call
```
(click)="submit()" in template
→ component.submit() method
→ this.orderService.createOrder(data)
→ HTTP POST /api/orders
```

### Signal 2: Angular Route → Page Load
```
Route guard resolves → component initialised
→ ngOnInit() calls this.service.getData()
→ HTTP GET /api/[resource]
```

### Signal 3: Java Controller → Service → Repository
```
@PostMapping → @Service method → @Repository.save()
```

### Signal 4: Service → Event → Consumer (async)
```
orderService.process() → applicationEventPublisher.publishEvent(OrderCreatedEvent)
→ @EventListener in NotificationService → sends email
```

### Signal 5: Scheduled Trigger
```
@Scheduled(cron="0 0 2 * * *") → statementService.generate()
→ reads all accounts → generates PDF → sends email
```

### Signal 6: External Integration
```
Service → restTemplate.post("https://payment-gateway.com/charge")
→ external processes payment → returns result
```

---

## How to Name Flows

Name every flow from the USER's perspective, using the verb they would use.
The name should answer "what is the user trying to accomplish?"

| Technical description | Business flow name |
|---|---|
| POST /api/orders → save to DB | Submit a Purchase Order |
| GET /api/orders/{id} → return DTO | View Order Details |
| PUT /api/orders/{id}/status → APPROVED | Approve an Order |
| @Scheduled → generate report | Generate Nightly Account Statements |
| POST /api/customers → save → publish event | Register a New Customer |

---

## Master Flowchart Patterns (Section 4A)

### Pattern: Linear flow (simple feature)

```mermaid
flowchart TD
  User([Customer]) --> Form[Order Form]
  Form -->|Submits order| Process[Order Processing]
  Process --> Valid{Valid order?}
  Valid -->|Yes| Save[(Order saved)]
  Valid -->|No| Error[User sees error]
  Save -.->|Async| Email[Confirmation email sent]
  Save --> Confirm[User sees confirmation]
```

### Pattern: Approval chain

```mermaid
flowchart TD
  User([Customer]) --> Form[Order Form]
  Form --> Submit[Order submitted]
  Submit --> Check{Total ≥ £10,000?}
  Check -->|No| Process[Order processed immediately]
  Check -->|Yes| Pending[Order awaits approval]
  Pending --> Manager([Manager]) -->|Reviews| Decision{Approve?}
  Decision -->|Yes| Process
  Decision -->|No| Reject[Order rejected]
  Process -.->|Async| Notify[Customer notified]
  Reject -.->|Async| NotifyR[Customer notified of rejection]
```

### Pattern: Multi-system integration

```mermaid
flowchart TD
  User([Account Holder]) --> Portal[Account Portal]
  Portal --> Request[Payment instruction submitted]
  Request --> Validate{Funds available?}
  Validate -->|No| Decline[User sees insufficient funds message]
  Validate -->|Yes| Reserve[Funds reserved]
  Reserve --> Pay([Payment System])
  Pay -->|Confirms| Complete[Payment recorded]
  Complete -.->|Async| Statement[Statement updated]
  Complete -.->|Async| Receipt[Receipt emailed]
```

### Pattern: Scheduled / background

```mermaid
flowchart TD
  Timer([Nightly Schedule - 2am]) --> Gen[Statement Generator]
  Gen --> Accounts[(All active accounts)]
  Accounts -->|For each account| Create[Statement created]
  Create --> PDF[PDF generated]
  PDF -.->|Async, one per account| Send[Statement emailed to account holder]
```

---

## Sequence Diagram Patterns (Section 4B)

### Pattern: Simple CRUD with validation

```mermaid
sequenceDiagram
  actor User
  participant UI as [Screen Name]
  participant API as [Feature] API
  participant BL as [Feature] Processing
  participant DB as [Entity] Records

  User->>UI: Completes form and clicks "[Button Label]"
  UI->>UI: Checks required fields are filled (instant)

  UI->>API: Submits [entity] details
  API->>BL: Process [entity] creation
  BL->>BL: Applies business validation rules

  alt All rules pass
    BL->>DB: Saves [entity] record
    DB-->>BL: [Entity] saved with unique reference
    BL-->>API: Success — reference [REF]
    API-->>UI: Created successfully
    UI-->>User: Shows "[Entity] [REF] has been saved"
  else Validation rule fails
    BL-->>API: Validation failed: [rule description]
    API-->>UI: Rule violation details
    UI-->>User: Shows "[Exact error message]" — stays on form
  end
```

### Pattern: Approval workflow

```mermaid
sequenceDiagram
  actor Submitter as [Submitter Role]
  actor Approver as [Approver Role]
  participant UI as [Screen Name]
  participant API as [Feature] API
  participant BL as [Feature] Processing
  participant DB as [Entity] Records
  participant NF as Notification Service

  Submitter->>UI: Completes and submits [request]
  UI->>API: Submit [request]
  API->>BL: Process submission
  BL->>DB: Save [entity] with status PENDING APPROVAL
  DB-->>BL: Saved
  BL->>NF: Notify approver: new [request] awaiting review
  NF--)Approver: Email — "[Request] requires your approval"
  BL-->>API: Submitted — awaiting approval
  API-->>UI: Status: Pending Approval
  UI-->>Submitter: Shows "Submitted — awaiting manager approval"

  note over Approver,UI: [Time passes — approval is asynchronous]

  Approver->>UI: Opens Approval Queue
  UI->>API: Load pending [requests]
  API-->>UI: List of [N] pending [requests]
  UI-->>Approver: Displays approval queue

  Approver->>UI: Reviews [request] and clicks "Approve"
  UI->>API: Approve [request ID]
  API->>BL: Process approval
  BL->>DB: Update status to APPROVED
  BL->>NF: Notify submitter: [request] approved
  NF--)Submitter: Email — "Your [request] has been approved"
  BL-->>API: Approved
  API-->>UI: Status updated
  UI-->>Approver: Shows "Approved successfully"
```

### Pattern: Async background process

```mermaid
sequenceDiagram
  participant Timer as Scheduled Trigger (2am nightly)
  participant JOB as Statement Generator
  participant DB as Account Records
  participant PDF as Document Creator
  participant NF as Email Service

  Timer->>JOB: Trigger nightly statement run
  JOB->>DB: Load all accounts due for statement
  DB-->>JOB: [N] accounts returned

  loop For each account
    JOB->>DB: Load transactions for period
    DB-->>JOB: Transaction history
    JOB->>PDF: Generate statement PDF
    PDF-->>JOB: PDF ready
    JOB--)NF: Queue statement email (async)
    NF--)DB: Log statement sent (background)
  end

  note over NF: Emails delivered over next 15 minutes
  note over JOB: Job completes — no user waiting for result
```

### Pattern: External system integration

```mermaid
sequenceDiagram
  actor User
  participant UI as Payment Screen
  participant API as Payment API
  participant BL as Payment Processing
  participant DB as Payment Records
  participant EXT as [External Payment System]

  User->>UI: Enters payment details and confirms
  UI->>API: Submit payment instruction
  API->>BL: Process payment
  BL->>DB: Record payment as PENDING
  BL->>EXT: Send payment request

  alt External system confirms
    EXT-->>BL: Payment authorised (reference: EXT-[REF])
    BL->>DB: Update status to COMPLETED
    BL-->>API: Payment complete
    API-->>UI: Confirmed
    UI-->>User: "Payment successful — reference [REF]"
  else External system declines
    EXT-->>BL: Payment declined (reason: [reason])
    BL->>DB: Update status to DECLINED
    BL-->>API: Payment declined
    API-->>UI: Declined
    UI-->>User: "Payment could not be processed: [reason]"
  else External system times out
    note over BL,EXT: No response after 30 seconds
    BL->>DB: Update status to PENDING REVIEW
    BL-->>API: Outcome unknown
    API-->>UI: Uncertain
    UI-->>User: "Payment is being verified — you will receive confirmation by email"
  end
```

---

## Diagram Label Translations

Always translate technical terms to business language in diagram labels:

| Technical label | Business label |
|---|---|
| `POST /api/orders` | "Submits order details" |
| `orderRepository.save(entity)` | "Saves order record" |
| `kafkaTemplate.send("order-events", event)` | "Notifies fulfilment system" |
| `OrderStatus.PENDING_APPROVAL` | "Awaiting manager approval" |
| `restTemplate.post(paymentGatewayUrl)` | "Sends payment to [Gateway Name]" |
| `@Scheduled(cron="0 0 2 * * *")` | "Nightly at 2am" |
| `applicationEventPublisher.publishEvent(e)` | "Triggers background notification" |
| `Optional.empty()` | "Record not found" |
| `throw new BusinessException("...")` | "Rejected: [plain English reason]" |
