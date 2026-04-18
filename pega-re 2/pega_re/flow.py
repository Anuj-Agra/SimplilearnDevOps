"""
flow.py — Decode Pega Case Types, their Stages/Steps, and every Flow rule.
Produces the process model the Product Owner reads top-down.
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


FLOW_SCHEMA = """
CREATE TABLE IF NOT EXISTS case_types (
    case_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER,
    class_name TEXT,
    label TEXT,
    starting_flow TEXT,
    stage_count INTEGER
);
CREATE TABLE IF NOT EXISTS stages (
    stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_type_id INTEGER,
    label TEXT,
    stage_order INTEGER,
    stage_type TEXT
);
CREATE TABLE IF NOT EXISTS steps (
    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_id INTEGER,
    label TEXT,
    step_order INTEGER,
    step_type TEXT,
    flow_ref TEXT
);
CREATE TABLE IF NOT EXISTS flows (
    flow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER,
    flow_name TEXT,
    class_name TEXT,
    shape_count INTEGER
);
CREATE TABLE IF NOT EXISTS flow_shapes (
    shape_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id INTEGER,
    shape_type TEXT,
    shape_name TEXT,
    shape_label TEXT,
    flow_action TEXT,
    when_rule TEXT,
    subflow_ref TEXT,
    next_shapes_json TEXT,
    attrs_json TEXT
);
CREATE TABLE IF NOT EXISTS decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER,
    decision_type TEXT,
    inputs_json TEXT,
    outcomes_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_stages_case ON stages(case_type_id);
CREATE INDEX IF NOT EXISTS idx_steps_stage ON steps(stage_id);
CREATE INDEX IF NOT EXISTS idx_shapes_flow ON flow_shapes(flow_id);
"""

ASSIGNMENT_SHAPES = {"Assignment", "AssignmentService"}
DECISION_SHAPES = {"Decision", "Fork", "Router"}


@dataclass
class FlowResult:
    case_type_count: int
    stage_count: int
    step_count: int
    flow_count: int
    shape_count: int
    assignment_shape_count: int
    broken_refs: list[str]


def analyse(catalog_path: str | Path, workdir: str | Path) -> FlowResult:
    workdir = Path(workdir)
    unpacked = workdir / "unpacked"
    conn = sqlite3.connect(catalog_path)
    conn.executescript(FLOW_SCHEMA)
    cur = conn.cursor()

    # Case Types
    case_rows = cur.execute(
        "SELECT rule_id, class_name, name, file_path FROM rules "
        "WHERE obj_class = 'Rule-Obj-CaseType' AND parsed_ok = 1"
    ).fetchall()

    ct_id_by_class: dict[str, int] = {}
    for rule_id, class_name, label, file_path in case_rows:
        ct = _parse_case_type(unpacked / file_path)
        cur.execute(
            "INSERT INTO case_types (rule_id, class_name, label, starting_flow, stage_count) VALUES (?, ?, ?, ?, ?)",
            (rule_id, class_name, label, ct.get("starting_flow"), len(ct.get("stages", []))),
        )
        case_type_id = cur.lastrowid
        ct_id_by_class[class_name] = case_type_id
        for i, stage in enumerate(ct.get("stages", [])):
            cur.execute(
                "INSERT INTO stages (case_type_id, label, stage_order, stage_type) VALUES (?, ?, ?, ?)",
                (case_type_id, stage.get("label"), i, stage.get("type", "Primary")),
            )
            stage_id = cur.lastrowid
            for j, step in enumerate(stage.get("steps", [])):
                cur.execute(
                    "INSERT INTO steps (stage_id, label, step_order, step_type, flow_ref) VALUES (?, ?, ?, ?, ?)",
                    (stage_id, step.get("label"), j, step.get("type", "Process"), step.get("flow_ref")),
                )

    # Flows
    flow_rows = cur.execute(
        "SELECT rule_id, name, class_name, file_path FROM rules "
        "WHERE obj_class = 'Rule-Obj-Flow' AND parsed_ok = 1"
    ).fetchall()

    flow_name_to_id: dict[tuple[str, str], int] = {}
    assignment_shape_count = 0
    for rule_id, name, class_name, file_path in flow_rows:
        shapes = _parse_flow_shapes(unpacked / file_path)
        cur.execute(
            "INSERT INTO flows (rule_id, flow_name, class_name, shape_count) VALUES (?, ?, ?, ?)",
            (rule_id, name, class_name, len(shapes)),
        )
        flow_id = cur.lastrowid
        flow_name_to_id[(class_name or "", name or "")] = flow_id
        for sh in shapes:
            if sh["shape_type"] in ASSIGNMENT_SHAPES:
                assignment_shape_count += 1
            cur.execute(
                "INSERT INTO flow_shapes "
                "(flow_id, shape_type, shape_name, shape_label, flow_action, when_rule, subflow_ref, next_shapes_json, attrs_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (flow_id, sh["shape_type"], sh.get("shape_name"), sh.get("shape_label"),
                 sh.get("flow_action"), sh.get("when_rule"), sh.get("subflow_ref"),
                 json.dumps(sh.get("next", [])), json.dumps(sh.get("attrs", {}))),
            )

    # Decision tables/trees/maps
    dec_rows = cur.execute(
        "SELECT rule_id, obj_class, name, file_path FROM rules "
        "WHERE obj_class LIKE 'Rule-Decision-%' AND parsed_ok = 1"
    ).fetchall()
    for rule_id, obj_class, _name, file_path in dec_rows:
        inputs, outcomes = _parse_decision(unpacked / file_path)
        cur.execute(
            "INSERT INTO decisions (rule_id, decision_type, inputs_json, outcomes_json) VALUES (?, ?, ?, ?)",
            (rule_id, obj_class.replace("Rule-Decision-", ""), json.dumps(inputs), json.dumps(outcomes)),
        )

    conn.commit()

    # Render per-Case-Type Mermaid diagrams
    ct_rows = cur.execute(
        "SELECT case_type_id, class_name, label FROM case_types"
    ).fetchall()
    for ct_id, class_name, label in ct_rows:
        mermaid = _render_case_type_mermaid(cur, ct_id, label or class_name)
        out = workdir / f"case_type_{ct_id}.html"
        out.write_text(_wrap_mermaid(mermaid, label or class_name))

    # Broken refs
    broken = []
    for (stage_id, flow_ref) in cur.execute(
        "SELECT step_id, flow_ref FROM steps WHERE flow_ref IS NOT NULL AND flow_ref != ''"
    ).fetchall():
        found = cur.execute("SELECT 1 FROM flows WHERE flow_name = ?", (flow_ref,)).fetchone()
        if not found:
            broken.append(f"step {stage_id} → flow {flow_ref}")

    counts = cur.execute(
        "SELECT (SELECT COUNT(*) FROM case_types), (SELECT COUNT(*) FROM stages), "
        "(SELECT COUNT(*) FROM steps), (SELECT COUNT(*) FROM flows), (SELECT COUNT(*) FROM flow_shapes)"
    ).fetchone()
    conn.close()

    return FlowResult(
        case_type_count=counts[0],
        stage_count=counts[1],
        step_count=counts[2],
        flow_count=counts[3],
        shape_count=counts[4],
        assignment_shape_count=assignment_shape_count,
        broken_refs=broken,
    )


def _parse_case_type(path: Path) -> dict:
    stages: list[dict] = []
    starting_flow = None
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
        starting_flow = root.attrib.get("pyStartingFlow")
        # Pega case-type stages are usually under <pyStages> with <rowdata pyStageLabel="..." pyStageID="..." pyStageType="...">
        current_stage = None
        for el in root.iter():
            tag = str(getattr(el, "tag", ""))
            if tag.endswith("pyStages"):
                continue
            if tag.endswith("rowdata"):
                # Stage row
                if el.attrib.get("pyStageLabel") or el.attrib.get("pyStageID"):
                    current_stage = {
                        "label": el.attrib.get("pyStageLabel") or el.attrib.get("pyStageID"),
                        "type": el.attrib.get("pyStageType", "Primary"),
                        "steps": [],
                    }
                    stages.append(current_stage)
                # Step row (has pyFlowName)
                elif el.attrib.get("pyFlowName") and current_stage is not None:
                    current_stage["steps"].append({
                        "label": el.attrib.get("pyStepLabel") or el.attrib.get("pyFlowName"),
                        "type": el.attrib.get("pyStepType", "Process"),
                        "flow_ref": el.attrib.get("pyFlowName"),
                    })
    except Exception:
        pass
    return {"starting_flow": starting_flow, "stages": stages}


def _parse_flow_shapes(path: Path) -> list[dict]:
    shapes: list[dict] = []
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
        # Flow shapes live under <pyShapes> with <rowdata pyShapeType="Assignment" pyShapeName="..." pyFlowAction="..." ...>
        name_to_shape: dict[str, dict] = {}
        shape_list: list[dict] = []
        for el in root.iter():
            tag = str(getattr(el, "tag", ""))
            if tag.endswith("rowdata"):
                st = el.attrib.get("pyShapeType")
                if not st:
                    continue
                sh = {
                    "shape_type": st,
                    "shape_name": el.attrib.get("pyShapeName"),
                    "shape_label": el.attrib.get("pyShapeLabel") or el.attrib.get("pyLabel"),
                    "flow_action": el.attrib.get("pyFlowAction"),
                    "when_rule": el.attrib.get("pyWhenRule") or el.attrib.get("pyWhen"),
                    "subflow_ref": el.attrib.get("pySubFlowName") or el.attrib.get("pyFlowName") if st == "SubProcess" else None,
                    "next": [],
                    "attrs": dict(el.attrib),
                }
                shape_list.append(sh)
                if sh["shape_name"]:
                    name_to_shape[sh["shape_name"]] = sh
        # Connectors: <rowdata pyFromShape="..." pyToShape="..." pyConnectorWhen="...">
        for el in root.iter():
            tag = str(getattr(el, "tag", ""))
            if tag.endswith("rowdata"):
                src = el.attrib.get("pyFromShape")
                dst = el.attrib.get("pyToShape")
                if src and dst and src in name_to_shape:
                    name_to_shape[src]["next"].append({
                        "to": dst,
                        "when": el.attrib.get("pyConnectorWhen"),
                        "likely": el.attrib.get("pyLikelihood"),
                    })
        shapes = shape_list
    except Exception:
        pass
    return shapes


def _parse_decision(path: Path) -> tuple[list, list]:
    inputs: list = []
    outcomes: list = []
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
        # Best effort — columns are inputs, return values are outcomes
        for el in root.iter():
            tag = str(getattr(el, "tag", ""))
            if tag.endswith("pyPropertyName") and el.text:
                inputs.append(el.text.strip())
            if tag.endswith("pyReturn") and el.text:
                outcomes.append(el.text.strip())
    except Exception:
        pass
    return inputs[:50], outcomes[:50]


def _render_case_type_mermaid(cur: sqlite3.Cursor, case_type_id: int, title: str) -> str:
    lines = [f"flowchart TD", f"    title[\"{_esc(title)}\"]:::ct", "    classDef ct fill:#0a1929,color:#fff"]
    lines.append("    classDef stage fill:#d4a017,color:#000")
    lines.append("    classDef asgn fill:#0a5c9a,color:#fff")

    stages = cur.execute(
        "SELECT stage_id, label, stage_order FROM stages WHERE case_type_id = ? ORDER BY stage_order",
        (case_type_id,),
    ).fetchall()

    prev_node = "title"
    for sid, slabel, sorder in stages:
        snode = f"S{sid}"
        lines.append(f'    {snode}["Stage: {_esc(slabel or str(sorder))}"]:::stage')
        lines.append(f"    {prev_node} --> {snode}")
        prev_node = snode

        steps = cur.execute(
            "SELECT step_id, label, flow_ref FROM steps WHERE stage_id = ? ORDER BY step_order",
            (sid,),
        ).fetchall()
        for step_id, step_label, flow_ref in steps:
            step_node = f"T{step_id}"
            label = _esc(step_label or flow_ref or "step")
            lines.append(f'    {step_node}["{label}"]')
            lines.append(f"    {snode} -.-> {step_node}")
    return "\n".join(lines)


def _wrap_mermaid(mermaid: str, title: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{_esc(title)}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>body{{font-family:-apple-system,Segoe UI,sans-serif;margin:20px}}h1{{color:#0a1929}}</style>
</head><body><h1>{_esc(title)}</h1>
<div class="mermaid">
{mermaid}
</div>
<script>mermaid.initialize({{startOnLoad:true, theme:'neutral'}});</script>
</body></html>"""


def _esc(s: str) -> str:
    return (s or "").replace('"', "'").replace("\n", " ")
