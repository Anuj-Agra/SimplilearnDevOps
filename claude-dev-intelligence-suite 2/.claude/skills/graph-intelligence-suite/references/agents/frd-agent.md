# AGENT: FRD (Functional Requirements Document)

Generate a professional Functional Requirements Document (FRD) from the graph,
enriched by targeted source-code reads. The graph tells us *what exists and how
it relates*; the code tells us *what it does*.

---

## FRD vs Functional Spec — Distinction

| Functional Spec (other skill) | FRD (this agent) |
|---|---|
| Business-facing, user-story style | Architecture-aware, module-by-module |
| Hides tech details entirely | References modules by name |
| Good for product owners | Good for developers + architects |
| Source: code scan | Source: graph + targeted code reads |

The FRD produced here bridges both worlds: it is readable by stakeholders AND
useful to engineers as a reference for migration, modernisation, or onboarding.

---

## Step 0 — Scope Clarification

Before generating, confirm:
1. **Scope**: Whole repo? A specific top-level module? A sub-module?
2. **Audience**: Development team? Architects? Business stakeholders? (adjusts language level)
3. **Format**: Word `.docx` (default) or Markdown?
4. **Graph path**: Where is `repo-graph.json`? (default: working directory)
5. **Codebase path**: Where is the source? (needed for targeted code reads)

---

## Step 1 — Load the Module Inventory from Graph

```bash
python3 scripts/project_graph.py \
  --graph repo-graph.json --mode subtree --node <scope>
```

From the subtree projection, build the **module inventory table**:

| Module ID | Label | Parent | Type | LOC | Fan-in | Fan-out | Instability |
|---|---|---|---|---|---|---|---|
| service-a:core | core | service-a | submodule | 2,400 | 3 | 5 | 0.63 |
| ... | | | | | | | |

This table becomes Section 3 of the FRD.

---

## Step 2 — Targeted Code Reads (Minimal Token Strategy)

For each module in scope, read **only high-signal files** — not everything:

### Priority 1: Entry Points (read first, always)
```bash
# Spring Boot entry points
find <module_path> -name "*Application.java" -o -name "*SpringBoot*.java" | head -5

# Angular entry
find <module_path> -name "app.module.ts" -o -name "main.ts" | head -3
```

### Priority 2: Controllers / API Surface (reveals WHAT the module exposes)
```bash
find <module_path> -name "*Controller.java" -o -name "*Resource.java" \
  -o -name "*Endpoint.java" | head -10
# Read each — focus on method signatures, not implementations
grep -n "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@RequestMapping\|@Operation\|@ApiOperation" \
  <controller_file> | head -30
```

### Priority 3: Service Layer (reveals WHAT the module does)
```bash
find <module_path> -name "*Service.java" | head -10
# Read only the public method signatures, not the bodies
grep -n "public\|@Transactional\|@Cacheable\|@Async\|//.*TODO\|//.*FIXME" \
  <service_file> | head -40
```

### Priority 4: Domain Model / Entities (reveals WHAT data it manages)
```bash
find <module_path> -name "*.java" | xargs grep -l "@Entity\|@Document\|record " | head -10
grep -n "private\|String\|Integer\|Long\|LocalDate\|@Column\|@NotNull" \
  <entity_file> | head -30
```

### Priority 5: Configuration (reveals WHAT infrastructure it uses)
```bash
find <module_path> -name "*.yml" -o -name "*.yaml" -o -name "*.properties" \
  | grep -i "application\|config" | head -5
grep -n "spring\.\|datasource\.\|kafka\.\|redis\.\|feign\.\|url\|host\|port" \
  <config_file> | head -30
```

**Token rule**: Read max 50 lines per file. If a file is larger, use `grep` to extract
the key signatures and annotations only.

---

## Step 3 — Build the FRD Section by Section

Follow the document structure in `references/templates/frd-template.md` exactly.

For each module section, fill in:

### 3a. Module Overview
```
Module: service-a:core
Purpose: [Infer from controllers + service method names]
Responsibility: [What data does it own? What processes does it execute?]
Dependencies: [From graph fan-out projection]
Consumers: [From graph fan-in projection]
Stability: [Instability score interpretation]
```

### 3b. Functional Capabilities
List each capability as: **"The system [verb] [what] [under what condition]"**

Extract from:
- Each `@GetMapping` → "The system retrieves [resource]"
- Each `@PostMapping` → "The system creates / submits [resource]"
- Each `@PutMapping` / `@PatchMapping` → "The system updates [resource]"
- Each `@DeleteMapping` → "The system removes [resource]"
- Each `@Scheduled` → "The system automatically [action] every [interval]"
- Each `@Async` → "The system processes [action] asynchronously"

### 3c. Data Requirements
From entity fields:
| Field | Type | Required | Validation | Business Meaning |
|---|---|---|---|---|
| customerId | String | Yes | Not blank, max 50 chars | Unique identifier for the customer |

### 3d. Integration Points
From graph edges + config:
| Integration | Direction | Protocol | Module |
|---|---|---|---|
| shared-lib | Inbound | Java compile | Data validation utilities |
| client-data-service | Outbound | REST/Feign | Fetch client profile |

### 3e. Non-Functional Characteristics (from graph metrics)
```
Stability index: 0.63 (moderate) — this module is a consumer, not a provider
Blast radius: Changing this module affects [fan-in] other modules
Test isolation: [test deps from graph]
```

---

## Step 4 — Assemble and Output

Read `references/templates/frd-template.md` for the full document outline,
then read `/mnt/skills/public/docx/SKILL.md` to produce the `.docx` file.

**Document structure**:
1. Title Page + metadata
2. Document Purpose & Audience
3. Module Inventory Table (from graph)
4. Architecture Overview (Mermaid diagram of top-level modules + key edges)
5. Per-Module Functional Requirements (Step 3 above, one section per module)
6. Cross-Module Integration Map (graph edges rendered as a table)
7. Data Model Summary
8. Stability & Risk Register (instability scores, circular deps, dead modules from graph)
9. Open Questions & Assumptions

---

## Quality Checklist

- [ ] Every module in the graph scope has a section in the FRD
- [ ] No module section was written from imagination — all from code + graph
- [ ] Integration points match actual graph edges (no phantom dependencies)
- [ ] Circular dependencies are called out explicitly in Section 8
- [ ] Dead modules are flagged (do not write functional requirements for dead code)
- [ ] Mermaid architecture diagram has max 20 nodes
- [ ] Language is appropriate for stated audience
