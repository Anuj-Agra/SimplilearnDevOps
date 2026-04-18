"""
tasks.py — Enrich every Assignment shape with router, SLA, trigger condition.
This is the ledger that answers the Tech Lead's core question.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

try:
    from lxml import etree as ET
except ImportError:
    from xml.etree import ElementTree as ET


TASKS_SCHEMA = """
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type_id INTEGER,
    case_type_label TEXT,
    stage_id INTEGER,
    stage_label TEXT,
    step_id INTEGER,
    step_label TEXT,
    flow_id INTEGER,
    flow_name TEXT,
    shape_name TEXT,
    task_label TEXT,
    flow_action TEXT,
    trigger_when TEXT,
    router_type TEXT,
    router_target TEXT,
    sla_rule TEXT,
    sla_goal_mins INTEGER,
    sla_deadline_mins INTEGER,
    sla_passed_action TEXT,
    local_actions_json TEXT,
    next_shapes_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_asgn_case ON assignments(case_type_label);
CREATE INDEX IF NOT EXISTS idx_asgn_router ON assignments(router_target);

CREATE TABLE IF NOT EXISTS slas (
    sla_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT,
    class_name TEXT,
    goal_mins INTEGER,
    deadline_mins INTEGER,
    passed_deadline_activity TEXT
);

CREATE TABLE IF NOT EXISTS workbaskets (
    name TEXT PRIMARY KEY,
    class_name TEXT,
    members_json TEXT
);
"""


@dataclass
class TaskResult:
    assignment_count: int
    sla_count: int
    workbasket_count: int
    ledger_csv: str
    ledger_html: str


def extract(catalog_path: str | Path, workdir: str | Path) -> TaskResult:
    workdir = Path(workdir)
    unpacked = workdir / "unpacked"
    conn = sqlite3.connect(catalog_path)
    conn.executescript(TASKS_SCHEMA)
    cur = conn.cursor()

    # Load all SLAs into memory for fast lookup
    sla_rows = cur.execute(
        "SELECT rule_id, name, class_name, file_path FROM rules "
        "WHERE obj_class = 'Rule-Obj-ServiceLevel' AND parsed_ok = 1"
    ).fetchall()
    sla_lookup: dict[str, dict] = {}
    for rule_id, name, class_name, file_path in sla_rows:
        meta = _parse_sla(unpacked / file_path)
        sla_lookup[name] = {"class_name": class_name, **meta}
        cur.execute(
            "INSERT INTO slas (rule_name, class_name, goal_mins, deadline_mins, passed_deadline_activity) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, class_name, meta["goal_mins"], meta["deadline_mins"], meta["passed_deadline_activity"]),
        )

    # Workbaskets
    wb_rows = cur.execute(
        "SELECT name, class_name, file_path FROM rules "
        "WHERE obj_class = 'Data-Admin-WorkBasket' AND parsed_ok = 1"
    ).fetchall()
    for name, class_name, file_path in wb_rows:
        members = _parse_workbasket_members(unpacked / file_path)
        cur.execute(
            "INSERT OR REPLACE INTO workbaskets (name, class_name, members_json) VALUES (?, ?, ?)",
            (name, class_name, json.dumps(members)),
        )

    # Walk the case-type → stage → step → flow → assignment chain
    rows = cur.execute("""
        SELECT ct.case_type_id, ct.label AS case_label,
               st.stage_id, st.label AS stage_label,
               sp.step_id, sp.label AS step_label, sp.flow_ref,
               f.flow_id, f.flow_name
        FROM case_types ct
        LEFT JOIN stages st ON st.case_type_id = ct.case_type_id
        LEFT JOIN steps  sp ON sp.stage_id = st.stage_id
        LEFT JOIN flows  f  ON f.flow_name = sp.flow_ref
    """).fetchall()

    for ct_id, case_label, stage_id, stage_label, step_id, step_label, flow_ref, flow_id, flow_name in rows:
        if not flow_id:
            continue
        shapes = cur.execute(
            "SELECT shape_name, shape_label, flow_action, when_rule, next_shapes_json, attrs_json "
            "FROM flow_shapes WHERE flow_id = ? AND shape_type = 'Assignment'",
            (flow_id,),
        ).fetchall()
        for shape_name, shape_label, flow_action, when_rule, next_json, attrs_json in shapes:
            attrs = json.loads(attrs_json or "{}")
            router_type, router_target = _resolve_router(attrs)
            sla_name = attrs.get("pySLAName") or attrs.get("pyServiceLevel")
            sla = sla_lookup.get(sla_name, {})
            task_label = shape_label or flow_action or shape_name or "(unnamed task)"

            cur.execute(
                "INSERT INTO assignments "
                "(case_type_id, case_type_label, stage_id, stage_label, step_id, step_label, "
                " flow_id, flow_name, shape_name, task_label, flow_action, trigger_when, "
                " router_type, router_target, sla_rule, sla_goal_mins, sla_deadline_mins, sla_passed_action, "
                " local_actions_json, next_shapes_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ct_id, case_label, stage_id, stage_label, step_id, step_label,
                 flow_id, flow_name, shape_name, task_label, flow_action, when_rule,
                 router_type, router_target, sla_name,
                 sla.get("goal_mins"), sla.get("deadline_mins"), sla.get("passed_deadline_activity"),
                 json.dumps(attrs.get("localActions", [])), next_json or "[]"),
            )

    conn.commit()

    # Export CSV + HTML ledger
    csv_path = workdir / "task_ledger.csv"
    html_path = workdir / "task_ledger.html"
    _export_csv(cur, csv_path)
    _export_html(cur, html_path)

    counts = cur.execute(
        "SELECT (SELECT COUNT(*) FROM assignments), (SELECT COUNT(*) FROM slas), (SELECT COUNT(*) FROM workbaskets)"
    ).fetchone()
    conn.close()

    return TaskResult(
        assignment_count=counts[0],
        sla_count=counts[1],
        workbasket_count=counts[2],
        ledger_csv=str(csv_path),
        ledger_html=str(html_path),
    )


def _parse_sla(path: Path) -> dict:
    meta = {"goal_mins": None, "deadline_mins": None, "passed_deadline_activity": None}
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
        def _as_mins(v):
            if v is None:
                return None
            try:
                # Pega stores intervals in various forms; normalise likely ones.
                v = v.strip()
                if v.endswith("H"):
                    return int(float(v[:-1]) * 60)
                if v.endswith("M"):
                    return int(float(v[:-1]))
                if v.endswith("D"):
                    return int(float(v[:-1]) * 60 * 24)
                return int(float(v))
            except ValueError:
                return None

        meta["goal_mins"] = _as_mins(root.attrib.get("pyGoalInterval"))
        meta["deadline_mins"] = _as_mins(root.attrib.get("pyDeadlineInterval"))
        meta["passed_deadline_activity"] = root.attrib.get("pyPassedDeadlineActivity")
    except Exception:
        pass
    return meta


def _parse_workbasket_members(path: Path) -> list[str]:
    members: list[str] = []
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
        for el in root.iter():
            tag = str(getattr(el, "tag", ""))
            if tag.endswith("rowdata"):
                op = el.attrib.get("pyUserIdentifier")
                if op:
                    # Privacy: mask operator IDs
                    members.append(f"<operator-id:{abs(hash(op)) % 10_000}>")
    except Exception:
        pass
    return members


def _resolve_router(attrs: dict) -> tuple[str, str]:
    route_activity = attrs.get("pyRouteActivity") or attrs.get("pyRouterRule") or ""
    if "ToWorklist" in route_activity:
        return "worklist", attrs.get("pyAssignTo") or attrs.get("pyTargetOperator") or "currentOperator"
    if "ToWorkbasket" in route_activity:
        return "workbasket", attrs.get("pyWorkBasket") or attrs.get("pyTargetWorkBasket") or "unknown"
    if "ToSkill" in route_activity or "Skill" in route_activity:
        return "skill", attrs.get("pySkillName") or "unknown"
    if route_activity:
        return "custom", route_activity
    return "unknown", ""


def _export_csv(cur: sqlite3.Cursor, path: Path) -> None:
    import csv
    rows = cur.execute(
        "SELECT case_type_label, stage_label, step_label, task_label, flow_action, "
        "trigger_when, router_type, router_target, sla_goal_mins, sla_deadline_mins, sla_passed_action "
        "FROM assignments ORDER BY case_type_label, stage_label, step_label"
    ).fetchall()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["CaseType", "Stage", "Step", "Task", "FlowAction",
                    "TriggeredWhen", "RouterType", "RouterTarget",
                    "SLAGoalMins", "SLADeadlineMins", "SLAPassedAction"])
        w.writerows(rows)


def _export_html(cur: sqlite3.Cursor, path: Path) -> None:
    rows = cur.execute(
        "SELECT case_type_label, stage_label, step_label, task_label, flow_action, "
        "trigger_when, router_type, router_target, sla_goal_mins, sla_deadline_mins, sla_passed_action "
        "FROM assignments ORDER BY case_type_label, stage_label, step_label"
    ).fetchall()

    body_rows = "\n".join(
        "<tr>" + "".join(f"<td>{_esc(str(c) if c is not None else '')}</td>" for c in r) + "</tr>"
        for r in rows
    )
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Pega Task Ledger</title>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
<style>
  body{{font-family:-apple-system,Segoe UI,sans-serif;margin:20px;color:#1a2332}}
  h1{{color:#0a1929}}
  table.dataTable thead th{{background:#0a1929;color:#fff}}
  td,th{{font-size:13px}}
</style></head><body>
<h1>Pega Task Generation Ledger</h1>
<p>Every assignment created by the application, with trigger, routing, and SLA.</p>
<table id="ledger" class="display compact" style="width:100%">
<thead><tr>
<th>Case Type</th><th>Stage</th><th>Step</th><th>Task</th><th>Flow Action</th>
<th>Triggered When</th><th>Router</th><th>Target</th>
<th>SLA Goal (min)</th><th>Deadline (min)</th><th>Escalation</th>
</tr></thead>
<tbody>
{body_rows}
</tbody>
</table>
<script>$(function(){{$('#ledger').DataTable({{pageLength:25, order:[[0,'asc'],[1,'asc'],[2,'asc']]}});}});</script>
</body></html>"""
    path.write_text(html)


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
