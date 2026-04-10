---
applyTo: "**/*.java,**/*.ts,**/*.component.ts"
description: "Automatically triggered when working with source files or when user asks about code quality, refactoring, technical debt, smells, or code improvement"
---

# Code Quality Skills

When quality or improvement concerns arise:

- **interactive-refactoring-agent** (`.claude/skills/interactive-refactoring-agent/SKILL.md`)
  Triggers: "refactor this class", "break up this service", "help me refactor",
  "step by step refactoring", "split this class", "refactor interactively"
  NOTE: This agent analyses FIRST, presents a priority menu, then waits for
  user selection before writing any code.

- **code-smell-detector** (`.claude/skills/code-smell-detector/SKILL.md`)
  Triggers: "code smells", "code quality", "God class", "long methods",
  "complexity", "messy code", "structural problems"

- **technical-debt-quantifier** (`.claude/skills/technical-debt-quantifier/SKILL.md`)
  Triggers: "technical debt", "debt cost", "debt register", "how much debt",
  "cost of not fixing", "debt financial model"

- **refactoring-advisor** (`.claude/skills/refactoring-advisor/SKILL.md`)
  Triggers: "how to refactor", "refactoring plan", "extract method",
  "split this", "simplify", "reduce complexity" (without interactive mode)

Load the relevant SKILL.md before generating any refactored code.
Follow the skill's code quality rules (constructor injection, OnPush, etc.)
