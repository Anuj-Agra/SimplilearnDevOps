"""
parser.py — Stream-parse rule XML into a typed rules table.
Uses lxml.iterparse with element clearing to keep memory flat at 200K+ rules.
"""
from __future__ import annotations

import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

try:
    from lxml import etree as ET
    _HAS_LXML = True
except ImportError:
    from xml.etree import ElementTree as ET
    _HAS_LXML = False

from .extractor import iter_rule_files

PARSER_SCHEMA = """
CREATE TABLE IF NOT EXISTS rules (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    obj_class TEXT,
    name TEXT,
    class_name TEXT,
    applies_to TEXT,
    ruleset TEXT,
    ruleset_version TEXT,
    file_path TEXT UNIQUE,
    parsed_ok INTEGER,
    parse_error TEXT
);
CREATE INDEX IF NOT EXISTS idx_rules_obj_class ON rules(obj_class);
CREATE INDEX IF NOT EXISTS idx_rules_class_name ON rules(class_name);
CREATE INDEX IF NOT EXISTS idx_rules_ruleset ON rules(ruleset);
CREATE INDEX IF NOT EXISTS idx_rules_name ON rules(name);

CREATE TABLE IF NOT EXISTS unknown_rule_types (
    obj_class TEXT PRIMARY KEY,
    count INTEGER,
    sample_file TEXT
);
"""

KNOWN_RULE_PREFIXES = (
    "Rule-Obj-Class", "Rule-Obj-Property", "Rule-Obj-CaseType", "Rule-Obj-Flow",
    "Rule-Obj-FlowAction", "Rule-Obj-Activity", "Rule-Obj-When", "Rule-Obj-ServiceLevel",
    "Rule-HTML-Section", "Rule-HTML-Harness", "Rule-HTML-Fragment",
    "Rule-Decision-Table", "Rule-Decision-Map", "Rule-Decision-Tree",
    "Rule-Declare-Expression", "Rule-Declare-OnChange", "Rule-Declare-Constraints",
    "Rule-Access-Role-Obj", "Rule-Access-Privilege",
    "Data-Admin-Operator-ID", "Data-Admin-WorkBasket", "Data-Admin-Organization",
)


@dataclass
class ParseResult:
    total: int
    parsed_ok: int
    parsed_fail: int
    by_obj_class: Counter
    unknown_types: list[str]


def parse_all(catalog_path: str | Path, unpacked_dir: str | Path) -> ParseResult:
    conn = sqlite3.connect(catalog_path)
    conn.executescript(PARSER_SCHEMA)
    cur = conn.cursor()

    by_class: Counter = Counter()
    unknown_samples: dict[str, str] = {}
    ok = fail = 0
    total = 0

    for path, _guess in iter_rule_files(catalog_path, unpacked_dir):
        total += 1
        row = _parse_one(path)
        if row["parsed_ok"]:
            ok += 1
            by_class[row["obj_class"]] += 1
            if not _is_known(row["obj_class"]):
                unknown_samples.setdefault(row["obj_class"], str(path))
        else:
            fail += 1

        cur.execute(
            "INSERT OR REPLACE INTO rules "
            "(obj_class, name, class_name, applies_to, ruleset, ruleset_version, "
            " file_path, parsed_ok, parse_error) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (row["obj_class"], row["name"], row["class_name"], row["applies_to"],
             row["ruleset"], row["ruleset_version"], row["file_path"],
             int(row["parsed_ok"]), row["parse_error"]),
        )

        if total % 5_000 == 0:
            conn.commit()

    # Log unknown types
    for oc, sample in unknown_samples.items():
        cur.execute(
            "INSERT OR REPLACE INTO unknown_rule_types (obj_class, count, sample_file) VALUES (?, ?, ?)",
            (oc, by_class[oc], sample),
        )

    conn.commit()
    conn.close()

    return ParseResult(
        total=total,
        parsed_ok=ok,
        parsed_fail=fail,
        by_obj_class=by_class,
        unknown_types=sorted(unknown_samples.keys()),
    )


def _parse_one(path: Path) -> dict:
    row = {
        "obj_class": None, "name": None, "class_name": None, "applies_to": None,
        "ruleset": None, "ruleset_version": None,
        "file_path": str(path), "parsed_ok": False, "parse_error": None,
    }
    try:
        # Only parse the root element's attributes + a handful of known children.
        # iterparse is O(file size) but we bail once we have everything.
        needed = {"pxObjClass", "pyRuleName", "pyLabel", "pyClassName",
                  "pyAppliesTo", "pyRuleSet", "pyRuleSetVersion"}
        found: dict[str, str] = {}

        if _HAS_LXML:
            context = ET.iterparse(str(path), events=("start",), recover=True)
        else:
            context = ET.iterparse(path, events=("start",))

        for _, elem in context:
            for k in needed:
                if k in elem.attrib and k not in found:
                    found[k] = elem.attrib[k]
                # child-element variant (some exports store these as child tags)
            # Also check if any child element *is* a needed key (some exports)
            if elem.tag in needed and elem.tag not in found and elem.text:
                found[elem.tag] = (elem.text or "").strip()

            if len(found) >= 3 and "pxObjClass" in found:
                # We have enough; stop walking this file.
                break

            # Memory hygiene
            if hasattr(elem, "clear"):
                elem.clear()

        row["obj_class"] = found.get("pxObjClass")
        row["name"] = found.get("pyRuleName") or found.get("pyLabel")
        row["class_name"] = found.get("pyClassName")
        row["applies_to"] = found.get("pyAppliesTo")
        row["ruleset"] = found.get("pyRuleSet")
        row["ruleset_version"] = found.get("pyRuleSetVersion")
        row["parsed_ok"] = bool(row["obj_class"])
        if not row["parsed_ok"]:
            row["parse_error"] = "no pxObjClass found"
    except Exception as e:
        row["parse_error"] = str(e)[:500]
    return row


def _is_known(obj_class: str | None) -> bool:
    if not obj_class:
        return False
    return any(obj_class.startswith(p) for p in KNOWN_RULE_PREFIXES)
