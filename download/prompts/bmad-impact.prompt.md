---
mode: 'agent'
description: 'Evaluate the cross-repo impact of a proposed change in one repo on the other repo'
tools: ['search/codebase', 'terminalCommand']
---
# Cross-Repo Impact Analysis

The user describes a change or requirement affecting ONE repo. Your job is to evaluate the impact on the OTHER repo.

## Steps
1. Read `.bmad/agents/analyst.md` for the analysis approach
2. Read `.bmad/agents/architect.md` for the technical contract perspective
3. Scan the affected repo to understand the current implementation
4. Identify ALL touchpoints where this change crosses the API boundary
5. Scan the other repo to find all code that would need to change

## Output Format

```
## Impact Analysis: <Change Description>

### Source Change (in <repo>)
- Files affected: <list>
- Endpoints affected: <list>
- Schemas affected: <list>

### Ripple Effect (on <other repo>)
- **Must Change**: <files/services/models that WILL break without updates>
- **Should Change**: <files that should be updated for consistency>
- **Consider**: <optional improvements enabled by this change>

### Recommended BMAD Action
→ Run /bmad to create the full pipeline for this change
→ Or run /bmad-stories to create stories for just the ripple effects
```

Always assess in BOTH directions — even if the user only mentions one repo.
