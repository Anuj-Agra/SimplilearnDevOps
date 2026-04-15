---
name: code-renovator
description: "Rewrite old Java code (classes, methods, or groups of related files) to match a new codebase's patterns and conventions. Use this skill whenever a user wants to migrate, renovate, or rewrite legacy code to follow a new architecture, framework, or coding style. Triggers include: 'rewrite this class', 'migrate this code', 'renovate this to match', 'convert to new pattern', 'refactor to new style', 'port this code', 'transform this to match our new codebase', 'code migration', 'code renovation', 'legacy rewrite', or any request that involves taking old code and producing new code that follows a provided example or style guide. Also triggers when the user provides two code samples and asks to make one look like the other, or when they mention mainframe modernization rewrite, Natural-to-Java conversion, or similar migration scenarios."
---

# Code Renovator

Rewrite legacy code to strictly follow a target codebase's patterns, conventions, and architectural style. The output must read as if it were written natively by the team that built the new codebase — not as a "translated" version of the old code.

## Core Principle — Pattern Fidelity

> The rewritten code must be **indistinguishable in style** from the example pattern code. If a reviewer looked at the output alongside the new codebase, they should not be able to tell which was the original and which was the rewrite.

This means: naming conventions, package structure, annotation usage, error handling style, logging patterns, dependency injection approach, DTO/entity patterns, test patterns, comment style — everything must match the example.

---

## Step 0 — Gather Inputs

Before writing a single line, collect and confirm these inputs with the user:

### Required Inputs

1. **Old code** — The legacy code to rewrite. Can be:
   - A single method or function
   - A full class file
   - A small group of related classes (e.g., controller + service + repository)
   - Uploaded files or pasted code

2. **Target pattern** — The example(s) showing how the new codebase looks. Can be:
   - One or more example class files from the new codebase (preferred — most information-rich)
   - A written style guide or conventions document
   - Both code examples AND written rules
   - A reference to pattern files already provided earlier in the conversation

### Optional Inputs (ask if not obvious)

3. **Mapping hints** — Any explicit instructions the user has about how old constructs should map to new ones. Examples:
   - "Our old `DaoManager` calls should become Spring `@Repository` classes"
   - "Replace all `System.out.println` with SLF4J `log.info`"
   - "The old `NATURAL FIND` becomes a JPA `findBy...` query"

4. **Scope boundaries** — What to include/exclude:
   - "Don't worry about tests yet, just the main class"
   - "Include the DTO and the mapper too"
   - "Skip the UI layer, just do the service"

5. **Behavioral notes** — Any business logic context:
   - "This validation rule is no longer needed in the new system"
   - "The error codes changed — use the new enum"
   - "This retry logic should use Resilience4j in the new code"

If the user just drops old code and a pattern example without commentary, proceed with sensible defaults and note your assumptions at the end.

---

## Step 1 — Analyse the Target Pattern

Before rewriting, thoroughly study the example pattern code. Extract and mentally catalogue every convention you observe. Read EVERY file the user provides as a pattern example — do not skip any.

### Pattern Extraction Checklist

Work through each of these categories. For each, note what the pattern code does:

**Structure & Naming**
- Package/directory naming convention
- Class naming (suffix conventions like `Service`, `Controller`, `Repository`, `Dto`, `Mapper`)
- Method naming (verb prefixes, camelCase vs other)
- Variable naming (field prefixes, parameter naming)
- Constant naming and placement

**Annotations & Metadata**
- Framework annotations used (Spring, Jakarta, Lombok, custom)
- Annotation ordering convention
- Custom annotation usage

**Architecture & Layering**
- How classes are layered (controller → service → repository, etc.)
- Dependency injection style (constructor injection, `@Autowired`, etc.)
- Interface usage (does every service have an interface, or not?)
- DTO/Entity separation pattern

**Error Handling**
- Exception types (custom vs standard)
- Try/catch patterns vs global exception handlers
- Error response structure

**Logging & Observability**
- Logger declaration style
- Log level usage patterns
- What gets logged at entry/exit of methods

**Validation & Guards**
- Input validation approach (Bean Validation, manual checks, guard clauses)
- Null handling (Optional, assertions, Lombok `@NonNull`)

**Testing** (if test examples are provided)
- Test class naming
- Test method naming convention
- Mocking framework and style
- Assertion library and patterns
- Test data setup approach

**Code Style**
- Import ordering
- Blank line conventions
- Comment style and density
- Method length tendencies
- Return style (early returns vs single return)

Document your findings as a **Pattern Profile** — a concise summary you will use as your strict reference during rewriting. Share this with the user for confirmation before proceeding.

### Pattern Profile Format

```
## Pattern Profile

**Architecture**: [e.g., Spring Boot layered — Controller → Service → Repository]
**DI Style**: [e.g., Constructor injection via Lombok @RequiredArgsConstructor]
**Naming**: [e.g., PascalCase classes with layer suffix, camelCase methods starting with verb]
**Error Handling**: [e.g., Custom BusinessException hierarchy, global @ControllerAdvice handler]
**Logging**: [e.g., Lombok @Slf4j, log.debug on entry, log.error on catch with exception]
**Validation**: [e.g., Jakarta Bean Validation annotations on DTOs, @Valid on controller params]
**Key Patterns Observed**: [anything distinctive — e.g., "all responses wrapped in ApiResponse<T>", "mapper classes use MapStruct", "pagination via Spring Page<T>"]
```

Present this to the user: "Here's what I've extracted from your pattern examples. Does this look right, or should I adjust anything before I start the rewrite?"

---

## Step 2 — Analyse the Old Code

Now study the old code to understand its **behaviour**, not its style. You need to answer:

1. **What does this code do?** — Business logic, data flow, side effects
2. **What external dependencies does it touch?** — Database, APIs, files, message queues
3. **What are the inputs and outputs?** — Method signatures, return types, exceptions thrown
4. **Are there edge cases or special logic?** — Null checks, retry logic, fallback behaviour, conditional branching
5. **What can be dropped?** — Old framework boilerplate, deprecated patterns, dead code

Create a **Behaviour Inventory** — a plain-English summary of what the old code does, organized by method or logical unit. This becomes your "contract" — the rewrite must preserve all of this behaviour unless the user explicitly says otherwise.

### Behaviour Inventory Format

```
## Behaviour Inventory — [OldClassName]

### Method: [oldMethodName]
- **Purpose**: [what it does in business terms]
- **Inputs**: [parameters and their meaning]
- **Output**: [return type and meaning]
- **Side Effects**: [DB writes, API calls, logging, etc.]
- **Edge Cases**: [null handling, empty collections, error paths]
- **Mapping Note**: [any non-obvious mapping to new patterns]
```

---

## Step 3 — Rewrite

Now produce the rewritten code. Follow these rules strictly:

### Rewrite Rules

1. **Pattern fidelity is king.** Every structural decision must match the pattern example. When in doubt, do what the pattern does — not what feels "better" or "cleaner" in the abstract.

2. **Preserve all behaviour.** Every item in the Behaviour Inventory must appear in the rewritten code. If something can't be directly mapped, flag it with a `// TODO: [RENOVATION]` comment explaining the gap.

3. **Don't invent patterns.** If the pattern example doesn't show how to handle something (e.g., async processing, caching), don't guess. Flag it:
   ```java
   // TODO: [RENOVATION] Old code used Thread.sleep() for retry.
   // No retry pattern found in target examples. Needs team decision.
   ```

4. **Map constructs, don't transliterate.** A for-loop in old code might become a Stream in the new pattern. A manual DAO call might become a Spring Data method. Follow the pattern, not the old syntax.

5. **Preserve business logic comments.** If the old code has comments explaining *why* something is done ("// FINRA Rule 4210 requires..."), carry them forward. Drop comments that explain *how* old framework plumbing works.

6. **One output file per logical class.** If the old code is one monolithic class and the new pattern separates concerns (controller/service/repo), produce separate files.

7. **Include necessary supporting types.** If the rewrite needs a new DTO, Mapper, or Exception class that doesn't exist yet, create it — following the pattern conventions.

### Output Format

For each rewritten file, present:

```
### [NewClassName.java]
**Maps from**: [OldClassName or "new — required by pattern"]
**Behaviour preserved**: [list from inventory]
**Assumptions**: [any decisions you made]
```

Followed by the complete code.

After all files, include a **Renovation Summary**:

```
## Renovation Summary

### Files Produced
- [list of all output files]

### Behaviour Coverage
- ✅ [behaviour items preserved]
- ⚠️ [behaviour items that needed assumptions — explain each]
- 🔴 [behaviour items that couldn't be mapped — needs human decision]

### TODO Items
- [list of all // TODO: [RENOVATION] items and their locations]

### Dependencies Added
- [any new libraries/dependencies the rewritten code requires]
```

---

## Step 4 — Output the Files

After the user confirms the rewrite looks good:

1. Create each `.java` file in the working directory with proper package-based subdirectories
2. Copy final files to `/mnt/user-data/outputs/`
3. Present to the user for download

If the user wants to iterate ("change the error handling approach", "use a different mapper library"), go back to Step 3 with the updated instructions and re-generate.

---

## Edge Cases & Guidance

### When the pattern is ambiguous
If the example code shows two different approaches for similar things (e.g., some methods use Optional, others use null checks), ask the user which to follow. Don't mix styles.

### When the old code has no new-pattern equivalent
Some legacy constructs (e.g., mainframe FIND/SORT, COBOL copybooks, Natural CALLNAT) have no 1:1 mapping. In these cases:
- Identify the *intent* of the construct
- Find the closest idiomatic way to achieve that intent in the new stack
- Flag it as an assumption in the Renovation Summary

### When the old code is massive
For large classes (500+ lines), break the rewrite into logical chunks:
1. First pass: structure and signatures only (skeleton)
2. Second pass: fill in method bodies one group at a time
3. Final pass: cross-cutting concerns (logging, error handling, validation)

### When test examples are provided
If the user provides test examples as part of the pattern, also generate rewritten tests following the test pattern exactly. Tests should cover the same scenarios as the old tests, but written in the new style.

### Multiple old files at once
If the user provides multiple related old files, analyse them together before rewriting. Understand cross-file dependencies first, then rewrite in dependency order (entities/DTOs → repositories → services → controllers).

---

## Anti-Patterns to Avoid

- **Don't "improve" the old logic** unless asked. The goal is renovation, not refactoring. If the old code has a clunky algorithm, preserve it unless the user says to optimize.
- **Don't add features** the old code doesn't have (e.g., don't add pagination if the old code didn't paginate).
- **Don't mix old and new style.** If you catch yourself writing something that looks like the old code, stop and re-check the pattern.
- **Don't skip the Pattern Profile.** Even if the rewrite seems obvious, extracting and confirming the pattern prevents drift and misunderstandings.
- **Don't hallucinate library usage.** If you're unsure whether the new codebase uses MapStruct vs manual mappers, ask. Don't assume.
