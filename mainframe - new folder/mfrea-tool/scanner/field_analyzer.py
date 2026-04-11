#!/usr/bin/env python3
"""
MFREA Field Lineage Analyzer
Performs deep field-level analysis across Natural/COBOL programs:
  - Where each field is defined (DDM, LDA, GDA, local, parameter)
  - Where each field is READ from a database
  - Where each field is WRITTEN to a database  
  - How each field's value was derived:
      - Direct user input (from MAP)
      - Assigned from another field (MOVE, ASSIGN, :=)
      - Calculated (COMPUTE, ADD, SUBTRACT, MULTIPLY, DIVIDE)
      - Concatenated (COMPRESS)
      - Extracted (EXAMINE, SEPARATE)
      - System variable (*DATX, *TIMX, *USER, *PROGRAM, *ISN)
      - Literal/hardcoded value
      - Parameter from caller (CALLNAT parameter)
      - Read from another file (cross-file copy)
  - Where each field appears on a screen (MAP)
  - Where each field is used in conditions (IF, DECIDE)
  - Where each field is passed as a parameter to CALLNAT

Usage:
  python field_analyzer.py --source /path/to/natural --output field_lineage.json
  python field_analyzer.py --source /path/to/natural --program CUSTMAIN --output lineage_CUSTMAIN.json
  python field_analyzer.py --source /path/to/natural --field CUST-STATUS --output lineage_field.json
"""

import os
import re
import json
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

# ═══════════════════════════════════════════════════════════════
# REGEX PATTERNS — Field-Level Analysis
# ═══════════════════════════════════════════════════════════════

# Assignment patterns: how a field gets its value
# MOVE source TO target  /  ASSIGN target = source  /  target := source
RE_MOVE = re.compile(
    r"MOVE\s+(.+?)\s+TO\s+([A-Za-z0-9_#@$.-]+)", re.IGNORECASE
)
RE_ASSIGN = re.compile(
    r"(?:ASSIGN\s+)?([A-Za-z0-9_#@$.-]+)\s*:=\s*(.+?)(?:\n|$)", re.IGNORECASE
)

# COMPUTE / arithmetic
RE_COMPUTE = re.compile(
    r"COMPUTE\s+([A-Za-z0-9_#@$.-]+)\s*=\s*(.+?)(?:\n|$)", re.IGNORECASE
)
RE_ADD = re.compile(
    r"ADD\s+(.+?)\s+TO\s+([A-Za-z0-9_#@$.-]+)", re.IGNORECASE
)
RE_SUBTRACT = re.compile(
    r"SUBTRACT\s+(.+?)\s+FROM\s+([A-Za-z0-9_#@$.-]+)", re.IGNORECASE
)
RE_MULTIPLY = re.compile(
    r"MULTIPLY\s+(.+?)\s+INTO\s+([A-Za-z0-9_#@$.-]+)", re.IGNORECASE
)
RE_DIVIDE = re.compile(
    r"DIVIDE\s+(.+?)\s+INTO\s+([A-Za-z0-9_#@$.-]+)", re.IGNORECASE
)

# COMPRESS (concatenation)
RE_COMPRESS = re.compile(
    r"COMPRESS\s+(.+?)\s+INTO\s+([A-Za-z0-9_#@$.-]+)", re.IGNORECASE
)

# EXAMINE / SEPARATE (extraction)
RE_EXAMINE = re.compile(
    r"EXAMINE\s+([A-Za-z0-9_#@$.-]+)\s+FOR\s+(.+?)(?:\s+REPLACE|$)", re.IGNORECASE
)
RE_SEPARATE = re.compile(
    r"SEPARATE\s+([A-Za-z0-9_#@$.-]+)\s+INTO\s+(.+?)(?:\n|$)", re.IGNORECASE
)

# RESET / INIT (value clearing)
RE_RESET = re.compile(
    r"RESET\s+(.+?)(?:\n|$)", re.IGNORECASE
)

# System variables
SYSTEM_VARS = {
    '*DATX': 'Current date (YYYYMMDD)',
    '*DAT4I': 'Current date (YYYY-MM-DD)',
    '*TIMX': 'Current time (HHIISS)',
    '*TIMN': 'Current time (HHMMSS)',
    '*USER': 'Current user ID',
    '*PROGRAM': 'Current program name',
    '*LIBRARY': 'Current library name',
    '*ISN': 'Current ISN of last DB access',
    '*NUMBER': 'Number of records in last FIND/READ',
    '*COUNTER': 'Loop counter',
    '*ERROR-NR': 'Last error number',
    '*PF-KEY': 'Last PF key pressed',
    '*PF-NAME': 'PF key name',
    '*APPLIC-ID': 'Application ID',
    '*INIT-ID': 'Init user ID',
    '*ETID': 'Adabas ET ID',
    '*CURSOR': 'Cursor position',
    '*LANGUAGE': 'Language code',
    '*DEVICE': 'Device type',
    '*LINEX': 'Current line',
    '*PAGEX': 'Current page',
}

# VIEW definition
RE_VIEW_DEF = re.compile(
    r"^\s*(\d+)\s+([A-Za-z0-9_#@$-]+)\s+VIEW\s+OF\s+([A-Za-z0-9_#@$-]+)",
    re.IGNORECASE | re.MULTILINE
)

# VIEW field listing (fields under a VIEW)
RE_VIEW_FIELD = re.compile(
    r"^\s*(\d+)\s+([A-Za-z0-9_#@$-]+)\s*$",
    re.MULTILINE
)

# DEFINE DATA field with format
RE_DEFINE_FIELD = re.compile(
    r"^\s*(\d+)\s+([#A-Za-z0-9_@$-]+)\s+\(([ANPBCDTL][\d.]*)\)",
    re.MULTILINE
)

# CALLNAT with parameters
RE_CALLNAT_FULL = re.compile(
    r"CALLNAT\s+'([A-Za-z0-9_#@$-]+)'\s+(.+?)(?:\n|$)", re.IGNORECASE
)

# INPUT USING MAP — fields populated from user
RE_MAP_INPUT = re.compile(
    r"(?:INPUT|REINPUT)\s+(?:USING\s+)?MAP\s+'([A-Za-z0-9_#@$-]+)'",
    re.IGNORECASE
)

# IF / DECIDE conditions — field used in logic
RE_IF_FIELD = re.compile(
    r"(?:IF|DECIDE\s+ON\s+EVERY\s+VALUE\s+OF)\s+([A-Za-z0-9_#@$.-]+)\s*([=<>!]|EQ|NE|LT|GT|LE|GE|NOT\s*=)",
    re.IGNORECASE
)

# Database operations with field context
RE_DB_STORE = re.compile(
    r"\b(STORE)\s+([A-Za-z0-9_#@$-]+)", re.IGNORECASE
)
RE_DB_UPDATE = re.compile(
    r"\b(UPDATE)\s+([A-Za-z0-9_#@$-]+)", re.IGNORECASE
)
RE_DB_READ = re.compile(
    r"\b(READ|FIND|GET|HISTOGRAM)\s+(?:\(\d+\)\s+)?([A-Za-z0-9_#@$-]+)",
    re.IGNORECASE
)
RE_DB_DELETE = re.compile(
    r"\b(DELETE)\s+([A-Za-z0-9_#@$-]+)", re.IGNORECASE
)

# FIND/READ WITH (search criteria fields)
RE_SEARCH_CRIT = re.compile(
    r"(?:WITH|WHERE|BY)\s+([A-Za-z0-9_#@$-]+)\s*=", re.IGNORECASE
)


# ═══════════════════════════════════════════════════════════════
# VALUE SOURCE CLASSIFICATION
# ═══════════════════════════════════════════════════════════════

def classify_source(source_expr):
    """Classify the source of a value assignment."""
    source = source_expr.strip().upper()

    # System variable
    for sysvar in SYSTEM_VARS:
        if sysvar in source:
            return {
                'type': 'SYSTEM-VARIABLE',
                'source': sysvar,
                'description': SYSTEM_VARS[sysvar]
            }

    # Literal string
    if source.startswith("'") or source.startswith('"'):
        return {
            'type': 'LITERAL',
            'source': source.strip("'\""),
            'description': f'Hardcoded value: {source}'
        }

    # Numeric literal
    if re.match(r'^-?\d+\.?\d*$', source):
        return {
            'type': 'LITERAL',
            'source': source,
            'description': f'Hardcoded number: {source}'
        }

    # Named constants
    if source in ('TRUE', 'FALSE', 'SPACES', 'ZEROS', 'ZERO', 'BLANK'):
        return {
            'type': 'CONSTANT',
            'source': source,
            'description': f'Constant: {source}'
        }

    # Expression with operators (calculation)
    if any(op in source for op in ['+', '-', '*', '/', '**']):
        return {
            'type': 'CALCULATED',
            'source': source_expr.strip(),
            'description': f'Calculated from expression'
        }

    # Another field (MOVE field TO field)
    if re.match(r'^[#A-Za-z][A-Za-z0-9_#@$.-]*$', source):
        return {
            'type': 'FIELD-COPY',
            'source': source,
            'description': f'Copied from field: {source}'
        }

    # Substring
    if '(' in source and ')' in source:
        return {
            'type': 'SUBSTRING',
            'source': source_expr.strip(),
            'description': f'Substring/array element'
        }

    return {
        'type': 'EXPRESSION',
        'source': source_expr.strip(),
        'description': 'Derived from expression'
    }


# ═══════════════════════════════════════════════════════════════
# FIELD ANALYZER — Per Program
# ═══════════════════════════════════════════════════════════════

def analyze_program_fields(filepath):
    """Deep field-level analysis of a single Natural program."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return None

    name = Path(filepath).stem.upper()

    # Remove comment lines
    lines = content.split('\n')
    clean_lines = [l for l in lines if not l.strip().startswith('*') and not l.strip().startswith('/*')]
    clean = '\n'.join(clean_lines)
    clean_upper = clean.upper()

    result = {
        'program': name,
        'filepath': str(filepath),
        'fields': {},       # field_name -> field_info
        'lineage': [],      # list of {target, source_type, source, context, line_hint}
    }

    # ── Step 1: Extract field definitions ──
    # VIEW fields (from Adabas DDM)
    views = {}  # alias -> ddm
    for m in RE_VIEW_DEF.finditer(clean):
        alias = m.group(2).upper()
        ddm = m.group(3).upper()
        views[alias] = ddm

    # DEFINE DATA fields with format
    for m in RE_DEFINE_FIELD.finditer(clean):
        level = int(m.group(1))
        field_name = m.group(2).upper()
        field_format = m.group(3).upper()

        # Determine scope
        scope = 'LOCAL'
        pos = m.start()
        preceding = clean_upper[:pos]
        if 'PARAMETER' in preceding[-200:]:
            scope = 'PARAMETER'
        elif 'GLOBAL' in preceding[-200:]:
            scope = 'GLOBAL'

        result['fields'][field_name] = {
            'name': field_name,
            'format': field_format,
            'level': level,
            'scope': scope,
            'ddm': None,
            'value_sources': [],
            'used_in_conditions': [],
            'used_in_db_ops': [],
            'displayed_on_maps': [],
            'passed_to_callnat': [],
            'search_key_in': [],
        }

    # Map VIEW fields to their DDM
    # (fields listed under a VIEW get tagged with the DDM)
    for alias, ddm in views.items():
        # Find position of VIEW definition
        pattern = re.compile(
            rf"^\s*\d+\s+{re.escape(alias)}\s+VIEW\s+OF\s+{re.escape(ddm)}\s*$(.*?)(?=^\s*\d+\s+\S+\s+VIEW|\bEND-DEFINE\b|^\s*LOCAL\s|^\s*PARAMETER\s)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )
        vm = pattern.search(clean)
        if vm:
            view_block = vm.group(1)
            for fm in RE_VIEW_FIELD.finditer(view_block):
                vfield = fm.group(2).upper()
                if vfield in result['fields']:
                    result['fields'][vfield]['ddm'] = ddm
                    result['fields'][vfield]['scope'] = 'VIEW'
                else:
                    result['fields'][vfield] = {
                        'name': vfield,
                        'format': '',
                        'level': int(fm.group(1)),
                        'scope': 'VIEW',
                        'ddm': ddm,
                        'value_sources': [],
                        'used_in_conditions': [],
                        'used_in_db_ops': [],
                        'displayed_on_maps': [],
                        'passed_to_callnat': [],
                        'search_key_in': [],
                    }

    # ── Step 2: Track value assignments (HOW each field gets its value) ──

    def add_lineage(target, source_type, source_detail, context=''):
        target = target.upper().strip()
        entry = {
            'target': target,
            'source_type': source_type,
            'source': source_detail,
            'context': context,
            'program': name,
        }
        result['lineage'].append(entry)
        if target in result['fields']:
            result['fields'][target]['value_sources'].append(entry)

    # MOVE source TO target
    for m in RE_MOVE.finditer(clean):
        source_expr = m.group(1).strip()
        target = m.group(2).strip()
        src_info = classify_source(source_expr)
        add_lineage(target, src_info['type'], src_info['source'], f"MOVE {source_expr} TO {target}")

    # target := source (Natural ASSIGN)
    for m in RE_ASSIGN.finditer(clean):
        target = m.group(1).strip()
        source_expr = m.group(2).strip()
        src_info = classify_source(source_expr)
        add_lineage(target, src_info['type'], src_info['source'], f"{target} := {source_expr}")

    # COMPUTE target = expression
    for m in RE_COMPUTE.finditer(clean):
        target = m.group(1).strip()
        expr = m.group(2).strip()
        add_lineage(target, 'CALCULATED', expr, f"COMPUTE {target} = {expr}")

    # ADD source TO target
    for m in RE_ADD.finditer(clean):
        source = m.group(1).strip()
        target = m.group(2).strip()
        add_lineage(target, 'CALCULATED', f"{target} + {source}", f"ADD {source} TO {target}")

    # SUBTRACT source FROM target
    for m in RE_SUBTRACT.finditer(clean):
        source = m.group(1).strip()
        target = m.group(2).strip()
        add_lineage(target, 'CALCULATED', f"{target} - {source}", f"SUBTRACT {source} FROM {target}")

    # MULTIPLY source INTO target
    for m in RE_MULTIPLY.finditer(clean):
        source = m.group(1).strip()
        target = m.group(2).strip()
        add_lineage(target, 'CALCULATED', f"{target} * {source}", f"MULTIPLY {source} INTO {target}")

    # DIVIDE source INTO target
    for m in RE_DIVIDE.finditer(clean):
        source = m.group(1).strip()
        target = m.group(2).strip()
        add_lineage(target, 'CALCULATED', f"{target} / {source}", f"DIVIDE {source} INTO {target}")

    # COMPRESS sources INTO target
    for m in RE_COMPRESS.finditer(clean):
        sources = m.group(1).strip()
        target = m.group(2).strip()
        add_lineage(target, 'CONCATENATED', sources, f"COMPRESS {sources} INTO {target}")

    # EXAMINE field (in-place modification)
    for m in RE_EXAMINE.finditer(clean):
        field = m.group(1).strip()
        pattern = m.group(2).strip()
        add_lineage(field, 'TRANSFORMED', f"EXAMINE FOR {pattern}", f"EXAMINE {field} FOR {pattern}")

    # SEPARATE source INTO targets
    for m in RE_SEPARATE.finditer(clean):
        source = m.group(1).strip()
        targets = m.group(2).strip()
        for t in re.split(r'\s+', targets):
            t = t.strip().upper()
            if re.match(r'^[#A-Za-z]', t):
                add_lineage(t, 'EXTRACTED', source, f"SEPARATE {source} INTO {targets}")

    # RESET fields (set to default/empty)
    for m in RE_RESET.finditer(clean):
        fields_str = m.group(1).strip()
        for f in re.split(r'[\s,]+', fields_str):
            f = f.strip().upper()
            if re.match(r'^[#A-Za-z][A-Za-z0-9_#@$-]*$', f) and f != 'INITIAL':
                add_lineage(f, 'RESET', 'DEFAULT', f"RESET {f}")

    # ── Step 3: MAP input (user-provided values) ──
    for m in RE_MAP_INPUT.finditer(clean):
        map_name = m.group(1).upper()
        # All editable fields on this map receive USER-INPUT
        # We can't know which fields without the map source, but we tag the event
        for field_name, field_info in result['fields'].items():
            if field_info['scope'] in ('LOCAL', 'PARAMETER'):
                field_info['displayed_on_maps'].append(map_name)
        # Mark in lineage that user input happened
        result['lineage'].append({
            'target': f'[MAP:{map_name}]',
            'source_type': 'USER-INPUT',
            'source': map_name,
            'context': f'INPUT USING MAP {map_name}',
            'program': name,
        })

    # ── Step 4: Database operations (READ populates fields, STORE/UPDATE writes them) ──
    for m in RE_DB_READ.finditer(clean):
        op = m.group(1).upper()
        view_ref = m.group(2).upper()
        ddm = views.get(view_ref, view_ref)
        # After a READ, all VIEW fields under this view are populated from DB
        for field_name, field_info in result['fields'].items():
            if field_info.get('ddm') == ddm:
                field_info['used_in_db_ops'].append({'operation': op, 'ddm': ddm, 'role': 'READ-INTO'})
                add_lineage(field_name, 'DATABASE-READ', f'{ddm}.{field_name}', f'{op} {view_ref}')

    for m in RE_DB_STORE.finditer(clean):
        view_ref = m.group(2).upper()
        ddm = views.get(view_ref, view_ref)
        for field_name, field_info in result['fields'].items():
            if field_info.get('ddm') == ddm:
                field_info['used_in_db_ops'].append({'operation': 'STORE', 'ddm': ddm, 'role': 'WRITTEN-FROM'})

    for m in RE_DB_UPDATE.finditer(clean):
        view_ref = m.group(2).upper()
        ddm = views.get(view_ref, view_ref)
        for field_name, field_info in result['fields'].items():
            if field_info.get('ddm') == ddm:
                field_info['used_in_db_ops'].append({'operation': 'UPDATE', 'ddm': ddm, 'role': 'WRITTEN-FROM'})

    for m in RE_DB_DELETE.finditer(clean):
        view_ref = m.group(2).upper()
        ddm = views.get(view_ref, view_ref)
        for field_name, field_info in result['fields'].items():
            if field_info.get('ddm') == ddm:
                field_info['used_in_db_ops'].append({'operation': 'DELETE', 'ddm': ddm, 'role': 'CRITERIA'})

    # ── Step 5: Condition usage (IF, DECIDE) ──
    for m in RE_IF_FIELD.finditer(clean):
        field = m.group(1).upper()
        operator = m.group(2).strip()
        if field in result['fields']:
            result['fields'][field]['used_in_conditions'].append({
                'condition': f'{field} {operator} ...',
                'program': name,
            })

    # ── Step 6: Search key usage ──
    for m in RE_SEARCH_CRIT.finditer(clean):
        field = m.group(1).upper()
        if field in result['fields']:
            result['fields'][field]['search_key_in'].append(name)

    # ── Step 7: CALLNAT parameter passing ──
    for m in RE_CALLNAT_FULL.finditer(clean):
        called_pgm = m.group(1).upper()
        params = m.group(2).strip()
        param_list = re.split(r'[\s,]+', params)
        for i, p in enumerate(param_list):
            p = p.strip().upper()
            if p in result['fields']:
                result['fields'][p]['passed_to_callnat'].append({
                    'called_program': called_pgm,
                    'param_position': i + 1,
                })
                add_lineage(f'{called_pgm}.PARAM-{i+1}', 'PARAMETER-PASS', p,
                           f'CALLNAT {called_pgm} ... {p} at position {i+1}')

    return result


# ═══════════════════════════════════════════════════════════════
# CROSS-PROGRAM FIELD INDEX
# ═══════════════════════════════════════════════════════════════

def build_field_index(all_results):
    """Build a cross-program index for each unique field name."""
    field_index = defaultdict(lambda: {
        'defined_in': [],
        'value_sources': [],
        'read_from_db': [],
        'written_to_db': [],
        'displayed_on_maps': [],
        'used_in_conditions': [],
        'passed_as_param': [],
        'search_key_in': [],
        'ddms': set(),
    })

    for prog_result in all_results:
        if not prog_result:
            continue
        pgm = prog_result['program']

        for fname, finfo in prog_result.get('fields', {}).items():
            idx = field_index[fname]
            idx['defined_in'].append({
                'program': pgm,
                'scope': finfo['scope'],
                'format': finfo['format'],
                'ddm': finfo.get('ddm'),
            })
            if finfo.get('ddm'):
                idx['ddms'].add(finfo['ddm'])

            for vs in finfo.get('value_sources', []):
                idx['value_sources'].append(vs)

            for dbop in finfo.get('used_in_db_ops', []):
                if dbop['role'] == 'READ-INTO':
                    idx['read_from_db'].append({'program': pgm, **dbop})
                else:
                    idx['written_to_db'].append({'program': pgm, **dbop})

            for m in finfo.get('displayed_on_maps', []):
                idx['displayed_on_maps'].append({'program': pgm, 'map': m})

            for c in finfo.get('used_in_conditions', []):
                idx['used_in_conditions'].append(c)

            for p in finfo.get('passed_as_param', []):
                idx['passed_as_param'].append({'from_program': pgm, **p})

            for s in finfo.get('search_key_in', []):
                idx['search_key_in'].append(s)

    # Convert sets to lists
    for fname in field_index:
        field_index[fname]['ddms'] = sorted(field_index[fname]['ddms'])

    return dict(field_index)


# ═══════════════════════════════════════════════════════════════
# LINEAGE CHAIN BUILDER
# ═══════════════════════════════════════════════════════════════

def build_lineage_chain(field_name, field_index, all_lineage, max_depth=6):
    """Build a full value provenance chain for a field.
    Traces: where does the value come from? And where does THAT come from?
    """
    chain = []
    visited = set()

    def trace(fname, depth):
        if depth > max_depth or fname in visited:
            return
        visited.add(fname)

        idx = field_index.get(fname, {})
        sources = idx.get('value_sources', [])

        for src in sources:
            node = {
                'field': fname,
                'depth': depth,
                'source_type': src.get('source_type', 'UNKNOWN'),
                'source': src.get('source', ''),
                'context': src.get('context', ''),
                'program': src.get('program', ''),
                'upstream': [],
            }

            # If source is another field, trace it recursively
            if src.get('source_type') == 'FIELD-COPY':
                source_field = src.get('source', '').upper()
                if source_field and source_field in field_index:
                    trace(source_field, depth + 1)
                    node['upstream'] = [e for e in chain if e['field'] == source_field]

            chain.append(node)

    trace(field_name.upper(), 0)
    return chain


# ═══════════════════════════════════════════════════════════════
# CLI & MAIN
# ═══════════════════════════════════════════════════════════════

def scan_directory(dir_path, max_workers=8, target_program=None):
    """Scan all Natural files for field-level analysis."""
    dir_path = Path(dir_path)
    extensions = {'.nsp', '.nsn', '.nsl', '.nsg', '.nsa', '.nsh', '.nsm',
                  '.nsc', '.nss', '.ns7', '.ns4', '.nat', '.txt', '.src', ''}

    files = []
    for root, dirs, filenames in os.walk(dir_path):
        for fname in filenames:
            fp = os.path.join(root, fname)
            ext = Path(fname).suffix.lower()
            if ext in extensions or not ext:
                if target_program:
                    if Path(fname).stem.upper() == target_program.upper():
                        files.append(fp)
                else:
                    files.append(fp)

    total = len(files)
    print(f"Analyzing {total:,} files for field lineage...")

    results = []
    processed = 0

    if total > 500 and max_workers > 1:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(analyze_program_fields, fp): fp for fp in files}
            for future in as_completed(futures):
                processed += 1
                if processed % 5000 == 0:
                    print(f"  {processed:,}/{total:,} ({processed*100//total}%)")
                try:
                    r = future.result()
                    if r:
                        results.append(r)
                except Exception:
                    pass
    else:
        for fp in files:
            processed += 1
            r = analyze_program_fields(fp)
            if r:
                results.append(r)

    print(f"  Done: {len(results):,} programs analyzed")
    return results


def main():
    parser = argparse.ArgumentParser(description='MFREA Field Lineage Analyzer')
    parser.add_argument('--source', required=True, help='Path to Natural source directory')
    parser.add_argument('--program', help='Analyze single program only')
    parser.add_argument('--field', help='Generate lineage for specific field')
    parser.add_argument('--output', default='field_lineage.json', help='Output JSON')
    parser.add_argument('--workers', type=int, default=8, help='Parallel workers')
    args = parser.parse_args()

    start = time.time()

    print("=" * 60)
    print("MFREA Field Lineage Analyzer")
    print("=" * 60)

    results = scan_directory(args.source, args.workers, args.program)

    print("\nBuilding cross-program field index...")
    field_index = build_field_index(results)

    # Collect all lineage entries
    all_lineage = []
    for r in results:
        all_lineage.extend(r.get('lineage', []))

    output = {
        'metadata': {
            'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'programs_analyzed': len(results),
            'unique_fields': len(field_index),
            'total_lineage_entries': len(all_lineage),
        },
        'programs': {r['program']: r for r in results},
        'field_index': field_index,
    }

    # If specific field requested, add its provenance chain
    if args.field:
        fname = args.field.upper()
        print(f"\nBuilding provenance chain for: {fname}")
        chain = build_lineage_chain(fname, field_index, all_lineage)
        output['provenance_chain'] = {
            'field': fname,
            'chain': chain,
        }
        print(f"  Chain depth: {max((c['depth'] for c in chain), default=0)} levels")

    # Write output
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    size_mb = os.path.getsize(args.output) / (1024 * 1024)

    elapsed = time.time() - start
    m = output['metadata']

    print(f"\n{'=' * 60}")
    print(f"ANALYSIS COMPLETE in {elapsed:.1f}s")
    print(f"  Programs:      {m['programs_analyzed']:>8,}")
    print(f"  Unique fields: {m['unique_fields']:>8,}")
    print(f"  Lineage links: {m['total_lineage_entries']:>8,}")
    print(f"  Output: {args.output} ({size_mb:.1f} MB)")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
