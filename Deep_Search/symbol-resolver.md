# Sub-Agent: Symbol Resolver

A focused sub-agent that resolves a symbol name to its full context — definition, signature, documentation, and location.

## When to invoke
The parent agent encounters a symbol name (function, class, type, variable) and needs to understand what it is before proceeding with deeper analysis.

## Protocol

Given a symbol name:

1. **Find definition** — Search for where the symbol is defined
   - Search: `{symbolName}` (definition)
   - Search: `function {symbolName}` / `class {symbolName}` / `type {symbolName}` / `interface {symbolName}`

2. **Extract signature** — Get the full function/class/type signature
   - Parameters and their types
   - Return type
   - Generic constraints
   - Decorators or annotations

3. **Find documentation** — Look for JSDoc, docstrings, or comments
   - Search: comments immediately above the definition
   - Search: README or docs that mention this symbol

4. **Determine scope** — Is it exported? Internal? Deprecated?
   - Is it `export`ed / `pub` / capitalized (Go)?
   - Are there deprecation markers?
   - Is it behind a feature flag?

## Output

```
SYMBOL: {name}
DEFINED: {file:line}
TYPE: function | class | interface | type | variable | constant
SIGNATURE: {full signature}
EXPORTED: yes | no (internal)
DEPRECATED: yes (reason) | no
DOCS: {extracted documentation or "none found"}
USED BY: {N} files (list top 3)
```
