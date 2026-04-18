---
name: pega-flow-analyzer
description: Use after pega-rule-parser to decode Pega Case Types, their Stages/Steps, and every Flow rule. Produces the process model the Product Owner needs to understand "what the application does". Does NOT extract per-assignment task detail — that is the Task Extractor's job.
---

# Skill: Pega Flow Analyzer

## Purpose
Build the end-to-end process model:

```
Case Type → Stage → Step → Flow → Flow Shape → (Assignment | Decision | Subprocess | End)
```

This is the single most important output for a Product Owner. It answers: *what happens, in what order, under what conditions.*

## Inputs
- `catalog.sqlite` with `rules` table populated
- Rule types consumed: `Rule-Obj-CaseType`, `Rule-Obj-Flow`, `Rule-Obj-FlowAction`, `Rule-Obj-When`, `Rule-Decision-*`, `Rule-Obj-Activity` (for referenced activities only)

## Outputs
- `case_types(case_type_id, class_name, label, starting_flow, stage_count)`
- `stages(stage_id, case_type_id, label, order, stage_type)`
- `steps(step_id, stage_id, label, order, step_type, flow_ref)`
- `flows(flow_id, rule_id, flow_name, class_name, shape_count)`
- `flow_shapes(shape_id, flow_id, shape_type, shape_name, flow_action, when_rule, next_shapes_json)`
- `decisions(decision_id, rule_id, decision_type, inputs_json, outcomes_json)`
- `workdir/case_type_<name>.html` — one process diagram per Case Type (Mermaid flowchart embedded in HTML)

## Shape types to preserve
`Assignment`, `Decision`, `Fork`, `Join`, `SubProcess`, `SplitForEach`, `Utility`, `End`, `Start`, `Router`.

## Instructions

1. Call `pega_re.flow.analyse(catalog_path, workdir)`.
2. For each `Rule-Obj-CaseType`, extract the `pyStages` list. Each stage has an ordered list of `pyProcesses` (steps). Each step references a `pyFlowName`.
3. For each `Rule-Obj-Flow`, parse the flow shapes from the `pxFlow` / `pyShapes` block. Preserve shape identity, label, type, outgoing connectors, and any referenced `FlowAction` / `When` / `SubProcess`.
4. For each `Assignment` shape, emit a *stub* row in the downstream `assignments` table with the fields the TaskExtractor will later enrich (router, SLA, operator).
5. Render a Mermaid `flowchart TD` per Case Type showing Stage → Step → Flow with assignments highlighted.
6. LLM role: generate a 3–5 sentence **plain-English summary** of each Case Type based on the extracted stages and step names. This summary must only reference names that exist in the catalog — no invented process steps.

## Quality checks
- Every `flow_ref` in `steps` must resolve to a row in `flows`. Unresolved refs go into a `broken_refs` warnings list.
- Every Assignment shape must have a `flow_action` — if missing, flag it (it may indicate a local action or a legacy pattern).
- Cycles in flow-to-subflow references are detected; they're allowed (loops are valid) but annotated.

## Non-goals
- Do not compute SLAs or routing targets — Task Extractor does that.
- Do not render UI.
- Do not write the final documentation — Doc Synthesizer does that.
