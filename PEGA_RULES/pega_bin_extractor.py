#!/usr/bin/env python3
"""
pega_bin_extractor.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREA — Pega Binary Rule Extractor

Extracts structured rule records from Pega Platform .bin binary export files.

Pega .bin files are proprietary binary containers that wrap compressed or
raw XML rule definitions. This extractor handles:

  1. Pega PRPC legacy binary format (magic bytes 0x504547 "PEG")
  2. ZIP-wrapped rule containers (Pega 7.x+, Pega Infinity)
  3. Raw XML rule dumps (exported via Pega DevOps tools)
  4. GZIP-compressed rule blobs within .bin wrappers
  5. Java serialised objects (limited — extracts XML payload only)

The extractor writes a rules_extracted.json with one record per rule,
ready for downstream graph building, flow tracing, and FRD generation.

Usage:
    python pega_bin_extractor.py --input-dir ./bins --manifest manifest.json
                                  --output rules_extracted.json --verbose

    python pega_bin_extractor.py --input-file rules.bin --output rules.json

    python pega_bin_extractor.py --input-dir ./bins --output rules.json
                                  --layer Enterprise --ruleset KYCPlatform
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import argparse
import gzip
import hashlib
import io
import json
import logging
import os
import re
import struct
import sys
import zipfile
import zlib
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from xml.etree import ElementTree as ET

# ── Optional deps (graceful degradation) ───────────────────────────────────
try:
    from lxml import etree as lxml_etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("prea.extractor")

# ── Constants ───────────────────────────────────────────────────────────────

# Known Pega binary magic signatures
MAGIC_PEGA_LEGACY  = b"PEG"          # Pega PRPC 5.x/6.x legacy
MAGIC_ZIP          = b"PK\x03\x04"   # ZIP (Pega 7+, Infinity)
MAGIC_GZIP         = b"\x1f\x8b"     # GZIP compressed blob
MAGIC_JAVA_SER     = b"\xac\xed"     # Java serialised object
MAGIC_XML          = b"<?xml"        # Raw XML dump

# Pega rule type markers found inside XML payloads
RULE_TYPE_PATTERNS: Dict[str, str] = {
    r"<flow[\s>]":              "Flow",
    r"<activity[\s>]":         "Activity",
    r"<section[\s>]":          "UI Section",
    r"<harness[\s>]":          "Harness",
    r"<header[\s>]":           "Header",
    r"<footer[\s>]":           "Footer",
    r"<navigation[\s>]":       "Navigation",
    r"<decision[\s>]":         "Decision Table",
    r"<map[\s>]":              "Data Transform",
    r"<declare[\s>]":          "Declare Expression",
    r"<when[\s>]":             "When Rule",
    r"<validate[\s>]":         "Validate Rule",
    r"<correspondence[\s>]":   "Correspondence",
    r"<report[\s>]":           "Report Definition",
    r"<connector[\s>]":        "Connector",
    r"<portal[\s>]":           "Portal",
    r"<ruleset[\s>]":          "RuleSet",
    r"<datapage[\s>]":         "Data Page",
    r"<procedure[\s>]":        "Procedure",
    r"<servicerest[\s>]":      "Service REST",
    r"<servicesoap[\s>]":      "Service SOAP",
    r"<connectorrest[\s>]":    "Connector REST",
}

# XML attributes that carry metadata
ATTR_CLASSNAME   = ["pzInsKey", "pyClassName", "classname", "class", "pxObjClass"]
ATTR_RULENAME    = ["pyRuleName", "ruleName", "name", "pyLabel"]
ATTR_RULESET     = ["pyRuleSet", "ruleSetName", "rsName"]
ATTR_VERSION     = ["pyRuleSetVersion", "ruleSetVersion", "version"]
ATTR_UPDATED     = ["pxUpdateDateTime", "pyUpdateDateTime", "updateDateTime"]
ATTR_CREATED     = ["pxCreateDateTime", "pyCreateDateTime", "createDateTime"]
ATTR_STATUS      = ["pyStatus", "status"]
ATTR_AUTHOR      = ["pxUpdateOpName", "pyUpdateOpName", "author"]

# Pega layer heuristics (derived from ruleset name patterns)
LAYER_PATTERNS: Dict[str, str] = {
    r"(?i)^(pega|prpc|platform|base|standard|common)": "Framework",
    r"(?i)(fs|finserv|financial|banking|insurance|industry|capital)": "Industry",
    r"(?i)(enterprise|ent|corp|group|shared|global)": "Enterprise",
    r"(?i)(impl|app|project|custom|local|client)": "Implementation",
}


# ── Data Model ──────────────────────────────────────────────────────────────

@dataclass
class PegaRule:
    rule_id:          str
    name:             str
    rule_type:        str
    pega_class:       str
    layer:            str
    ruleset:          str
    ruleset_version:  str
    status:           str
    created:          str
    updated:          str
    author:           str
    source_file:      str
    checksum:         str
    raw_xml:          str
    dependencies:     List[str] = field(default_factory=list)
    ui_fields:        List[Dict[str, Any]] = field(default_factory=list)
    conditions:       List[Dict[str, str]] = field(default_factory=list)
    actors:           List[str] = field(default_factory=list)
    flow_steps:       List[Dict[str, Any]] = field(default_factory=list)
    decision_rows:    List[Dict[str, Any]] = field(default_factory=list)
    data_mappings:    List[Dict[str, str]] = field(default_factory=list)
    notes:            str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("raw_xml", None)   # omit raw XML from default JSON (too large)
        return d


# ── Binary Format Detectors ─────────────────────────────────────────────────

def detect_format(data: bytes) -> str:
    """Detect the binary format of a Pega .bin file."""
    if data[:4] == MAGIC_ZIP:
        return "zip"
    if data[:2] == MAGIC_GZIP:
        return "gzip"
    if data[:2] == MAGIC_JAVA_SER:
        return "java_serialized"
    if data[:3] == MAGIC_PEGA_LEGACY:
        return "pega_legacy"
    if data[:5].lower() == MAGIC_XML or data[:5] == b"<?XML":
        return "raw_xml"
    if b"<?xml" in data[:1024]:
        return "raw_xml_with_header"
    # Scan for ZIP local file header anywhere (embedded ZIP)
    if b"PK\x03\x04" in data[:65536]:
        return "embedded_zip"
    # Scan for XML fragments — likely a raw dump
    if b"<flow" in data[:65536] or b"<section" in data[:65536] or b"<activity" in data[:65536]:
        return "raw_xml_fragment"
    return "unknown"


# ── Format-Specific Parsers ─────────────────────────────────────────────────

def parse_zip(data: bytes, source_file: str) -> List[str]:
    """
    Extract XML payloads from a ZIP-wrapped Pega export.
    Pega 7+ and Infinity export rulesets as ZIP archives containing:
      - One XML file per rule (named <ClassName>.<RuleName>.xml or similar)
      - A prdExport.xml manifest at the root
    """
    xmls = []
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for entry in zf.namelist():
                if entry.lower().endswith(".xml"):
                    try:
                        content = zf.read(entry)
                        # Handle nested GZIP within ZIP
                        if content[:2] == MAGIC_GZIP:
                            content = gzip.decompress(content)
                        xmls.append(content.decode("utf-8", errors="replace"))
                    except Exception as e:
                        log.debug("Skipping ZIP entry %s: %s", entry, e)
                # Recurse into nested ZIPs (Pega sometimes nests ruleset ZIPs)
                elif entry.lower().endswith(".zip") or entry.lower().endswith(".bin"):
                    try:
                        nested = zf.read(entry)
                        xmls.extend(parse_zip(nested, f"{source_file}/{entry}"))
                    except Exception:
                        pass
    except zipfile.BadZipFile:
        log.warning("Bad ZIP in %s — attempting raw scan", source_file)
        xmls.extend(scan_for_xml_fragments(data))
    return xmls


def parse_gzip(data: bytes) -> List[str]:
    """Decompress GZIP blob and recurse."""
    try:
        inner = gzip.decompress(data)
        fmt = detect_format(inner)
        if fmt == "zip":
            return parse_zip(inner, "<gzip_inner>")
        return extract_xml_from_raw(inner)
    except Exception as e:
        log.debug("GZIP decompress failed: %s", e)
        # Try zlib raw inflate (Pega sometimes omits GZIP headers)
        try:
            inner = zlib.decompress(data[2:])   # skip 2-byte zlib header
            return extract_xml_from_raw(inner)
        except Exception:
            return []


def parse_pega_legacy(data: bytes, source_file: str) -> List[str]:
    """
    Parse Pega PRPC 5.x/6.x legacy binary format.

    Legacy format structure:
      Offset  Size  Description
      0       3     Magic "PEG"
      3       1     Format version (0x01 or 0x02)
      4       4     Record count (big-endian uint32)
      8       4     Index offset (big-endian uint32)
      12      ...   Data blocks

    Each data block:
      0       4     Block size (big-endian uint32)
      4       2     Compression flag (0=none, 1=zlib, 2=gzip)
      6       2     Rule type code
      8       N     Payload bytes
    """
    xmls = []
    if len(data) < 12:
        return xmls

    try:
        version = data[3]
        record_count = struct.unpack(">I", data[4:8])[0]
        index_offset = struct.unpack(">I", data[8:12])[0]

        log.debug("Legacy format v%d, %d records, index@%d", version, record_count, index_offset)

        # Sanity check
        if record_count > 500_000 or index_offset > len(data):
            log.warning("Legacy header looks corrupt — falling back to raw scan")
            return scan_for_xml_fragments(data)

        offset = 12
        for _ in range(record_count):
            if offset + 8 > len(data):
                break
            block_size = struct.unpack(">I", data[offset:offset+4])[0]
            compress    = struct.unpack(">H", data[offset+4:offset+6])[0]
            # rule_type_code = struct.unpack(">H", data[offset+6:offset+8])[0]
            payload = data[offset+8: offset+8+block_size]
            offset += 8 + block_size

            if compress == 1:
                try: payload = zlib.decompress(payload)
                except Exception: pass
            elif compress == 2:
                try: payload = gzip.decompress(payload)
                except Exception: pass

            if payload[:5].lower() in (b"<?xml", b"<?XML"):
                xmls.append(payload.decode("utf-8", errors="replace"))
            else:
                xmls.extend(scan_for_xml_fragments(payload))

    except (struct.error, ValueError) as e:
        log.warning("Legacy parse error (%s) — raw scan fallback", e)
        xmls = scan_for_xml_fragments(data)

    return xmls


def parse_java_serialized(data: bytes) -> List[str]:
    """
    Extract XML from Java serialised object streams.
    Pega sometimes wraps rule XML in Java ObjectOutputStream format.
    We don't fully deserialise — we scan for UTF-8 XML strings embedded
    in the stream using the Java string length prefix pattern.
    """
    xmls = []
    i = 0
    while i < len(data) - 4:
        # Java serialisation uses 2-byte length prefix for strings (0x74 opcode)
        if data[i] == 0x74:
            length = struct.unpack(">H", data[i+1:i+3])[0]
            if 20 < length < 1_000_000 and i+3+length <= len(data):
                chunk = data[i+3:i+3+length]
                if b"<?xml" in chunk or b"<flow" in chunk or b"<section" in chunk:
                    xmls.append(chunk.decode("utf-8", errors="replace"))
                    i += 3 + length
                    continue
        i += 1
    if not xmls:
        xmls.extend(scan_for_xml_fragments(data))
    return xmls


def extract_xml_from_raw(data: bytes) -> List[str]:
    """Parse a raw byte sequence that is (or contains) XML."""
    text = data.decode("utf-8", errors="replace")
    if text.strip().startswith("<?xml") or text.strip().startswith("<"):
        return [text]
    return scan_for_xml_fragments(data)


def scan_for_xml_fragments(data: bytes) -> List[str]:
    """
    Last-resort scanner: find all XML fragments in arbitrary binary data.
    Looks for <?xml or known Pega root elements and extracts balanced content.
    """
    xmls = []
    text = data.decode("utf-8", errors="replace")

    # Markers that indicate a Pega rule root element
    root_patterns = [
        "<?xml", "<flow ", "<flow>", "<activity ", "<section ", "<harness ",
        "<decision ", "<map ", "<declare ", "<when ", "<validate ",
        "<correspondence ", "<report ", "<datapage ", "<connector ",
    ]

    for pattern in root_patterns:
        start = 0
        while True:
            idx = text.find(pattern, start)
            if idx == -1:
                break
            # Find a reasonable end — look for closing tag
            end = text.find("</", idx + len(pattern))
            if end == -1:
                break
            # Grab up to 2MB from here
            fragment = text[idx: min(idx + 2_000_000, len(text))]
            xmls.append(fragment)
            start = idx + 1

    return list(dict.fromkeys(xmls))   # deduplicate while preserving order


# ── XML Rule Parser ──────────────────────────────────────────────────────────

def infer_rule_type(xml_text: str) -> str:
    """Infer the Pega rule type from XML content."""
    for pattern, rule_type in RULE_TYPE_PATTERNS.items():
        if re.search(pattern, xml_text, re.IGNORECASE):
            return rule_type
    return "Unknown"


def infer_layer(ruleset_name: str) -> str:
    """Infer architectural layer from ruleset name using heuristics."""
    for pattern, layer in LAYER_PATTERNS.items():
        if re.search(pattern, ruleset_name or ""):
            return layer
    return "Unknown"


def extract_attr(root, attr_candidates: List[str]) -> str:
    """Try multiple attribute name candidates on an XML element."""
    for attr in attr_candidates:
        val = root.get(attr, "")
        if val:
            return val.strip()
    # Try as child elements too
    for attr in attr_candidates:
        el = root.find(f".//{attr}")
        if el is not None and el.text:
            return el.text.strip()
    return ""


def extract_dependencies(root) -> List[str]:
    """
    Extract rule references from an XML tree.
    Pega rules reference each other via:
      - <step methodName="..."> in flows
      - <localflow name="..."> subprocess calls
      - <callactivity name="...">
      - dataTransformName attributes in maps
      - whenName attributes in conditionals
      - pzInsKey references
    """
    deps = set()
    dep_attrs = [
        "methodName", "name", "target", "flowName", "activityName",
        "dataTransformName", "whenName", "validationName", "sectionName",
        "harnessName", "reportName", "decisionName", "mapName",
    ]
    for el in root.iter():
        for attr in dep_attrs:
            val = el.get(attr, "")
            if val and not val.startswith(".") and not val.startswith("py"):
                deps.add(val.strip())
        # Step references in flow XML
        if el.tag in ("step", "Step", "localflow", "LocalFlow", "subprocess"):
            name = el.get("name") or el.get("stepName") or el.get("methodName", "")
            if name:
                deps.add(name.strip())
    return sorted(deps)


def extract_ui_fields(root) -> List[Dict[str, Any]]:
    """Extract field/control definitions from UI rule XML."""
    fields = []
    field_tags = ["field", "Field", "control", "Control", "column", "Column"]
    for el in root.iter():
        if el.tag in field_tags:
            field_def = {
                "name": el.get("name") or el.get("fieldName") or el.get("label") or "",
                "type": el.get("type") or el.get("controlType") or "Text",
                "required": el.get("required") or el.get("mandatory") or "false",
                "visible_when": el.get("visibleWhen") or el.get("conditionalDisplay") or "",
                "read_only": el.get("readOnly") or el.get("readonly") or "false",
                "label": el.get("label") or el.get("caption") or "",
                "data_page": el.get("dataPage") or el.get("listDataPage") or "",
            }
            if field_def["name"]:
                fields.append(field_def)
    return fields


def extract_flow_steps(root) -> List[Dict[str, Any]]:
    """Extract flow step definitions from a Flow rule XML."""
    steps = []
    step_tags = ["step", "Step", "assignment", "Assignment", "decision", "Decision",
                 "subprocess", "Subprocess", "utility", "Utility", "split", "join"]
    seen = set()
    for el in root.iter():
        if el.tag.lower() in [t.lower() for t in step_tags]:
            name = el.get("name") or el.get("stepName") or el.get("label") or el.tag
            if name in seen:
                continue
            seen.add(name)
            step = {
                "name": name,
                "type": el.tag,
                "method": el.get("methodName") or el.get("method") or "",
                "actor": el.get("workParty") or el.get("actor") or "",
                "when": el.get("when") or el.get("condition") or "",
                "transition": [
                    {"to": c.get("to") or c.get("name", ""), "when": c.get("when") or c.get("condition", "")}
                    for c in el
                    if c.tag.lower() in ("transition", "connector", "when", "next")
                ],
            }
            steps.append(step)
    return steps


def extract_conditions(root) -> List[Dict[str, str]]:
    """Extract when/condition rules from any rule type."""
    conditions = []
    for el in root.iter():
        when_expr = el.get("when") or el.get("condition") or el.get("expression") or ""
        if when_expr and len(when_expr) > 2:
            conditions.append({
                "context": el.tag,
                "expression": when_expr.strip(),
                "outcome": el.get("outcome") or el.get("action") or "",
            })
    return conditions


def extract_actors(root) -> List[str]:
    """Extract work parties / actors from a rule."""
    actors = set()
    actor_attrs = ["workParty", "actor", "operator", "skillID", "workgroup"]
    for el in root.iter():
        for attr in actor_attrs:
            val = el.get(attr, "")
            if val and not val.startswith(".") and len(val) < 100:
                actors.add(val.strip())
    return sorted(actors)


def extract_decision_rows(root) -> List[Dict[str, Any]]:
    """Extract rows from Decision Table / Decision Tree XML."""
    rows = []
    for el in root.iter():
        if el.tag.lower() in ("row", "branch", "rule"):
            conditions = {c.tag: c.get("value") or c.text or ""
                         for c in el if c.get("type") == "condition"}
            result     = el.get("result") or el.get("action") or ""
            if conditions or result:
                rows.append({"conditions": conditions, "result": result})
    return rows


def extract_data_mappings(root) -> List[Dict[str, str]]:
    """Extract source→target mappings from Data Transform XML."""
    mappings = []
    for el in root.iter():
        if el.tag.lower() in ("map", "transform", "set", "mapping"):
            src = el.get("source") or el.get("from") or el.get("fieldName") or ""
            tgt = el.get("target") or el.get("to") or el.get("mapTo") or ""
            if src or tgt:
                mappings.append({"source": src.strip(), "target": tgt.strip()})
    return mappings


def parse_rule_xml(xml_text: str, source_file: str,
                   manifest_data: Optional[Dict] = None,
                   counter: List[int] = None) -> Optional[PegaRule]:
    """
    Parse a single XML string into a PegaRule record.
    Returns None if the XML is not a recognisable Pega rule.
    """
    if counter is None:
        counter = [0]

    # Skip empty or near-empty XML
    if len(xml_text.strip()) < 50:
        return None

    try:
        root = ET.fromstring(xml_text.encode("utf-8", errors="replace"))
    except ET.ParseError:
        # Attempt to strip garbage prefix before the XML declaration
        m = re.search(r"<\?xml", xml_text)
        if m:
            try:
                root = ET.fromstring(xml_text[m.start():].encode("utf-8", errors="replace"))
            except ET.ParseError:
                return None
        else:
            return None

    # Extract core metadata
    name         = extract_attr(root, ATTR_RULENAME)
    pega_class   = extract_attr(root, ATTR_CLASSNAME)
    ruleset      = extract_attr(root, ATTR_RULESET)
    version      = extract_attr(root, ATTR_VERSION)
    updated      = extract_attr(root, ATTR_UPDATED)
    created      = extract_attr(root, ATTR_CREATED)
    status       = extract_attr(root, ATTR_STATUS) or "Active"
    author       = extract_attr(root, ATTR_AUTHOR)
    rule_type    = infer_rule_type(xml_text)

    # Fall back to root tag as rule name if not found in attributes
    if not name:
        name = root.tag

    # Skip obvious non-rule XML (manifest, metadata only)
    if rule_type == "Unknown" and not pega_class and not ruleset:
        return None

    # Layer: prefer manifest data, fall back to heuristic
    if manifest_data and ruleset in manifest_data.get("layer_map", {}):
        layer = manifest_data["layer_map"][ruleset]
    else:
        layer = infer_layer(ruleset)

    counter[0] += 1
    rule_id = f"RULE-{counter[0]:06d}"

    checksum = hashlib.md5(xml_text.encode("utf-8", errors="replace")).hexdigest()[:12]

    return PegaRule(
        rule_id         = rule_id,
        name            = name,
        rule_type       = rule_type,
        pega_class      = pega_class,
        layer           = layer,
        ruleset         = ruleset,
        ruleset_version = version,
        status          = status,
        created         = created[:10] if created else "",
        updated         = updated[:10] if updated else "",
        author          = author,
        source_file     = os.path.basename(source_file),
        checksum        = checksum,
        raw_xml         = xml_text,
        dependencies    = extract_dependencies(root),
        ui_fields       = extract_ui_fields(root),
        conditions      = extract_conditions(root),
        actors          = extract_actors(root),
        flow_steps      = extract_flow_steps(root),
        decision_rows   = extract_decision_rows(root),
        data_mappings   = extract_data_mappings(root),
    )


# ── File-Level Dispatcher ────────────────────────────────────────────────────

def extract_from_file(file_path: Path, manifest_data: Optional[Dict] = None,
                      counter: List[int] = None) -> List[PegaRule]:
    """
    Main dispatch function. Reads a .bin file, detects format,
    extracts XML payloads, and parses each into PegaRule records.
    """
    if counter is None:
        counter = [0]

    log.debug("Processing: %s", file_path.name)

    try:
        data = file_path.read_bytes()
    except (OSError, IOError) as e:
        log.error("Cannot read %s: %s", file_path, e)
        return []

    if not data:
        return []

    fmt = detect_format(data)
    log.debug("  Format: %s  (%d bytes)", fmt, len(data))

    xml_payloads: List[str] = []

    if fmt == "zip":
        xml_payloads = parse_zip(data, str(file_path))
    elif fmt == "embedded_zip":
        # Find and extract the embedded ZIP
        zip_start = data.index(b"PK\x03\x04")
        xml_payloads = parse_zip(data[zip_start:], str(file_path))
    elif fmt == "gzip":
        xml_payloads = parse_gzip(data)
    elif fmt == "pega_legacy":
        xml_payloads = parse_pega_legacy(data, str(file_path))
    elif fmt == "java_serialized":
        xml_payloads = parse_java_serialized(data)
    elif fmt in ("raw_xml", "raw_xml_with_header", "raw_xml_fragment"):
        xml_payloads = extract_xml_from_raw(data)
    else:
        log.warning("  Unknown format — attempting raw XML scan")
        xml_payloads = scan_for_xml_fragments(data)

    log.debug("  XML payloads found: %d", len(xml_payloads))

    rules = []
    for xml_text in xml_payloads:
        rule = parse_rule_xml(xml_text, str(file_path), manifest_data, counter)
        if rule:
            rules.append(rule)

    return rules


# ── Manifest Parser ──────────────────────────────────────────────────────────

def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Load a Pega manifest JSON to build a ruleset → layer mapping.

    Expected manifest formats:
      1. Pega DevOps pipeline manifest:
         { "rulesets": [{ "name": "KYCPlatform", "version": "01-01-01", "layer": "Enterprise" }] }

      2. prdExport.xml converted to JSON:
         { "ruleSetList": [{ "RuleSetName": "...", "LayerName": "..." }] }

      3. Custom PREA manifest:
         { "layer_map": { "KYCPlatform": "Enterprise", "PegaFW": "Framework" } }

      4. Simple name→layer dict (PREA shorthand):
         { "KYCPlatform": "Enterprise", "PegaFW": "Framework" }
    """
    try:
        with manifest_path.open(encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        log.warning("Could not load manifest %s: %s", manifest_path, e)
        return {}

    layer_map = {}

    # Format 3 — already a layer_map
    if "layer_map" in raw:
        layer_map = raw["layer_map"]

    # Format 1 — DevOps rulesets array
    elif "rulesets" in raw:
        for rs in raw["rulesets"]:
            name  = rs.get("name") or rs.get("ruleSetName") or ""
            layer = rs.get("layer") or rs.get("layerName") or infer_layer(name)
            if name:
                layer_map[name] = layer

    # Format 2 — prdExport style
    elif "ruleSetList" in raw:
        for rs in raw["ruleSetList"]:
            name  = rs.get("RuleSetName") or rs.get("name") or ""
            layer = rs.get("LayerName") or infer_layer(name)
            if name:
                layer_map[name] = layer

    # Format 4 — simple dict (all string values are layer names)
    elif all(isinstance(v, str) for v in raw.values()):
        layer_map = raw

    log.info("Manifest loaded: %d ruleset→layer mappings", len(layer_map))
    return {"layer_map": layer_map, "raw": raw}


# ── Post-Processing ──────────────────────────────────────────────────────────

def deduplicate_rules(rules: List[PegaRule]) -> List[PegaRule]:
    """
    Remove duplicate rules using checksum + name + class as key.
    In Pega's layer system, the same rule may appear in multiple layers
    (override pattern). We keep ALL copies but tag duplicates.
    """
    seen_checksums = set()
    seen_keys = {}
    result = []

    for rule in rules:
        key = f"{rule.name}::{rule.pega_class}"
        if rule.checksum in seen_checksums:
            continue   # exact duplicate — skip
        seen_checksums.add(rule.checksum)

        if key in seen_keys:
            # Same rule, different layer — it's an override
            rule.notes = f"Overrides {seen_keys[key].layer} layer version"
        else:
            seen_keys[key] = rule

        result.append(rule)

    return result


def enrich_rules(rules: List[PegaRule]) -> List[PegaRule]:
    """
    Post-extraction enrichment:
    - Resolve dependency names to rule_ids where possible
    - Tag rules that have no dependents (leaf rules)
    - Tag rules with many dependents (hub rules)
    """
    name_to_id = {r.name: r.rule_id for r in rules}
    id_set = {r.rule_id for r in rules}

    # Build reverse dependency map
    dependents: Dict[str, List[str]] = {r.rule_id: [] for r in rules}
    for rule in rules:
        for dep_name in rule.dependencies:
            dep_id = name_to_id.get(dep_name)
            if dep_id and dep_id in dependents:
                dependents[dep_id].append(rule.rule_id)

    for rule in rules:
        n_dependents = len(dependents.get(rule.rule_id, []))
        n_deps = len(rule.dependencies)
        if n_dependents == 0:
            rule.notes = (rule.notes + " | Leaf rule (no dependents)").lstrip(" | ")
        if n_dependents > 20:
            rule.notes = (rule.notes + f" | Hub rule ({n_dependents} dependents)").lstrip(" | ")
        if n_deps == 0 and n_dependents == 0 and rule.rule_type != "Correspondence":
            rule.notes = (rule.notes + " | Isolated — decommission candidate").lstrip(" | ")

    return rules


def build_summary(rules: List[PegaRule]) -> Dict[str, Any]:
    """Build a summary dict for the extraction report."""
    from collections import Counter
    type_counts  = Counter(r.rule_type for r in rules)
    layer_counts = Counter(r.layer for r in rules)
    rs_counts    = Counter(r.ruleset for r in rules)
    status_counts= Counter(r.status for r in rules)

    return {
        "total_rules": len(rules),
        "extraction_time": datetime.now().isoformat(),
        "by_rule_type": dict(type_counts.most_common()),
        "by_layer": dict(layer_counts.most_common()),
        "by_ruleset": dict(rs_counts.most_common(20)),
        "by_status": dict(status_counts.most_common()),
        "rules_with_dependencies": sum(1 for r in rules if r.dependencies),
        "rules_with_ui_fields": sum(1 for r in rules if r.ui_fields),
        "rules_with_flow_steps": sum(1 for r in rules if r.flow_steps),
        "rules_with_conditions": sum(1 for r in rules if r.conditions),
    }


# ── Main Extraction Pipeline ─────────────────────────────────────────────────

def run_extraction(input_paths: List[Path],
                   manifest_data: Optional[Dict],
                   output_path: Path,
                   include_raw_xml: bool = False,
                   verbose: bool = False) -> Dict[str, Any]:
    """
    Main extraction pipeline.
    Returns a summary dict; writes rules to output_path.
    """
    if verbose:
        log.setLevel(logging.DEBUG)

    all_rules: List[PegaRule] = []
    counter = [0]

    files = sorted(input_paths)
    iterator = tqdm(files, desc="Extracting rules") if HAS_TQDM else files

    for fp in iterator:
        rules = extract_from_file(fp, manifest_data, counter)
        all_rules.extend(rules)
        if not HAS_TQDM:
            log.info("  %s → %d rules", fp.name, len(rules))

    log.info("Raw extraction: %d rules from %d files", len(all_rules), len(files))

    # Post-processing
    all_rules = deduplicate_rules(all_rules)
    log.info("After dedup: %d unique rules", len(all_rules))

    all_rules = enrich_rules(all_rules)

    summary = build_summary(all_rules)
    log.info("Summary: %s", {k: v for k, v in summary.items() if k.startswith("by_layer")})

    # Write output
    output_data = {
        "summary": summary,
        "rules": [
            {**r.to_dict(), **({"raw_xml": r.raw_xml} if include_raw_xml else {})}
            for r in all_rules
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, default=str)

    log.info("Output written: %s (%d rules)", output_path, len(all_rules))
    return summary


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PREA — Pega Binary Rule Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all .bin files in a directory
  python pega_bin_extractor.py --input-dir ./exports --output rules.json

  # Single file with manifest
  python pega_bin_extractor.py --input-file app.bin --manifest manifest.json --output rules.json

  # Include raw XML in output (large!)
  python pega_bin_extractor.py --input-dir ./bins --output rules.json --include-raw-xml

  # Filter by layer (post-extraction)
  python pega_bin_extractor.py --input-dir ./bins --output rules.json --layer Enterprise
        """,
    )
    parser.add_argument("--input-dir",       help="Directory containing .bin files")
    parser.add_argument("--input-file",      help="Single .bin file to process")
    parser.add_argument("--manifest",        help="Path to manifest JSON (optional)")
    parser.add_argument("--output",          default="rules_extracted.json", help="Output JSON path")
    parser.add_argument("--layer",           help="Filter results to this layer (optional)")
    parser.add_argument("--ruleset",         help="Filter results to this ruleset (optional)")
    parser.add_argument("--include-raw-xml", action="store_true", help="Include raw XML in output")
    parser.add_argument("--verbose",         action="store_true", help="Debug logging")

    args = parser.parse_args()

    if not args.input_dir and not args.input_file:
        parser.error("Provide --input-dir or --input-file")

    # Collect input files
    input_paths: List[Path] = []
    if args.input_dir:
        d = Path(args.input_dir)
        if not d.is_dir():
            parser.error(f"Not a directory: {d}")
        input_paths = list(d.rglob("*.bin")) + list(d.rglob("*.zip")) + list(d.rglob("*.jar"))
        if not input_paths:
            log.warning("No .bin/.zip/.jar files found in %s", d)
            sys.exit(1)
        log.info("Found %d binary files in %s", len(input_paths), d)

    if args.input_file:
        fp = Path(args.input_file)
        if not fp.exists():
            parser.error(f"File not found: {fp}")
        input_paths.append(fp)

    # Load manifest
    manifest_data = None
    if args.manifest:
        manifest_data = load_manifest(Path(args.manifest))

    # Run
    summary = run_extraction(
        input_paths    = input_paths,
        manifest_data  = manifest_data,
        output_path    = Path(args.output),
        include_raw_xml= args.include_raw_xml,
        verbose        = args.verbose,
    )

    # Post-filter if requested
    if args.layer or args.ruleset:
        with open(args.output) as f:
            data = json.load(f)
        rules = data["rules"]
        if args.layer:
            rules = [r for r in rules if r["layer"] == args.layer]
        if args.ruleset:
            rules = [r for r in rules if r["ruleset"] == args.ruleset]
        data["rules"] = rules
        data["summary"]["total_rules_after_filter"] = len(rules)
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2)
        log.info("Filtered to %d rules (layer=%s, ruleset=%s)", len(rules), args.layer, args.ruleset)

    # Print summary
    print("\n" + "═" * 60)
    print("  PREA EXTRACTION COMPLETE")
    print("═" * 60)
    print(f"  Total rules extracted : {summary['total_rules']:,}")
    print(f"  Extraction timestamp  : {summary['extraction_time']}")
    print(f"\n  By Layer:")
    for layer, count in summary.get("by_layer", {}).items():
        print(f"    {layer:<20} {count:>8,}")
    print(f"\n  By Rule Type (top 10):")
    for rtype, count in list(summary.get("by_rule_type", {}).items())[:10]:
        print(f"    {rtype:<30} {count:>6,}")
    print(f"\n  Output: {args.output}")
    print("═" * 60)


if __name__ == "__main__":
    main()
