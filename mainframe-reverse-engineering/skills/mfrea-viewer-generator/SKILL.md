---
name: mfrea-viewer-generator
description: "Generates the MFREA (Mainframe Reverse Engineering Agent) interactive HTML viewer, Python scanner, and FRD generator. Use this skill whenever the user asks to create, generate, or build the MFREA tool, mainframe dependency viewer, mainframe call graph viewer, reverse engineering viewer, program dependency tree, Adabas usage viewer, or any interactive HTML tool for visualising mainframe Natural/JCL/COBOL call chains and database access. Also triggers on: 'generate the viewer', 'create the HTML', 'build the MFREA tool', 'I need the dependency graph viewer', 'generate scanner', 'create the reverse engineering tool', 'build the mainframe analysis tool'."
---

# MFREA Viewer Generator Agent

This skill generates a complete mainframe reverse engineering toolkit consisting of three components:

1. **Interactive HTML Viewer** — React-based browser UI with 4 tabs (dependency tree, Adabas filter, ref table filter, functional/FRD view)
2. **Python Scanner** — Parses 52K+ Natural modules and 13K+ JCL files into a graph.json
3. **FRD Generator** — Command-line tool for generating Functional Requirements Documents

## When to Generate What

| User Request | Action |
|---|---|
| "Generate the viewer" / "Create the HTML" / "Build the MFREA tool" | Generate ALL three files |
| "Just the viewer" / "Just the HTML" | Generate only `viewer/index.html` |
| "Just the scanner" / "Parse my code" | Generate only `scanner/scanner.py` |
| "Generate an FRD" / "Create FRD generator" | Generate only `scanner/frd_generator.py` |
| "Update the viewer to add X" | Read the template, modify, and output |

## Generation Workflow

### Step 1: Read the templates

Before generating ANY output, read these reference files:

- For the viewer: `view` the file at `scripts/viewer.html`
- For the scanner: `view` the file at `scripts/scanner.py`
- For the FRD generator: `view` the file at `scripts/frd_generator.py`

### Step 2: Create the files

Use the `create_file` tool to write each file to `/mnt/user-data/outputs/mfrea-tool/`:

```
/mnt/user-data/outputs/mfrea-tool/
├── viewer/index.html          ← from viewer-template.html
├── scanner/scanner.py         ← from scanner-template.py
├── scanner/frd_generator.py   ← from frd-generator-template.py
└── README.md                  ← generate inline (usage instructions)
```

### Step 3: Present the files

Use `present_files` to share all generated files with the user.

## Customisation Requests

If the user asks for modifications to the viewer, read the template first, then apply the changes. Common customisation requests:

| Request | What to Change |
|---|---|
| "Add a new tab" | Add a new tab name to `tabNames` array and a new component |
| "Change colours" | Modify CSS variables in `:root` |
| "Add export to Excel" | Add a button that generates CSV from the current view |
| "Show more detail in the tree" | Modify `TreeNode` component |
| "Add a graph/network view" | Add a canvas-based force-directed layout tab |
| "Filter by library" | Add a library dropdown filter to the sidebar |
| "Add program type filter" | Add chip filters for program/subprogram/JCL/map |

## Key Architecture Notes for Modifications

The viewer is a single-file React app using:
- **React 18** via CDN (UMD build)
- **Babel standalone** for JSX transformation
- **No build step** — works by opening the HTML file directly
- **graph.json** loaded via FileReader API (client-side, no server needed)

Key state:
- `graph` — the loaded JSON data
- `selected` — currently selected program name
- `upstream` / `downstream` — computed Sets of highlighted programs
- `expandedSet` — Set of expanded tree nodes
- `tab` — active tab index (0-3)

Key data structures in graph.json:
- `modules[name].calls` — array of `{target, type}` for downstream
- `modules[name].called_by` — array of caller names for upstream
- `modules[name].db_access` — array of `{ddm, operation, fields}`
- `modules[name].ref_tables` — array of `{table, field, type}`
- `adabas_index[ddm].programs` — all programs accessing a DDM
- `ref_table_index[table]` — all programs reading a ref table

## Scanner Architecture Notes

The scanner uses pure Python stdlib (no dependencies):
- `re` for regex pattern matching
- `concurrent.futures.ProcessPoolExecutor` for parallel file scanning
- Outputs JSON with `json.dump`

Key regex patterns:
- `RE_CALLNAT` — matches `CALLNAT 'name'`
- `RE_FETCH` — matches `FETCH 'name'`
- `RE_DB_OP` — matches `READ/FIND/STORE/UPDATE/DELETE view-name`
- `RE_VIEW` — matches `VIEW OF ddm-name` in DEFINE DATA
- `RE_JCL_EXEC` — matches `EXEC PGM=name` in JCL
- `RE_JCL_PARM` — matches PARM values (often contains Natural program names)

## README Template

When generating the README, include:
1. What the tool does (one paragraph)
2. Quick start: scan command, open viewer command
3. FRD generation examples (program, DDM, field)
4. File structure
5. Scanner performance expectations (~5 min for 65K files)
