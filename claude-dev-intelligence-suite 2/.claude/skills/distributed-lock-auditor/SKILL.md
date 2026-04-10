---
name: distributed-lock-auditor
description: >
  Find operations that are safe on a single instance but break under horizontal
  scaling with parallel connections: scheduled jobs running on every instance,
  counter increments, inventory reservation, idempotency enforcement, and
  singleton-assumption business logic. Use when asked: 'distributed lock',
  'horizontal scaling issues', 'multiple instances', 'scheduled job on every
  instance', 'race condition at scale', 'idempotency at scale', 'Redisson lock',
  'distributed coordination'. Produces Redisson/Redis distributed lock patterns.
---
# Distributed Lock Auditor

Find single-instance assumptions that break under horizontal scaling.

## Step 1 — Scheduled Jobs (CRITICAL — runs N times on N instances)
```bash
grep -rn "@Scheduled\|@EnableScheduling\|ScheduledExecutorService\|cron\b" \
  <java_path> --include="*.java" | grep -v "//\|test\|Test"

# Check if leader election / distributed lock exists for each
grep -rn "@SchedulerLock\|ShedLock\|net.javacrumbs.shedlock\|LeaderElection\|\
  RedissonLock\|getLock\|tryLock\|@ConditionalOnSingleCandidate" \
  <java_path> --include="*.java" | head -20
```

## Step 2 — Counter / Sequence Operations
```bash
# In-memory counters (break under multi-instance)
grep -rn "AtomicInteger\|AtomicLong\|private static.*int\|private static.*long\|\
  incrementAndGet\|getAndIncrement" \
  <java_path> --include="*.java" | \
  grep -v "final\|test\|Test\|log\b" | head -20

# Sequence generation that should be DB-level
grep -rn "sequenceNumber\|orderNumber\|referenceNumber\|nextId\|nextSequence" \
  <java_path> --include="*.java" | \
  grep -v "@Id\|@SequenceGenerator\|@GeneratedValue\|database" | head -20
```

## Step 3 — Inventory / Reservation Logic
```bash
# Check-then-act patterns (read then write without lock — race condition)
grep -rn "findById\|findByCode\|getStock\|getInventory" \
  <java_path> --include="*.java" -A5 | \
  grep -B3 "\.save\(\|\.update\(\|setQuantity\|setStock" | head -30

# Optimistic locking (good — detect presence)
grep -rn "@Version\|@OptimisticLocking\|ObjectOptimisticLockingFailureException\|\
  OptimisticLockException" <java_path> --include="*.java" | head -10
```

## Step 4 — Output + Generated Patterns

```
DISTRIBUTED LOCK AUDIT: [System]

CRITICAL — MULTI-INSTANCE UNSAFE:

  DL-001: @Scheduled job [ClassName.methodName] runs on EVERY instance
    Risk: With 3 instances, job runs 3 times — duplicate processing
    Fix: Add ShedLock annotation (generated below)

  DL-002: Inventory reservation in [ClassName] has check-then-act race
    Risk: Two concurrent requests can both see stock > 0 and both reserve
    Fix: Use optimistic locking @Version OR distributed lock (generated below)

  DL-003: Order reference number generated in-memory
    Risk: Two instances may generate same reference number simultaneously
    Fix: Use DB sequence or Redis INCR (atomic)

GENERATED PATTERNS:

// ShedLock for @Scheduled jobs
@Scheduled(cron = "0 0 2 * * *")
@SchedulerLock(name = "[job-name]", lockAtMostFor = "PT10M", lockAtLeastFor = "PT5M")
public void scheduledJob() { ... }

// Redisson distributed lock for critical section
@Autowired
private RedissonClient redisson;

public void reserveInventory(String productId, int quantity) {
  RLock lock = redisson.getLock("inventory-lock:" + productId);
  try {
    if (lock.tryLock(5, 10, TimeUnit.SECONDS)) {
      // Safe: only one instance at a time reaches here
      doReserveInventory(productId, quantity);
    } else {
      throw new BusinessException("Could not acquire lock — try again");
    }
  } catch (InterruptedException e) {
    Thread.currentThread().interrupt();
    throw new BusinessException("Interrupted while waiting for lock");
  } finally {
    if (lock.isHeldByCurrentThread()) lock.unlock();
  }
}
```
