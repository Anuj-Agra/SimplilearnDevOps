# Scanning Guide

Complete scanning commands for Java backends, Angular frontends, shared libraries, and cross-service relationships.

---

## Java Backend Scanning (per service)

### Priority 1: Feature surface

```bash
grep -rn "@RestController\|@Controller" <service>/src --include="*.java"
grep -rn "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@PatchMapping\|@RequestMapping" <service>/src --include="*.java"
```

### Priority 2: Security and access control

```bash
grep -rn "ROLE_\|hasRole\|hasAuthority\|@PreAuthorize\|@Secured\|@RolesAllowed" <service>/src --include="*.java"
find <service>/src -name "*Security*" -o -name "*Auth*Config*" | grep -v test
```

### Priority 3: Data models

```bash
grep -rn "@Entity\|@Document\|@Table" <service>/src --include="*.java" | grep -v test
grep -rln "enum " <service>/src --include="*.java" | grep -v test
```

### Priority 4: Business rules

```bash
find <service>/src -path "*/service/*" -name "*.java" -not -name "*Test*" | sort
grep -rn "@Valid\|@NotNull\|@NotBlank\|@NotEmpty\|@Size\|@Min\|@Max\|@Pattern\|@Email\|@Future\|@Past\|@Positive" <service>/src --include="*.java" | grep -v test
```

### Priority 5: Error handling

```bash
grep -rn "@ControllerAdvice\|@ExceptionHandler" <service>/src --include="*.java"
find <service>/src -name "*Exception*" -name "*.java" | grep -v test
```

### Priority 6: Background processes

```bash
grep -rn "@Scheduled\|@Async" <service>/src --include="*.java" | grep -v test
grep -rn "@EventListener\|@TransactionalEventListener" <service>/src --include="*.java" | grep -v test
```

### Priority 7: Notifications

```bash
grep -rn "MailSender\|JavaMailSender\|EmailService\|EmailTemplate" <service>/src --include="*.java" | grep -v test
find <service>/src -name "*.ftl" -o -name "*.vm" -o -name "*email*.html" 2>/dev/null
```

---

## Angular Frontend Scanning (per app)

### Priority 1: Route structure

```bash
find <app>/src -name "*routing*" -o -name "*routes*" | grep -v node_modules
grep -rn "path:\|canActivate\|canDeactivate\|loadChildren\|component:" <app>/src --include="*.ts" | grep -iv "test\|spec\|mock"
```

### Priority 2: Screen components

```bash
find <app>/src -name "*.component.html" | sort
find <app>/src -path "*/pages/*" -o -path "*/views/*" -o -path "*/screens/*" | grep "\.component\." | sort
```

### Priority 3: Forms and inputs

```bash
grep -rn "FormGroup\|FormControl\|FormBuilder\|Validators\." <app>/src --include="*.ts" | grep -iv "test\|spec"
grep -rn "ngModel\|formControlName\|required\|minlength\|maxlength\|pattern" <app>/src --include="*.html"
```

### Priority 4: User interactions

```bash
grep -rn "(click)\|routerLink\|mat-button\|submit" <app>/src --include="*.html" | head -100
grep -rn "HttpClient\|this\.http\." <app>/src --include="*.ts" | grep -v spec
```

### Priority 5: Error messages

```bash
grep -rn "toast\|snackbar\|MatSnackBar\|error.*message\|success.*message" <app>/src --include="*.ts" --include="*.html" | grep -iv test | head -50
```

### Priority 6: i18n

```bash
find <app>/src -name "*.json" \( -path "*/i18n/*" -o -path "*/locale/*" -o -path "*/translations/*" \)
```

### Priority 7: Guards

```bash
find <app>/src -name "*guard*" -name "*.ts" -not -name "*.spec.ts" | sort
```

---

## Shared Library Scanning

```bash
find <lib>/src -name "*.java" \( -path "*/model/*" -o -path "*/dto/*" \) | sort
grep -rln "enum " <lib>/src --include="*.java"
grep -rn "public static final\|public enum" <lib>/src --include="*.java" | grep -v test | head -30
```

---

## Cross-Service Relationships

```bash
grep -rn "@FeignClient" <root> --include="*.java" | grep -v test
grep -rn "RestTemplate\|WebClient" <root> --include="*.java" | grep -v test
grep -rn "@KafkaListener\|@RabbitListener\|@JmsListener\|KafkaTemplate\|RabbitTemplate" <root> --include="*.java" | grep -v test
```

---

## Mono-Repo Topology Detection

```bash
# Directory structure (excluding noise)
find <root> -maxdepth 3 -type d -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/target/*" -not -path "*/build/*" -not -path "*/dist/*" | sort | head -100

# All build entry points
find <root> -maxdepth 3 -name "pom.xml" -o -name "build.gradle" -o -name "build.gradle.kts" | sort
find <root> -maxdepth 3 -name "angular.json" | sort
find <root> -maxdepth 3 -name "package.json" -not -path "*/node_modules/*" | sort
```

### Classification rules

| Type | Detection | Role in spec |
|---|---|---|
| Backend Service | Build file + `@SpringBootApplication` + `@RestController` | Features, business rules, data |
| Frontend App | `angular.json` + `src/app/` + routing modules | Screens, forms, interactions |
| API Gateway | Route configs, filters, no business logic | Cross-cutting concerns |
| Shared Library | Build file, no `main()`, no controllers | Shared rules and models |
| Infrastructure | Docker, K8s, CI/CD | Skip entirely |

---

## Module Boundary Detection

### Grouping rules

1. One service = one module (default)
2. Multiple services in same domain = merge into one module
3. One service with distinct feature areas = split into sub-modules
4. Frontend pages align with backend modules based on which service they call
5. Shared libraries are not modules — attribute their features to consuming modules

### Sub-module signals

- Separate package namespaces within a service
- Separate Angular feature modules under one app
- Separate route groups/prefixes
- Separate entity sets that don't reference each other
