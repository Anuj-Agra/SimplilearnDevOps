# PegaRE Installation & Setup Guide

## Quick Start (5 minutes)

### 1. Clone and Install
```bash
# Clone the repository (or download the zip file)
git clone <your-repo-url> pegare
cd pegare

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pega_re; print('✅ PegaRE installed successfully')"
```

### 2. Test with Sample Data
```bash
# Run the auto-dispatcher to see available commands
python -m pega_re.auto_dispatcher --help

# Test with your Pega JAR files
python -m pega_re.auto_dispatcher "analyze my pega application" \
    --input /path/to/extracted_jars \
    --output ./analysis_results
```

### 3. View Results
```bash
# Open the generated documentation
open ./analysis_results/program_doc.html
open ./analysis_results/task_ledger.html
```

---

## Detailed Installation

### System Requirements
- **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11)
- **Memory:** 4GB+ RAM (for large applications with 200K+ rules)
- **Storage:** 2GB+ free space (for unpacked JARs + generated outputs)
- **OS:** Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)

### Dependencies Explained
```bash
# Core dependencies (always required)
pip install lxml networkx

# LangGraph orchestration (recommended for large apps)
pip install langgraph langchain-core

# Optional but helpful
pip install pandas jupyter plotly  # For data analysis
pip install pytest black mypy      # For development
```

### Installation Options

#### Option A: Standard Installation
```bash
# Download the PegaRE package
wget <download-url> -O pegare.zip
unzip pegare.zip
cd pegare

# Install dependencies
pip install -r requirements.txt

# Test installation
python examples/run_full_pipeline.py --validate-only /path/to/test_data
```

#### Option B: Virtual Environment (Recommended)
```bash
# Create isolated environment
python -m venv pegare_env
source pegare_env/bin/activate  # On Windows: pegare_env\Scripts\activate

# Install in virtual environment
cd pegare
pip install -r requirements.txt

# Create launcher script
echo '#!/bin/bash
source /path/to/pegare_env/bin/activate
cd /path/to/pegare
python -m pega_re.auto_dispatcher "$@"' > pegare_launcher.sh
chmod +x pegare_launcher.sh
```

#### Option C: Docker Installation (For Complex Environments)
```bash
# Build Docker container
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y git
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "-m", "pega_re.auto_dispatcher"]
EOF

docker build -t pegare .
docker run -v /path/to/jars:/data/input -v /path/to/output:/data/output \
    pegare "analyze pega application" --input /data/input --output /data/output
```

---

## Using the Auto-Dispatcher

The auto-dispatcher automatically selects the right agents based on your request:

### Natural Language Commands

```bash
# Complete analysis
python -m pega_re.auto_dispatcher "analyze my pega application" \
    --input /path/to/jars --output ./results

# Focus on specific areas
python -m pega_re.auto_dispatcher "extract all tasks and workflows" \
    --input /path/to/jars

python -m pega_re.auto_dispatcher "show me the UI screens and forms" \
    --input /path/to/jars

python -m pega_re.auto_dispatcher "build class hierarchy and dependencies" \
    --input /path/to/jars

python -m pega_re.auto_dispatcher "generate executive summary for steering committee" \
    --input /path/to/jars --app-name "CRD KYC Platform"
```

### Keyword Mapping
The system automatically detects intent from keywords:

| Keywords | Agents Called | Output |
|---|---|---|
| `analyze`, `full`, `complete`, `everything` | All agents | Complete program documentation |
| `tasks`, `assignments`, `workflows`, `SLA` | extractor → parser → flow → tasks | Task ledger |
| `UI`, `screens`, `forms`, `harness`, `section` | extractor → parser → ui | UI catalog |
| `hierarchy`, `classes`, `dependencies` | extractor → parser → hierarchy | Class tree |
| `flows`, `processes`, `case types` | extractor → parser → flow | Process diagrams |
| `executive`, `summary`, `report` | Full pipeline → doc-synthesizer | Executive summary |

### Advanced Options

```bash
# Resume from checkpoint
python -m pega_re.auto_dispatcher "continue analysis" --resume checkpoint-123

# Specify app context
python -m pega_re.auto_dispatcher "analyze for executive presentation" \
    --app-name "Mainframe Modernization Program" \
    --context "steering-committee"

# Export specific format
python -m pega_re.auto_dispatcher "extract tasks as CSV" \
    --input /path/to/jars --format csv

# Verbose mode
python -m pega_re.auto_dispatcher "show me everything" \
    --input /path/to/jars --verbose
```

---

## Integration with Your Workflow

### For GitHub Copilot Users
```bash
# Generate step-by-step prompts for Copilot Chat
python -m pega_re.auto_dispatcher "generate copilot workflow" \
    --input /path/to/jars --output ./copilot_prompts
```

### For Jupyter/Analysis Workflows
```python
# In Jupyter notebook
from pega_re.auto_dispatcher import PegaAnalyzer

analyzer = PegaAnalyzer()
result = analyzer.analyze_from_text(
    "show me all the tasks and their SLAs",
    input_dir="/path/to/jars"
)

# Access structured data
import pandas as pd
tasks_df = pd.read_csv(result.task_ledger_csv)
print(f"Found {len(tasks_df)} tasks across {tasks_df['CaseType'].nunique()} case types")
```

### For CI/CD Pipelines
```yaml
# GitHub Actions example
- name: Analyze Pega Application
  run: |
    python -m pega_re.auto_dispatcher "generate program documentation" \
        --input ./pega-exports \
        --output ./analysis \
        --format json-summary
    
    # Upload results to Confluence/SharePoint
    curl -X POST "$CONFLUENCE_API/content" \
        -H "Content-Type: application/json" \
        -d @./analysis/api_summary.json
```

---

## Troubleshooting

### Common Issues

**"No module named 'pega_re'"**
```bash
# Make sure you're in the right directory
cd /path/to/pegare
python -c "import sys; print(sys.path)"

# Or add to Python path
export PYTHONPATH="/path/to/pegare:$PYTHONPATH"
```

**"No JAR files found"**
```bash
# Check your input directory structure
python -m pega_re.auto_dispatcher "validate my input" --input /path/to/jars
# Should show: ✅ Found X JAR files or extracted directories
```

**"Memory error with large applications"**
```bash
# Use LangGraph for better memory management
python -m pega_re.auto_dispatcher "analyze with checkpointing" \
    --input /path/to/jars --method langgraph
```

**"Parse errors on rule files"**
```bash
# Run in verbose mode to see which files are failing
python -m pega_re.auto_dispatcher "diagnose parsing issues" \
    --input /path/to/jars --verbose

# Check the review queue in generated documentation
open ./output/program_doc.html#review-queue
```

### Performance Tuning

**For applications with 200K+ rules:**
```bash
# Use streaming mode with progress checkpoints
python -m pega_re.auto_dispatcher "analyze large application" \
    --input /path/to/jars \
    --batch-size 5000 \
    --checkpoint-every 50000
```

**For faster development/testing:**
```bash
# Analyze just the first ruleset
python -m pega_re.auto_dispatcher "quick analysis of main ruleset" \
    --input /path/to/jars \
    --filter "ruleset:MyCoKYC*"
```

---

## Environment Setup for Different Teams

### Product Owner / Business Analyst
```bash
# Focus on business process understanding
alias pega-business="python -m pega_re.auto_dispatcher 'show business processes and tasks'"
alias pega-summary="python -m pega_re.auto_dispatcher 'executive summary'"

pega-business --input /path/to/jars
pega-summary --input /path/to/jars --app-name "Your App"
```

### Technical Lead / Architect
```bash
# Focus on technical dependencies and complexity
alias pega-tech="python -m pega_re.auto_dispatcher 'full technical analysis'"
alias pega-deps="python -m pega_re.auto_dispatcher 'show dependencies and hierarchy'"

pega-tech --input /path/to/jars --verbose
pega-deps --input /path/to/jars
```

### Program Manager / PMO
```bash
# Focus on executive reporting and metrics
alias pega-metrics="python -m pega_re.auto_dispatcher 'generate metrics for steering committee'"
alias pega-roadmap="python -m pega_re.auto_dispatcher 'roadmap analysis'"

pega-metrics --input /path/to/jars --app-name "Modernization Program"
```

---

## Next Steps

1. **Test with your data:** Run `python -m pega_re.auto_dispatcher "validate input" --input /your/jar/path`
2. **First analysis:** `python -m pega_re.auto_dispatcher "analyze my application" --input /your/jar/path`
3. **Review outputs:** Open the generated HTML files in your browser
4. **Integrate:** Set up aliases or scripts for your team's workflow
5. **Scale up:** Use LangGraph mode for production analysis of large applications

For support or questions, check the troubleshooting section above or review the generated `program_doc.html` which includes a detailed review queue of any issues found.
