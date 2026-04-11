#!/usr/bin/env python3
"""
MFREA Scanner — Mainframe Reverse Engineering Agent
Scans 52K+ Natural modules and 13K+ JCL files to extract:
  - Call chains (CALLNAT, FETCH, PERFORM, EXEC PGM)
  - Adabas file/DDM access with field lists
  - Reference table reads (READ BY length pattern)
  - Program metadata (type, library, purpose hints)

Output: JSON graph suitable for the interactive viewer.

Usage:
  python scanner.py --natural /path/to/natural --jcl /path/to/jcl --output graph.json
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

# ── Regex patterns for Natural ──────────────────────────────────────────

# CALLNAT 'PROGNAME' or CALLNAT 'PROGNAME' parms
RE_CALLNAT = re.compile(
    r"CALLNAT\s+'([A-Za-z0-9_#@$-]+)'", re.IGNORECASE
)

# FETCH 'PROGNAME' or FETCH RETURN 'PROGNAME'
RE_FETCH = re.compile(
    r"FETCH\s+(?:RETURN\s+)?'([A-Za-z0-9_#@$-]+)'", re.IGNORECASE
)

# PERFORM subroutine-name
RE_PERFORM = re.compile(
    r"PERFORM\s+([A-Za-z0-9_#@$-]+)", re.IGNORECASE
)

# INPUT USING MAP 'MAPNAME' or INPUT MAP 'MAPNAME'
RE_MAP = re.compile(
    r"(?:INPUT|WRITE|REINPUT)\s+(?:USING\s+)?MAP\s+'([A-Za-z0-9_#@$-]+)'", re.IGNORECASE
)

# Database operations: READ/FIND/GET/STORE/UPDATE/DELETE/HISTOGRAM file-view
RE_DB_OP = re.compile(
    r"\b(READ|FIND|GET|STORE|UPDATE|DELETE|HISTOGRAM)\s+(?:\(\d+\)\s+)?([A-Za-z0-9_#@$-]+)",
    re.IGNORECASE
)

# DEFINE DATA ... USING 'LDA/GDA/PDA-name'
RE_DATA_AREA = re.compile(
    r"(?:LOCAL|GLOBAL|PARAMETER)\s+USING\s+'?([A-Za-z0-9_#@$-]+)'?", re.IGNORECASE
)

# Field references after database view: specific field names in Natural
# We capture lines after a READ/FIND that reference fields
RE_FIELD_REF = re.compile(
    r"\b([A-Z][A-Z0-9_-]{2,})\b"
)

# DDM/View reference in DEFINE DATA
RE_VIEW = re.compile(
    r"^\s*\d+\s+([A-Za-z0-9_#@$-]+)\s+VIEW\s+OF\s+([A-Za-z0-9_#@$-]+)",
    re.IGNORECASE | re.MULTILINE
)

# Reference table pattern: READ tablename BY field-name = value (length-based read)
RE_REF_TABLE = re.compile(
    r"READ\s+([A-Za-z0-9_#@$-]+)\s+(?:WITH\s+)?(?:BY\s+)?(?:LENGTH|DESCRIPTOR|KEY)\b",
    re.IGNORECASE
)

# Alternative ref table: FIND ... WITH ... = (lookup pattern)
RE_REF_LOOKUP = re.compile(
    r"(?:FIND|READ)\s+([A-Za-z0-9_#@$-]+)\s+WITH\s+([A-Za-z0-9_#@$-]+)\s*=",
    re.IGNORECASE
)

# ── Regex patterns for JCL ──────────────────────────────────────────────

# EXEC PGM=program or EXEC PROC=proc
RE_JCL_EXEC = re.compile(
    r"//\w+\s+EXEC\s+(?:PGM=|PROC=)([A-Za-z0-9_#@$]+)", re.IGNORECASE
)

# PARM= in JCL (often contains Natural program names)
RE_JCL_PARM = re.compile(
    r"PARM=\(?'?([^')]+)'?\)?", re.IGNORECASE
)

# DD DSN= dataset references
RE_JCL_DD = re.compile(
    r"//(\w+)\s+DD\s+.*DSN=([A-Za-z0-9_.()]+)", re.IGNORECASE
)

# ── File type detection ─────────────────────────────────────────────────

NATURAL_EXTENSIONS = {
    '.nsp': 'program', '.nsn': 'subprogram', '.nsl': 'lda',
    '.nsg': 'gda', '.nsa': 'pda', '.nsh': 'helproutine',
    '.nsm': 'map', '.nsc': 'copycode', '.nss': 'subroutine',
    '.ns7': 'program', '.ns4': 'subprogram',
}

def detect_natural_type(filepath, content):
    """Detect Natural module type from extension or content."""
    ext = Path(filepath).suffix.lower()
    if ext in NATURAL_EXTENSIONS:
        return NATURAL_EXTENSIONS[ext]
    content_upper = content[:500].upper()
    if 'DEFINE DATA PARAMETER' in content_upper:
        return 'subprogram'
    if 'DEFINE SUBROUTINE' in content_upper:
        return 'subroutine'
    if 'DEFINE MAP' in content_upper or 'FORMAT PAGE' in content_upper:
        return 'map'
    return 'program'


# ── Scanner functions ───────────────────────────────────────────────────

def scan_natural_file(filepath):
    """Parse a single Natural file and extract all relationships."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return None

    name = Path(filepath).stem.upper()
    lib = _infer_library(filepath)
    mod_type = detect_natural_type(filepath, content)

    result = {
        'name': name,
        'type': mod_type,
        'library': lib,
        'filepath': str(filepath),
        'calls': [],          # programs called
        'called_by': [],      # populated later
        'maps': [],           # maps used
        'db_access': [],      # {ddm, operation, fields}
        'views': [],          # DDM views defined
        'data_areas': [],     # LDAs/GDAs/PDAs
        'ref_tables': [],     # reference table reads
        'line_count': content.count('\n') + 1,
    }

    # Remove comment lines (lines starting with * in Natural)
    lines = content.split('\n')
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('*') or stripped.startswith('/*'):
            continue
        clean_lines.append(line)
    clean_content = '\n'.join(clean_lines)

    # Extract CALLNAT references
    for m in RE_CALLNAT.finditer(clean_content):
        called = m.group(1).upper()
        if called not in [c['target'] for c in result['calls']]:
            result['calls'].append({'target': called, 'type': 'CALLNAT'})

    # Extract FETCH references
    for m in RE_FETCH.finditer(clean_content):
        called = m.group(1).upper()
        if called not in [c['target'] for c in result['calls']]:
            result['calls'].append({'target': called, 'type': 'FETCH'})

    # Extract MAP references
    for m in RE_MAP.finditer(clean_content):
        map_name = m.group(1).upper()
        if map_name not in result['maps']:
            result['maps'].append(map_name)

    # Extract VIEW definitions (DDM references)
    for m in RE_VIEW.finditer(clean_content):
        view_alias = m.group(1).upper()
        ddm_name = m.group(2).upper()
        result['views'].append({'alias': view_alias, 'ddm': ddm_name})

    # Extract database operations
    ddm_aliases = {v['alias']: v['ddm'] for v in result['views']}
    for m in RE_DB_OP.finditer(clean_content):
        operation = m.group(1).upper()
        view_ref = m.group(2).upper()
        # Skip common Natural keywords that aren't DDM references
        if view_ref in ('WORK', 'FILE', 'PRINTER', 'PC', 'SCREEN',
                        'TITLE', 'HEADER', 'TRAILER', 'NOTITLE', 'NOHDR',
                        'INPUT', 'AND', 'OR', 'NOT', 'END', 'IF', 'WITH'):
            continue
        ddm_name = ddm_aliases.get(view_ref, view_ref)
        # Extract fields used near this statement (next 5 lines)
        pos = m.end()
        context = clean_content[pos:pos+500]
        fields = _extract_fields_from_context(context, ddm_name)
        result['db_access'].append({
            'ddm': ddm_name,
            'operation': operation,
            'fields': fields,
            'view_alias': view_ref,
        })

    # Extract data area references
    for m in RE_DATA_AREA.finditer(clean_content):
        da = m.group(1).upper()
        if da not in result['data_areas']:
            result['data_areas'].append(da)

    # Extract reference table reads
    for m in RE_REF_LOOKUP.finditer(clean_content):
        table = m.group(1).upper()
        field = m.group(2).upper()
        if table not in [r['table'] for r in result['ref_tables']]:
            result['ref_tables'].append({'table': table, 'field': field, 'type': 'LOOKUP'})

    return result


def scan_jcl_file(filepath):
    """Parse a single JCL file and extract relationships."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return None

    name = Path(filepath).stem.upper()

    result = {
        'name': name,
        'type': 'jcl',
        'library': _infer_library(filepath),
        'filepath': str(filepath),
        'calls': [],
        'called_by': [],
        'steps': [],
        'datasets': [],
        'db_access': [],
        'views': [],
        'maps': [],
        'data_areas': [],
        'ref_tables': [],
        'line_count': content.count('\n') + 1,
    }

    # Extract EXEC PGM/PROC steps
    for m in RE_JCL_EXEC.finditer(content):
        pgm = m.group(1).upper()
        result['steps'].append(pgm)
        # If it's NATBATCH or similar, look for PARM to find Natural program
        if pgm in ('NATBATCH', 'NATPARM', 'ADANUC', 'ADARUN'):
            # Search nearby for PARM containing program name
            context = content[m.start():m.start()+500]
            parm_match = RE_JCL_PARM.search(context)
            if parm_match:
                parm_val = parm_match.group(1).upper()
                # PARM often has format: 'LIBRARY,PROGRAM' or just 'PROGRAM'
                parts = [p.strip() for p in parm_val.split(',')]
                for part in parts:
                    clean = part.strip("'\" ")
                    if clean and len(clean) > 1 and clean not in ('NATBATCH', 'STACK', 'IM', 'NOIO'):
                        if clean not in [c['target'] for c in result['calls']]:
                            result['calls'].append({'target': clean, 'type': 'JCL-EXEC'})
        else:
            if pgm not in [c['target'] for c in result['calls']]:
                result['calls'].append({'target': pgm, 'type': 'JCL-EXEC'})

    # Extract DD DSN references
    for m in RE_JCL_DD.finditer(content):
        dd_name = m.group(1).upper()
        dsn = m.group(2).upper()
        result['datasets'].append({'dd': dd_name, 'dsn': dsn})

    return result


def _infer_library(filepath):
    """Infer library name from folder structure."""
    parts = Path(filepath).parts
    # Look for a folder name that looks like a library
    for i, part in enumerate(parts):
        if part.lower() in ('natural', 'jcl', 'cobol', 'maps', 'ddm', 'copybooks'):
            if i > 0:
                return parts[i-1].upper()
    # Fallback: use parent folder
    return Path(filepath).parent.name.upper()


def _extract_fields_from_context(context, ddm_name):
    """Extract likely field names from the context after a DB statement."""
    fields = []
    # Look for field references in the next few lines
    lines = context.split('\n')[:8]
    for line in lines:
        stripped = line.strip().upper()
        if stripped.startswith('*') or stripped.startswith('/*'):
            continue
        # Stop at next statement
        if any(kw in stripped for kw in ['END-', 'CALLNAT', 'FETCH', 'IF ', 'DECIDE',
                                          'INPUT', 'WRITE', 'PERFORM', 'ESCAPE']):
            break
        # Find field-like identifiers (CAPS with hyphens)
        for fm in RE_FIELD_REF.finditer(stripped):
            field = fm.group(1)
            # Skip Natural keywords
            if field not in ('END', 'DEFINE', 'DATA', 'LOCAL', 'GLOBAL', 'VIEW',
                           'PARAMETER', 'USING', 'WITH', 'WHERE', 'AND', 'OR',
                           'NOT', 'TRUE', 'FALSE', 'THEN', 'ELSE', 'FOR',
                           'FROM', 'TO', 'STEP', 'WHILE', 'UNTIL', 'LOOP',
                           'VALUE', 'CONST', 'INIT', 'REDEFINE', 'FILLER',
                           'NONE', 'NULL', 'ZERO', 'ZEROS', 'SPACES', 'BLANK',
                           'MOVE', 'COMPUTE', 'ADD', 'SUBTRACT', 'MULTIPLY',
                           'DIVIDE', 'COMPRESS', 'EXAMINE', 'SEPARATE',
                           'PRINT', 'DISPLAY', 'FORMAT', 'PAGE', 'GIVE',
                           'OBTAIN', 'RELEASE', 'ACCEPT', 'REJECT',
                           'STORE', 'UPDATE', 'DELETE', 'READ', 'FIND', 'GET',
                           'HISTOGRAM', 'SORTED', 'DESCENDING', 'ASCENDING'):
                if len(field) > 2 and '-' in field or len(field) > 4:
                    fields.append(field)
    return list(set(fields))[:20]  # Cap at 20 fields per access


# ── Main scanning orchestrator ──────────────────────────────────────────

def scan_directory(dir_path, file_type='natural', max_workers=8):
    """Scan a directory of files using multiple processes."""
    dir_path = Path(dir_path)
    if not dir_path.exists():
        print(f"ERROR: Directory not found: {dir_path}")
        sys.exit(1)

    # Collect files
    if file_type == 'natural':
        extensions = set(NATURAL_EXTENSIONS.keys()) | {'.nat', '.txt', '.src', ''}
        scan_func = scan_natural_file
    else:
        extensions = {'.jcl', '.txt', '.job', '.proc', ''}
        scan_func = scan_jcl_file

    files = []
    for root, dirs, filenames in os.walk(dir_path):
        for fname in filenames:
            fp = os.path.join(root, fname)
            ext = Path(fname).suffix.lower()
            if ext in extensions or not ext:
                files.append(fp)

    total = len(files)
    print(f"Found {total:,} {file_type} files to scan...")

    results = {}
    errors = 0
    processed = 0

    # Use multiprocessing for large codebases
    if total > 1000 and max_workers > 1:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scan_func, fp): fp for fp in files}
            for future in as_completed(futures):
                processed += 1
                if processed % 5000 == 0:
                    print(f"  Scanned {processed:,}/{total:,} ({processed*100//total}%)")
                try:
                    result = future.result()
                    if result:
                        results[result['name']] = result
                except Exception:
                    errors += 1
    else:
        for fp in files:
            processed += 1
            if processed % 2000 == 0:
                print(f"  Scanned {processed:,}/{total:,} ({processed*100//total}%)")
            result = scan_func(fp)
            if result:
                results[result['name']] = result

    print(f"  Completed: {len(results):,} modules parsed, {errors} errors")
    return results


def build_graph(natural_modules, jcl_modules):
    """Build the complete dependency graph with bidirectional links."""
    all_modules = {}
    all_modules.update(natural_modules)
    all_modules.update(jcl_modules)

    # Build called_by (reverse index)
    for name, mod in all_modules.items():
        for call in mod.get('calls', []):
            target = call['target']
            if target in all_modules:
                if name not in [c for c in all_modules[target].get('called_by', [])]:
                    all_modules[target].setdefault('called_by', []).append(name)

    # Build Adabas file index
    adabas_index = defaultdict(lambda: {'programs': [], 'fields': set()})
    for name, mod in all_modules.items():
        for access in mod.get('db_access', []):
            ddm = access['ddm']
            adabas_index[ddm]['programs'].append({
                'program': name,
                'operation': access['operation'],
                'fields': access['fields'],
            })
            adabas_index[ddm]['fields'].update(access['fields'])

    # Convert sets to lists for JSON
    for ddm in adabas_index:
        adabas_index[ddm]['fields'] = sorted(adabas_index[ddm]['fields'])

    # Build reference table index
    ref_table_index = defaultdict(list)
    for name, mod in all_modules.items():
        for ref in mod.get('ref_tables', []):
            ref_table_index[ref['table']].append({
                'program': name,
                'field': ref['field'],
                'type': ref['type'],
            })

    # Identify root programs (not called by anything) and leaf programs
    roots = []
    leaves = []
    for name, mod in all_modules.items():
        if not mod.get('called_by'):
            roots.append(name)
        if not mod.get('calls'):
            leaves.append(name)

    # Compute stats
    stats = {
        'total_modules': len(all_modules),
        'natural_modules': len(natural_modules),
        'jcl_modules': len(jcl_modules),
        'total_calls': sum(len(m.get('calls', [])) for m in all_modules.values()),
        'unique_ddms': len(adabas_index),
        'unique_ref_tables': len(ref_table_index),
        'root_programs': len(roots),
        'leaf_programs': len(leaves),
        'program_types': defaultdict(int),
    }
    for mod in all_modules.values():
        stats['program_types'][mod['type']] += 1
    stats['program_types'] = dict(stats['program_types'])

    graph = {
        'metadata': {
            'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': stats,
        },
        'modules': all_modules,
        'adabas_index': dict(adabas_index),
        'ref_table_index': dict(ref_table_index),
        'roots': sorted(roots),
        'leaves': sorted(leaves),
    }

    return graph


# ── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='MFREA Scanner — Mainframe Reverse Engineering Agent')
    parser.add_argument('--natural', required=True, help='Path to Natural modules directory')
    parser.add_argument('--jcl', required=True, help='Path to JCL files directory')
    parser.add_argument('--output', default='graph.json', help='Output JSON file (default: graph.json)')
    parser.add_argument('--workers', type=int, default=8, help='Parallel workers (default: 8)')
    args = parser.parse_args()

    print("=" * 60)
    print("MFREA Scanner — Mainframe Reverse Engineering Agent")
    print("=" * 60)

    start = time.time()

    print(f"\n[1/3] Scanning Natural modules: {args.natural}")
    natural_modules = scan_directory(args.natural, 'natural', args.workers)

    print(f"\n[2/3] Scanning JCL files: {args.jcl}")
    jcl_modules = scan_directory(args.jcl, 'jcl', args.workers)

    print(f"\n[3/3] Building dependency graph...")
    graph = build_graph(natural_modules, jcl_modules)

    # Write output
    output_path = args.output
    with open(output_path, 'w') as f:
        json.dump(graph, f, indent=None, default=str)  # No indent for speed on large files
    size_mb = os.path.getsize(output_path) / (1024 * 1024)

    elapsed = time.time() - start
    s = graph['metadata']['stats']

    print(f"\n{'=' * 60}")
    print(f"SCAN COMPLETE in {elapsed:.1f}s")
    print(f"{'=' * 60}")
    print(f"  Natural modules:   {s['natural_modules']:>8,}")
    print(f"  JCL modules:       {s['jcl_modules']:>8,}")
    print(f"  Total modules:     {s['total_modules']:>8,}")
    print(f"  Total call links:  {s['total_calls']:>8,}")
    print(f"  Unique DDMs:       {s['unique_ddms']:>8,}")
    print(f"  Ref tables:        {s['unique_ref_tables']:>8,}")
    print(f"  Root programs:     {s['root_programs']:>8,}")
    print(f"  Output: {output_path} ({size_mb:.1f} MB)")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
