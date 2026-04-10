---
name: cache-strategy-generator
description: >
  Generate complete caching strategies for each cacheable data type in the system:
  what to cache, appropriate TTL, eviction strategy, local vs distributed cache,
  and cache warming approach. Use when asked: 'caching strategy', 'what to cache',
  'cache design', 'Redis cache', 'Caffeine cache', 'TTL configuration', 'cache
  warming', 'cache eviction', 'thundering herd cache', 'cache miss storm',
  'cache invalidation', 'add caching'. Parallel connections amplify cache misses.
---
# Cache Strategy Generator

Design a complete caching strategy for every cacheable data pattern in the system.

## Step 1 — Find Cacheable Data Patterns
```bash
# Existing caches
grep -rn "@Cacheable\|@CacheEvict\|@CachePut\|CacheManager\|@EnableCaching" \
  <java_path> --include="*.java" | head -30

# High-read methods that should be cached (currently uncached)
grep -rn "findByCode\|findByType\|getConfig\|getReferenceData\|getLookup\|findAll\b" \
  <java_path> --include="*.java" -l | \
  xargs grep -L "@Cacheable" 2>/dev/null | head -20

# Methods reading data that rarely changes
grep -rn "findAll\b\|findByStatus.*ACTIVE\|findByEnabled.*true\|getAll" \
  <java_path> --include="*.java" | grep -v "test\|Test" | head -30
```

## Step 2 — Classify Each Data Type

| Data type | Change frequency | Read frequency | Cache type | TTL |
|---|---|---|---|---|
| User session data | Per request | Every request | Local (ThreadLocal) | Request lifetime |
| Auth tokens / permissions | On role change | Every request | Distributed (Redis) | 5 minutes |
| Reference data (countries, currencies) | Monthly | Every request | Local (Caffeine) | 1 hour |
| Product catalogue | Daily | High | Distributed (Redis) | 15 minutes |
| User profile | On update | High | Distributed (Redis) | 5 minutes |
| Search results | Continuous | Medium | Distributed (Redis) | 30 seconds |
| Computed reports | On data change | Low | Distributed (Redis) | 10 minutes |

## Step 3 — Thundering Herd Protection

For each high-traffic cache, add:
```java
// Probabilistic early expiration — prevents all threads missing cache simultaneously
// Use Caffeine's refreshAfterWrite (not expireAfterWrite) for hot keys
@Bean
public CacheManager cacheManager() {
  CaffeineCacheManager manager = new CaffeineCacheManager();
  manager.setCaffeine(Caffeine.newBuilder()
    .maximumSize(1000)
    .expireAfterWrite(60, TimeUnit.MINUTES)
    .refreshAfterWrite(45, TimeUnit.MINUTES)  // Refresh before expiry
    .recordStats());
  return manager;
}
```

## Step 4 — Output: Complete Cache Configuration

```
CACHE STRATEGY: [System]

RECOMMENDED CACHE LAYERS:
  Layer 1 — In-process (Caffeine): static reference data, config values
    Max size: 10,000 entries | Eviction: LRU
    Data: countries, currencies, product types, system config

  Layer 2 — Distributed (Redis): user data, frequently-read entities
    Max memory: 2GB | Eviction: allkeys-lru
    Data: user profiles, permissions, product catalogue

  Layer 3 — No cache: write-heavy data, financial transactions, audit logs

GENERATED SPRING CONFIG (application.yml):
  spring.cache.type: caffeine
  spring.cache.caffeine.spec: maximumSize=5000,expireAfterWrite=3600s

  spring.data.redis.host: ${REDIS_HOST:localhost}
  spring.data.redis.port: 6379
  spring.data.redis.timeout: 2s
  spring.data.redis.lettuce.pool.max-active: 16

CACHE WARMING STRATEGY:
  On application startup:
    1. Load all [reference data] into Caffeine cache
    2. Pre-warm Redis with top-100 most-accessed [products] from DB
    Estimated warm-up time: [N] seconds
    Implement via ApplicationRunner bean

CACHE INVALIDATION RULES:
  When [Entity] is updated → evict cache key '[entity]::[id]'
  When [Config] changes → evict all '[config]::*' keys
  Pattern: @CacheEvict(value="products", key="#product.id")
```
