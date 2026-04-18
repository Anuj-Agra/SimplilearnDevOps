"""
hierarchy.py — Build the Ruleset → Class → Property → Access-Role hierarchy.
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

try:
    from lxml import etree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import networkx as nx
    _HAS_NX = True
except ImportError:
    _HAS_NX = False


HIERARCHY_SCHEMA = """
CREATE TABLE IF NOT EXISTS classes (
    class_name TEXT PRIMARY KEY,
    parent_class TEXT,
    ruleset TEXT,
    is_work_class INTEGER DEFAULT 0,
    is_data_class INTEGER DEFAULT 0,
    rule_count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS properties (
    class_name TEXT,
    property_name TEXT,
    data_type TEXT,
    is_required INTEGER DEFAULT 0,
    PRIMARY KEY (class_name, property_name)
);
CREATE TABLE IF NOT EXISTS access_roles (
    role_name TEXT,
    class_name TEXT,
    privilege_name TEXT,
    access_level INTEGER,
    PRIMARY KEY (role_name, class_name, privilege_name)
);
"""


@dataclass
class HierarchyResult:
    class_count: int
    property_count: int
    role_count: int
    work_classes: int
    data_classes: int
    tree_path: str
    html_path: str


def build(catalog_path: str | Path, workdir: str | Path) -> HierarchyResult:
    workdir = Path(workdir)
    unpacked = workdir / "unpacked"
    conn = sqlite3.connect(catalog_path)
    conn.executescript(HIERARCHY_SCHEMA)
    cur = conn.cursor()

    # Classes
    class_rows = cur.execute(
        "SELECT name, class_name, file_path, ruleset FROM rules "
        "WHERE obj_class = 'Rule-Obj-Class' AND parsed_ok = 1"
    ).fetchall()

    class_counts_by_class = dict(cur.execute(
        "SELECT class_name, COUNT(*) FROM rules WHERE parsed_ok = 1 GROUP BY class_name"
    ).fetchall())

    for name, _owning_class, file_path, ruleset in class_rows:
        if not name:
            continue
        parent = _extract_parent_class(unpacked / file_path)
        is_work = _class_chain_contains(name, parent, "Work-")
        is_data = _class_chain_contains(name, parent, "Data-")
        cur.execute(
            "INSERT OR REPLACE INTO classes (class_name, parent_class, ruleset, is_work_class, is_data_class, rule_count) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, parent, ruleset, int(is_work), int(is_data), class_counts_by_class.get(name, 0)),
        )

    # Properties
    prop_rows = cur.execute(
        "SELECT name, class_name, file_path FROM rules "
        "WHERE obj_class = 'Rule-Obj-Property' AND parsed_ok = 1"
    ).fetchall()
    for name, class_name, file_path in prop_rows:
        if not (name and class_name):
            continue
        dt, req = _extract_property_meta(unpacked / file_path)
        cur.execute(
            "INSERT OR REPLACE INTO properties (class_name, property_name, data_type, is_required) VALUES (?, ?, ?, ?)",
            (class_name, name, dt, int(req)),
        )

    # Access roles
    role_rows = cur.execute(
        "SELECT name, class_name, file_path FROM rules "
        "WHERE obj_class IN ('Rule-Access-Role-Obj', 'Rule-Access-Privilege') AND parsed_ok = 1"
    ).fetchall()
    for name, class_name, file_path in role_rows:
        privileges = _extract_privileges(unpacked / file_path)
        for priv, level in privileges:
            cur.execute(
                "INSERT OR REPLACE INTO access_roles (role_name, class_name, privilege_name, access_level) VALUES (?, ?, ?, ?)",
                (name, class_name, priv, level),
            )

    conn.commit()

    # Build nested tree
    tree = _build_tree(cur)
    tree_path = workdir / "hierarchy_tree.json"
    tree_path.write_text(json.dumps(tree, indent=2))

    html_path = workdir / "hierarchy.html"
    html_path.write_text(_render_hierarchy_html(tree))

    counts = cur.execute(
        "SELECT COUNT(*), SUM(is_work_class), SUM(is_data_class) FROM classes"
    ).fetchone()
    prop_count = cur.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
    role_count = cur.execute("SELECT COUNT(*) FROM access_roles").fetchone()[0]
    conn.close()

    return HierarchyResult(
        class_count=counts[0] or 0,
        property_count=prop_count,
        role_count=role_count,
        work_classes=counts[1] or 0,
        data_classes=counts[2] or 0,
        tree_path=str(tree_path),
        html_path=str(html_path),
    )


def _extract_parent_class(path: Path) -> str | None:
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
        return root.attrib.get("pyParentClassName") or _find_child_text(root, "pyParentClassName")
    except Exception:
        return None


def _extract_property_meta(path: Path) -> tuple[str | None, bool]:
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
        dt = root.attrib.get("pyPropertyType") or _find_child_text(root, "pyPropertyType")
        required = (root.attrib.get("pyPropertyRequired") or "").lower() == "true"
        return dt, required
    except Exception:
        return None, False


def _extract_privileges(path: Path) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
        # Pega encodes privileges as <pyPrivileges> ... <rowdata pyPrivilegeName="..." pyAccessLevel="5"/>
        for el in root.iter():
            tag = getattr(el, "tag", "")
            if isinstance(tag, str) and tag.endswith("rowdata"):
                priv = el.attrib.get("pyPrivilegeName")
                try:
                    level = int(el.attrib.get("pyAccessLevel", "0"))
                except ValueError:
                    level = 0
                if priv:
                    out.append((priv, level))
    except Exception:
        pass
    return out


def _find_child_text(root, child_tag: str) -> str | None:
    for el in root.iter():
        tag = getattr(el, "tag", "")
        if isinstance(tag, str) and tag.endswith(child_tag):
            return (el.text or "").strip() or None
    return None


def _class_chain_contains(cls: str, parent: str | None, marker: str) -> bool:
    return (marker in (cls or "")) or (marker in (parent or ""))


def _build_tree(cur: sqlite3.Cursor) -> dict:
    rows = cur.execute(
        "SELECT class_name, parent_class, ruleset, is_work_class, is_data_class, rule_count FROM classes"
    ).fetchall()
    by_parent: dict[str | None, list] = defaultdict(list)
    nodes: dict[str, dict] = {}
    for name, parent, ruleset, iw, id_, rc in rows:
        nodes[name] = {
            "name": name, "parent": parent, "ruleset": ruleset,
            "is_work": bool(iw), "is_data": bool(id_), "rule_count": rc,
            "children": [],
        }
    for n in nodes.values():
        by_parent[n["parent"]].append(n)
    for n in nodes.values():
        n["children"] = sorted(by_parent.get(n["name"], []), key=lambda c: c["name"])
    roots = sorted(by_parent[None] + [n for n in nodes.values() if n["parent"] and n["parent"] not in nodes],
                   key=lambda c: c["name"])
    return {"roots": roots, "total": len(nodes)}


def _render_hierarchy_html(tree: dict) -> str:
    return """<!doctype html><html><head><meta charset="utf-8">
<title>Pega Class Hierarchy</title>
<style>
  body{font-family:-apple-system,Segoe UI,sans-serif;margin:20px;color:#1a2332}
  h1{color:#0a1929}
  details{margin-left:1.2em}
  summary{cursor:pointer;padding:2px 0}
  .work{color:#0a5c9a}
  .data{color:#0f6b3b}
  .count{color:#666;font-size:.85em}
</style></head><body>
<h1>Pega Class Hierarchy</h1>
<div id="tree"></div>
<script>
const data = __DATA__;
const root = document.getElementById('tree');
function render(node, into){
  const d=document.createElement('details');
  const s=document.createElement('summary');
  const cls=node.is_work?'work':node.is_data?'data':'';
  s.innerHTML=`<span class="${cls}">${node.name}</span> <span class="count">(${node.rule_count} rules, ${node.ruleset||'?'})</span>`;
  d.appendChild(s);
  (node.children||[]).forEach(c=>render(c,d));
  into.appendChild(d);
}
data.roots.forEach(r=>render(r,root));
</script></body></html>""".replace("__DATA__", json.dumps(tree))
