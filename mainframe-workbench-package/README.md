# Mainframe Renovation Workbench

> AI-powered analysis and documentation suite for Natural/COBOL → Java + Angular modernisation

---

## Quick Start

1. **Open** `mainframe-renovation-workbench.html` in any modern browser (Chrome, Edge, Firefox)
2. **Upload** your source files using the sidebar drag-and-drop zone
3. **Select** a tab and click **Run Agent**
4. **Download** all outputs via **Download Project ZIP** in the header

No installation required. No server required. Works entirely in the browser.

> ⚠️ Requires internet access — agents call the Claude API, which is authenticated automatically when opened inside **Claude.ai Artifacts**.

---

## File Structure

```
mainframe-workbench-package/
├── mainframe-renovation-workbench.html   ← Main application (single file)
├── README.md                             ← This file
├── AGENTS.md                             ← Agent system prompt reference
├── USAGE_GUIDE.md                        ← Detailed usage instructions
└── docs/
    ├── output-schema.md                  ← Expected output formats per agent
    ├── field-mapping-template.md         ← Adabas DDM → JPA mapping template
    ├── jira-story-template.md            ← Jira story format reference
    └── renovation-checklist.md           ← Java + Angular migration checklist
```

---

## Supported File Types

| Extension | Type | How Processed |
|-----------|------|---------------|
| `.nsp` `.nsn` `.nss` `.nsg` | Natural source | Read as plain text |
| `.cbl` `.cob` `.cpy` `.bms` | COBOL / BMS maps | Read as plain text |
| `.txt` `.csv` | Plain text | Read as plain text |
| `.xlsx` `.xls` | Excel workbooks | All sheets extracted via SheetJS |
| `.docx` | Word documents | Text extracted via Mammoth.js |
| `.pdf` | PDF documents | Sent natively to Claude document API |
| `.png` `.jpg` `.jpeg` | Screenshots / 3270 maps | Sent as vision input |

---

## The Six Agents

| # | Tab | Agent Role | Key Output |
|---|-----|-----------|------------|
| 1 | 📋 Code Analysis | Mainframe Expert | Program inventory, CICS call chains, field usage matrix |
| 2 | 📄 BRD / FRD | Business Analyst | Numbered requirements, screen specs, business rules catalogue |
| 3 | 🎯 Jira Stories | Agile Delivery Lead | Epics → Stories → Gherkin AC, Java/Angular sub-tasks |
| 4 | 📊 Mermaid Diagram | Architecture Diagrammer | CICS→Program→Adabas hierarchy, ER diagram, TO-BE architecture |
| 5 | ☕ Java + Angular | Renovation Architect | Spring Boot + Angular code stubs, validation migration |
| 6 | 🔍 Obsolescence | Quality Analyst | Dead fields 🔴, redundant programs 🟡, dead validations |

---

## Recommended Workflow

```
Step 1 — INGEST
  Upload all Natural libraries (.nsp/.nsn)
  Upload all COBOL programs (.cbl/.cpy)
  Upload Adabas DDM definitions (.txt or .nsd)
  Upload reference table definitions
  Upload any PDF specs, Excel mapping sheets, Word documents
  Upload CICS screen screenshots (.png)

Step 2 — ANALYSE (run in order)
  → Tab 1: Code Analysis       (builds the foundation)
  → Tab 4: Mermaid Diagram     (validates the call hierarchy visually)
  → Tab 6: Obsolescence        (prune before documenting)

Step 3 — DOCUMENT
  → Tab 2: BRD / FRD           (stakeholder-ready requirements)
  → Tab 3: Jira Stories        (sprint-ready backlog)

Step 4 — RENOVATE
  → Tab 5: Java + Angular      (code stubs and field mappings)

Step 5 — EXPORT
  → Click "Download Project ZIP" to get all outputs as .md/.mmd files
```

---

## Tips

- **Upload everything at once** — all agents share the same file context, so uploading once is enough.
- **Re-run agents** — if you add more files after a first run, just hit Run Agent again on any tab.
- **Large codebases** — if you have hundreds of programs, prioritise the entry-point programs (called directly by CICS transactions) and the most important Adabas DDMs first.
- **PDF specs** — upload any existing functional specs, data dictionaries, or legacy design docs as PDFs — Claude reads them natively.
- **Excel DDMs** — if your Adabas DDMs are in Excel format, upload directly; all sheets are extracted automatically.

---

## Technology Stack (Application)

| Library | Version | Purpose |
|---------|---------|---------|
| SheetJS (xlsx) | 0.18.5 | Excel file parsing |
| Mammoth.js | 1.6.0 | Word document text extraction |
| Marked.js | 9.1.6 | Markdown rendering |
| JSZip | 3.10.1 | Project ZIP download |
| Mermaid | 10.x | Diagram rendering |
| Claude API | claude-sonnet-4-20250514 | All six AI agents |

All libraries loaded from CDN — no npm install required.

---

## License

Internal use. Built with Claude by Anthropic.
