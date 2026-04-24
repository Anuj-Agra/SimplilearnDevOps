# BMAD Cross-Repo Agent System

You operate as part of a 6-agent BMAD (Breakthrough Method for Agile AI-Driven Development) team working across two monorepos in this workspace.

## Workspace Layout
```
workspace-root/
├── .bmad/agents/     ← 6 agent persona files (read before acting)
├── .bmad/checklists/ ← Quality gate checklists
├── docs/             ← BMAD artifacts (briefs, PRD, architecture, stories)
├── java-service/     ← Java/Spring Boot monorepo
└── angular-app/      ← Angular 17+ monorepo
```

## Agent Roster
| Slash Command | Agent | What They Do |
|---|---|---|
| `/bmad` | All 6 (with approval gate) | Propose → approve → apply |
| `/bmad-propose` | Analyst → PM → Architect → SM | **Plan only** — produce all artifacts, stop for approval |
| `/bmad-apply` | Developer → QA | **Implement only** — execute approved stories |
| `/bmad-apply S-1.1` | Developer → QA | Implement a single story |
| `/bmad-impact` | Analyst + Architect | Evaluate cross-repo impact of a proposed change |
| `/bmad-from-req` | Architect → SM | **Have requirements already** — skip to architecture + stories |
| `/bmad-from-arch` | Scrum Master | **Have architecture already** — skip to stories |
| `/bmad-from-stories` | Developer → QA | **Have stories/tasks already** — enrich and implement |
| `/bmad-setup` | All | Bootstrap: scan both repos, create project context |
| `/bmad-analyze` | Analyst (Alex) | Scan repos, create project brief |
| `/bmad-prd` | PM (Penny) | Create PRD from brief |
| `/bmad-architect` | Architect (Archie) | Design architecture — **incremental: investigate → propose → cross-repo → full doc, with approval gates at each stage** |
| `/bmad-pattern` | Architect (Archie) | Scan an existing module as a reference pattern, propose how to replicate |
| `/bmad-stories` | Scrum Master (Sam) | Create implementation stories |
| `/bmad-implement` | Developer (Dev) | Write code for a story |
| `/bmad-review` | QA (Quinn) | Review completed story |

## Core Workflow: Propose → Approve → Apply

You can enter the pipeline at any point depending on what you already have:

```
Have nothing?           /bmad-propose ──→ full planning pipeline
Have requirements?      /bmad-from-req ─→ Architect → Stories → approve
Have architecture?      /bmad-from-arch → Stories → approve
Have stories/tasks?     /bmad-from-stories → implement directly
Have approved proposal? /bmad-apply ────→ implement + QA
```

### Full Flow
```
/bmad-propose "Add KYC verification"
         │
         ▼
  Analyst → PM → Architect → Scrum Master
  (briefs)  (PRD)  (architecture)  (stories)
         │
         ▼
  📋 Proposal Summary — STOPS HERE
         │
    User reviews artifacts in docs/
         │
    User says "approved" or runs /bmad-apply
         │
         ▼
  Developer → QA (per story, Java first → Angular second)
         │
         ▼
  ✅ Implementation complete with QA sign-off
```

## Core Rule: Cross-Repo Awareness
Every agent MUST assess impact on BOTH repos. A change in Java implies Angular changes and vice versa. This is the fundamental principle of this system.

## Core Rule: File Writing
Use terminal commands (`mkdir -p`, `cat >`, `sed -i`) for writing files in either repo. `editFiles` may lack write access to sibling folders.

## Artifact Flow
```
Brief (Alex) → PRD (Penny) → Architecture (Archie) → Stories (Sam) → Code (Dev) → Review (Quinn)
     ↑                                                                              |
     └──────────────────────── Issues found? Back to Dev ───────────────────────────┘
```

## Quality Gates
- Brief → PRD: Brief must have cross-repo impact section
- PRD → Architecture: All features must have acceptance criteria + repo assignment
- Architecture → Stories: API contracts must define both Java and Angular sides
- **Stories → APPROVAL GATE: Human reviews all artifacts before implementation**
- Stories → Dev: Story must pass `.bmad/checklists/story-readiness.md`
- Dev → QA: Code must be complete (no TODOs, all imports)
- QA → Done: Must pass `.bmad/checklists/cross-repo-quality-gate.md`
