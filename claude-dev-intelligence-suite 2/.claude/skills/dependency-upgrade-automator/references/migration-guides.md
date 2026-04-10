# Known Migration Guides

## Spring Boot 2.x → 3.x

### Mandatory Changes
1. **Java 17 minimum** — update `java.version` in pom.xml, Dockerfile, CI pipeline
2. **javax → jakarta** — all javax.* imports rename to jakarta.*
   ```bash
   find src -name "*.java" | xargs sed -i \
     -e 's/javax\.persistence\./jakarta\.persistence\./g' \
     -e 's/javax\.validation\./jakarta\.validation\./g' \
     -e 's/javax\.servlet\./jakarta\.servlet\./g' \
     -e 's/javax\.annotation\./jakarta\.annotation\./g' \
     -e 's/javax\.transaction\./jakarta\.transaction\./g'
   ```
3. **Spring Security** — `WebSecurityConfigurerAdapter` removed
   ```java
   // OLD (Spring Boot 2)
   @Configuration
   public class SecurityConfig extends WebSecurityConfigurerAdapter {
     @Override protected void configure(HttpSecurity http) throws Exception { ... }
   }
   // NEW (Spring Boot 3)
   @Configuration
   public class SecurityConfig {
     @Bean public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
       // same config body, return http.build();
     }
   }
   ```
4. **Actuator** — `management.endpoints.web.base-path` default changed to `/actuator`
5. **Spring Data** — `CrudRepository.findById` return type unchanged but some query methods renamed
6. **Hibernate 6** — `@GeneratedValue(strategy=AUTO)` behaviour changed for sequences

---

## Spring Boot 3.0 → 3.2+

1. **Virtual threads (Project Loom)** — enable with `spring.threads.virtual.enabled=true`
2. **RestClient** — new synchronous HTTP client replacing RestTemplate (optional)
3. **@MockitoBean / @MockitoSpyBean** — new annotations in Spring Test 6.2

---

## Angular 12 → 14

1. **Strict mode defaults** — `ng new` generates strict TypeScript config; existing code may fail
2. **InjectionToken** — typed tokens now required
3. **Angular CDK** — some overlay APIs changed

## Angular 14 → 15

1. **Standalone components GA** — no breaking change but migration recommended
2. **NgOptimizedImage** — new image directive, replaces `<img>` for performance

## Angular 15 → 16

1. **Signals preview** — no breaking changes
2. **Required inputs** — `@Input({ required: true })` new API
3. **DestroyRef** — replaces `ngOnDestroy` pattern in some cases

## Angular 16 → 17

1. **New control flow** — `@if`, `@for`, `@switch` replace `*ngIf`, `*ngFor`, `*ngSwitch`
   ```bash
   # Automated migration
   npx ng generate @angular/core:control-flow
   ```
2. **@defer blocks** — new lazy loading syntax
3. **Vite + esbuild** — new default builder (significant build speed improvement)
   Update `angular.json`: `"builder": "@angular-devkit/build-angular:browser-esbuild"`

---

## RxJS 6 → 7

1. **Observable.pipe** — unchanged
2. **Imports** — operators moved; `import { map } from 'rxjs/operators'` → `import { map } from 'rxjs'`
3. **ReplaySubject** — `scheduler` parameter removed
4. **toPromise()** deprecated — replace with `firstValueFrom()` or `lastValueFrom()`

```bash
# Find deprecated toPromise() calls
grep -rn "\.toPromise()" src --include="*.ts"
# Replace with: firstValueFrom(observable$)
```

---

## Hibernate 5 → 6

1. **HQL syntax** — `select distinct` behaviour changed
2. **@GeneratedValue** — SEQUENCE strategy now preferred over AUTO
3. **UUID** — native UUID type support improved; `@Type(type="uuid-char")` may be removed
4. **criteria API** — some deprecated methods removed

---

## Jackson 2.13 → 2.15+

1. **MapperFeature** — some features moved/renamed
2. **@JsonMerge** — behaviour standardised
3. **Large payload protection** — `StreamReadConstraints` added (may reject very large JSON)
   ```yaml
   # application.yml — if you have large payloads
   spring.jackson.mapper.stream-read-constraints.max-string-length: 50000000
   ```

---

## Lombok 1.18.x upgrades

Lombok upgrades are generally safe but:
1. Verify `lombok.version` in pom.xml matches Spring Boot BOM
2. Check `annotationProcessorPaths` in maven-compiler-plugin includes lombok

---

## TypeScript 4.x → 5.x

1. **Decorators** — new decorator standard (Stage 3); Angular handles this via `useDefineForClassFields`
2. **const enums** — cross-file usage restrictions tightened
3. **Bundler module resolution** — update `tsconfig.json` `moduleResolution: "bundler"` for Angular 17+
