---
applyTo: "**/pom.xml,**/build.gradle,**/package.json,**/settings.gradle,**/*.gradle.kts"
description: "Automatically triggered when working with build files, dependency declarations, or when user asks about module structure, dependencies, or architecture"
---

# Graph & Architecture Skills

When the user asks about module structure, dependencies, what depends on what,
or wants to scan/visualise the codebase, invoke:

- **repo-graph-architect** (`.claude/skills/repo-graph-architect/SKILL.md`)
  Triggers: "graph my repo", "scan dependencies", "build dependency tree",
  "module hierarchy", "visualize", "map my modules"

- **graph-intelligence-suite** (`.claude/skills/graph-intelligence-suite/SKILL.md`)
  Triggers: "what depends on", "blast radius", "circular dependencies",
  "dead modules", "most critical module", "trace dependency", "impact of changing"
  REQUIRES: `graph/repo-graph.json` to exist first

- **migration-planner** (`.claude/skills/migration-planner/SKILL.md`)
  Triggers: "migration plan", "modernisation", "phase the migration",
  "mainframe migration", "strangler fig", "decommission order"

- **change-impact-analyser** (`.claude/skills/change-impact-analyser/SKILL.md`)
  Triggers: "impact of this change", "what breaks", "regression scope",
  "what do I need to retest", "PR impact"

Load the skill SKILL.md before responding. Check for `graph/repo-graph.json` first.
