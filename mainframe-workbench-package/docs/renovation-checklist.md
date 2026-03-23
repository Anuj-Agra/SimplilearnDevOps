# Java + Angular Renovation Checklist

Use this checklist to track progress across the full mainframe → Java/Angular migration. Check off items as they are completed.

---

## Phase 0 — Discovery & Inventory

- [ ] All Natural libraries identified and source extracted
- [ ] All COBOL programs identified and source extracted
- [ ] All Adabas file numbers listed with file names and record counts
- [ ] All reference tables catalogued (name, key field, entry count)
- [ ] CICS transaction IDs mapped to entry programs
- [ ] 3270 screen screenshots captured for all key screens
- [ ] Existing documentation (PDFs, Word docs, Excel specs) collected
- [ ] Workbench Code Analysis agent run — output reviewed
- [ ] Workbench Obsolescence agent run — obsolete items agreed with business

---

## Phase 1 — Requirements

- [ ] BRD reviewed and signed off by business sponsor
- [ ] FRD reviewed and signed off by functional lead
- [ ] All business rules extracted and numbered (BR-001...)
- [ ] All functional requirements numbered (FR-001...)
- [ ] Non-functional requirements agreed (performance SLAs, availability, security)
- [ ] Data retention and archival requirements agreed
- [ ] Audit trail requirements agreed
- [ ] Regulatory / compliance requirements identified

---

## Phase 2 — Architecture

- [ ] Target database vendor selected (PostgreSQL / Oracle / DB2)
- [ ] Java version agreed (recommend: Java 21 LTS)
- [ ] Spring Boot version agreed (recommend: 3.x)
- [ ] Angular version agreed (recommend: Angular 17+)
- [ ] Build tool agreed (Maven / Gradle)
- [ ] Maven/Gradle module structure defined
- [ ] Angular workspace structure defined (apps vs libs)
- [ ] API design agreed (REST conventions, versioning strategy)
- [ ] Authentication / authorisation approach agreed (OAuth2 / LDAP / SAML)
- [ ] Mermaid diagrams reviewed and validated by technical lead

---

## Phase 3 — Backend (Java Spring Boot)

### Per Adabas file:
- [ ] JPA @Entity created with all fields mapped from DDM
- [ ] AttributeConverters created for Adabas date/time formats
- [ ] MU/PE fields handled (@ElementCollection or @OneToMany)
- [ ] @Repository interface created (Spring Data JPA)
- [ ] DTO record created with Jakarta Bean Validation annotations
- [ ] MapStruct mapper created (Entity ↔ DTO)
- [ ] Liquibase migration script written for table creation
- [ ] Indexes defined (matching Adabas descriptors)

### Per Natural program / business function:
- [ ] @Service class created with business logic
- [ ] All Natural validations reimplemented (annotations or guard clauses)
- [ ] All reference table lookups replaced (@Cacheable service or enum)
- [ ] Exception handling implemented (custom exception classes)
- [ ] @RestController created with endpoints
- [ ] OpenAPI/Swagger annotations added
- [ ] Unit tests written (target: 80%+ coverage on service layer)
- [ ] Integration tests written (Spring Boot Test + Testcontainers)

### Cross-cutting:
- [ ] Global @ExceptionHandler (replaces Natural error handling)
- [ ] Audit logging (@EntityListeners or AOP)
- [ ] @Transactional boundaries match original Adabas backout unit
- [ ] Caching configured (@EnableCaching + @Cacheable on reference lookups)
- [ ] Application.yml / profiles configured (dev / test / prod)

---

## Phase 4 — Frontend (Angular)

### Per CICS screen / BMS map:
- [ ] Angular component created
- [ ] Reactive form created (FormGroup + FormControl)
- [ ] All field validators implemented (mirror original BMS field attributes)
- [ ] Business rule validations implemented (cross-field validators)
- [ ] PF key navigation replaced with router navigation
- [ ] API service calls implemented (replace CALLNAT / Adabas READ)
- [ ] Loading / error / success states handled
- [ ] Accessibility attributes added (labels, aria)

### Cross-cutting:
- [ ] Angular routing module configured
- [ ] HTTP interceptor for auth token
- [ ] HTTP interceptor for error handling (replace Natural error handling)
- [ ] Shared validators module (mirror BR catalogue)
- [ ] Shared components (table, form field wrappers)
- [ ] Environment files configured (dev / test / prod API URLs)
- [ ] Unit tests written (Jasmine / Jest)
- [ ] E2E tests written (Cypress / Playwright) for critical flows

---

## Phase 5 — Data Migration

- [ ] Adabas extract scripts written and tested per FNR
- [ ] Staging database created
- [ ] Transformation rules documented per field (especially date formats, code translations)
- [ ] MU/PE field denormalisation scripts written and tested
- [ ] Reference table data migrated to target tables
- [ ] Record count reconciliation report produced
- [ ] Key field checksum reconciliation report produced
- [ ] Business-critical data validated by business owner
- [ ] Migration rehearsal run completed (full dry-run)

---

## Phase 6 — Testing

- [ ] Unit test coverage report — backend ≥ 80%
- [ ] Unit test coverage report — frontend ≥ 70%
- [ ] Integration test suite passing in CI
- [ ] Golden data set captured from mainframe
- [ ] Parallel run executed — mainframe vs Java for all CICS transactions
- [ ] Discrepancies investigated and resolved
- [ ] Regression sign-off document produced
- [ ] Performance testing executed — response times vs mainframe baseline
- [ ] Security scan executed (OWASP top 10)
- [ ] UAT completed by business team
- [ ] UAT sign-off obtained

---

## Phase 7 — Cutover

- [ ] Cutover runbook written and reviewed
- [ ] Rollback plan written and tested
- [ ] Data migration scheduled and communicated
- [ ] Mainframe freeze window agreed
- [ ] Go-live date communicated to all stakeholders
- [ ] Support team briefed
- [ ] Monitoring and alerting configured (replace mainframe SMF records)
- [ ] Post-go-live hypercare period defined
- [ ] Mainframe decommission date agreed (after stability confirmed)

---

## Obsolescence — Confirmed Removals

Track items confirmed as obsolete and not to be migrated:

| Item | Type | Original Name | Decision | Agreed By | Date |
|------|------|--------------|----------|-----------|------|
| | Field | | Remove | | |
| | Program | | Delete | | |
| | Validation | | Drop (framework handles) | | |
| | Ref table | | Convert to enum | | |
