# OpenSpec Cross-Repo Linker

Links two repositories' OpenSpec workflows so that API-surface changes automatically propagate between your **Java microservice** and **Angular frontend**.

## The Problem

Both repos have OpenSpec initialized and work great independently. But when the Java service adds an endpoint, nothing tells the Angular app it needs a matching service + model. You end up with drift, missing types, and broken integrations.

## The Solution

A lightweight **linking layer** that sits alongside both repos with 12 Copilot Chat slash commands and a background file watcher.

```
your-projects/
├── openspec-cross-repo/         ← this workspace
│   ├── .github/prompts/         (12 slash commands)
│   ├── .vscode/                 (auto-start watcher)
│   ├── scripts/watch-sync.mjs   (background monitor)
│   ├── openspec/specs/contract/ (shared API contract)
│   └── AGENTS.md
├── my-java-service/             ← your Java repo
└── my-angular-app/              ← your Angular repo
```

## Setup (5 minutes)

1. Place this folder alongside your repos
2. Edit `openspec-cross-repo.code-workspace` — update repo paths
3. Edit `.vscode/settings.json` — set `openapiSync.javaRepoPath` and `openapiSync.angularRepoPath`
4. `File → Open Workspace from File → openspec-cross-repo.code-workspace`
5. VS Code Settings → search "prompt files" → enable

The watcher starts automatically in the terminal.

## Auto-Sync (One Command)

```
/xspec-auto
```

Runs 9 phases autonomously: discover → generate specs → detect unlinked changes → propagate → apply Java → apply Angular → verify types → update contract → gap detect. Skips phases with nothing to do.

## Background Watcher

Polls both repos every 3 seconds. Alerts when:
- New API-surface change has no cross-repo link
- Both sides of a linked change are complete (ready to archive)
- One repo archives while the other is still active

## All Slash Commands

| Command | What it does |
|---------|-------------|
| `/xspec-auto` | Run all phases automatically |
| `/xspec-generate-specs` | Generate specs for all domains from code |
| `/xspec-generate-java-specs` | Generate specs from Java only |
| `/xspec-generate-angular-specs` | Generate specs from Angular only |
| `/xspec-generate-domain` | Generate specs for one domain |
| `/xspec-gap-detect` | Compare specs vs code — find drift |
| `/xspec-detect` | Find unlinked API-surface changes |
| `/xspec-propose` | Create linked proposals in both repos |
| `/xspec-propagate` | Propagate change from repo A → repo B |
| `/xspec-apply-both` | Apply linked change in both repos |
| `/xspec-sync-contract` | Update shared contract spec |
| `/xspec-status` | Cross-repo dashboard |

## Tips

- Select **Opus** in the Copilot model picker for best results
- Open both spec files before running commands for extra context
- Run `/xspec-detect` periodically to catch unlinked changes
- Update `.github/instructions/` files to match your code conventions
