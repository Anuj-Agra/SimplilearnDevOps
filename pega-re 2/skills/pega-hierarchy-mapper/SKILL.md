---
name: pega-hierarchy-mapper
description: Use after pega-rule-parser to build the Ruleset → Class → Property → Access-Role hierarchy the Product Owner uses to understand the application's structure. Produces both a queryable table and a nested JSON tree.
---

# Skill: Pega Hierarchy Mapper

## Purpose
Answer "what is the shape of this application?" for a Product Owner or Tech Lead. Produces the inheritance-aware class hierarchy, the ruleset layering, and the access-role matrix.

## Inputs
- `catalog.sqlite` with tables `rules`, `raw_files` populated by prior agents

## Outputs (new tables + files)
- `classes(class_name, parent_class, ruleset, is_work_class, is_data_class, rule_count)`
- `properties(class_name, property_name, data_type, is_required)`
- `access_roles(role_name, class_name, privilege_name, access_level)`
- `workdir/hierarchy_tree.json` — nested tree: ruleset → class → children-classes → properties
- `workdir/hierarchy.html` — collapsible D3.js tree view

## Instructions

1. Call `pega_re.hierarchy.build(catalog_path, workdir)`.
2. `Rule-Obj-Class` rules give parent/child relationships via `pyParentClassName`. Build a `networkx.DiGraph` of class inheritance. Mark a class as `is_work_class` if it (or any ancestor) extends `Work-` or `@baseclass.Work-`. Mark `is_data_class` similarly for `Data-`.
3. `Rule-Obj-Property` rules are pinned to a class via `pyClassName`. Group them.
4. `Rule-Access-Role-Obj` / `Rule-Access-Privilege` rules give the access-role matrix.
5. Output the hierarchy as a nested JSON tree, then render the HTML using the D3 collapsible tree template in `pega_re/ui.py::render_hierarchy_html`.
6. LLM role: if asked to explain a class cluster, summarise in 2–3 sentences **based on the rule counts and property names visible in the tables**. Do not invent business meaning.

## Hierarchy levels the PO sees

```
Application
└── Ruleset (versioned, layered)
    └── Work Class vs Data Class
        └── Class (with inheritance chain)
            └── Properties
            └── Access Roles / Privileges
```

## Non-goals
- Do not traverse flows here — that's FlowAnalyzer.
- Do not render UI here — that's UIRenderer.
- Do not speculate about business intent beyond what the naming and counts warrant.
