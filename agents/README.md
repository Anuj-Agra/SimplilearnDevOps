# Agents

Each sub-folder is a self-contained agent definition.

## Naming convention

```
NN-agent-name/
├── system-prompt.md   ← Full system prompt. Copy verbatim into Claude or API system field.
└── config.json        ← Recommended model, temperature, max_tokens, skill dependencies.
```

## Version history

Track changes to prompts using Git. Tag releases as `v<major>.<minor>` when prompts are validated against real PEGA output.

## Testing a prompt

1. Copy `system-prompt.md` contents
2. Open Claude.ai → New conversation → (in a Project) paste as System Prompt
3. Use the matching example from `examples/sample-inputs/`
4. Compare output against `examples/sample-outputs/`
