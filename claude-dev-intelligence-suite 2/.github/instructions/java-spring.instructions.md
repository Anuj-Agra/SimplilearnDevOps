---
applyTo: "**/*.java,**/pom.xml,**/application.yml,**/application.properties"
description: "Automatically triggered when working with Java/Spring files or when user asks about Spring beans, transactions, Hibernate, concurrency, or connection pools"
---

# Java & Spring Skills

When working with Java files or user mentions Spring-specific concerns:

- **concurrency-hazard-scanner** (`.claude/skills/concurrency-hazard-scanner/SKILL.md`)
  Triggers: "race conditions", "thread safety", "shared state", "@Service mutable",
  "static field", "singleton state", "ConcurrentHashMap"

- **spring-transaction-analyser** (`.claude/skills/spring-transaction-analyser/SKILL.md`)
  Triggers: "@Transactional", "transaction not working", "rollback not happening",
  "self-invocation", "private method transaction", "transaction scope"

- **spring-bean-lifecycle-auditor** (`.claude/skills/spring-bean-lifecycle-auditor/SKILL.md`)
  Triggers: "bean not injected", "scope mismatch", "request scoped in singleton",
  "prototype bean", "circular bean dependency"

- **hibernate-n1-deep-scanner** (`.claude/skills/hibernate-n1-deep-scanner/SKILL.md`)
  Triggers: "N+1", "lazy loading", "hibernate performance", "too many queries",
  "FetchType", "EntityGraph", "JOIN FETCH"

- **connection-pool-analyser** (`.claude/skills/connection-pool-analyser/SKILL.md`)
  Triggers: "connection pool", "HikariCP", "pool exhausted", "too many connections",
  "pool size", "database connections"

- **reactive-migration-advisor** (`.claude/skills/reactive-migration-advisor/SKILL.md`)
  Triggers: "WebFlux", "reactive", "non-blocking", "Project Reactor", "Mono", "Flux",
  "migrate to reactive", "handle more connections"

Load the relevant SKILL.md before generating any Java code or analysis.
