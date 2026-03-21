"""
tools/parser/bin_reader.py

Extracts useful information from PEGA native .bin (binary) rule files.

PEGA .bin files are Java-serialised objects. They are NOT human-readable
in the standard sense, but contain many readable UTF-8 string segments
interspersed between binary data.  The engine uses these strings to:

  1. Confirm the rule type (pxObjClass), rule name, and class
  2. Discover cross-rule references (flow steps, activity calls,
     sub-flow names, connector names, when conditions, etc.)
  3. Build a partial "pseudo-parsed" rule dict that the graph and
     context assembler can work with — even without the full JSON

Strategy:
  - Read the file as raw bytes
  - Extract all printable ASCII / UTF-8 segments above a minimum length
  - Search extracted strings for known PEGA field name patterns
  - Parse key=value or label/value pairs that follow PEGA's
    Java-serialised object structure
  - Return a dict that mirrors (as closely as possible) the JSON
    structure the rest of the engine expects

Limitations:
  - Cannot recover structured data (arrays, nested objects) reliably
  - Some field values may be truncated or partially corrupted by binary data
  - Cross-rule reference extraction is heuristic, not guaranteed complete
"""

from __future__ import annotations

import re
import struct
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

# PEGA field names we actively look for in extracted strings
_RULE_IDENTITY_FIELDS = {
    "pyRuleName", "pyClassName", "pxObjClass",
    "pyRuleSetName", "pyRuleSetVersion", "pyLabel", "pyDescription",
}

_REFERENCE_FIELDS = {
    "pyFlowActionName", "pyActivityName", "pySubFlowName",
    "pyConnectorName", "pyDataTransformName", "pySLAName",
    "pyWhenName", "pyDecisionName", "pyRouterName",
    "pyFlowName", "pyCaseTypeName", "pyScreenName",
    "pyPreActivity", "pyPostActivity", "pyValidateActivity",
    "pySubFlowClass", "pyFlowActionClass",
}

_ALL_FIELDS = _RULE_IDENTITY_FIELDS | _REFERENCE_FIELDS

# Minimum length of printable string segment to keep
_DEFAULT_MIN_LEN = 4

# Regex: printable ASCII segment
_PRINTABLE_RE = re.compile(rb"[\x20-\x7e]{4,}")

# PEGA rule types we recognise
_KNOWN_RULE_TYPES = {
    "Rule-Obj-CaseType", "Rule-Obj-Flow", "Rule-Obj-Activity",
    "Rule-Obj-Flowsection", "Rule-HTML-Section", "Rule-Obj-When",
    "Rule-Obj-DataTransform", "Rule-Obj-Decision", "Rule-Obj-SLA",
    "Rule-Obj-Router", "Rule-Connect-REST", "Rule-Connect-SOAP",
    "Rule-Obj-Declare-DeclarePage",
}


# ─── Public API ───────────────────────────────────────────────────────────────

def read_bin_file(
    bin_path: Path,
    min_string_length: int = _DEFAULT_MIN_LEN,
    reference_patterns: list[str] | None = None,
) -> dict:
    """
    Read a PEGA .bin file and return a partial rule dict.

    The returned dict mirrors the JSON structure expected by the rest of
    the engine, with as many fields populated as can be extracted.

    Fields always present (may be empty string):
      pyRuleName, pyClassName, pxObjClass, pyRuleSetName, pyRuleSetVersion

    Fields present if extractable:
      pyLabel, pyDescription
      + any cross-rule reference fields found in _REFERENCE_FIELDS

    Additionally returns:
      _bin_source: True  (flag to indicate this was parsed from BIN)
      _raw_strings: list of all extracted printable strings (for debugging)
    """
    try:
        data = bin_path.read_bytes()
    except OSError as e:
        logger.warning("Could not read BIN file %s: %s", bin_path, e)
        return _empty_rule(bin_path)

    strings = _extract_strings(data, min_string_length)
    result  = _parse_strings(strings, bin_path.stem, reference_patterns or list(_REFERENCE_FIELDS))

    logger.debug(
        "BIN %s → type=%s name=%s class=%s  (%d strings extracted, %d refs found)",
        bin_path.name,
        result.get("pxObjClass", "?"),
        result.get("pyRuleName", "?"),
        result.get("pyClassName", "?"),
        len(strings),
        len([k for k in result if k in _REFERENCE_FIELDS and result[k]])
    )

    return result


def extract_cross_references(bin_path: Path, min_string_length: int = 4) -> dict[str, list[str]]:
    """
    Lightweight extraction of only cross-rule reference strings from a BIN file.
    Returns a dict: { field_name: [value1, value2, ...] }
    Used when we already have rule identity from the manifest and only need refs.
    """
    try:
        data = bin_path.read_bytes()
    except OSError:
        return {}

    strings = _extract_strings(data, min_string_length)
    return _extract_reference_values(strings)


# ─── String extraction ────────────────────────────────────────────────────────

def _extract_strings(data: bytes, min_len: int) -> list[str]:
    """
    Extract all printable ASCII segments from raw bytes.
    Also handles Java modified UTF-8 short strings (2-byte length prefix).
    """
    results: list[str] = []

    # Method 1: regex over raw bytes
    for m in _PRINTABLE_RE.finditer(data):
        s = m.group(0).decode("ascii", errors="ignore").strip()
        if len(s) >= min_len:
            results.append(s)

    # Method 2: Java short string format (2-byte big-endian length + UTF-8 bytes)
    # Common in Java serialization streams
    i = 0
    while i < len(data) - 3:
        try:
            length = struct.unpack(">H", data[i:i+2])[0]
            if 4 <= length <= 512:
                candidate = data[i+2:i+2+length]
                if len(candidate) == length:
                    try:
                        s = candidate.decode("utf-8").strip()
                        # Only keep if mostly printable
                        printable = sum(1 for c in s if 32 <= ord(c) < 127 or ord(c) > 127)
                        if printable / max(len(s), 1) > 0.8 and len(s) >= min_len:
                            results.append(s)
                    except UnicodeDecodeError:
                        pass
        except struct.error:
            pass
        i += 1

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped = []
    for s in results:
        if s not in seen:
            seen.add(s)
            deduped.append(s)

    return deduped


# ─── String parsing ───────────────────────────────────────────────────────────

def _parse_strings(strings: list[str], filename_stem: str, ref_patterns: list[str]) -> dict:
    """
    Parse extracted strings to identify field values.
    Returns a rule dict compatible with reference_extractor's expectations.
    """
    result: dict = {
        "pyRuleName":       "",
        "pyClassName":      "",
        "pxObjClass":       "",
        "pyRuleSetName":    "",
        "pyRuleSetVersion": "",
        "pyLabel":          "",
        "pyDescription":    "",
        "_bin_source":      True,
        "_raw_strings":     strings,
    }

    # -- Identity fields: look for field_name followed by value ---------------
    for i, s in enumerate(strings):
        # Pattern: "fieldName" immediately followed by "value" in next string(s)
        if s in _ALL_FIELDS:
            # Value is likely in the next 1-3 strings
            for j in range(i + 1, min(i + 4, len(strings))):
                candidate = strings[j]
                if candidate and candidate not in _ALL_FIELDS and len(candidate) >= 2:
                    field_name = s
                    if field_name in result and not result[field_name]:
                        result[field_name] = candidate
                    break

        # Pattern: "fieldName=value" in same string
        for field in _ALL_FIELDS:
            if f"{field}=" in s or f"{field}:" in s:
                parts = re.split(r"[=:]", s, maxsplit=1)
                if len(parts) == 2 and parts[0].strip() == field:
                    val = parts[1].strip().strip('"').strip("'")
                    if val and field in result and not result.get(field):
                        result[field] = val

    # -- Detect rule type from embedded strings --------------------------------
    if not result["pxObjClass"]:
        for s in strings:
            for rt in _KNOWN_RULE_TYPES:
                if rt in s:
                    result["pxObjClass"] = rt
                    break
            if result["pxObjClass"]:
                break

    # -- Detect rule name from filename if not found --------------------------
    if not result["pyRuleName"]:
        result["pyRuleName"] = filename_stem

    # -- Extract cross-reference values ---------------------------------------
    refs = _extract_reference_values(strings)
    for field_name, values in refs.items():
        if values:
            # Store first value as a scalar (for simple fields)
            result[field_name] = values[0]
            # Store all values in a list for multi-valued fields
            result[f"_all_{field_name}"] = values

    # -- Attempt to reconstruct flow steps list --------------------------------
    # Look for patterns like "Assignment", "Utility", "SubFlow", "Decision", "End"
    step_types = {"Assignment", "Utility", "SubFlow", "Spinoff", "Decision", "Split", "End"}
    found_steps = []
    for i, s in enumerate(strings):
        if s in step_types:
            step_name = ""
            # Look backwards for the step name
            for j in range(max(0, i-3), i):
                candidate = strings[j]
                if candidate and candidate not in step_types and candidate not in _ALL_FIELDS:
                    if re.match(r"^[A-Za-z][A-Za-z0-9_\-]*$", candidate):
                        step_name = candidate
            found_steps.append({
                "pyStepType": s,
                "pyStepName": step_name,
            })

    if found_steps:
        result["pyFlowSteps"] = found_steps

    return result


def _extract_reference_values(strings: list[str]) -> dict[str, list[str]]:
    """
    Find values that follow reference field names in the string sequence.
    Returns { field_name: [value1, value2, ...] }
    """
    refs: dict[str, list[str]] = {f: [] for f in _REFERENCE_FIELDS}

    for i, s in enumerate(strings):
        if s not in _REFERENCE_FIELDS:
            continue

        # Collect values following this field name
        for j in range(i + 1, min(i + 5, len(strings))):
            val = strings[j]
            if not val or val in _ALL_FIELDS or len(val) < 2:
                break
            # Valid rule name: starts with letter, contains alphanumeric + _ -
            if re.match(r"^[A-Za-z][A-Za-z0-9_\-\.]*$", val) and len(val) <= 200:
                if val not in refs[s]:
                    refs[s].append(val)
            break   # Only take the first value per field occurrence

    return {k: v for k, v in refs.items() if v}


def _empty_rule(bin_path: Path) -> dict:
    return {
        "pyRuleName":   bin_path.stem,
        "pyClassName":  "",
        "pxObjClass":  "",
        "_bin_source":  True,
        "_raw_strings": [],
        "_error":       "Could not read file",
    }
