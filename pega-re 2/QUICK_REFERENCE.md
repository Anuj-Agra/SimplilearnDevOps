# PegaRE Quick Reference Card

## Installation
```bash
pip install -r requirements.txt
```

## Most Common Commands

### Complete Analysis
```bash
# For extracted JAR directories (manifest + bin files)
python -m pega_re.auto_dispatcher "analyze my pega application" \
    --input /path/to/extracted_jar_directories --app-name "Your App"

# For original JAR files (if you still have them)
python -m pega_re.auto_dispatcher "analyze my pega application" \
    --input /path/to/jar_files --app-name "Your App"
```

### Specific Analysis Types
```bash
# Task extraction (who does what when) - works with extracted JAR directories
python -m pega_re.auto_dispatcher "extract all tasks and workflows" --input /path/to/extracted_dirs

# UI screens and forms
python -m pega_re.auto_dispatcher "show me the UI screens" --input /path/to/extracted_dirs

# Class hierarchy and dependencies  
python -m pega_re.auto_dispatcher "build class hierarchy" --input /path/to/extracted_dirs

# Executive summary for management
python -m pega_re.auto_dispatcher "generate executive summary" \
    --input /path/to/extracted_dirs --app-name "Modernization Program"
```

### GitHub Copilot Workflow
```bash
# Generate step-by-step prompts for GitHub Copilot Chat
python -m pega_re.auto_dispatcher "generate copilot workflow" \
    --input /path/to/extracted_dirs --output ./copilot_prompts

# Then copy each prompt into Copilot Chat one by one
# Perfect for: Learning the system, custom analysis, integration projects
```

### Troubleshooting
```bash
# Validate input files
python -m pega_re.auto_dispatcher "validate my input" --input /path/to/jars

# Diagnose parsing issues
python -m pega_re.auto_dispatcher "troubleshoot issues" --input /path/to/jars --verbose
```

### GitHub Copilot Workflow
```bash
python -m pega_re.auto_dispatcher "generate copilot workflow" \
    --input /path/to/jars --output ./prompts
```

## Key Output Files

| File | What It Contains |
|---|---|
| `program_doc.html` | Complete navigable documentation |
| `executive_summary.md` | 1-page steering committee summary |
| `task_ledger.html` | Every task with routing & SLAs |
| `ui/index.html` | Browsable catalog of all screens |
| `hierarchy.html` | Collapsible class dependency tree |
| `catalog.sqlite` | Complete rule database |

## Advanced Options

```bash
# Resume from checkpoint (large apps)
python -m pega_re.auto_dispatcher "continue analysis" --resume checkpoint-123

# LangGraph orchestration (better for 200K+ rules)
python -m pega_re.auto_dispatcher "analyze with checkpointing" \
    --input /path/to/jars --method langgraph

# JSON output for API integration
python -m pega_re.auto_dispatcher "analyze my app" \
    --input /path/to/jars --format json > results.json
```

## For Your Modernization Program

```bash
# Monthly steering committee update
python -m pega_re.auto_dispatcher "generate metrics for steering committee" \
    --input /path/to/pega_jars \
    --app-name "CRD KYC Modernization" \
    --output ./monthly_reports/$(date +%Y%m)

# Workstream capacity planning
python -m pega_re.auto_dispatcher "extract tasks for capacity planning" \
    --input /path/to/jars

# UI modernization inventory
python -m pega_re.auto_dispatcher "catalog all screens for UI modernization" \
    --input /path/to/jars
```

## Natural Language Keywords

| Intent | Keywords That Work |
|---|---|
| Full analysis | analyze, complete, everything, comprehensive |
| Task extraction | tasks, assignments, workflows, SLA, routing |
| UI analysis | UI, screens, forms, harness, section, interface |
| Hierarchy | hierarchy, classes, dependencies, structure |
| Process flows | flows, processes, case types, stages |
| Executive reporting | executive, summary, report, management |
| Validation | validate, check, verify, diagnose |

## Troubleshooting

**"No module named 'pega_re'"**
```bash
cd /path/to/pegare && python -c "import pega_re; print('OK')"
```

**"No JAR files found"**
```bash
python -m pega_re.auto_dispatcher "validate input" --input /your/path
```

**"Memory error"**
```bash
python -m pega_re.auto_dispatcher "analyze with checkpointing" \
    --input /path/to/jars --method langgraph
```

## Quick Aliases (Optional)
```bash
# Add to your ~/.bashrc or ~/.zshrc
alias pegare="python -m pega_re.auto_dispatcher"
alias pegare-validate="pegare 'validate input'"
alias pegare-analyze="pegare 'analyze my pega application'"
alias pegare-tasks="pegare 'extract all tasks'"
alias pegare-ui="pegare 'show UI screens'"
```

Then use: `pegare-analyze --input /path/to/jars`
