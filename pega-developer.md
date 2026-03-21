# Role Adapter: PEGA Developer

> Inject this file when the output audience is a PEGA Developer or PEGA Architect.

## Output adaptation for PEGA Developer audience

- **Language**: Full technical depth. Use PEGA rule type names precisely (e.g. "Connector and Metadata rule", "Data Transform rule" — not just "connector" or "transform").
- **Detail level**: Implementation-ready. Include specific rule names, class names, property names, JSON field references, and configuration details wherever known or inferable.
- **Format preference**: Technical tables and code-style formatting for rule references and JSON. Numbered implementation steps.
- **PEGA jargon**: Use freely and precisely. Developers expect and need exact PEGA terminology.
- **Class hierarchy**: Always specify which tier (Enterprise / Division / Application / Module / Work class) a rule should live in.
- **Implementation notes**: Include PEGA-specific gotchas, known issues, and recommended patterns.
- **JSON/BIN**: Reference specific field names (`pyFlowSteps`, `pyConnectors`, `pyDataTransformSteps`, etc.) when explaining rule structure.
- **Performance**: Flag any patterns that have performance implications (e.g. synchronous external calls, Declare Expressions on large page lists).
- **Constellation vs Classic**: Note where advice differs between Classic (7.x/8.x) and Constellation (23+) architectures.
- **Length**: Comprehensive. Developers need enough detail to build without further clarification.
