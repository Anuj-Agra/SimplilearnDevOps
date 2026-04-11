# External System Interaction Reference

Patterns for extracting, translating, and documenting every interaction
between this module and any system outside its boundary.

---

## What Counts as an External System?

An external system is anything the module talks to that is NOT:
- Its own classes and services
- Its own database (which is internal data)
- Its own message queue topics (if it owns both producer and consumer)

**External systems include:**
- Other microservices / modules owned by other teams
- Third-party APIs (payment gateways, identity verification, address lookup)
- Message queues where another team owns the consumer (Kafka, RabbitMQ, SQS)
- File-based integrations (SFTP drops, S3 buckets consumed by others)
- Inbound webhooks (external system POSTing to this module)
- Shared databases owned by another team
- Email / notification services
- Monitoring / logging platforms (if explicitly called)

---

## Step-by-Step Extraction Process

### Step 1 — Find Every Outbound Call

```bash
# HTTP clients
grep -rn "restTemplate\.\|webClient\.\|@FeignClient\|HttpClient\.\|OkHttpClient\|\
  exchange\(\|getForObject\(\|postForEntity\(" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test"

# External URLs
grep -rn "https://\|http://" \
  <java_path>/src/main/resources --include="*.yml" --include="*.properties" | \
  grep -v "localhost\|127\.0\|swagger\|actuator\|#" | head -20

# Messaging producers
grep -rn "kafkaTemplate\.send\|rabbitTemplate\.convertAndSend\|sqsClient\.sendMessage\|\
  snsClient\.publish\|messagingTemplate\.send" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test"

# File / cloud storage
grep -rn "s3Client\.\|azureBlobClient\.\|sftpClient\.\|FTPClient\.\|Files\.copy\|Files\.write" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test"

# Inbound webhooks (external calling us)
grep -rn "@PostMapping\|@PutMapping" <java_path> --include="*.java" | \
  grep -i "webhook\|callback\|notify\|inbound\|hook\|event"
```

### Step 2 — Read the Calling Code to Extract the Contract

For each external call found, read its implementation class and extract:

**A. What is sent:**
Look at the request object, DTO, or method parameters passed to the external call.
Translate each field from its Java name to its business meaning.

```bash
# Find the request body class for each external call
grep -rn "new [A-Z][a-zA-Z]*Request\|\.body(\|\.bodyValue(\|\.toUriString\|UriComponentsBuilder" \
  <calling_class>.java | head -20

# Read the request DTO in full
cat <RequestDto>.java
```

**B. What comes back:**
Look at what the code does with the response. The cases it handles ARE the response types.

```bash
# Find response handling (each case = a response type to document)
grep -rn "getStatusCode\|getBody\|\.getStatus\|HttpStatus\.\|switch.*status\|\
  if.*200\|if.*201\|if.*4[0-9][0-9]\|if.*5[0-9][0-9]\|onSuccess\|onError\|\
  onFailure\|orElse\|map(\|flatMap(\|doOnError\|onErrorReturn\|fallback" \
  <calling_class>.java | head -30
```

**C. What happens with each response:**
Trace what the code does AFTER receiving each type of response.

```bash
# What gets saved after a successful response
grep -rn "\.save\(\|\.update\(\|repository\.\|status.*=\|setState\|setStatus" \
  <service_class>.java | head -20

# What gets published/notified after success
grep -rn "publishEvent\|kafkaTemplate\.send\|sendEmail\|sendNotification" \
  <service_class>.java | head -10

# What happens on failure
grep -rn "catch\|onError\|orElseThrow\|orElse\|fallback\|retry\|queue" \
  <service_class>.java | head -20
```

**D. Timing and reliability configuration:**
```bash
# Timeout values
grep -rn "timeout\|Timeout\|readTimeout\|connectTimeout\|responseTimeout\|\
  @TimeLimiter\|TimeLimiterConfig\|timeoutDuration" \
  <java_path> --include="*.java" --include="*.yml" | head -15

# Retry configuration
grep -rn "maxAttempts\|retryOn\|@Retryable\|@Retry\|RetryConfig\|BackOffPolicy\|\
  exponentialBackoff\|waitDuration\|maxRetries" \
  <java_path> --include="*.java" --include="*.yml" | head -15

# Circuit breaker / fallback
grep -rn "@CircuitBreaker\|@Bulkhead\|fallbackMethod\|fallback\|onFallback\|\
  CircuitBreakerRegistry\|BulkheadRegistry" \
  <java_path> --include="*.java" | head -10
```

---

## Translation Rules: Technical → Business Language

Apply these translations when writing Section 13. Never let technical terms through.

### Field Names

| Technical | Business language |
|---|---|
| `customerId` | "Customer reference number" |
| `accountNumber` | "Account number" |
| `transactionId` | "Transaction reference" |
| `authToken` | "Authentication credentials" (or omit entirely — internal) |
| `correlationId` | (omit — internal plumbing) |
| `timestamp` | "Date and time of the request" |
| `amount` | "Payment amount" or "Transaction value" |
| `currencyCode` | "Currency" |
| `statusCode` / `resultCode` | "Outcome" or "Result" |
| `errorMessage` / `reason` | "Explanation of why it was declined" |

### Response Status Codes

| Code | Business name |
|---|---|
| 200 / 201 | "Request accepted and processed" |
| 400 | "Request rejected — information provided was invalid" |
| 401 | "Request rejected — authentication failed" |
| 403 | "Request rejected — this action is not permitted" |
| 404 | "Record not found in external system" |
| 409 | "Request rejected — duplicate or conflicting record" |
| 422 | "Request rejected — business rule violation" |
| 429 | "External system is busy — too many requests" |
| 500 / 503 | "External system is experiencing problems" |
| Timeout | "External system did not respond in time" |
| Connection refused | "External system is unavailable" |

### System Names

Name external systems as a business stakeholder would know them — not as URLs or service IDs:

| Technical | Business name |
|---|---|
| `paymentGatewayUrl` / `stripe.api.url` | "Payment Gateway" (or "Stripe" if named) |
| `kycServiceUrl` / `identity-check-service` | "Identity Verification Service" |
| `addressLookupUrl` / `postcode-api` | "Address Lookup Service" |
| `notificationServiceUrl` | "Notification Service" |
| `inventoryServiceUrl` | "Inventory System" |
| `orderManagementService` | "Order Management System" |
| `crdServiceUrl` / `client-reference-data` | "Client Reference Data System" |
| `emailServiceUrl` / `ses.amazonaws.com` | "Email Delivery Service" |

---

## Section 13.2 — Writing the Interaction Spec

### Good example — Payment processing interaction

```
EXT-001: Payment Gateway

Interaction 001.1 — Process a Payment

Triggered when: Customer confirms payment on the Checkout screen and clicks
  "Pay Now". This happens after the order has been validated and saved.

What this system sends:
  | Information                        | Purpose                                 | Required |
  |------------------------------------|------------------------------------------|---------|
  | Customer's full name               | Card holder verification                | Yes     |
  | Payment card details (tokenised)   | To charge the card                      | Yes     |
  | Payment amount in pence            | Exact amount to charge                  | Yes     |
  | Currency                           | GBP, USD, or EUR                        | Yes     |
  | Order reference number             | To link the payment to this order       | Yes     |
  | Customer's billing address         | Fraud prevention check                  | Yes     |

"The system sends the customer's tokenised card details, billing address,
and the order total to the Payment Gateway to request authorisation."

What comes back:

  Response A — "Payment Authorised"
  | Information              | Meaning                                        |
  |--------------------------|------------------------------------------------|
  | Authorisation code       | Unique reference for this approved transaction |
  | Masked card number       | Last 4 digits — shown on receipt               |
  | Authorised amount        | Confirms exact amount authorised               |

  Response B — "Payment Declined"
  | Information        | Meaning                                                  |
  |--------------------|----------------------------------------------------------|
  | Decline reason     | Why the payment was declined (insufficient funds, etc.)  |
  | Retry allowed      | Whether the customer can try a different card            |

  Response C — "Gateway Unavailable"
  No data returned. The Payment Gateway did not respond within 10 seconds.

What this system does with each response:

  | Response           | System Action                              | User Sees                           |
  |--------------------|---------------------------------------------|--------------------------------------|
  | Authorised         | Order status → PAID. Receipt generated.    | "Payment successful — Order [REF]"  |
  |                    | Fulfilment team notified.                  | Email receipt sent within 30 seconds|
  | Declined           | Order status → PAYMENT_FAILED.             | "Payment declined: [decline reason]"|
  |                    | Nothing charged. Order held for 24 hours.  | Prompted to retry with another card |
  | Unavailable        | Order status → PAYMENT_PENDING.            | "Payment is being verified —        |
  |                    | System retries every 5 minutes for 1 hour. |  you will receive confirmation soon"|
  |                    | If 1 hour passes: order cancelled,         |                                      |
  |                    | customer emailed to retry.                 |                                      |

Timing:
  The customer waits up to 10 seconds while the payment is processed.
  A "Processing payment..." indicator is shown during this time.
  If the gateway is unavailable: customer sees the "verifying" message
  immediately — they do not wait 10 seconds.

Retry behaviour:
  On gateway unavailability: system retries automatically every 5 minutes,
  up to 12 retries (1 hour total). Customer does not need to do anything.
  Each retry attempt is logged. Customer is emailed the final outcome.
```

---

## Common Mistakes to Avoid in Section 13

| ❌ Do not write | ✅ Write instead |
|---|---|
| "Sends a POST request to /v2/payments" | "Sends the payment details to the Payment Gateway" |
| "Receives a 200 OK with JSON body" | "Receives confirmation that the payment was authorised" |
| "Deserialises the PaymentResponse DTO" | "Reads the authorisation code from the response" |
| "Sets paymentStatus = COMPLETED in DB" | "Records the payment as completed" |
| "Throws PaymentDeclinedException" | "The system treats this as a declined payment" |
| "Calls notificationService.sendEmail()" | "Sends a confirmation email to the customer" |
| "Timeout after 30000ms" | "If the Payment Gateway does not respond within 30 seconds" |
| "3 retries with exponential backoff" | "The system tries again up to 3 times, waiting longer between each attempt" |
| "Circuit breaker opens after 5 failures" | "If the Payment Gateway repeatedly fails, the system stops trying immediately and shows the customer an error" |
