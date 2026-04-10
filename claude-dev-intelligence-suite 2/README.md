# Dev Intelligence Suite for Claude
### A complete AI-powered SDLC toolkit for Java/Angular mono-repos

---

## What Is This?

This package gives Claude six specialised skills that work together to analyse
your codebase, write documentation, generate tests, and find production risks —
all without you having to explain your system from scratch every time.

The skills share a single `repo-graph.json` file (built once, reused everywhere)
and are designed to be used in sequence across your development lifecycle.

---

## Skills at a Glance

| # | Skill | What it does | Run when |
|---|---|---|---|
| 1 | **Repo Graph Architect** | Scans your mono-repo, builds a full dependency graph | First time, or when structure changes |
| 2 | **Graph Intelligence Suite** | Q&A, FRD generation, API performance analysis — all from the graph | Any time after step 1 |
| 3 | **Functional Spec Generator** | Writes a 10-section non-technical FRD from your code | Sprint 0, before development |
| 4 | **Persona Suite** | Five expert personas review the same material differently | Before sign-off, sprint planning |
| 5 | **Gap Detector** | Finds functional, technical, scenario, and performance gaps | Before every release |
| 6 | **Playwright Test Generator** | Writes full UI + API test suites from your code | After FRD is reviewed |

---

## Installation

### Step 1 — Copy `.claude/` into your project

```bash
# In your repository root:
cp -r path/to/claude-dev-intelligence-suite/.claude ./
```

Your project root should now look like:
```
your-project/
├── .claude/
│   ├── settings.json
│   └── skills/
│       ├── repo-graph-architect/
│       ├── graph-intelligence-suite/
│       ├── functional-spec-generator/
│       ├── persona-suite/
│       ├── playwright-test-generator/
│       └── gap-detector/
├── src/
└── ...
```

### Step 2 — Copy the `config/` folder (optional but recommended)

```bash
cp -r path/to/claude-dev-intelligence-suite/config ./
```

### Step 3 — Create the output directories

```bash
mkdir -p graph docs/frd docs/specs docs/gap-reports tests
```

### Step 4 — Open Claude and start a new Project

1. Go to [claude.ai](https://claude.ai) → **Projects** → **New Project**
2. Name it after your system (e.g. "Orders Platform Analysis")
3. Upload the `.claude/` folder (or the package `.skill` files individually if uploading manually)
4. You're ready.

---

## Python Requirements

The graph scripts require Python 3.9+. No external libraries needed — standard library only.

```bash
python3 --version   # Must be 3.9 or higher
```

---

## Playwright Test Runner Requirements

```bash
# In your tests/ directory (after test generation):
npm init -y
npm install --save-dev @playwright/test
npx playwright install chromium firefox
```

---

## Recommended First Run (15-minute quick-start)

### 1. Build the graph (run once)

```
Tell Claude:
"Build a dependency graph for my mono-repo at /path/to/my/project"
```

Claude will scan, build `graph/repo-graph.json`, and produce `graph/repo-graph.html`.
Open the HTML file in your browser for an interactive map of your entire system.

**Expected time**: 2–10 minutes depending on repo size.

---

### 2. Generate your FRD

```
Tell Claude:
"Create an FRD for the Orders module using the graph we just built"
```

Claude will load the graph projection for the Orders module (without re-scanning),
read only the high-signal source files, and produce a Word document in `docs/frd/`.

**Expected time**: 5–15 minutes per module.

---

### 3. Run a persona round-table on the FRD

```
Tell Claude:
"Run a round-table review of the Orders FRD with all five personas"
```

You will get five perspectives in sequence: PO, BA, Architect, Developer, Test Architect.
Each will flag different problems.

---

### 4. Run the gap detector

```
Tell Claude:
"Run a full gap analysis on the Orders module"
```

Claude will run all four engines and produce a prioritised risk report.

---

### 5. Generate tests

```
Tell Claude:
"Generate a full Playwright test suite for the Orders module"
```

Claude produces the Page Object Models, UI spec files, API spec files, and shared fixtures.

---

## All Trigger Phrases

### Repo Graph Architect
```
"Graph my repo at [path]"
"Build the dependency tree"
"Scan my project"
"Map all modules in [path]"
"Visualize my project structure"
```

### Graph Intelligence Suite (requires graph to exist first)
```
"What depends on [module name]?"
"What is the blast radius of [module name]?"
"Are there any circular dependencies?"
"What are my dead modules?"
"Show me the dependency chain from [A] to [B]"
"Which module is most critical to the system?"
"What's the longest dependency chain?"
"Show me API performance risks"
```

### Functional Spec Generator
```
"Create an FRD for [module/system]"
"Document what [module] does"
"Write a functional spec for [module]"
"Generate user stories for [module]"
"Extract business rules from [module]"
```

### Persona Suite
```
"Review this as the Product Owner"           → PO: business value + user impact
"Review this as the Business Analyst"        → BA: completeness + ambiguity
"Review this as the Technical Architect"     → Architect: structure + risk
"Review this as the Developer"               → Developer: buildability + edge cases
"Review this as the Test Architect"          → Test Architect: coverage + strategy
"Run a round-table review with all personas" → All five in sequence
```

### Gap Detector
```
"Find all gaps in [module/FRD]"              → All four engines
"What functional gaps exist?"                → Missing user journeys
"Find technical gaps"                        → Broken contracts, missing error handling
"What will break production?"                → Edge case scenarios
"Find performance gaps"                      → N+1, pagination, caching issues
```

### Playwright Test Generator
```
"Write Playwright tests for [module]"
"Generate E2E tests for [feature]"
"Write API tests for [controller/resource]"
"Generate the full test suite"
"Write tests for the [screen name] screen"
```

---

## Workflows

### Workflow A: Full Discovery (new codebase or new team member)
```
1. Repo Graph Architect  → graph/repo-graph.json + graph/repo-graph.html
2. Functional Spec Gen   → docs/frd/[system]-frd-v1.docx
3. Persona Suite (all)   → Review and validate the FRD
4. Gap Detector (all)    → docs/gap-reports/gap-analysis-[date].md
```
**Time**: Half a day for a medium-sized system.

---

### Workflow B: Module Sprint Prep
```
1. Graph Q&A             → "What modules are in [area]? What depends on them?"
2. Functional Spec Gen   → docs/frd/[module]-frd-v1.docx  (just that module)
3. BA Persona            → Requirements completeness check
4. Gap Detector          → Functional + scenario gaps only
5. Playwright Tests      → Test suite for the module
```
**Time**: 1–2 hours per module.

---

### Workflow C: Pre-Release Risk Review
```
1. Gap Detector (all)    → Full risk report
2. Architect Persona     → Architecture + stability review
3. Test Architect        → Test coverage assessment
```
**Time**: 1 hour.

---

### Workflow D: Onboarding a New Developer
```
1. Graph Q&A             → "Explain [module] in plain English"
2. PO Persona            → "What does this system do for users?"
3. Developer Persona     → "What are the implementation risks in [module]?"
```
**Time**: 30 minutes.

---

## Token Efficiency Notes

The suite is designed to be token-efficient. Here's how:

| Operation | Without graph | With graph | Saving |
|---|---|---|---|
| Understand module structure | Full directory scan (~5,000 tokens) | Index projection (~200 tokens) | 96% |
| Answer "what depends on X?" | Read all build files (~8,000 tokens) | Fan-in projection (~1,500 tokens) | 81% |
| Generate FRD for one module | Full scan (~15,000 tokens) | Subtree projection + targeted reads (~4,000 tokens) | 73% |

**Always build the graph first.** It pays for itself on the second question.

---

## Refreshing the Graph

Re-run `repo-graph-architect` when:
- A new top-level module is added or removed
- A dependency between modules changes
- A module is refactored into two or more modules
- You start a new sprint and want fresh metrics

No need to re-run for: internal code changes within a module (adding a method,
changing business logic) — those don't change the structural graph.

---

## Output Files Reference

| File | Generated by | Commit to git? |
|---|---|---|
| `graph/repo-graph.json` | repo-graph-architect | ✅ Yes — shared context for all skills |
| `graph/repo-graph.html` | repo-graph-architect | Optional — useful for onboarding |
| `docs/frd/*.docx` | functional-spec-generator | ✅ Yes — living documentation |
| `docs/gap-reports/*.md` | gap-detector | ✅ Yes — audit trail |
| `docs/specs/*.docx` | graph-intelligence-suite | ✅ Yes |
| `tests/ui/**/*.ts` | playwright-test-generator | ✅ Yes |
| `tests/api/**/*.ts` | playwright-test-generator | ✅ Yes |
| `tests/playwright.config.ts` | playwright-test-generator | ✅ Yes |

---

## Skill Dependencies

```
repo-graph-architect
        │
        ▼
graph/repo-graph.json  ←──────────────────────┐
        │                                      │
        ├──▶ graph-intelligence-suite          │
        │        ├── GRAPH-QA agent            │
        │        ├── FRD agent                 │
        │        └── API-PERF agent            │
        │                                      │
        └──▶ functional-spec-generator         │
                        │                      │
                        ▼                      │
              docs/frd/*.docx  ─────────────────┤
                        │                      │
                        ├──▶ persona-suite      │
                        │       ├── PO          │
                        │       ├── BA          │
                        │       ├── Architect ──┘
                        │       ├── Developer
                        │       └── Test Architect
                        │
                        ├──▶ gap-detector
                        │       ├── Functional engine
                        │       ├── Technical engine ──▶ repo-graph.json
                        │       ├── Scenario engine
                        │       └── Performance engine ──▶ repo-graph.json
                        │
                        └──▶ playwright-test-generator
                                ├── UI Suite (Angular)
                                └── API Suite (Java)
```

All skills can also run independently without a graph — the graph just accelerates them.

---

## Troubleshooting

**"The skill isn't triggering"**
→ Check `config/workflow-config.json` for the exact trigger phrases and use one of them.

**"The graph script fails"**
→ Ensure Python 3.9+ is installed: `python3 --version`
→ Run scripts from the project root: `python3 .claude/skills/repo-graph-architect/scripts/graph_builder.py --help`

**"The FRD is too technical"**
→ Remind Claude: "You are writing for a non-technical product owner. Remove all technical terms."
→ The skill's anti-jargon checklist will catch most issues on the quality gate pass.

**"The Playwright tests don't run"**
→ Check `.env` file has `ANGULAR_BASE_URL`, `API_BASE_URL`, and credential variables.
→ Ensure the app is running before running tests.

**"The graph is stale"**
→ Re-run `repo-graph-architect` with the same repo path. Overwrite `graph/repo-graph.json`.

---

## File Structure of This Package

```
claude-dev-intelligence-suite/
├── README.md                              ← This file
├── .claude/                               ← Copy this into your project root
│   ├── settings.json
│   └── skills/
│       ├── repo-graph-architect/
│       │   ├── SKILL.md
│       │   ├── references/parsers/
│       │   │   ├── maven.md
│       │   │   ├── gradle.md
│       │   │   ├── npm.md
│       │   │   └── python.md
│       │   ├── references/visualiser-template.md
│       │   └── scripts/
│       │       ├── graph_builder.py
│       │       └── cycle_detector.py
│       ├── graph-intelligence-suite/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   │   ├── graph-projection-engine.md
│       │   │   ├── agents/graph-qa-agent.md
│       │   │   ├── agents/frd-agent.md
│       │   │   ├── agents/api-perf-agent.md
│       │   │   └── templates/frd-template.md
│       │   └── scripts/project_graph.py
│       ├── functional-spec-generator/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── frd-output-template.md
│       │       └── output-template.md
│       ├── persona-suite/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── po-persona.md
│       │       ├── ba-persona.md
│       │       ├── architect-persona.md
│       │       ├── developer-persona.md
│       │       └── test-architect-persona.md
│       ├── playwright-test-generator/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── ui-test-patterns.md
│       │       └── api-test-patterns.md
│       └── gap-detector/
│           ├── SKILL.md
│           └── references/
│               ├── scenario-gaps.md
│               └── performance-gaps.md
├── config/
│   ├── skills-manifest.json               ← Full skill metadata
│   └── workflow-config.json               ← Trigger phrases + output paths
└── project-structure/                     ← Ideal project layout (reference only)
    └── README.md                          ← Folder-by-folder explanation
```

---

## Extended Skills (30 additional)

### Architecture & Code Quality
| Skill | Trigger phrases |
|---|---|
| `migration-planner` | "migration plan", "modernisation roadmap", "phased migration" |
| `dead-code-eliminator` | "remove dead code", "decommission", "safe to remove" |
| `api-contract-generator` | "OpenAPI spec", "swagger", "API contract", "openapi.yaml" |

### Security & Compliance
| Skill | Trigger phrases |
|---|---|
| `security-audit` | "security audit", "OWASP", "vulnerabilities", "pen test prep" |
| `gdpr-compliance-scanner` | "GDPR", "PII mapping", "compliance audit", "Article 30", "KYC audit" |
| `data-lineage-mapper` | "data lineage", "trace this field", "where does X go" |
| `db-schema-reverse-engineer` | "data model", "ER diagram", "entity relationships" |

### Delivery & Operations
| Skill | Trigger phrases |
|---|---|
| `change-impact-analyser` | "impact of this change", "regression scope", "what breaks" |
| `cicd-pipeline-auditor` | "audit my pipeline", "CI/CD review", "pipeline gaps" |
| `release-notes-generator` | "release notes", "changelog", "what changed in this release" |
| `jira-ticket-generator` | "create Jira tickets", "backlog items", "acceptance criteria" |
| `dependency-risk-tracker` | "dependency audit", "CVE scan", "outdated dependencies" |

### Concurrency & Thread Safety
| Skill | Trigger phrases |
|---|---|
| `concurrency-hazard-scanner` | "race conditions", "thread safety", "shared mutable state" |
| `reactive-migration-advisor` | "migrate to reactive", "WebFlux", "non-blocking", "Project Reactor" |

### Connection & Resource Management
| Skill | Trigger phrases |
|---|---|
| `connection-pool-analyser` | "connection pool", "HikariCP", "pool sizing", "pool exhaustion" |
| `timeout-bulkhead-auditor` | "missing timeouts", "bulkhead", "thread pool isolation" |
| `backpressure-queue-analyser` | "back pressure", "Kafka", "dead letter queue", "queue depth" |

### Resilience Patterns
| Skill | Trigger phrases |
|---|---|
| `circuit-breaker-auditor` | "circuit breaker", "cascading failure", "Resilience4j" |
| `retry-storm-detector` | "retry storm", "exponential backoff", "retry jitter" |
| `graceful-degradation-planner` | "graceful degradation", "fallback", "degraded mode" |

### Observability
| Skill | Trigger phrases |
|---|---|
| `observability-gap-detector` | "observability", "missing metrics", "structured logging", "tracing" |
| `correlation-id-auditor` | "correlation ID", "trace propagation", "MDC propagation" |
| `slo-sla-generator` | "SLO", "SLA", "latency targets", "error budget", "alerting rules" |

### Performance Testing
| Skill | Trigger phrases |
|---|---|
| `load-test-generator` | "load tests", "Gatling", "k6", "stress test", "spike test" |
| `latency-budget-decomposer` | "latency budget", "where is time spent", "call chain latency" |

### Caching & State
| Skill | Trigger phrases |
|---|---|
| `cache-strategy-generator` | "caching strategy", "what to cache", "Redis cache", "TTL config" |
| `distributed-lock-auditor` | "distributed lock", "horizontal scaling", "scheduled job on every instance" |

### API Design
| Skill | Trigger phrases |
|---|---|
| `api-versioning-auditor` | "API versioning", "breaking changes", "backward compatibility" |
| `idempotency-scanner` | "idempotency", "duplicate requests", "double submit", "retry-safe" |
| `rate-limiter-auditor` | "rate limiting", "throttling", "Bucket4j", "too many requests" |
