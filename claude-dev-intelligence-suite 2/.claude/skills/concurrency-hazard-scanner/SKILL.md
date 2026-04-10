---
name: concurrency-hazard-scanner
description: >
  Find race conditions, thread-safety violations, and shared mutable state in Java
  Spring applications before they cause production incidents under parallel load.
  Use when asked: 'concurrency issues', 'thread safety', 'race conditions', 'shared
  state', 'parallel requests', 'concurrent access bugs', 'thread-safe review',
  'synchronisation issues', 'singleton state', '@Service mutable fields'. The most
  dangerous class of bug in a parallel-connection API — only manifests under load.
---
# Concurrency Hazard Scanner

Find thread-safety violations that only appear under parallel connection load.

## Scan 1 — Mutable State in Spring Singletons (CRITICAL)
Spring beans are singletons by default. Any mutable instance field is shared
across ALL concurrent requests.

```bash
# Find @Service/@Component/@Repository with non-final instance fields
grep -rn "@Service\|@Component\|@Repository\|@Controller\|@RestController" \
  <java_path> --include="*.java" -l | while read f; do
  # Check for non-final, non-static instance fields
  grep -n "private [^(static|final)].*[A-Za-z]" "$f" | \
    grep -v "final\|static\|Logger\|log\b\|//\|@Autowired\|@Value\|@Inject" | \
    head -5
done
```

## Scan 2 — Unsafe Collections Used as Shared State
```bash
# HashMap/ArrayList/HashSet where ConcurrentHashMap/CopyOnWriteArrayList needed
grep -rn "= new HashMap<\|= new ArrayList<\|= new HashSet<" \
  <java_path> --include="*.java" | \
  grep -v "final.*=\|local\|method\|void \|return " | head -30
```

## Scan 3 — Static Mutable State
```bash
# Static fields that are not final (shared across all instances AND all threads)
grep -rn "private static [^f].*[^;]\|protected static [^f]" \
  <java_path> --include="*.java" | \
  grep -v "final\|Logger\|log\b\|INSTANCE\|//\|test\|Test" | head -30
```

## Scan 4 — ThreadLocal Leaks in Thread Pools
```bash
# ThreadLocal without remove() — leaks between requests in pooled threads
grep -rn "ThreadLocal\|InheritableThreadLocal" \
  <java_path> --include="*.java" -l | \
  xargs grep -L "\.remove()\|finally.*remove\|try.*remove" 2>/dev/null | head -20
```

## Scan 5 — Unsynchronised Counter Patterns
```bash
# int/long fields used as counters without AtomicInteger/AtomicLong
grep -rn "private int \|private long \|private volatile\b" \
  <java_path> --include="*.java" | \
  grep -v "final\|static final\|//\|test" | head -20

# ++ operator on shared field (non-atomic read-modify-write)
grep -rn "\+\+\|--\b" <java_path> --include="*.java" | \
  grep -v "for.*int\|i++\|j++\|k++\|index\|//\|test" | head -20
```

## Scan 6 — @Async Without Proper Context Propagation
```bash
grep -rn "@Async" <java_path> --include="*.java" -A10 | \
  grep -B5 "SecurityContextHolder\|MDC\.\|RequestContextHolder" | head -30
```

## Scan 7 — Double-Checked Locking Antipattern
```bash
grep -rn "if.*null.*{" <java_path> --include="*.java" -A5 | \
  grep -B3 "synchronized\|if.*null" | head -20
```

## Output: Concurrency Hazard Report

```
CONCURRENCY HAZARD REPORT: [System]

CRITICAL — Race Conditions:
  CC-001: Mutable field '[fieldName]' in @Service [ClassName]
    Type: Shared mutable state in singleton
    Risk: Concurrent requests corrupt each other's data
    Fix: Make field @RequestScope, or use local variables, or use AtomicXxx

  CC-002: HashMap used as cache in [ClassName]
    Risk: HashMap is not thread-safe — ConcurrentModificationException under load
    Fix: Replace with ConcurrentHashMap or Caffeine cache

HIGH — ThreadLocal Leaks:
  CC-003: ThreadLocal in [Class] never calls .remove()
    Risk: Previous request's data leaks into next request on same thread
    Fix: Add try/finally block with threadLocal.remove()

MEDIUM — Unsafe Counters:
  CC-004: Non-atomic counter in [Class]
    Fix: Replace int with AtomicInteger

SAFE PATTERNS DETECTED (for reference):
  ✅ [ClassName] uses ConcurrentHashMap correctly
  ✅ [ClassName] fields are all final
```
