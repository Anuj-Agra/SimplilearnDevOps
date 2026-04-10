---
name: jira-ticket-generator
description: >
  Convert FRD sections, gap-detector findings, or feature descriptions into structured
  Jira epics, stories, and subtasks — with acceptance criteria, story point estimates,
  component labels, and priority. Use when asked: 'create Jira tickets', 'write user
  stories', 'backlog items', 'generate tickets', 'Jira stories from FRD', 'sprint
  backlog', 'create epics', 'acceptance criteria', 'story points', 'breakdown this
  feature'. Produces tickets ready to paste into Jira or export as JSON.
---
# JIRA Ticket Generator

Convert analysis outputs into structured, ready-to-use Jira tickets.

## Input Sources (ask user which)
1. **From FRD** — each FR-XXX becomes a story, each module becomes an epic
2. **From gap-detector** — each gap becomes a bug or improvement ticket
3. **From feature description** — free-text broken into structured tickets
4. **From use case** — each use case becomes an epic with story children

## Ticket Anatomy

### Epic
```
TYPE: Epic
TITLE: [Business capability name — matches FRD module name]
DESCRIPTION:
  As a product team, we want to [deliver this capability] so that [business outcome].

  Scope (from FRD Section 2):
  In scope: [bulleted list]
  Out of scope: [bulleted list]

ACCEPTANCE CRITERIA:
  All child stories completed and accepted by PO
  FRD section [X] fully implemented
  Gap-detector re-run shows 0 critical/high gaps for this module

LABELS: [module-name], [sprint-label], [team-label]
PRIORITY: [Critical/High/Medium/Low]
STORY POINTS: [sum of children]
```

### Story
```
TYPE: Story
PARENT: [Epic]
TITLE: As a [role], I can [action] so that [benefit]

DESCRIPTION:
  [2-3 sentence context paragraph]

  FRD Reference: FR-[MOD]-[###]

ACCEPTANCE CRITERIA (Given/When/Then):
  Scenario: [happy path name]
  Given:  [precondition]
  When:   [user action]
  Then:   [expected result]
  And:    [additional assertion]

  Scenario: [validation failure]
  Given:  [user on the screen]
  When:   [submits with invalid data]
  Then:   [specific error message appears]

  Scenario: [permission check]
  Given:  [user without permission]
  When:   [attempts to access]
  Then:   [redirected / error shown]

STORY POINTS: [1/2/3/5/8/13 — use Fibonacci]
  Estimate rationale:
    1-2: Simple CRUD, no business logic
    3-5: Form with validation + business rules
    8:   Multi-step workflow or complex rules
    13:  Cross-module feature or new integration

LABELS: [module], [frontend/backend/fullstack], [sprint]
PRIORITY: [based on FRD section and gap severity]
```

### Bug (from gap-detector)
```
TYPE: Bug
TITLE: [Gap ID]: [Plain English description of the missing scenario]
SEVERITY: [Critical/High/Medium/Low — from gap severity]

DESCRIPTION:
  Gap Reference: [FG/TG/SG/PG]-[###]
  
  Current behaviour: [what happens now — or "not handled"]
  Expected behaviour: [what should happen]
  Impact: [user/business impact]

STEPS TO REPRODUCE:
  1. [Set up the condition]
  2. [Perform the action]
  3. [Observe the incorrect result]

ACCEPTANCE CRITERIA:
  Given: [condition from gap]
  When:  [action]
  Then:  [correct behaviour]

STORY POINTS: [estimate]
```

## Batch Output Format
Produce a complete sprint backlog in this order:
1. Epics (one per FRD module)
2. Stories (ordered by FRD section)
3. Bugs (ordered by gap severity: Critical → High → Medium)
4. Summary table: [Total epics, stories, bugs, estimated points]

## JSON Export Option (for Jira API import)
```json
{
  "issues": [
    {
      "fields": {
        "project": { "key": "PROJ" },
        "issuetype": { "name": "Story" },
        "summary": "[title]",
        "description": "[description]",
        "priority": { "name": "High" },
        "labels": ["module-name"],
        "story_points": 5
      }
    }
  ]
}
```
