# Working with Extracted JAR Contents

## Your Setup: Manifest + Binary Files

Since you've already extracted your JAR files into manifest and binary files, PegaRE can work directly with your extracted directory structure. **No need to re-JAR or convert anything.**

### Expected Directory Structure

PegaRE expects your extracted content to look like this:

```
your_extracted_jars/
├── jar1_extracted/
│   ├── META-INF/
│   │   ├── MANIFEST.MF
│   │   └── pega.xml              ← Pega rule manifest
│   └── <ruleset>/<version>/
│       └── <ClassName>/
│           └── <RuleType>/
│               └── <RuleName>.xml ← Individual rule files
├── jar2_extracted/
│   ├── META-INF/
│   └── ...
└── jar3_extracted/
    ├── META-INF/
    └── ...
```

### Quick Validation

Check if your structure is compatible:
```bash
python -m pega_re.auto_dispatcher "validate my input" \
    --input /path/to/your_extracted_jars
```

This will show you:
- ✅ Found X extracted JAR directories
- 📊 Estimated scale: ~N rule files detected
- 📋 Rulesets discovered: [list]

### Most Common Commands for Your Setup

```bash
# Complete analysis of your extracted JARs
python -m pega_re.auto_dispatcher "analyze my pega application" \
    --input /path/to/your_extracted_jars \
    --app-name "CRD KYC Platform"

# Focus on task extraction (your key requirement)
python -m pega_re.auto_dispatcher "extract all tasks and workflows" \
    --input /path/to/your_extracted_jars

# Generate executive summary for steering committee
python -m pega_re.auto_dispatcher "generate executive summary for steering committee" \
    --input /path/to/your_extracted_jars \
    --app-name "CRD KYC Modernization Program"
```

### Example for Your CRD KYC Use Case

```bash
# Assuming your extracted JARs are in /data/pega_extracts/
python -m pega_re.auto_dispatcher "analyze my pega application" \
    --input /data/pega_extracts \
    --output ./crd_analysis \
    --app-name "CRD KYC Platform"
```

**What happens:**
1. PegaRE detects you have extracted JAR directories (not .jar files)
2. Catalogs all your manifest and rule files  
3. Streams through your 200K+ rules
4. Generates the complete documentation

### Directory Structure Examples

Your extracted JARs might look like any of these patterns (all supported):

**Pattern 1: Standard JAR extraction**
```
/your_path/
├── CRD_Rules_v1/
│   ├── META-INF/pega.xml
│   └── MyCoKYC/01-05-12/MyCo-App-Work-KYCReview/Rule-Obj-Flow/
├── CRD_Rules_v2/
│   ├── META-INF/pega.xml
│   └── MyCoKYC/01-05-13/...
```

**Pattern 2: Organized by system**
```
/your_path/
├── kyc_rules_extracted/
├── client_data_extracted/  
├── workflow_rules_extracted/
└── ui_rules_extracted/
```

**Pattern 3: Single combined extraction**
```
/your_path/extracted_all/
├── META-INF/pega.xml
├── MyCoKYC/01-05-12/...
├── MyCoClientData/01-02-08/...
└── MyCoWorkflow/02-01-15/...
```

All patterns work - PegaRE automatically detects your structure.

### File Types PegaRE Handles

From your extracted content, PegaRE processes:
- **`.xml` files** - Individual Pega rules
- **`.pegarules` files** - Binary rule exports  
- **`pega.xml`** - Rule manifests
- **`MANIFEST.MF`** - JAR metadata

Binary files, images, and other assets are cataloged but not parsed (as expected).

### Integration with Your Program Workflow

Since you're managing the CRD KYC modernization program:

```bash
# Monthly analysis for steering committee
python -m pega_re.auto_dispatcher "generate metrics for steering committee" \
    --input /your_extracted_path \
    --app-name "CRD KYC Modernization - $(date +%B)" \
    --output ./monthly_reports/$(date +%Y%m)

# Task complexity analysis for workstream planning
python -m pega_re.auto_dispatcher "extract all tasks for capacity planning" \
    --input /your_extracted_path \
    --output ./workstream_planning
```

### Troubleshooting Common Issues

**"No JAR files or extracted JAR directories found"**
- Make sure each directory contains a `META-INF/pega.xml` file
- The directory name doesn't matter, but the internal structure does

**"Found directories but no rule files"**
- Check that rule files are in the expected `<ruleset>/<version>/<class>/<ruletype>/` structure
- Run with `--verbose` to see what files are being discovered

**"Scale warning: only X rule files detected"**  
- Normal if you extracted only specific rulesets
- For 200K+ rules, you should see a message like "Medium/Large application"

### Performance Notes for Your Scale

With 200K+ rules from extracted JARs:
- **Memory usage**: ~1-2GB peak (streaming architecture)
- **Processing time**: 30-45 minutes for complete analysis
- **Recommended**: Use LangGraph method for checkpointing on large analyses

```bash
# For your scale, use LangGraph with checkpointing
python -m pega_re.auto_dispatcher "analyze large application with checkpointing" \
    --input /your_extracted_path \
    --method langgraph \
    --app-name "CRD KYC Platform"
```

### Next Steps

1. **Validate your structure**: `python -m pega_re.auto_dispatcher "validate my input" --input /your/path`
2. **Run first analysis**: `python -m pega_re.auto_dispatcher "analyze my pega application" --input /your/path`
3. **Check task ledger**: Open `./pegare_output/task_ledger.html` (your key deliverable)
4. **Review executive summary**: `./pegare_output/executive_summary.md` for C-Suite updates

The system is ready for your extracted JAR structure - no additional setup needed!
