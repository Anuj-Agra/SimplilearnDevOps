# PegaRE — Intelligent Pega Reverse Engineering

**Works perfectly with GitHub Copilot!** Just tell it what you want in plain English, and PegaRE automatically selects the right agents and generates the documentation you need.

```bash
# Natural language interface - GitHub Copilot powered
python -m pega_re.auto_dispatcher "analyze my pega application" --input /path/to/extracted_jars
python -m pega_re.auto_dispatcher "extract all tasks and workflows" --input /path/to/extracted_jars  
python -m pega_re.auto_dispatcher "generate executive summary" --input /path/to/extracted_jars

# Or use GitHub Copilot Chat with skill files step-by-step
python -m pega_re.auto_dispatcher "generate copilot workflow" --input /path/to/jars
```

**Scale target:** 200,000+ rules across multiple rulesets.
**Perfect for:** Technical Program Managers using GitHub Copilot for modernization programs.
**No external APIs needed:** Works completely offline with deterministic Python modules.

## What You Get

🎯 **Task Generation Ledger** — Every assignment: what task, triggered when, routed to whom, with which SLA
📋 **Executive Documentation** — Steering committee-ready program overview
🌳 **Application Hierarchy** — Ruleset → Class → Property tree with inheritance
🔄 **Process Maps** — Case Type → Stage → Step → Flow diagrams
🖼️ **UI Catalog** — Every screen rendered as browsable HTML
📊 **Metrics Dashboard** — Rule counts, complexity, modernization readiness

## Natural Language Commands

| What You Say | What It Does | Outputs |
|---|---|---|
| `"analyze my pega application"` | Complete analysis | Program documentation + all deliverables |
| `"extract all tasks and workflows"` | Task-focused analysis | Interactive task ledger with SLAs |
| `"show me the UI screens"` | UI analysis | Browsable HTML catalog of every screen |
| `"build class hierarchy"` | Structure analysis | Collapsible dependency tree |
| `"generate executive summary"` | Leadership reporting | 1-page summary + metrics |
| `"validate my input files"` | Diagnostics | File inventory + health check |

## Quick Start (3 commands)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Analyze (replace with your JAR path)
python -m pega_re.auto_dispatcher "analyze my pega application" \
    --input /path/to/extracted_jars \
    --app-name "Your Application Name"

# 3. Open results
open ./pegare_output/program_doc.html
```

## Three Ways to Use with GitHub Copilot

### 1. **Copilot Chat Workflow** (Step-by-step prompts)
```bash
# Generate sequential prompts for Copilot Chat
python -m pega_re.auto_dispatcher "generate copilot workflow" --input /path/to/jars

# Then copy-paste each prompt into GitHub Copilot Chat
```

### 2. **Direct Python Integration** (No AI needed)  
```python
from pega_re import extractor, parser, tasks

# Pure deterministic analysis
extraction = extractor.extract_and_catalog("/path/to/jars", "./output")
task_data = tasks.extract("./output/catalog.sqlite", "./output")
```

### 3. **Natural Language Interface** (Copilot-powered)
```bash
pegare "analyze my pega application" --input /path/to/extracted_jars
pegare "extract tasks for capacity planning" --input /path/to/jars
```

## Architecture Overview

**🎯 Auto-Dispatcher** — Understands your intent, picks the right agents automatically
**🤖 7 Specialist Agents** — Each has a skill file (prompt) that works with any LLM
**⚡ Streaming Engine** — Handles 200K+ rules without memory issues
**🔄 LangGraph Orchestration** — Checkpointing, resumability, parallel execution

### The Seven Agents
1. **Extractor** → Unpacks JARs, catalogs files
2. **Parser** → Streams XML into typed records  
3. **Hierarchy** → Builds class/ruleset tree
4. **Flow** → Maps business processes
5. **Tasks** → **Answers "who does what when"** ⭐
6. **UI** → Renders screens as HTML
7. **Docs** → Executive-ready documentation

See `COPILOT_INTEGRATION.md` for complete GitHub Copilot setup and `EXTRACTED_JARS_GUIDE.md` for working with your manifest+bin files.

**🔥 Perfect for your setup:** No Claude.ai needed, works 100% with GitHub Copilot, handles extracted JAR directories natively.
