# Usage Guide — Mainframe Renovation Workbench

## Before You Start

### What to collect

Gather as many of the following as possible before your first session. More context = better outputs.

**Source code (highest priority)**
- Natural programs: `.nsp` (subprograms), `.nsn` (programs), `.nsg` (global data areas), `.nsl` (local data areas)
- COBOL programs: `.cbl`, `.cob`
- Copybooks / copycode: `.cpy`, `.nsc`
- BMS maps (CICS screen definitions): `.bms`

**Database definitions**
- Adabas DDM definitions (export from Natural as text, or copy from PREDICT)
- Reference table definitions (the programs that load/read them, or Excel exports of the table contents)

**Documentation**
- Existing functional specifications (`.pdf`, `.docx`)
- Data dictionaries (`.xlsx`, `.pdf`)
- System architecture documents (`.pdf`, `.docx`)
- Any existing mapping documents (`.xlsx`)

**Screenshots**
- CICS 3270 terminal screenshots of key screens (`.png`, `.jpg`)
- These help the UI Reader agent map fields to labels accurately

---

## Step-by-Step Workflow

### Step 1 — Open the Application

Open `mainframe-renovation-workbench.html` in Chrome, Edge, or Firefox.
Rename your project using the editable field in the header.

### Step 2 — Upload Files

Drag all your files onto the sidebar upload zone, or click it to browse.
- You can upload in batches — just keep adding files
- Files are displayed with colour-coded type badges
- Remove any accidentally uploaded file with the × button

There is no upload limit other than browser memory. For very large codebases (500+ programs), consider uploading the most critical transaction programs first.

### Step 3 — Run Code Analysis First

Always start with **Tab 1: Code Analysis**. This agent builds the foundation that all other agents benefit from. It identifies:
- All programs and their libraries
- The CICS transaction entry points
- The call hierarchy
- Which fields are used where

Click **Run Agent** and wait for the stream to complete (typically 30–90 seconds depending on file volume).

### Step 4 — Run Mermaid Diagram

Switch to **Tab 4: Mermaid Diagram** and run the agent. The diagram tab renders Mermaid syntax visually inline. You get three diagrams:
1. AS-IS call hierarchy (CICS → Programs → Adabas)
2. AS-IS entity relationships
3. TO-BE Java + Angular architecture

Use these to validate your understanding of the system before writing requirements.

### Step 5 — Run Obsolescence Analysis

Switch to **Tab 6: Obsolescence** and run before writing requirements. This tells you what NOT to carry forward, which keeps your BRD/FRD and Jira stories clean.

Mark any fields flagged as 🔴 HIGH RISK for discussion with your SMEs before removing.

### Step 6 — Generate BRD / FRD

Switch to **Tab 2: BRD / FRD** and run the agent. The output is a professional document with:
- Numbered functional requirements (FR-001...)
- Numbered business rules (BR-001...)
- Screen-by-screen UI specifications
- Data requirements per Adabas file

Review this with business stakeholders before proceeding to Jira stories.

### Step 7 — Generate Jira Stories

Switch to **Tab 3: Jira Stories** and run the agent. The output is structured as:
- Epics (EP-001...) — one per major transaction or functional area
- Stories (US-001...) in "As a... I want... So that..." format
- Gherkin acceptance criteria (Given / When / Then)
- Technical sub-tasks specifying Angular components and Java classes

Copy the output into your Jira project, or use the story keys as references in planning sessions.

### Step 8 — Generate Java + Angular Guide

Switch to **Tab 5: Java + Angular** and run the agent. This is your hands-on renovation guide with:
- Complete class stubs (no implementation yet — that is the developer's job)
- Field mappings with original Adabas field names as comments
- Validation annotations mirroring the original Natural validation logic
- Recommended project/module structure

Share this with your development team as the starting blueprint.

### Step 9 — Download Everything

Click **Download Project ZIP** in the header. You receive a `.zip` containing:
```
your-project-name-renovation/
├── README.md
├── 01-code-analysis.md
├── 02-brd-frd.md
├── 03-jira-stories.md
├── 04-mermaid-diagrams.mmd
├── 05-java-angular-guide.md
└── 06-obsolescence-report.md
```

Share the ZIP with your team, store it in Confluence, or commit it to your project repository.

---

## Tips for Large Codebases

### Prioritise entry points
Start with the programs called directly by CICS transactions (`DFHCOMMAREA` handlers, top-level `CALLNAT` targets). These give the most coverage with the fewest files.

### Group by business function
Run separate sessions per functional area (e.g. one session for Order Management, one for Customer Maintenance). Rename the project in the header for each session so your ZIP files are clearly labelled.

### Use Excel DDMs
If your Adabas DDMs are maintained in Excel, upload the `.xlsx` directly. The app extracts every sheet as CSV text, so field names, lengths, and descriptions are all visible to the agents.

### Upload the PREDICT export
If you have a PREDICT data dictionary export (often a `.txt` or structured report), upload it alongside your programs. It gives the agents the authoritative field descriptions and cross-references.

### Screenshot 3270 screens
Take screenshots of every key CICS screen (use your terminal emulator's screen capture). Upload them all — the agents use vision to read field labels, PF key assignments, and navigation hints that don't always appear in BMS source.

---

## Troubleshooting

**"API error" message when running an agent**
- Ensure you are using the file inside Claude.ai, where API authentication is handled automatically.
- If running locally outside Claude.ai, you would need to add your Anthropic API key to the fetch headers in the HTML source.

**Agent produces generic output instead of file-specific output**
- Check the file list sidebar — if files show 0B or are missing, the upload may have failed. Try re-uploading.
- Very large files (>10MB) may be truncated. Split large Natural libraries across multiple sessions.

**Mermaid diagram does not render**
- The diagram source (Mermaid syntax) is always shown as a code block even if visual rendering fails.
- Copy the code block content and paste into https://mermaid.live to render it manually.

**Excel file not reading correctly**
- Ensure the file is `.xlsx` format (not `.xlsm` with macros). Save as `.xlsx` first if needed.
- Password-protected Excel files cannot be read — remove the password first.

**Word document shows "[Could not extract text]"**
- Very old `.doc` (Word 97-2003) format may fail. Open in Word and Save As `.docx` first.
