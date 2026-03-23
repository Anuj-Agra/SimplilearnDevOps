# Adabas DDM → JPA Entity Field Mapping Template

Use this template when reviewing the Java + Angular agent output or manually creating JPA entities from your Adabas DDMs.

---

## Adabas Data Type → Java Type Mapping

| Adabas Format | Adabas Description | Java Type | JPA Column | Notes |
|--------------|-------------------|-----------|------------|-------|
| `A` | Alphanumeric | `String` | `@Column(length=N)` | |
| `N` | Numeric unpacked | `BigDecimal` or `Long` | `@Column(precision=P, scale=S)` | Use BigDecimal for monetary |
| `P` | Packed decimal | `BigDecimal` | `@Column(precision=P, scale=S)` | |
| `B` | Binary | `byte[]` | `@Lob` | |
| `F` | Floating point | `Double` | `@Column` | |
| `G` | Date (YYYYMMDD) | `LocalDate` | `@Column` + `@Convert` | Use AttributeConverter |
| `T` | Time (HHMMSS) | `LocalTime` | `@Column` + `@Convert` | Use AttributeConverter |
| `U` | Unpacked numeric | `Long` | `@Column` | |

---

## MU / PE Field Handling

Adabas Multiple Value (MU) and Periodic Group (PE) fields have no direct relational equivalent. Use one of these strategies:

### Option 1 — @ElementCollection (simple MU fields)
```java
// Original Adabas: MU field PHONE-NR (up to 10 occurrences)
@ElementCollection
@CollectionTable(name = "customer_phones", joinColumns = @JoinColumn(name = "customer_id"))
@Column(name = "phone_number")
private List<String> phoneNumbers;
```

### Option 2 — @OneToMany child entity (PE groups)
```java
// Original Adabas: PE group ORDER-LINE (up to 50 occurrences)
@OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
private List<OrderLineEntity> orderLines;
```

### Option 3 — JSON column (variable-length, infrequently queried)
```java
@Column(columnDefinition = "jsonb")
@Convert(converter = JsonListConverter.class)
private List<String> tags; // Only if database supports JSON (PostgreSQL)
```

---

## Sample DDM → Entity Mapping

### Adabas DDM (Natural format)
```
1 CUSTOMER-ID            A 10  /* Customer identifier
1 CUSTOMER-NAME          A 40  /* Full name
1 CUSTOMER-TYPE          A 2   /* Ref table: CUST-TYPE
1 DATE-OF-BIRTH          G 8   /* Format YYYYMMDD
1 CREDIT-LIMIT           P 9.2 /* Monetary value
1 STATUS                 A 1   /* A=Active I=Inactive S=Suspended
2 PHONE-NUMBERS               /* MU field, max 5
  3 PHONE-NR             A 15
```

### Generated JPA Entity
```java
@Entity
@Table(name = "customers")
public class CustomerEntity {

    @Id
    @Column(name = "customer_id", length = 10, nullable = false)
    private String customerId; // Adabas: CUSTOMER-ID A10

    @Column(name = "customer_name", length = 40)
    @NotBlank
    private String customerName; // Adabas: CUSTOMER-NAME A40

    @Column(name = "customer_type", length = 2)
    @Pattern(regexp = "[A-Z]{2}", message = "Must be 2 uppercase letters")
    private String customerType; // Adabas: CUSTOMER-TYPE A2 — ref table CUST-TYPE

    @Column(name = "date_of_birth")
    private LocalDate dateOfBirth; // Adabas: DATE-OF-BIRTH G8 YYYYMMDD

    @Column(name = "credit_limit", precision = 9, scale = 2)
    @DecimalMin("0.00")
    @DecimalMax("9999999.99")
    private BigDecimal creditLimit; // Adabas: CREDIT-LIMIT P9.2

    @Column(name = "status", length = 1)
    @Pattern(regexp = "[AIS]", message = "Must be A, I, or S")
    private String status; // Adabas: STATUS A1 — A=Active I=Inactive S=Suspended

    @ElementCollection(fetch = FetchType.LAZY)
    @CollectionTable(name = "customer_phones", joinColumns = @JoinColumn(name = "customer_id"))
    @Column(name = "phone_nr", length = 15)
    @Size(max = 5, message = "Maximum 5 phone numbers") // Adabas MU max occurrences
    private List<String> phoneNumbers; // Adabas: PHONE-NR MU A15
}
```

---

## Reference Table → Spring Configuration Mapping

### Adabas reference table lookup (Natural)
```natural
FIND CUST-TYPE-REF WITH CT-CODE = #CUSTOMER-TYPE
  IF NO RECORDS FOUND
    MOVE 'INVALID CUSTOMER TYPE' TO #ERROR-MSG
  END-NOREC
END-FIND
```

### Java equivalent — Option A: Enum (closed set, rarely changes)
```java
public enum CustomerType {
    AC("AC", "Account Customer"),
    PR("PR", "Prospect"),
    IN("IN", "Internal");

    private final String code;
    private final String description;
    // constructor, getters
}
```

### Java equivalent — Option B: @Cacheable service (larger table, may change)
```java
@Service
public class CustomerTypeService {

    private final CustomerTypeRepository repo;

    @Cacheable("customerTypes")
    public Optional<CustomerTypeEntity> findByCode(String code) {
        return repo.findByCode(code);
    }

    @CacheEvict(value = "customerTypes", allEntries = true)
    public void refreshCache() {}
}
```

### Validation (replaces Natural FIND ... IF NO RECORDS FOUND)
```java
// Jakarta Validator
public class CustomerTypeValidator implements ConstraintValidator<ValidCustomerType, String> {
    @Autowired private CustomerTypeService svc;

    @Override
    public boolean isValid(String code, ConstraintValidatorContext ctx) {
        return svc.findByCode(code).isPresent();
    }
}
```

---

## Date Conversion — Adabas G8 → Java LocalDate

```java
@Converter(autoApply = false)
public class AdabasDateConverter implements AttributeConverter<LocalDate, String> {

    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyyMMdd");

    @Override
    public String convertToDatabaseColumn(LocalDate date) {
        return date == null ? "00000000" : date.format(FMT);
    }

    @Override
    public LocalDate convertToEntityAttribute(String s) {
        if (s == null || s.equals("00000000") || s.isBlank()) return null;
        return LocalDate.parse(s, FMT);
    }
}
```
