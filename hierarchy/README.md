# Hierarchy Context Files

PEGA uses a 4-tier class inheritance model. These context files scope all agent output to the correct tier of your client's PEGA codebase.

## How to use

1. Identify the hierarchy tier relevant to your analysis (Enterprise, Division, Application, or Module/Work type)
2. Open the corresponding `context.md` file
3. **Fill in your client's actual class names, application names, and RuleSet versions**
4. Inject the completed context file into your agent prompt alongside the skill files

## Injection location

Add the hierarchy context file at the end of the assembled system prompt, after skill files, before the role adapter:

```
[Agent system-prompt.md]
[Skill files...]
--- 
# Client PEGA Hierarchy Context
[hierarchy/L<n>-<tier>/context.md content]
---
[Role adapter]
```

## When to use which tier

| Tier | Use when analysing... |
|------|----------------------|
| L1 Enterprise | Shared data models, enterprise-wide rules, Org- classes |
| L2 Division | Division-level policy rules, Div- class overrides |
| L3 Application | Application flows, application-level UI, application connectors |
| L4 Module | Specific work type flows (CDD, EDD), work class UI, work class SLAs |
