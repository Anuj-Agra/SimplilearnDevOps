# PEGA Reverse Engineering — Agent & Skill Toolkit

## What This Is

A set of **copy-paste-ready agents and skills** for reverse-engineering a PEGA codebase using only VS Code + Copilot Chat. No Java, no Python, no PEGA runtime needed. You only need your exported **manifest JSON** and **binary (.bin)** files.

## Quick Start (60 seconds)

1. **Copy this entire folder** into your VS Code workspace root
2. **Open Copilot Chat** (Ctrl+Shift+I or Cmd+Shift+I)
3. **Drop a manifest JSON** into the chat along with the agent prompt
4. **Follow the orchestrator** — paste from `ORCHESTRATOR.md` to get step-by-step guidance

## How To Use With Copilot Chat

### Method 1: Direct Paste (Fastest)
```
1. Open any agent file (e.g., agents/01-flow-analyzer.md)
2. Select ALL text (Ctrl+A)
3. Open Copilot Chat
4. Paste the agent text + drag-drop your manifest JSON file
5. Press Enter
```

### Method 2: File Reference
```
In Copilot Chat, type:
  @workspace /explain #file:agents/01-flow-analyzer.md

Then follow up with:
  "Now apply this analysis to the attached manifest"
  [drag-drop your JSON file]
```

### Method 3: Using VS Code Tasks
```
1. Open Command Palette (Ctrl+Shift+P)
2. Type "Tasks: Run Task"
3. Select the agent task you want to run
4. Copilot will be pre-loaded with instructions
```

## Folder Structure

```
pega-reverse-engineering/
│
├── README.md                  ← You are here
├── ORCHESTRATOR.md            ← Master workflow — start here
│
├── config/
│   └── project-config.md      ← Your app hierarchy + manifest versions
│
├── agents/                    ← Self-contained analysis agents (copy-paste)
│   ├── 01-flow-analyzer.md
│   ├── 02-decision-mapper.md
│   ├── 03-integration-scanner.md
│   ├── 04-ui-extractor.md
│   ├── 05-deep-analyzer.md
│   ├── 06-frd-generator.md
│   └── 07-diagram-builder.md
│
├── skills/                    ← Reusable capabilities (referenced by agents)
│   ├── recursive-tracer.md
│   ├── manifest-parser.md
│   ├── condition-extractor.md
│   ├── screenshot-navigator.md
│   └── output-formatter.md
│
├── workspace/                 ← Persistent tracking (edit as you go)
│   ├── MASTER-TASK-LIST.md
│   ├── analysis-log.md
│   └── findings/              ← Drop agent outputs here
│       └── .gitkeep
│
├── templates/                 ← Output templates
│   ├── flow-template.md
│   ├── decision-template.md
│   ├── integration-template.md
│   └── frd-section-template.md
│
├── references/                ← PEGA knowledge base for agents
│   ├── pega-rule-types.md
│   └── pega-manifest-schema.md
│
└── .vscode/
    └── tasks.json             ← VS Code task runner shortcuts
```

## Workflow Order

```
Step 1: Edit config/project-config.md with YOUR app details
Step 2: Run Agent 01 (Flow Analyzer) on each major flow
Step 3: Run Agent 02 (Decision Mapper) on identified decision rules
Step 4: Run Agent 03 (Integration Scanner) on connectors
Step 5: Run Agent 04 (UI Extractor) on screens/sections
Step 6: Run Agent 05 (Deep Analyzer) iteratively on complex flows
Step 7: Run Agent 07 (Diagram Builder) to create Mermaid flowcharts
Step 8: Run Agent 06 (FRD Generator) with ALL prior outputs
```

Update `workspace/MASTER-TASK-LIST.md` after each step.

## Tips

- **Start small**: Pick ONE flow and run it through all agents before scaling
- **Chain outputs**: Each agent's output becomes the next agent's input
- **Use screenshots**: Drag PEGA Designer Studio screenshots into Copilot for visual cross-referencing
- **Save everything**: Drop all agent outputs into `workspace/findings/`
- **Track progress**: The MASTER-TASK-LIST.md is your single source of truth
