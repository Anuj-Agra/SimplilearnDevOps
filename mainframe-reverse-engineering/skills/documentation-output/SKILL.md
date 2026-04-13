---
name: documentation-output
description: "Formats mainframe code analysis into polished documentation: Word documents, Excel matrices, structured markdown, and screenshot-ready layouts. Use when the user says 'DOCUMENT', 'create a document', 'export to Word', 'export to Excel', 'format for documentation', 'create a report', 'formal output', 'presentation-ready', or wants analysis results packaged for stakeholders, auditors, or handover."
---

# Documentation Output Formatting

Transform analysis results into polished, professional documentation.

## Output Format Selection

| User Wants | Format | Approach |
|-----------|--------|----------|
| Formal report for stakeholders | Word (.docx) | Use `docx` skill for structured report |
| Traceability matrix or inventory | Excel (.xlsx) | Use `xlsx` skill for tabular data |
| Quick shareable reference | Markdown (.md) | Render as markdown artifact |
| Flowcharts and diagrams | Mermaid in markdown | Fenced ```mermaid blocks |
| Presentation slides | PowerPoint (.pptx) | Use `pptx` skill |

## Word Document Template

When creating a formal Word report, structure it as:

### Document Structure

```
COVER PAGE
  - Title: [Application/System Name] - Code Analysis Report
  - Subtitle: [Analysis Type: Deep Dive / Impact Assessment / etc.]
  - Date, Author, Version

TABLE OF CONTENTS

1. EXECUTIVE SUMMARY
   - 2-3 sentences for non-technical readers
   - Key findings count: X programs, Y files, Z risks
   - Recommendation summary

2. SCOPE & METHODOLOGY
   - What was analysed (libraries, programs, transactions)
   - Analysis approach (top-down / bottom-up / both)
   - Limitations (code not available, assumptions made)

3. COMPONENT INVENTORY
   Table: all programs, files, maps, transactions found
   | Component | Type | Library | Purpose | Dependencies |

4. CALL CHAIN ANALYSIS
   - Call hierarchy diagram (Mermaid rendered as image)
   - Call chain table with parameters
   - Cross-reference matrix

5. DATA FLOW ANALYSIS
   - Data flow diagram (Mermaid rendered as image)
   - Database access matrix
   - Field-level traceability matrix

6. SCREEN FLOW ANALYSIS (if CICS)
   - Screen navigation diagram
   - Field inventory per screen
   - Validation rule summary

7. BUSINESS RULES
   - Rule catalogue table
   - Rule categorisation summary
   - Missing validation report

8. RISK ASSESSMENT
   - Risk items with severity rating
   - Dead code identified
   - Missing error handling
   - Data integrity concerns

9. RECOMMENDATIONS
   - Prioritised action items
   - Effort estimates
   - Testing recommendations

APPENDIX A: Program Source References
APPENDIX B: Mermaid Diagram Source Code
APPENDIX C: Raw Analysis Output
```

### Rendering Mermaid Diagrams for Word

Since Word cannot render Mermaid natively, provide two options:
1. Include the Mermaid source in an appendix for the reader to render
2. Describe the diagram in a text-based representation:

```
PGM-MAIN
  ├──[if exists]──→ SUB-GETDATA ──→ READ FILE-152
  ├──[if new]────→ SUB-CREATE ──→ STORE FILE-152
  └──[always]────→ MAP-DISPLAY
```

## Excel Workbook Template

When creating an Excel traceability workbook, use these sheets:

### Sheet 1: Program Inventory
| Program | Library | Type | Language | Purpose | Called By | Calls | Files Accessed |

### Sheet 2: Database Access Matrix
| Program | Library | DDM | File# | READ | FIND | STORE | UPDATE | DELETE | GET | HISTOGRAM |
(Use ✓ or count for each operation)

### Sheet 3: Field Traceability Matrix
| Adabas File | DDM | Field Name | Short Name | Format | Programs Reading | Programs Writing | Maps Displaying | Maps Editing | Validated? |

### Sheet 4: Validation Rules
| Rule# | Program | Field | Type | Condition | Error Message | Severity |

### Sheet 5: CICS Screen Fields
| Transaction | Screen | Field Label | Internal Name | Type | Len | Editable | Mandatory | Source | Validation |

### Sheet 6: JCL Job Map
| Job | Step | Program | Files In | Files Out | Adabas Access | Condition |

### Sheet 7: Impact Assessment
| Component | Change Needed | Risk | Effort | Dependencies | Priority |

### Sheet 8: Cross-Reference
Pivot table showing: Rows=Programs, Columns=Adabas Files, Cells=Operation type

### Formatting Standards
- Header row: bold, dark blue background (#1B3A5C), white text
- Alternating row colours: white / light blue (#F0F5FA)
- Column widths: auto-fit to content
- Freeze panes: top row and first column
- Named ranges for key tables
- Conditional formatting: red for HIGH risk, yellow for MEDIUM, green for LOW

## Markdown Documentation Template

When producing markdown output for immediate viewing:

```markdown
# [System Name] - Analysis Report

## Executive Summary
[2-3 sentence overview]

## Component Inventory
| Component | Type | Library | Purpose |
|-----------|------|---------|---------|

## Call Chain
```mermaid
graph TD
    ...
```

## Database Access
| Program | DDM | File# | Operations | Key Fields |
|---------|-----|-------|-----------|------------|

## Validation Rules
| Rule# | Field | Type | Condition | Error Action |
|-------|-------|------|-----------|-------------|

## Risks & Recommendations
- ⚠️ [risk 1]
- ⚠️ [risk 2]
- 📌 [recommendation 1]
```

## Iterative Feedback Support

After producing any documentation, offer these refinement options:
1. "Want me to drill deeper into any specific section?"
2. "Should I add more detail to the risk assessment?"
3. "Want me to generate the Excel workbook version?"
4. "Should I format the Mermaid diagrams as text-based trees for Word?"

When the user provides feedback or corrections:
- Apply changes to the relevant section
- Regenerate affected diagrams
- Update cross-references
- Note what was changed and why
