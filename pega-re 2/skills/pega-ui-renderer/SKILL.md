---
name: pega-ui-renderer
description: Use after pega-rule-parser to convert every Rule-HTML-Section and Rule-HTML-Harness into standalone, viewable HTML. Produces a navigable UI catalog so the Product Owner can see every screen the application presents.
---

# Skill: Pega UI Renderer

## Purpose
Give the Product Owner and Tech Lead a **browsable catalog of every UI surface** the application exposes, as plain HTML files that open in any browser without a Pega runtime.

## Inputs
- `catalog.sqlite` with `rules` table populated
- Rule types consumed: `Rule-HTML-Section`, `Rule-HTML-Harness`, `Rule-HTML-Fragment`

## Outputs
- `ui_rules(ui_id, rule_id, ui_type, class_name, name, parent_harness, referenced_sections_json, referenced_properties_json, rendered_html_path, fidelity)`
- `workdir/ui/<class>/<harness_or_section>.html` — one standalone HTML file per UI rule
- `workdir/ui/index.html` — master index grouped by Harness → Section tree
- `workdir/ui/README.md` — fidelity notes and known limitations

## Rendering strategy (fidelity ladder)

Pega sections use a mix of dynamic layouts, repeat grids, and server-side directives. We aim for **structural fidelity**, not pixel-perfect runtime re-creation:

| Pega construct | Rendered as |
|---|---|
| Dynamic Layout (single row, double header, etc.) | `<div class="pega-dl">` with labelled `<div class="field">` children |
| Repeat Grid | `<table>` with column headers from the grid's columns block |
| Property reference (`.Customer.FullName`) | `<span class="pega-ref" data-ref="Customer.FullName">{Customer.FullName}</span>` |
| When rule on visibility | `<div class="pega-conditional" data-when="IsEligible">...</div>` with a visible badge |
| Button (flow action) | `<button class="pega-action" data-action="Submit">Submit</button>` |
| Include section | Inlined as `<section class="pega-included" data-section="X">...</section>`, one level deep |

A minimal shared stylesheet (`workdir/ui/_pega.css`) gives a plausible Pega look: grey labels, thin borders, a header bar on harnesses.

## Instructions

1. Call `pega_re.ui.render_all(catalog_path, workdir)`.
2. For each `Rule-HTML-Harness`, walk its `pyHTMLSource` / `pyLayout` block; render to HTML file. Record every included section in `referenced_sections_json`.
3. For each `Rule-HTML-Section`, do the same. Sections referenced by a harness get rendered both standalone and inlined in the harness.
4. Sections with runtime-only constructs (e.g. JavaScript-only custom controls) render with a visible banner: *"⚠ Dynamic content — structure shown, runtime behaviour not reproduced."* and set `fidelity = 'partial'`.
5. Build `index.html` as a two-pane layout: left nav lists every Harness grouped by class; right pane loads the selected UI in an `<iframe>`.
6. LLM role: for each top-level Harness, generate a 2-sentence description of what the screen appears to do, based **only** on visible labels, section names, and button actions. Do not infer business purpose from class names alone.

## Fidelity levels
- `full` — all constructs rendered structurally, no warnings
- `partial` — one or more dynamic constructs skipped with a banner
- `stub` — the rule references so many external pieces (or uses so much custom JS) that only a placeholder is emitted; logged for human review

## Non-goals
- No attempt to wire up actual data — property refs show as `{property.name}` placeholders.
- No attempt to reproduce Pega skin CSS pixel-for-pixel.
- No execution of embedded JavaScript / Java activities.
