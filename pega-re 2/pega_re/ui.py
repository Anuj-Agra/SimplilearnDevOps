"""
ui.py — Render Pega Sections and Harnesses into standalone HTML.
Structural fidelity, not pixel-perfect runtime recreation.
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


UI_SCHEMA = """
CREATE TABLE IF NOT EXISTS ui_rules (
    ui_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER,
    ui_type TEXT,
    class_name TEXT,
    name TEXT,
    parent_harness TEXT,
    referenced_sections_json TEXT,
    referenced_properties_json TEXT,
    rendered_html_path TEXT,
    fidelity TEXT
);
CREATE INDEX IF NOT EXISTS idx_ui_type ON ui_rules(ui_type);
CREATE INDEX IF NOT EXISTS idx_ui_class ON ui_rules(class_name);
"""


PEGA_CSS = """
body{font-family:-apple-system,Segoe UI,Arial,sans-serif;margin:0;color:#1a2332;background:#f4f6f9}
.pega-harness{max-width:1100px;margin:0 auto;background:#fff;min-height:100vh}
.pega-harness-header{background:#0a1929;color:#fff;padding:14px 20px;font-size:18px;font-weight:600}
.pega-harness-body{padding:20px}
.pega-section{border:1px solid #d0d7de;border-radius:4px;padding:14px 18px;margin:12px 0;background:#fff}
.pega-section-title{font-weight:600;color:#0a1929;margin:0 0 10px 0;font-size:14px;text-transform:uppercase;letter-spacing:.4px}
.pega-dl{display:grid;grid-template-columns:180px 1fr;gap:8px 14px;align-items:start}
.pega-dl.cols2{grid-template-columns:180px 1fr 180px 1fr}
.pega-field-label{color:#57606a;font-size:13px;padding-top:6px}
.pega-field-value{border:1px solid #d0d7de;border-radius:3px;padding:6px 8px;font-size:13px;background:#fafbfc;min-height:18px}
.pega-ref{color:#0a5c9a;font-style:italic}
.pega-conditional{border-left:3px solid #d4a017;padding-left:10px;margin:6px 0}
.pega-conditional::before{content:"when: " attr(data-when);display:inline-block;background:#fff4d6;color:#8b6914;padding:2px 6px;border-radius:3px;font-size:11px;margin-right:8px}
.pega-action{background:#0a5c9a;color:#fff;border:0;padding:8px 16px;border-radius:3px;cursor:pointer;font-size:13px;margin:4px 4px 4px 0}
.pega-action:hover{background:#084a7c}
.pega-action.secondary{background:#eaeef2;color:#1a2332;border:1px solid #d0d7de}
.pega-grid{width:100%;border-collapse:collapse;margin:8px 0}
.pega-grid th{background:#f4f6f9;text-align:left;padding:8px;border:1px solid #d0d7de;font-size:13px}
.pega-grid td{padding:6px 8px;border:1px solid #d0d7de;font-size:13px}
.pega-warn{background:#fff4d6;border:1px solid #d4a017;color:#8b6914;padding:10px 14px;border-radius:3px;margin:10px 0;font-size:13px}
"""


@dataclass
class UIResult:
    rendered_count: int
    harness_count: int
    section_count: int
    partial_fidelity: int
    stub_fidelity: int
    index_path: str


def render_all(catalog_path: str | Path, workdir: str | Path) -> UIResult:
    workdir = Path(workdir)
    unpacked = workdir / "unpacked"
    ui_dir = workdir / "ui"
    ui_dir.mkdir(parents=True, exist_ok=True)
    (ui_dir / "_pega.css").write_text(PEGA_CSS)

    conn = sqlite3.connect(catalog_path)
    conn.executescript(UI_SCHEMA)
    cur = conn.cursor()

    ui_rows = cur.execute(
        "SELECT rule_id, obj_class, name, class_name, file_path FROM rules "
        "WHERE obj_class IN ('Rule-HTML-Harness', 'Rule-HTML-Section', 'Rule-HTML-Fragment') "
        "AND parsed_ok = 1"
    ).fetchall()

    harness_count = section_count = partial = stub = 0
    rendered = 0

    # First pass: build a name→file_path index so Sections can be inlined into Harnesses
    section_files: dict[str, Path] = {}
    for rule_id, obj_class, name, class_name, file_path in ui_rows:
        if obj_class == "Rule-HTML-Section" and name:
            section_files[f"{class_name}.{name}"] = unpacked / file_path
            section_files[name] = unpacked / file_path

    for rule_id, obj_class, name, class_name, file_path in ui_rows:
        html, referenced_sections, referenced_props, fidelity = _render_one(
            unpacked / file_path, obj_class, name, class_name, section_files
        )
        ui_type = obj_class.replace("Rule-HTML-", "").lower()
        safe_cls = (class_name or "unknown").replace("-", "_")
        out_dir = ui_dir / safe_cls
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{ui_type}_{(name or 'unnamed').replace('/', '_')}.html"
        out_path.write_text(html)

        if obj_class == "Rule-HTML-Harness":
            harness_count += 1
        else:
            section_count += 1
        if fidelity == "partial":
            partial += 1
        elif fidelity == "stub":
            stub += 1
        rendered += 1

        cur.execute(
            "INSERT INTO ui_rules (rule_id, ui_type, class_name, name, parent_harness, "
            "referenced_sections_json, referenced_properties_json, rendered_html_path, fidelity) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (rule_id, ui_type, class_name, name, None,
             json.dumps(referenced_sections), json.dumps(referenced_props),
             str(out_path.relative_to(workdir)), fidelity),
        )

    conn.commit()

    # Build index
    index_path = ui_dir / "index.html"
    index_path.write_text(_render_index(cur))
    conn.close()

    return UIResult(
        rendered_count=rendered,
        harness_count=harness_count,
        section_count=section_count,
        partial_fidelity=partial,
        stub_fidelity=stub,
        index_path=str(index_path),
    )


def _render_one(path: Path, obj_class: str, name: str, class_name: str,
                section_files: dict[str, Path]) -> tuple[str, list, list, str]:
    """
    Returns (html, referenced_sections, referenced_properties, fidelity)
    """
    referenced_sections: list[str] = []
    referenced_props: list[str] = []
    fidelity = "full"

    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
    except Exception:
        return _stub_html(name or "unknown", "Rule could not be parsed"), [], [], "stub"

    # Walk the XML tree looking for known constructs.
    body_parts: list[str] = []
    warnings: list[str] = []

    for el in root.iter():
        tag = str(getattr(el, "tag", ""))
        # Layouts
        if tag.endswith("Layout") or "Layout" in tag:
            body_parts.append('<div class="pega-dl">')
        elif tag.endswith("Field") or tag.endswith("Cell"):
            label = el.attrib.get("pyLabel") or el.attrib.get("label") or ""
            prop = el.attrib.get("pyPropertyName") or el.attrib.get("reference")
            if prop:
                referenced_props.append(prop)
                body_parts.append(
                    f'<div class="pega-field-label">{_esc(label or prop)}</div>'
                    f'<div class="pega-field-value"><span class="pega-ref" data-ref="{_esc(prop)}">{{{_esc(prop)}}}</span></div>'
                )
        elif tag.endswith("IncludeSection") or tag.endswith("Section"):
            ref = el.attrib.get("pySectionName") or el.attrib.get("name")
            if ref:
                referenced_sections.append(ref)
                inlined = _inline_section(ref, class_name, section_files, depth=1)
                body_parts.append(inlined or f'<div class="pega-section"><p class="pega-section-title">Included: {_esc(ref)}</p><p class="pega-ref">(section contents)</p></div>')
        elif tag.endswith("Button") or tag.endswith("Action"):
            action = el.attrib.get("pyAction") or el.attrib.get("pyFlowAction") or el.attrib.get("label") or "action"
            body_parts.append(f'<button class="pega-action" data-action="{_esc(action)}">{_esc(action)}</button>')
        elif tag.endswith("RepeatGrid") or tag.endswith("Grid"):
            body_parts.append('<table class="pega-grid"><thead><tr><th>(repeat grid — columns from rule)</th></tr></thead><tbody><tr><td>…</td></tr></tbody></table>')
            fidelity = "partial"
            warnings.append("Repeat grid rendered as placeholder")
        elif tag.endswith("Visible") or tag.endswith("When"):
            when = el.attrib.get("pyConditionName") or el.attrib.get("name")
            if when:
                body_parts.append(f'<div class="pega-conditional" data-when="{_esc(when)}">')
        elif tag.endswith("Script") or tag.endswith("CustomHTML"):
            body_parts.append('<div class="pega-warn">⚠ Dynamic content (custom HTML/JS) — structure shown, runtime behaviour not reproduced.</div>')
            fidelity = "partial" if fidelity == "full" else fidelity

    inner = "\n".join(body_parts)
    if not inner.strip():
        return _stub_html(name or "unknown", "No recognisable UI constructs"), [], [], "stub"

    warnings_html = ""
    if warnings:
        warnings_html = '<div class="pega-warn">' + "; ".join(warnings) + "</div>"

    if obj_class == "Rule-HTML-Harness":
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{_esc(name)}</title>
<link rel="stylesheet" href="../_pega.css"></head><body>
<div class="pega-harness">
  <div class="pega-harness-header">{_esc(name)} <span style="opacity:.6;font-weight:400;font-size:13px;margin-left:12px">{_esc(class_name)}</span></div>
  <div class="pega-harness-body">
    {warnings_html}
    <div class="pega-section">{inner}</div>
  </div>
</div></body></html>"""
    else:
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{_esc(name)}</title>
<link rel="stylesheet" href="../_pega.css"></head><body>
<div class="pega-harness">
  <div class="pega-harness-header">Section: {_esc(name)} <span style="opacity:.6;font-weight:400;font-size:13px;margin-left:12px">{_esc(class_name)}</span></div>
  <div class="pega-harness-body">
    {warnings_html}
    <div class="pega-section"><div class="pega-section-title">{_esc(name)}</div>{inner}</div>
  </div>
</div></body></html>"""

    return html, referenced_sections, referenced_props, fidelity


def _inline_section(ref: str, class_name: str, section_files: dict[str, Path], depth: int) -> str | None:
    if depth > 1:
        return f'<section class="pega-section"><div class="pega-section-title">Included: {_esc(ref)}</div><p class="pega-ref">(nested include omitted)</p></section>'
    p = section_files.get(f"{class_name}.{ref}") or section_files.get(ref)
    if not p or not p.exists():
        return None
    html, _, _, _ = _render_one(p, "Rule-HTML-Section", ref, class_name, section_files)
    # Extract just the inner section div
    start = html.find('<div class="pega-section">')
    end = html.rfind("</div></div></body>")
    if start >= 0 and end > start:
        return html[start:end]
    return html


def _stub_html(name: str, reason: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{_esc(name)}</title>
<link rel="stylesheet" href="../_pega.css"></head><body>
<div class="pega-harness">
  <div class="pega-harness-header">{_esc(name)}</div>
  <div class="pega-harness-body">
    <div class="pega-warn">⚠ Stub rendering — {_esc(reason)}. See original rule XML for details.</div>
  </div>
</div></body></html>"""


def _render_index(cur: sqlite3.Cursor) -> str:
    rows = cur.execute(
        "SELECT class_name, ui_type, name, rendered_html_path, fidelity FROM ui_rules "
        "ORDER BY class_name, ui_type DESC, name"
    ).fetchall()
    items = "\n".join(
        f'<li class="f-{fidelity}"><a href="{_esc(path)}" target="ui-frame">[{ui_type}] {_esc(name or "(unnamed)")}'
        f'<span class="cls"> — {_esc(cls or "?")}</span></a></li>'
        for cls, ui_type, name, path, fidelity in rows
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Pega UI Catalog</title>
<style>
  body{{margin:0;font-family:-apple-system,Segoe UI,sans-serif;display:flex;height:100vh}}
  #nav{{width:360px;overflow-y:auto;background:#f4f6f9;border-right:1px solid #d0d7de;padding:10px}}
  #nav h1{{color:#0a1929;font-size:16px;margin:0 0 10px 0}}
  #nav ul{{list-style:none;padding:0;margin:0}}
  #nav li{{padding:4px 6px;font-size:13px}}
  #nav a{{color:#0a5c9a;text-decoration:none}}
  #nav .cls{{color:#57606a;font-size:11px}}
  #nav li.f-partial::before{{content:"◐ ";color:#d4a017}}
  #nav li.f-stub::before{{content:"◯ ";color:#999}}
  #frame{{flex:1}}
  iframe{{width:100%;height:100%;border:0}}
</style></head><body>
<div id="nav">
<h1>Pega UI Catalog ({len(rows)})</h1>
<ul>{items}</ul>
</div>
<div id="frame"><iframe name="ui-frame"></iframe></div>
</body></html>"""


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
