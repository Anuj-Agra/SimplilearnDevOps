# BMAD Cross-Repo

AI-driven development framework for managing changes across your **Java** and **Angular** monorepos. Powered by GitHub Copilot Chat.

You describe what you want to build or change. The system investigates your codebase, proposes a plan, waits for your approval, then implements and reviews — across both repos.

---

## Setup

### 1. Drop into your workspace root

Place the `.bmad/`, `.github/`, `docs/`, and `AGENTS.md` alongside your two monorepo folders:

```
workspace-root/               ← open this in VS Code
├── .bmad/                     ← from this package
├── .github/                   ← from this package
├── docs/                      ← from this package
├── AGENTS.md                  ← from this package
├── your-java-repo/            ← your existing Java monorepo
└── your-angular-repo/         ← your existing Angular monorepo
```

### 2. Update folder names

If your repos aren't named `java-service` and `angular-app`, update references in:
- `.github/copilot-instructions.md` — workspace structure section
- `.github/instructions/java.instructions.md` — `applyTo` path
- `.github/instructions/angular.instructions.md` — `applyTo` path

### 3. Enable Copilot prompt files

In VS Code settings, enable:
- `Chat: Prompt Files`
- `GitHub Copilot > Chat > Code Generation: Use Instruction Files`

### 4. First run

```
/bmad-setup
```

This scans both monorepos and creates `docs/project-context.md` — a map of your modules, endpoints, services, models, and conventions. Everything else builds on this.

---

## How It Works

Every command follows the same principle: **investigate → present → wait for your acknowledgment → continue**. Nothing is dumped in one shot. At every stage, if the system detects something you may not have considered (security, entitlements, pattern conflicts, missing validation), it asks you before proceeding.

---

## Workflows

### "I want to build something new"

```
/bmad-propose Add a KYC verification endpoint that accepts client
documents, validates them, and returns a verification status.
The Angular app needs a status badge on the client detail page.
```

What happens:
1. Both repos are scanned. You're shown what exists today and asked to confirm the scope.
2. The feature is broken into epics and prioritized. You're asked about edge cases, failure paths, and missing requirements.
3. The technical architecture is designed — but only within the boundary you specified. If you said "backend", only backend is designed first. You're asked about auth, entitlements, and patterns before the cross-repo impact is expanded.
4. Implementation stories are created one at a time, each with full file paths. You confirm each before the next.

At the end, you get a proposal summary. Nothing is implemented yet.

When ready:

```
/bmad-apply
```

Code is written (Java first, Angular second), reviewed against quality gates, and cross-repo type alignment is verified. Each file is shown to you before being written.

---

### "I already have requirements"

If you have a Jira ticket, a requirements doc, or a list of what needs to happen:

```
/bmad-from-req

Requirements:
1. GET /api/clients/{id}/kyc-status returns PENDING/APPROVED/REJECTED
2. Only COMPLIANCE_OFFICER role can access
3. Client detail page shows status badge with color coding
4. Badge updates on page refresh
```

This skips discovery. Your requirements are taken as-is. The system goes straight to architecture (incrementally, with approval gates) and story creation. Then waits for `/bmad-apply`.

You can also paste Jira ticket text, reference a file in the workspace, or describe requirements conversationally.

---

### "I already have a technical design"

If you have an architecture doc, API spec, or technical design:

```
/bmad-from-arch

The architecture is in docs/architecture.md — create stories from it.
```

Or paste your design inline. This skips straight to story creation, then waits for `/bmad-apply`.

---

### "I already have tasks / stories"

If you have a Jira sprint, a task list, or stories ready:

```
/bmad-from-stories

Tasks:
- Create KycStatusDto in Java with status enum
- Add GET /api/clients/{id}/kyc-status endpoint
- Create kyc-status.model.ts in Angular
- Add getKycStatus() to client.service.ts
```

The system enriches vague tasks with real file paths by scanning your repos, adds cross-repo verification steps, confirms with you, then implements.

---

### "What happens if I change X?"

Before making any change, check the ripple effects across repos:

```
/bmad-impact I'm adding a lastVerifiedDate field to the KycStatus entity in Java.
```

You'll see:
- What currently exists (with file paths)
- What must change in Angular (interfaces, services, components)
- What should change (consistency improvements)
- Questions about things you may not have considered

Works from either direction — describe a Java change to see Angular impact, or describe an Angular need to see what backend work is required.

---

### "Use the same pattern as an existing module"

When you want to replicate how something was already built:

```
/bmad-pattern Use the same pattern as the accounts module for a new reporting feature.
```

The system scans the referenced module in both repos, extracts the full pattern (class structure, naming, annotations, auth approach, test patterns), presents it with real code examples, and proposes how to apply it. You confirm before it becomes the basis for the architecture.

You can also reference patterns mid-conversation: "like the accounts module" works at any stage.

---

### "Apply only one story"

If a proposal has multiple stories and you want to implement them selectively:

```
/bmad-apply S-1.2
```

Or multiple:

```
/bmad-apply S-1.1 S-1.2 S-2.1
```

---

## What Gets Asked Automatically

At every stage, the system detects implications and asks before proceeding. You'll see questions like:

- *"This new button — does it need role-based access / entitlement checks?"*
- *"Existing controllers use pattern A, but this would need pattern B. Align or diverge?"*
- *"This DTO field has no validation — should I add @NotNull / @Size?"*
- *"This spans modules X and Y — should both be in scope?"*
- *"No error handling story — should I add one?"*
- *"Modifying this response shape will break existing Angular calls — new version or update Angular first?"*

Nothing is assumed. You decide, the system proceeds.

---

## Entry Points Summary

| What you have | Command | What happens next |
|---|---|---|
| An idea or feature request | `/bmad-propose` | Full planning → approval → implement |
| Requirements (Jira, doc, list) | `/bmad-from-req` | Architecture → stories → approval → implement |
| Technical design / API spec | `/bmad-from-arch` | Stories → approval → implement |
| Tasks / story list | `/bmad-from-stories` | Enrich → confirm → implement |
| Approved proposal | `/bmad-apply` | Implement + review |
| Single story to implement | `/bmad-apply S-1.1` | Implement + review that story |
| Curiosity about impact | `/bmad-impact` | Analysis only, no changes |
| Existing pattern to replicate | `/bmad-pattern` | Extract → propose → confirm |
| First time setup | `/bmad-setup` | Scan repos, create context |

---

## How It's Organized

```
.bmad/
├── agents/          ← AI persona definitions (you don't need to touch these)
├── checklists/      ← Quality gates for code review
├── templates/       ← (extensible) output templates
└── workflows/       ← (extensible) custom workflows

.github/
├── copilot-instructions.md    ← Context loaded on every chat (edit for your repo names)
├── instructions/              ← Auto-applied when editing Java or TypeScript files
└── prompts/                   ← The slash commands you use in Copilot Chat

docs/                          ← All artifacts live here
├── project-context.md         ← Generated by /bmad-setup
├── briefs/                    ← Discovery output
├── prd.md                     ← Product requirements
├── architecture.md            ← Technical design + API contracts
└── stories/                   ← Implementation stories with task checklists
    ├── S-1.1.md
    ├── S-1.2.md
    └── ...
```

---

## Tips

- **Select Opus** in the Copilot Chat model picker for best results on complex multi-file work.
- Run `/bmad-setup` first — the project context it creates makes everything else significantly better.
- For large features, use `/bmad-propose` and review each stage carefully. For small changes, `/bmad-from-req` or `/bmad-from-stories` is faster.
- `/bmad-impact` is your best friend before touching shared code. Use it liberally.
- If generated code doesn't match your conventions, update `.github/instructions/java.instructions.md` or `angular.instructions.md` — these are auto-applied whenever Copilot edits files in those repos.
- All artifacts in `docs/` are plain markdown. Edit them directly if the system got something wrong — subsequent commands will read your edits.
- The system uses terminal commands (`cat >`, `sed -i`) for writing files in both repos because VS Code's file edit API may not have write access to sibling folders.
