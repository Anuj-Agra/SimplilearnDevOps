# Cody Agent System — Global Instructions

These instructions apply to ALL Cody agents and any Copilot Chat interaction in this workspace.

## Search-First Principle

All Cody agents follow a **search-first** architecture:
1. NEVER answer a question about code from memory or assumption
2. ALWAYS search the codebase first, then answer based on what you find
3. If a search returns no results, try broader or alternative queries
4. Cite specific file paths and line numbers in every response

## Context Building Rules

When exploring code, build context **recursively**:
- Found a function → search for its callers AND callees
- Found a type → search for all implementations AND usages
- Found an import → trace it to its source module
- Found a config value → find where it's read AND where it's set
- Found a test → find the code it tests AND related test files

## Response Quality Standards

Every response must include:
- **File paths**: Always reference actual files, never say "somewhere in the codebase"
- **Evidence**: Show the code or search results that support your analysis
- **Confidence level**: State whether you found definitive evidence or are inferring
- **Next steps**: Suggest which Cody sub-agent can go deeper if needed

## Tool Usage Priority

When answering questions about code, use tools in this order:
1. `search/symbol` — for specific function/class/type lookups
2. `search/usages` — for finding all references to a symbol
3. `search/codebase` — for natural language queries across the codebase
4. `search/file` — for finding files by name or pattern
5. `readFile` — for reading full file contents when snippets aren't enough
6. `runInTerminal` — for running grep, find, or other discovery commands

## Conventions

- Always refer to files with paths relative to workspace root
- When showing code, always include the file path as context
- Use markdown code blocks with the correct language identifier
- When multiple options exist, present them as a ranked list with tradeoffs
- Don't repeat information the user already knows
