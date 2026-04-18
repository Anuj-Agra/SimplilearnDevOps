---
name: pega-doc-synthesizer
description: Use as the final step after all specialist agents have populated the catalog. Composes the Program Documentation for Product Owner and Technical Lead consumption. This is the only agent that produces narrative prose; all its inputs are drawn from the deterministic catalog.
---

# Skill: Pega Doc Synthesizer

## Purpose
Produce the **Program Documentation** — a single navigable deliverable that lets a PO understand the application top-down and a TL drill to any rule bottom-up. It must reflect only what is in the catalog; it may not invent rules, flows, or tasks.

## Inputs
- `catalog.sqlite` with **all** tables populated
- `workdir/ui/`, `workdir/task_ledger.html`, `workdir/hierarchy.html`, per-Case-Type HTML

## Outputs
- `workdir/program_doc.md` — the master document
- `workdir/program_doc.html` — same content rendered with internal nav, embedded Mermaid diagrams, and links to the sibling HTML artefacts
- `workdir/executive_summary.md` — 1-page PO-facing summary (lead with what the app does, top Case Types, total tasks, top SLAs)

## Document structure

```
1. Executive Summary
   1.1 What this application does (1 paragraph, derived from Case Type labels + stage names)
   1.2 Scale (rule counts, case type count, task count, UI count)
   1.3 Key risks flagged (unresolved refs, stub-fidelity UI, unknown rule types)

2. Application Hierarchy
   2.1 Rulesets and versions (table)
   2.2 Class hierarchy tree (link to hierarchy.html)
   2.3 Access roles matrix

3. Case Types (one subsection per Case Type)
   3.x.1 Purpose (LLM-generated, 3–5 sentences, grounded in catalog)
   3.x.2 Stages and steps (table)
   3.x.3 Process diagram (embedded Mermaid)
   3.x.4 Tasks generated (filtered task ledger for this Case Type)
   3.x.5 UI surfaces (links to rendered harnesses)

4. Task Generation Ledger
   4.1 Full ledger (link to task_ledger.html)
   4.2 Tasks grouped by workbasket
   4.3 SLA hotspots (tasks with shortest deadlines)

5. UI Catalog
   5.1 Harness index (link to ui/index.html)
   5.2 Fidelity notes

6. Dependency Graph
   6.1 Most-referenced rules (top 50)
   6.2 Orphaned rules (never referenced)
   6.3 Circular references (flagged, not resolved)

7. Review Queue
   7.1 Rules that failed to parse
   7.2 Unknown rule types
   7.3 Broken references
   7.4 Stub-fidelity UI
```

## Instructions

1. Call `pega_re.docgen.synthesize(catalog_path, workdir, app_name)`.
2. Generate sections 1–7 in order. Every numeric claim (e.g. "the app has 14 Case Types and 312 generated tasks") must be backed by a SQL query against the catalog, shown as a footnote or data-attribute.
3. For LLM-written prose sections (1.1, 3.x.1):
   - Ground every sentence in at least one catalog entity (class, flow, stage, assignment).
   - Do not describe business value, customer outcomes, or regulatory alignment unless those terms appear as literal ruleset / class / label text.
   - If a Case Type has too little structured content to describe, write: *"Insufficient structural evidence to summarise — see detailed tables below."*
4. Render the HTML version with a sticky left nav, anchor links, and Mermaid.js loaded from CDN.
5. Emit `executive_summary.md` — max 1 page, leads with the count-level facts, then three bullet risks.

## Hierarchy view the PO clicks through

```
Executive Summary
    ↓ (click)
Case Type X (purpose + stages)
    ↓ (click any stage)
Stage Y (steps table)
    ↓ (click any step)
Flow Z (embedded Mermaid)
    ↓ (click any Assignment shape)
Task row in Task Ledger (router, SLA, UI link)
    ↓ (click UI link)
Rendered HTML of the harness
```

## Non-goals
- No marketing prose, no benefits framing, no "modernisation recommendations" unless explicitly asked.
- No invented process names or step names.
- No mixing of this doc with MFREA output — Pega and mainframe stay in separate docs even if they integrate.
