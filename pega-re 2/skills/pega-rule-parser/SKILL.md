---
name: pega-rule-parser
description: Use after pega-extractor to stream-parse every rule XML in the catalog into typed records. Handles 200K+ rules via incremental SQLite writes. Routes each rule to the correct downstream agent based on pxObjClass.
---

# Skill: Pega Rule Parser

## Purpose
Turn the raw file catalog from `pega-extractor` into a **structured rule catalog** — one row per rule, typed by `pxObjClass`, with the core identity fields extracted and the XML body kept on disk for later re-reading.

## Inputs
- `workdir/catalog.sqlite` from pega-extractor (table: `raw_files`)
- `workdir/unpacked/` containing the rule XML files

## Outputs (new tables in `catalog.sqlite`)
- `rules(rule_id, obj_class, name, class_name, applies_to, ruleset, ruleset_version, file_path, parsed_ok, parse_error)`
- `unknown_rule_types(obj_class, count, sample_file)` — anything not in the known list

## Instructions

1. Call `pega_re.parser.parse_all(catalog_path, unpacked_dir)`. It uses `lxml.iterparse` with `clear()` to keep memory flat regardless of corpus size.
2. The parser extracts only these attributes from each rule's root element: `pxObjClass`, `pyRuleName` (or `pyLabel`), `pyClassName`, `pyAppliesTo`, `pyRuleSet`, `pyRuleSetVersion`. It does **not** parse rule bodies — that is the job of the specialist agents.
3. Rules that fail to parse get `parsed_ok=False` and the first 500 chars of the exception in `parse_error`. Do not halt on parse failures; the goal is coverage, not perfection.
4. After parsing, emit a summary:
   - total rules parsed OK
   - top 20 `obj_class` values by count
   - unknown `obj_class` values (these are flagged for human review in the final doc)
5. If you (the LLM) are asked to classify an ambiguous rule, read the raw XML from `file_path` — do not invent.

## Routing table (which agent consumes which obj_class)

| obj_class prefix | Consumed by |
|---|---|
| `Rule-Obj-Class`, `Rule-Obj-Property`, `Rule-Declare-*`, `Rule-Access-*` | HierarchyMapper |
| `Rule-Obj-CaseType`, `Rule-Obj-Flow`, `Rule-Obj-FlowAction`, `Rule-Obj-Activity`, `Rule-Obj-When`, `Rule-Decision-*` | FlowAnalyzer |
| `Rule-Obj-ServiceLevel`, `Data-Admin-Operator-ID`, `Data-Admin-WorkBasket` | TaskExtractor |
| `Rule-HTML-Section`, `Rule-HTML-Harness`, `Rule-HTML-Fragment` | UIRenderer |

## Non-goals
- No LLM calls during parsing. Parsing is 100% deterministic.
- No full XML load — use iterparse.
- Do not try to "fix" broken rules. Quarantine them.
