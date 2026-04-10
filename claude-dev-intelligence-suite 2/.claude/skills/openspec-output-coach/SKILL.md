---
name: openspec-output-coach
description: >
  Takes feedback on OpenSpec spec-driven development output — when the AI
  implemented the wrong thing, missed scope, produced poor tasks, or generated
  a vague design — and diagnoses exactly why the spec artifacts fell short and
  what to change to get better AI output next time. Use when asked: 'improve
  my OpenSpec output', 'OpenSpec spec is wrong', 'AI built the wrong thing',
  'tasks are too vague', 'proposal is too broad', 'OpenSpec feedback', 'spec
  quality', 'improve my proposal', 'AI missed the scope', 'tasks not atomic',
  'design too vague', 'project.md needs work', 'AGENTS.md improvement', 'why
  did AI implement wrong', 'better openspec results', 'spec-driven development
  quality', '/opsx:propose improvement', 'spec feedback loop'. Works on all
  OpenSpec artifacts: proposal.md, specs/, design.md, tasks.md, project.md,
  AGENTS.md. Teaches you to write specs that AI can execute precisely.
---
# OpenSpec Output Coach

Analyse OpenSpec artifacts → collect feedback on what went wrong →
diagnose root causes → prescribe exact rewrites that fix output permanently.

---

## The Core Principle

> The AI is not wrong. The spec was ambiguous.
>
> Every failure in AI output traces back to a gap in the spec artifact.
> Fix the spec, not the prompt.

OpenSpec has five artifact layers. Problems in AI output are caused by gaps
in one or more of them:

```
project.md     ← WHO we are, WHAT conventions we follow, domain language
AGENTS.md      ← HOW the AI should behave in this repo
proposal.md    ← WHY this change, WHAT scope, WHAT success looks like
specs/         ← WHAT the system SHALL do (requirements + scenarios)
design.md      ← WHAT approach to take (constraints, patterns, NOT the how)
tasks.md       ← WHAT to build, broken into atomic, verifiable steps
```

---

## Phase 1 — Read the Artifacts

Ask the user to share what they have. Read everything before diagnosing.

```bash
# Read the full change folder
cat openspec/changes/[change-name]/proposal.md
cat openspec/changes/[change-name]/specs/*.md
cat openspec/changes/[change-name]/design.md
cat openspec/changes/[change-name]/tasks.md

# Read the source of truth
cat openspec/project.md
cat AGENTS.md  # or .claude/CLAUDE.md or .cursor/rules etc.
```

Also ask: **"What did the AI actually produce, and what were you expecting?"**
The gap between expected and actual output is the diagnostic signal.

---

## Phase 2 — Collect Structured Feedback

Present this form. Ask the user to check every item that applies:

```
OPENSPEC OUTPUT FEEDBACK
════════════════════════════════════════════════════════════

What went wrong with the AI's output? Check all that apply:

SCOPE PROBLEMS
  □ AI built MORE than specified (scope creep)
    Example: "I asked for a login form, AI also added registration and forgot password"

  □ AI built LESS than specified (incomplete)
    Example: "AI only did the happy path, ignored error states"

  □ AI built the WRONG thing (misunderstood intent)
    Example: "Wanted a modal dialog, AI created a new page"

  □ AI made assumptions that changed the feature
    Example: "AI decided to use Redis for session storage — I wanted in-memory"

TASK PROBLEMS
  □ Tasks were too large — AI lost track halfway through
    Example: "Task 2.1 was 'implement the whole orders module' — too broad"

  □ Tasks had no clear acceptance criteria — AI didn't know when done
    Example: "Task said 'add validation' — AI added one validator and stopped"

  □ Tasks had hidden dependencies — AI did them in wrong order
    Example: "AI tried to use the DTO before the DTO task was complete"

  □ Tasks were ambiguous — AI guessed and guessed wrong
    Example: "'update the service' — which service? which update?"

  □ AI couldn't verify its own work — no testable outcome stated
    Example: Task passed but feature was broken — no way to catch it

SPEC PROBLEMS
  □ Requirements were too vague — "should" instead of "shall"
    Example: "The system should handle errors" — AI added try/catch and moved on"

  □ Scenarios were missing — AI didn't know about edge cases
    Example: "No scenario for empty list — AI returned null instead of []"

  □ Business rules not stated — AI invented its own logic
    Example: "No rule for max file size — AI used 10MB default arbitrarily"

  □ User roles not defined — AI assumed wrong access level
    Example: "AI made the endpoint public — should have been admin only"

DESIGN PROBLEMS
  □ Design was too prescriptive — told AI HOW, not WHAT
    Example: "Design specified exact class names — AI couldn't deviate when needed"

  □ Design was too vague — AI picked the wrong pattern
    Example: "Use a service layer" — AI created a God Service doing everything"

  □ Design conflicted with existing code — AI ignored existing patterns
    Example: "Said 'use REST' but existing code uses GraphQL — AI mixed them"

  □ Technology constraints not stated — AI chose wrong stack
    Example: "AI used Feign client, project uses RestTemplate everywhere"

PROJECT.MD / AGENTS.MD PROBLEMS
  □ Domain language not defined — AI used wrong terminology
    Example: "We call it 'account holder' but AI used 'user' everywhere"

  □ Coding conventions not stated — AI used different patterns
    Example: "AI used field injection, project always uses constructor injection"

  □ Architecture constraints not stated — AI violated boundaries
    Example: "AI called repository directly from controller — should go via service"

  □ Existing system context missing — AI re-invented existing features
    Example: "AI created a new auth system — one already exists in AuthService"

════════════════════════════════════════════════════════════
```

---

## Phase 3 — Diagnose Root Causes

Map each piece of feedback to the artifact that caused it.
Read `references/diagnosis-patterns.md` for detailed root cause analysis.

### Quick Diagnosis Map

| What went wrong | Root artifact | Specific gap |
|---|---|---|
| AI built wrong thing | `proposal.md` | Intent not clear — "what" underspecified |
| AI added too much | `proposal.md` | Scope not bounded — no explicit out-of-scope |
| AI built too little | `specs/` | Requirements missing — only happy path covered |
| Tasks too large | `tasks.md` | Tasks not broken to 1-hour atomic units |
| No acceptance criteria | `tasks.md` | Each task missing "done when..." statement |
| Wrong tech choices | `design.md` or `project.md` | Stack constraints not stated |
| Violated architecture | `AGENTS.md` or `project.md` | Existing patterns not documented |
| Wrong terminology | `project.md` | Domain glossary missing |
| AI guessed business rules | `specs/` | Rules not stated as "SHALL" statements |
| AI ignored edge cases | `specs/scenarios/` | Scenarios file missing or incomplete |
| AI made wrong assumptions | `design.md` | Constraints section empty |

---

## Phase 4 — Prescribe Exact Rewrites

For each diagnosed gap, generate the exact rewrite of the relevant artifact section.
Never say "improve your proposal" — always show the before/after.

Read `references/rewrite-patterns.md` for the full pattern library.

### Output Format

```
OPENSPEC IMPROVEMENT PLAN
════════════════════════════════════════════════════════════
Change:    [change-name]
Issues:    [N] root causes diagnosed
Artifacts: [list of artifacts needing rewrite]

ISSUE-001 [CRITICAL]: AI built registration flow — not in scope
Root artifact: proposal.md → scope not bounded

BEFORE (caused the problem):
  ## What's changing
  Add authentication to the application.

AFTER (prevents the problem):
  ## What's changing
  Add a login form with email/password authentication only.

  ## Explicitly out of scope
  - Registration / account creation (handled by admin separately)
  - Password reset / forgot password (backlog item AUTH-004)
  - Social login / OAuth (future milestone)
  - Session management changes (AUTH-002 covers this separately)

  ## Success looks like
  A user with an existing account can enter their email and password,
  submit the form, and land on the dashboard.
  An incorrect password shows a specific error message.
  Three consecutive failures lock the account.

WHY THIS WORKS: OpenSpec's AI reads proposal.md first to bound its
  work. Explicit out-of-scope prevents scope creep. "Success looks like"
  gives the AI a test it can verify against.

════════════════════════════════════════════════════════════

ISSUE-002 [HIGH]: Tasks too large — AI lost track of state
Root artifact: tasks.md → tasks not atomic

BEFORE:
  - [ ] 2.1 Implement the order service

AFTER:
  - [ ] 2.1 Add OrderService class with createOrder(CreateOrderRequest) method
        Done when: class exists, compiles, throws NotImplementedException
  - [ ] 2.2 Implement order validation in validateOrder(Order) — private method
        Done when: throws InvalidOrderException if items empty, customer null, or total ≤ 0
        Test: OrderServiceTest validates all three failure cases
  - [ ] 2.3 Implement discount calculation in calculateDiscount(Order) — private method
        Done when: returns 10% of total if customer.isVip(), else 0
        Test: OrderServiceTest covers VIP and non-VIP cases
  - [ ] 2.4 Implement persistence — call orderRepository.save(order)
        Done when: createOrder returns saved entity with generated ID
        Test: integration test verifies record exists in H2 after call

WHY THIS WORKS: Each task is ~1 hour. "Done when" gives the AI a
  verifiable exit condition — it knows when to stop. Explicit test
  references mean the AI writes and runs tests per task.

════════════════════════════════════════════════════════════

ISSUE-003 [HIGH]: AI used wrong HTTP client
Root artifact: project.md → tech conventions not stated

ADD to project.md → Tech Stack section:

  ## HTTP Client Conventions
  All outbound HTTP calls use RestTemplate (not WebClient, not Feign).
  A configured RestTemplate bean exists in HttpConfig.java.
  Import it via constructor injection: @Autowired RestTemplate restTemplate.
  Do NOT add new client dependencies — use what exists.

  ## Dependency Injection
  Always constructor injection. Never @Autowired on fields.
  Use @RequiredArgsConstructor (Lombok) on service classes.

  ## Error Handling
  All service-layer exceptions extend BusinessException (runtime).
  GlobalExceptionHandler in web/ handles all exceptions centrally.
  Services never catch and swallow exceptions.

WHY THIS WORKS: project.md is read by the AI at the start of every
  change. Conventions stated here apply to ALL future changes, not
  just this one.

════════════════════════════════════════════════════════════

ISSUE-004 [MEDIUM]: Business rule missing — AI chose wrong discount threshold
Root artifact: specs/ → business rules not stated

ADD to specs/requirements.md:

  ## Business Rules

  BR-001: VIP Discount
  The system SHALL apply a 10% discount to orders placed by VIP customers.
  A VIP customer is defined as: customer.tier == "VIP" (see Customer entity).
  The discount is calculated on the pre-tax total, not the post-tax total.
  The discount is applied before the order is saved.
  Discount cannot exceed £500 regardless of order size.

  BR-002: Approval Threshold
  Orders with a pre-discount total exceeding £10,000 SHALL require manager approval.
  Orders at exactly £10,000 do NOT require approval.
  The threshold is configurable via application property: orders.approval.threshold.

WHY THIS WORKS: "SHALL" is a testable, unambiguous obligation. The AI
  reads this as a hard requirement, not a suggestion. Boundary conditions
  ("exceeding" vs "at exactly") eliminate guessing at the edge case.

════════════════════════════════════════════════════════════

PREDICTED IMPROVEMENT:
  With these changes, re-running /opsx:apply on this change should:
  ✅ Stay within the login-only scope
  ✅ Complete tasks in correct order with verifiable outcomes
  ✅ Use RestTemplate (not Feign)
  ✅ Apply the 10% VIP discount with the correct £500 cap

APPLY ORDER:
  1. Update project.md first (affects all future changes too)
  2. Rewrite proposal.md out-of-scope section
  3. Add business rules to specs/requirements.md
  4. Break tasks.md into atomic tasks with Done When criteria
  5. Re-run: /opsx:apply
════════════════════════════════════════════════════════════
```

---

## Phase 5 — Build Your Spec Quality Checklist

After each coaching session, append to the user's `openspec/project.md` a
"Spec Writing Standards" section so future proposals start from a higher baseline.

Generate this section based on patterns found across all diagnosed issues:

```markdown
## Spec Writing Standards (generated from output coaching)

### proposal.md must always include:
- [ ] "What's changing" — 2-3 specific sentences, not a paragraph
- [ ] "Explicitly out of scope" — minimum 3 items
- [ ] "Success looks like" — a testable end state description

### specs/requirements.md must always include:
- [ ] All requirements use "SHALL" (mandatory) or "SHOULD" (preferred)
- [ ] Every business rule has: condition + threshold + effect + boundary value
- [ ] No vague terms: no "appropriate", "reasonable", "as needed", "standard"

### specs/scenarios.md must always include:
- [ ] Happy path
- [ ] Each validation failure (one scenario per required field)
- [ ] Each business rule violation
- [ ] Permission denied scenario
- [ ] At least one edge case (empty list, null, zero, boundary value)

### design.md must always include:
- [ ] Which existing classes/services to extend (not create from scratch if avoidable)
- [ ] Which tech choices are CONSTRAINED (RestTemplate not Feign, etc.)
- [ ] Which architectural boundaries to respect (no controller → repository)
- [ ] What NOT to change

### tasks.md must always follow:
- [ ] Each task is ≤ 1 hour of work
- [ ] Each task has "Done when: [specific verifiable outcome]"
- [ ] Each task names its test file if a test is expected
- [ ] Tasks are in dependency order (no task uses output of a later task)
```
