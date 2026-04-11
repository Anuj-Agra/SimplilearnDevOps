#!/usr/bin/env python3
"""
pega_manifest_parser.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREA — Pega Manifest Parser

Parses one or more Pega manifest files (JSON or XML) to produce:
  1. A consolidated layer_map: { rulesetName → layerName }
  2. A ruleset inventory: version history, last updated, owner
  3. An application stack: ordered list of layers with their rulesets

Supports manifest formats:
  - Pega DevOps deployment manifest (JSON)
  - prdExport.xml (Pega export manifest, XML format)
  - Pega Application ZIP manifest.json (Pega Infinity)
  - PREA custom manifest (simple JSON)
  - Pega Product Rules Export manifest

Usage:
    python pega_manifest_parser.py --manifests ./exports/ --output layer_map.json

    python pega_manifest_parser.py --manifest manifest.json --output layer_map.json

    python pega_manifest_parser.py --manifests ./exports/ --output layer_map.json --print
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import argparse
import json
import logging
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Any
from xml.etree import ElementTree as ET

log = logging.getLogger("prea.manifest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")

# ── Known layer name normalisations ─────────────────────────────────────────

LAYER_ALIASES: Dict[str, str] = {
    # Framework variants
    "fw": "Framework", "framework": "Framework", "pega": "Framework",
    "prpc": "Framework", "platform": "Framework", "base": "Framework",
    "standard": "Framework", "pegafw": "Framework",
    # Industry variants
    "industry": "Industry", "ind": "Industry",
    "fs": "Industry", "finserv": "Industry", "financial services": "Industry",
    "banking": "Industry", "capital markets": "Industry",
    # Enterprise variants
    "enterprise": "Enterprise", "ent": "Enterprise", "corp": "Enterprise",
    "corporate": "Enterprise", "shared": "Enterprise", "global": "Enterprise",
    # Implementation variants
    "implementation": "Implementation", "impl": "Implementation",
    "app": "Implementation", "application": "Implementation",
    "project": "Implementation", "custom": "Implementation",
    "local": "Implementation",
}

LAYER_PATTERNS: List[tuple] = [
    (r"(?i)^(pega|prpc|platform|base|standard|common|fw)", "Framework"),
    (r"(?i)(fs|finserv|financial|banking|insurance|capital|industry)", "Industry"),
    (r"(?i)(enterprise|ent|corp|corporate|shared|global)", "Enterprise"),
    (r"(?i)(impl|app|project|custom|local|client)", "Implementation"),
]


def normalise_layer(raw: str) -> str:
    """Normalise a raw layer string to one of the canonical 4 layers."""
    if not raw:
        return "Unknown"
    key = raw.lower().strip()
    if key in LAYER_ALIASES:
        return LAYER_ALIASES[key]
    for pattern, layer in LAYER_PATTERNS:
        if re.search(pattern, raw):
            return layer
    return raw.title()   # Return as-is if we can't normalise


# ── Data Model ───────────────────────────────────────────────────────────────

@dataclass
class RuleSetRecord:
    name:             str
    version:          str
    layer:            str
    description:      str = ""
    owner:            str = ""
    last_updated:     str = ""
    is_locked:        bool = False
    built_on:         str = ""    # parent ruleset (Pega inheritance)
    rule_count:       int = 0


@dataclass
class ManifestResult:
    layer_map:        Dict[str, str]     # ruleset_name → layer
    rulesets:         List[RuleSetRecord]
    application_name: str = ""
    application_ver:  str = ""
    pega_version:     str = ""
    source_files:     List[str] = field(default_factory=list)
    warnings:         List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["rulesets"] = [asdict(r) for r in self.rulesets]
        return d


# ── Format-Specific Parsers ──────────────────────────────────────────────────

def parse_devops_manifest(raw: Dict, source: str) -> ManifestResult:
    """
    Parse Pega DevOps pipeline manifest.
    Format:
    {
      "application": { "name": "KYCPlatform", "version": "01-01-01" },
      "pegaVersion": "8.7.4",
      "rulesets": [
        { "name": "KYCCore", "version": "01-01-01", "layer": "Enterprise" },
        ...
      ]
    }
    """
    result = ManifestResult(layer_map={}, rulesets=[], source_files=[source])

    app = raw.get("application") or raw.get("app") or {}
    result.application_name = app.get("name") or raw.get("applicationName") or ""
    result.application_ver  = app.get("version") or raw.get("applicationVersion") or ""
    result.pega_version      = raw.get("pegaVersion") or raw.get("prpcVersion") or ""

    for rs in raw.get("rulesets") or raw.get("ruleSetList") or []:
        name    = rs.get("name") or rs.get("ruleSetName") or rs.get("rsName") or ""
        version = rs.get("version") or rs.get("ruleSetVersion") or ""
        layer   = normalise_layer(rs.get("layer") or rs.get("layerName") or rs.get("type") or "")

        if not layer or layer == "Unknown":
            layer = normalise_layer(name)

        rec = RuleSetRecord(
            name        = name,
            version     = version,
            layer       = layer,
            description = rs.get("description") or "",
            owner       = rs.get("owner") or rs.get("author") or "",
            last_updated= rs.get("lastUpdated") or rs.get("updateDateTime") or "",
            is_locked   = bool(rs.get("locked") or rs.get("isLocked")),
            built_on    = rs.get("builtOn") or rs.get("parentRuleSet") or "",
            rule_count  = int(rs.get("ruleCount") or rs.get("rules") or 0),
        )
        result.rulesets.append(rec)
        if name:
            result.layer_map[name] = layer

    return result


def parse_prd_export_xml(xml_text: str, source: str) -> ManifestResult:
    """
    Parse Pega prdExport.xml manifest (XML format produced by Pega's archive export).
    """
    result = ManifestResult(layer_map={}, rulesets=[], source_files=[source])
    try:
        root = ET.fromstring(xml_text.encode("utf-8", errors="replace"))
    except ET.ParseError as e:
        result.warnings.append(f"XML parse error in {source}: {e}")
        return result

    # Application metadata
    app_el = root.find(".//Application") or root.find(".//application")
    if app_el is not None:
        result.application_name = app_el.get("name") or app_el.get("pyAppName") or ""
        result.application_ver  = app_el.get("version") or ""

    result.pega_version = root.get("pegaVersion") or root.get("PRPCVersion") or ""

    # Ruleset entries
    for el in root.iter():
        if el.tag.lower() in ("ruleset", "rulesetrecord", "rulesetversion", "pxrulesetversion"):
            name    = el.get("RuleSetName") or el.get("pyRuleSet") or el.get("name") or ""
            version = el.get("RuleSetVersion") or el.get("pyRuleSetVersion") or ""
            layer   = normalise_layer(el.get("LayerName") or el.get("pyLayerName") or el.get("type") or "")
            if not layer or layer == "Unknown":
                layer = normalise_layer(name)

            if name:
                rec = RuleSetRecord(
                    name    = name,
                    version = version,
                    layer   = layer,
                    owner   = el.get("pyUpdateOpName") or "",
                    last_updated = el.get("pyUpdateDateTime") or "",
                )
                result.rulesets.append(rec)
                result.layer_map[name] = layer

    return result


def parse_infinity_manifest(raw: Dict, source: str) -> ManifestResult:
    """
    Parse Pega Infinity application ZIP manifest.json.
    Format (Pega 8.x+):
    {
      "name": "MyApp",
      "version": "01.01.01",
      "builtOnApplication": "PegaFW",
      "rulesets": [...]
    }
    """
    result = ManifestResult(layer_map={}, rulesets=[], source_files=[source])
    result.application_name = raw.get("name") or raw.get("applicationName") or ""
    result.application_ver  = raw.get("version") or ""
    result.pega_version      = raw.get("pegaVersion") or raw.get("targetPegaVersion") or ""

    # Handle nested structure variants
    rs_list = (
        raw.get("rulesets") or
        raw.get("ruleSets") or
        raw.get("content", {}).get("rulesets") or
        []
    )

    for rs in rs_list:
        if isinstance(rs, str):
            # Simple list of names
            rec = RuleSetRecord(name=rs, version="", layer=normalise_layer(rs))
            result.rulesets.append(rec)
            result.layer_map[rs] = rec.layer
            continue

        name    = rs.get("name") or rs.get("ruleSetName") or ""
        version = rs.get("version") or rs.get("ruleSetVersion") or ""
        layer   = normalise_layer(rs.get("layer") or rs.get("type") or "")
        if not layer or layer == "Unknown":
            layer = normalise_layer(name)

        rec = RuleSetRecord(name=name, version=version, layer=layer)
        result.rulesets.append(rec)
        if name:
            result.layer_map[name] = layer

    return result


def parse_simple_dict(raw: Dict, source: str) -> ManifestResult:
    """
    Parse PREA shorthand manifest: { "RuleSetName": "LayerName", ... }
    or { "layer_map": { ... } }
    """
    result = ManifestResult(layer_map={}, rulesets=[], source_files=[source])
    layer_data = raw.get("layer_map") or raw

    for name, layer in layer_data.items():
        if isinstance(layer, str):
            norm = normalise_layer(layer)
            result.layer_map[name] = norm
            result.rulesets.append(RuleSetRecord(name=name, version="", layer=norm))

    return result


# ── Auto-Detect and Parse ────────────────────────────────────────────────────

def parse_manifest_file(file_path: Path) -> ManifestResult:
    """Auto-detect format and parse a manifest file."""
    source = file_path.name

    # XML manifest (prdExport.xml, etc.)
    if file_path.suffix.lower() == ".xml":
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            return parse_prd_export_xml(text, source)
        except Exception as e:
            log.warning("XML parse failed for %s: %s", file_path, e)
            return ManifestResult(layer_map={}, rulesets=[], warnings=[str(e)])

    # JSON manifest
    try:
        with file_path.open(encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        log.warning("JSON parse failed for %s: %s", file_path, e)
        return ManifestResult(layer_map={}, rulesets=[], warnings=[str(e)])

    # Detect JSON format
    if "rulesets" in raw or "ruleSetList" in raw:
        if "application" in raw or "applicationName" in raw or "pegaVersion" in raw:
            return parse_devops_manifest(raw, source)
        if "name" in raw and ("builtOnApplication" in raw or "targetPegaVersion" in raw):
            return parse_infinity_manifest(raw, source)
        return parse_devops_manifest(raw, source)   # generic with rulesets

    if "layer_map" in raw or (all(isinstance(v, str) for v in raw.values()) and raw):
        return parse_simple_dict(raw, source)

    # If it has name + version at top level, treat as Infinity
    if "name" in raw and "version" in raw:
        return parse_infinity_manifest(raw, source)

    log.warning("Unrecognised manifest format in %s — trying generic parse", source)
    return parse_devops_manifest(raw, source)


def merge_results(results: List[ManifestResult]) -> ManifestResult:
    """Merge multiple manifest parse results into one consolidated result."""
    merged = ManifestResult(layer_map={}, rulesets=[])
    seen_rs = set()

    for res in results:
        merged.layer_map.update(res.layer_map)
        for rs in res.rulesets:
            key = f"{rs.name}::{rs.version}"
            if key not in seen_rs:
                seen_rs.add(key)
                merged.rulesets.append(rs)
        if res.application_name and not merged.application_name:
            merged.application_name = res.application_name
        if res.pega_version and not merged.pega_version:
            merged.pega_version = res.pega_version
        merged.source_files.extend(res.source_files)
        merged.warnings.extend(res.warnings)

    return merged


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PREA Manifest Parser")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--manifests", help="Directory containing manifest files")
    grp.add_argument("--manifest",  help="Single manifest file path")
    parser.add_argument("--output",  default="layer_map.json", help="Output JSON path")
    parser.add_argument("--print",   action="store_true", help="Print summary to stdout")
    args = parser.parse_args()

    files: List[Path] = []
    if args.manifest:
        files = [Path(args.manifest)]
    else:
        d = Path(args.manifests)
        files = list(d.glob("*.json")) + list(d.glob("*.xml"))

    if not files:
        log.error("No manifest files found")
        return

    results = [parse_manifest_file(f) for f in files]
    merged  = merge_results(results)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(merged.to_dict(), f, indent=2, default=str)
    log.info("Layer map written: %s (%d rulesets)", out, len(merged.rulesets))

    if args.print:
        print(f"\nApplication : {merged.application_name} v{merged.application_ver}")
        print(f"Pega Version: {merged.pega_version}")
        print(f"\nRuleset → Layer Map ({len(merged.layer_map)} entries):")
        for name, layer in sorted(merged.layer_map.items()):
            print(f"  {name:<45} → {layer}")
        if merged.warnings:
            print(f"\nWarnings:")
            for w in merged.warnings:
                print(f"  ⚠ {w}")


if __name__ == "__main__":
    main()
