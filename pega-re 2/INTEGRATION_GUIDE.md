# Integrating PegaRE into Your Existing Project

## Installation Options

### Option 1: Install as Package (Recommended)
```bash
# From source directory
cd pega-re
python build_package.py --build --install

# Or using pip directly
pip install -e .

# Verify installation
python -c "from pega_re import PegaAnalyzer; print('✅ PegaRE imported successfully')"
```

### Option 2: Copy Module into Project
```bash
# Copy the pega_re module into your existing project
cp -r pega-re/pega_re /your/existing/project/
cp -r pega-re/skills /your/existing/project/
```

## Integration Patterns

### 1. Simple Analysis Integration

```python
# In your existing project code
from pega_re import PegaAnalyzer

def analyze_pega_application(input_path: str, app_name: str) -> dict:
    """Integrate Pega analysis into your workflow."""
    analyzer = PegaAnalyzer()
    
    result = analyzer.analyze_from_text(
        query="analyze my pega application",
        input_dir=input_path,
        output_dir=f"./analysis_output_{app_name.lower().replace(' ', '_')}",
        app_name=app_name
    )
    
    return {
        "success": result.success,
        "program_doc": result.primary_deliverable,
        "task_ledger": result.task_ledger_path,
        "ui_catalog": result.ui_catalog_path,
        "metrics": result.metrics_summary,
        "errors": result.errors
    }

# Usage in your existing workflow
pega_results = analyze_pega_application(
    input_path="/data/extracted_pega_jars",
    app_name="CRD KYC Platform"
)

if pega_results["success"]:
    print(f"Analysis complete: {pega_results['program_doc']}")
    # Integrate with your existing reporting...
```

### 2. Agent-Based Integration

```python
# For more control over the analysis pipeline
from pega_re import PegaREAgentSuite

class YourExistingAnalysisClass:
    def __init__(self):
        self.pega_agents = PegaREAgentSuite()
        
    def run_comprehensive_analysis(self, pega_input: str, mainframe_input: str):
        """Run both Pega and mainframe analysis."""
        
        # Your existing mainframe analysis (MFREA)
        mf_results = self.analyze_mainframe(mainframe_input)
        
        # Pega analysis using PegaRE
        pega_results = self.pega_agents.execute_full_pipeline(
            input_dir=pega_input,
            workdir="./combined_analysis",
            app_name="Integrated Analysis"
        )
        
        # Combine results for executive reporting
        return self.synthesize_results(mf_results, pega_results)
        
    def synthesize_results(self, mf_results, pega_results):
        """Combine mainframe and Pega analysis results."""
        # Your integration logic here
        pass
```

### 3. Individual Module Integration

```python
# Use specific PegaRE modules in your existing pipeline
from pega_re import extractor, parser, tasks

def extract_pega_tasks_only(input_dir: str) -> list:
    """Extract only task information for capacity planning."""
    
    # Step 1: Extract and catalog files
    extraction_result = extractor.extract_and_catalog(
        input_dir=input_dir,
        workdir="./temp_analysis"
    )
    
    if not extraction_result.rule_files:
        return []
    
    # Step 2: Parse rules 
    parse_result = parser.parse_all(
        catalog_path="./temp_analysis/catalog.sqlite",
        unpacked_dir="./temp_analysis/unpacked"
    )
    
    # Step 3: Extract tasks
    task_result = tasks.extract(
        catalog_path="./temp_analysis/catalog.sqlite", 
        workdir="./temp_analysis"
    )
    
    # Return task data for your existing workflow
    import pandas as pd
    task_df = pd.read_csv(task_result.ledger_csv)
    return task_df.to_dict('records')

# Integrate into your existing capacity planning
pega_tasks = extract_pega_tasks_only("/data/pega_jars")
your_existing_capacity_model.add_tasks(pega_tasks)
```

### 4. Scheduled/Automated Integration

```python
# For automated monthly reporting
import schedule
import time
from datetime import datetime
from pega_re import PegaAnalyzer

def monthly_pega_analysis():
    """Automated monthly analysis for steering committee."""
    
    analyzer = PegaAnalyzer()
    timestamp = datetime.now().strftime("%Y%m")
    
    result = analyzer.analyze_from_text(
        query="generate executive summary for steering committee",
        input_dir="/data/pega_production_extract",
        output_dir=f"/reports/monthly/{timestamp}_pega",
        app_name=f"CRD KYC Platform - {datetime.now().strftime('%B %Y')}"
    )
    
    if result.success:
        # Email the executive summary
        send_executive_report(result.executive_summary_path)
        
        # Update your dashboard
        update_modernization_dashboard(result.metrics_summary)
    
    return result

# Schedule monthly execution  
schedule.every().month.do(monthly_pega_analysis)

def send_executive_report(report_path: str):
    """Your existing email integration."""
    pass

def update_modernization_dashboard(metrics: dict):
    """Your existing dashboard integration.""" 
    pass
```

## Configuration for Your Environment

### 1. Skill File Customization

```python
# Customize skill files for your specific needs
from pega_re.agents import PegaREAgentSuite
from pathlib import Path

# Point to your customized skill files
custom_skills_dir = Path("/your/project/custom_skills")
suite = PegaREAgentSuite(project_root=custom_skills_dir.parent)

# Or modify skills programmatically
def customize_task_extraction():
    """Customize task extraction for your specific requirements."""
    task_agent = suite.tasks
    
    # Add your custom logic to the task extraction
    original_skill = task_agent.skill_content
    enhanced_skill = original_skill + """

## Custom Requirements for CRD KYC
- Focus on regulatory compliance tasks
- Identify AML/KYC specific workflows  
- Extract SLA requirements for audit purposes
- Map tasks to regulatory requirements (MiFID II, GDPR)
"""
    task_agent.skill_content = enhanced_skill
    return task_agent
```

### 2. Integration with Your Existing Tools

```python
# Integration with Confluence
def upload_to_confluence(analysis_result):
    """Upload PegaRE results to your Confluence space."""
    if analysis_result.success:
        # Your Confluence API integration
        confluence_client.upload_page(
            space_key="MODERNIZATION",
            title=f"Pega Analysis - {datetime.now().strftime('%B %Y')}",
            content_file=analysis_result.primary_deliverable
        )

# Integration with Excel reporting  
def update_excel_workbook(analysis_result):
    """Update your existing Excel workbooks with Pega metrics."""
    import pandas as pd
    
    # Load task ledger into your Excel template
    tasks_df = pd.read_csv(analysis_result.task_ledger_path.replace('.html', '.csv'))
    
    # Update your capacity planning workbook
    with pd.ExcelWriter('/reports/monthly_capacity.xlsx', mode='a') as writer:
        tasks_df.to_excel(writer, sheet_name='Pega_Tasks', index=False)

# Integration with PowerPoint  
def add_to_steering_deck(analysis_result):
    """Add Pega metrics to your steering committee PowerPoint."""
    from pptx import Presentation
    
    pres = Presentation('/templates/steering_committee_template.pptx')
    
    # Add metrics slide
    slide = pres.slides.add_slide(pres.slide_layouts[1])
    slide.shapes.title.text = "Pega Application Analysis"
    
    # Add key metrics from analysis_result.metrics_summary
    # Your PowerPoint integration logic...
    
    pres.save('/reports/steering_committee_with_pega.pptx')
```

## Example Integration Scenarios

### Scenario 1: Mainframe Modernization Program

```python
class ModernizationProgram:
    def __init__(self):
        self.pega_analyzer = PegaAnalyzer()
        self.mfrea_analyzer = YourMFREAAnalyzer()  # Your existing tool
        
    def monthly_analysis(self):
        """Combined analysis for steering committee."""
        
        # Analyze mainframe components
        mainframe_results = self.mfrea_analyzer.analyze_natural_adabas()
        
        # Analyze Pega components  
        pega_results = self.pega_analyzer.analyze_from_text(
            "generate program metrics for modernization",
            input_dir="/data/pega_extracts"
        )
        
        # Synthesize for executive reporting
        combined_metrics = {
            "mainframe_complexity": mainframe_results.complexity_score,
            "pega_task_count": pega_results.metrics_summary.get("assignments", 0),
            "total_modernization_surface": "calculated from both",
            "recommended_approach": "parallel modernization with Pega as target state"
        }
        
        return combined_metrics
```

### Scenario 2: Continuous Integration

```bash
# Add to your CI/CD pipeline
name: Pega Analysis
on:
  schedule:
    - cron: '0 2 1 * *'  # Monthly on 1st at 2 AM

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install PegaRE
        run: |
          cd pega-re
          pip install -e .
      
      - name: Run Analysis
        run: |
          pegare "generate monthly program metrics" \
            --input ${{ secrets.PEGA_EXTRACT_PATH }} \
            --app-name "CRD KYC - $(date +%B)" \
            --output ./analysis_results
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: pega-analysis
          path: ./analysis_results/
```

## Dependencies and Requirements

### Core Dependencies (Always Required)
```
lxml>=4.9.0      # XML parsing
networkx>=3.0    # Graph analysis
```

### Optional Dependencies
```bash
# For LangGraph orchestration (large applications)
pip install "pegare[langgraph]"

# For data analysis integration  
pip install "pegare[analysis]"

# For development
pip install "pegare[dev]"

# Everything
pip install "pegare[all]"
```

## Troubleshooting Integration

### Import Issues
```python
# Check if PegaRE is properly installed
try:
    from pega_re import PegaAnalyzer
    print("✅ PegaRE available")
except ImportError as e:
    print(f"❌ PegaRE not available: {e}")
    # Install steps...
```

### Memory Issues with Large Applications
```python
# Use LangGraph for better memory management
from pega_re import run_full_pipeline, has_langgraph

if has_langgraph():
    result = run_full_pipeline(
        input_dir="/path/to/large/app",
        workdir="./output", 
        app_name="Large App",
        llm_agent=None  # Use deterministic mode
    )
else:
    print("Install langgraph for large application support: pip install 'pegare[langgraph]'")
```

This integration guide gives you multiple patterns for incorporating PegaRE into your existing modernization program workflow!
