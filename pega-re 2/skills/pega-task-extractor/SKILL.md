---
name: pega-task-extractor
description: Use after pega-flow-analyzer to enrich every Assignment with the task detail a Tech Lead and Product Owner need — which task is generated, triggered by what, routed to whom, with what SLA and escalation. This is the "who does what when" ledger.
---

# Skill: Pega Task Extractor

## Purpose
For every user-facing task the application generates, produce a row that answers:

- **What** — assignment label + flow action
- **When** — which stage/step/flow shape emits it, and under what precondition (When rule)
- **Who** — router type (worklist / workbasket / skill-based) and resolved target
- **For how long** — SLA goal, deadline, passed-deadline escalation
- **What happens next** — outgoing connectors and their conditions

## Inputs
- `catalog.sqlite` with `rules`, `flows`, `flow_shapes`, `case_types`, `stages`, `steps` populated
- Rule types consumed: `Rule-Obj-ServiceLevel`, `Data-Admin-Operator-ID`, `Data-Admin-WorkBasket`, `Rule-Obj-FlowAction`, plus the Assignment shapes already in `flow_shapes`

## Outputs
- `assignments(assignment_id, case_type_id, stage_id, step_id, flow_id, shape_name, task_label, flow_action, trigger_when, router_type, router_target, sla_rule, sla_goal_mins, sla_deadline_mins, sla_passed_action, local_actions_json, next_shapes_json)`
- `slas(sla_id, rule_name, class_name, goal_interval, deadline_interval, passed_deadline_activity)`
- `workbaskets(name, class_name, members_json)`
- `workdir/task_ledger.csv` — one row per assignment, sortable by Case Type / Stage / SLA
- `workdir/task_ledger.html` — interactive filterable table (DataTables.js)

## Instructions

1. Call `pega_re.tasks.extract(catalog_path, workdir)`.
2. For each row in `flow_shapes` where `shape_type = 'Assignment'`:
   - Resolve `flow_action` → `Rule-Obj-FlowAction` to get the task label and any local actions.
   - Read the shape's `pyRouteActivity` / `pyRouterRule` to determine router type:
     - `ToWorklist` → router_type = `worklist`, target = the operator reference
     - `ToWorkbasket` → router_type = `workbasket`, target = workbasket name
     - `ToSkill` → router_type = `skill`, target = skill name
     - Custom router activity → router_type = `custom`, target = activity name
   - Resolve `pySLAName` → `Rule-Obj-ServiceLevel` to get goal/deadline intervals (in minutes).
3. For each row, compute `trigger_when`: walk the incoming connectors; if any has a `When` rule, record its name and condition. If multiple connectors converge, note "multi-trigger".
4. Resolve workbasket membership from `Data-Admin-WorkBasket` rules, but only record operator names and skill tags — **do not expose real operator IDs** in the output doc; mask as `<operator-id>` if personal names appear.
5. Render `task_ledger.html` with columns: Case Type | Stage | Step | Task | Flow Action | Triggered When | Routed To | SLA Goal | Deadline | Escalation.
6. LLM role: for any task where `trigger_when` is complex, summarise the condition in one sentence. Never invent — if the When rule body is empty or opaque, write `"condition: (see rule <name>)"`.

## Hierarchy the Tech Lead reads this at

```
Task Ledger (flat, filterable)
     │
     ├── grouped by Case Type → Stage → Step
     └── grouped by Router Target → (all tasks landing in a given workbasket)
```

Both groupings are exposed in the HTML via column filters.

## Non-goals
- Do not render the section/harness UI — UIRenderer does that.
- Do not include background agents or listeners — those are separate from user tasks (flag them in a `background_jobs` side table if found, but don't mix with assignments).
- Do not compute actual operator PII; keep anonymised.
