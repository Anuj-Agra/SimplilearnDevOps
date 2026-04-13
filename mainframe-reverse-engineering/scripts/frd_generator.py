#!/usr/bin/env python3
"""
FRD Generator — Generates Functional Requirements Document from scan graph.
Traces a selected program/table/field and produces a non-technical FRD.

Usage:
  python frd_generator.py --graph graph.json --program CUSTMAIN --output frd_CUSTMAIN.md
  python frd_generator.py --graph graph.json --ddm DDM-CUSTOMER --output frd_DDM-CUSTOMER.md
  python frd_generator.py --graph graph.json --field CUST-STATUS --ddm DDM-CUSTOMER --output frd_field.md
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def load_graph(path):
    with open(path) as f:
        return json.load(f)


def trace_downstream(graph, program_name, visited=None, depth=0, max_depth=15):
    """Recursively trace all programs called by this program."""
    if visited is None:
        visited = set()
    if program_name in visited or depth > max_depth:
        return []
    visited.add(program_name)

    mod = graph['modules'].get(program_name)
    if not mod:
        return [{'name': program_name, 'depth': depth, 'type': 'unknown', 'calls': [], 'db': [], 'maps': []}]

    node = {
        'name': program_name,
        'depth': depth,
        'type': mod.get('type', 'unknown'),
        'library': mod.get('library', ''),
        'calls': [c['target'] for c in mod.get('calls', [])],
        'db': mod.get('db_access', []),
        'maps': mod.get('maps', []),
        'ref_tables': mod.get('ref_tables', []),
        'children': [],
    }

    for call in mod.get('calls', []):
        target = call['target']
        if target not in visited:
            child_tree = trace_downstream(graph, target, visited, depth + 1, max_depth)
            node['children'].extend(child_tree)

    return [node]


def trace_upstream(graph, program_name, visited=None, depth=0, max_depth=10):
    """Trace all programs that call this program (callers)."""
    if visited is None:
        visited = set()
    if program_name in visited or depth > max_depth:
        return []
    visited.add(program_name)

    mod = graph['modules'].get(program_name)
    if not mod:
        return [{'name': program_name, 'depth': depth, 'callers': []}]

    callers = mod.get('called_by', [])
    node = {
        'name': program_name,
        'depth': depth,
        'type': mod.get('type', 'unknown'),
        'callers': callers,
        'parents': [],
    }

    for caller in callers:
        if caller not in visited:
            parent_tree = trace_upstream(graph, caller, visited, depth + 1, max_depth)
            node['parents'].extend(parent_tree)

    return [node]


def generate_functional_description(mod, graph):
    """Generate non-technical description from program analysis."""
    desc_parts = []
    name = mod.get('name', 'Unknown')
    mod_type = mod.get('type', 'program')

    # Infer purpose from name and operations
    name_lower = name.lower()
    if any(k in name_lower for k in ['inq', 'inquiry', 'disp', 'display', 'view', 'show', 'list']):
        desc_parts.append(f"This module provides inquiry/display functionality")
    elif any(k in name_lower for k in ['upd', 'update', 'edit', 'modify', 'chg', 'change']):
        desc_parts.append(f"This module handles data updates and modifications")
    elif any(k in name_lower for k in ['add', 'create', 'new', 'ins', 'insert', 'reg']):
        desc_parts.append(f"This module handles new record creation")
    elif any(k in name_lower for k in ['del', 'remove', 'purge', 'arch']):
        desc_parts.append(f"This module handles record removal or archival")
    elif any(k in name_lower for k in ['val', 'valid', 'chk', 'check', 'verify']):
        desc_parts.append(f"This module performs data validation")
    elif any(k in name_lower for k in ['rpt', 'report', 'print', 'extract', 'exp']):
        desc_parts.append(f"This module generates reports or data extracts")
    elif any(k in name_lower for k in ['batch', 'job', 'night', 'daily', 'proc']):
        desc_parts.append(f"This module performs batch processing")
    elif any(k in name_lower for k in ['menu', 'main', 'drv', 'driver', 'ctrl']):
        desc_parts.append(f"This module serves as a menu or process controller")
    else:
        desc_parts.append(f"This module provides business functionality")

    # Add data context
    ddms = set()
    ops = defaultdict(list)
    for access in mod.get('db_access', []):
        ddms.add(access['ddm'])
        ops[access['operation']].append(access['ddm'])

    if ddms:
        desc_parts.append(f"working with data from: {', '.join(sorted(ddms))}")

    if ops.get('READ') or ops.get('FIND'):
        desc_parts.append("It retrieves existing records for processing")
    if ops.get('STORE'):
        desc_parts.append("It creates new records")
    if ops.get('UPDATE'):
        desc_parts.append("It modifies existing records")
    if ops.get('DELETE'):
        desc_parts.append("It removes records")

    if mod.get('maps'):
        desc_parts.append(f"The user interacts through screen(s): {', '.join(mod['maps'])}")

    return '. '.join(desc_parts) + '.'


def generate_frd_for_program(graph, program_name):
    """Generate a full FRD document for a program."""
    mod = graph['modules'].get(program_name)
    if not mod:
        return f"# ERROR: Program '{program_name}' not found in graph.\n"

    downstream = trace_downstream(graph, program_name)
    upstream = trace_upstream(graph, program_name)

    lines = []
    lines.append(f"# Functional Requirements Document")
    lines.append(f"## {program_name}")
    lines.append(f"")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Module Type:** {mod.get('type', 'unknown').title()}")
    lines.append(f"**Library:** {mod.get('library', 'N/A')}")
    lines.append(f"")

    # Section 1: Functional Overview
    lines.append(f"## 1. Functional Overview")
    lines.append(f"")
    lines.append(generate_functional_description(mod, graph))
    lines.append(f"")

    # Section 2: User Interaction
    if mod.get('maps'):
        lines.append(f"## 2. User Interface")
        lines.append(f"")
        lines.append(f"The following screens are presented to the user:")
        lines.append(f"")
        for map_name in mod['maps']:
            lines.append(f"- **{map_name}** — User interaction screen")
        lines.append(f"")
    else:
        lines.append(f"## 2. User Interface")
        lines.append(f"")
        lines.append(f"This module does not have direct user interaction (batch/background process).")
        lines.append(f"")

    # Section 3: Data Accessed
    lines.append(f"## 3. Data Entities")
    lines.append(f"")
    if mod.get('db_access'):
        lines.append(f"| Data Entity (DDM) | Access Type | Key Fields |")
        lines.append(f"|---|---|---|")
        seen_ddms = set()
        for access in mod['db_access']:
            ddm = access['ddm']
            if ddm not in seen_ddms:
                seen_ddms.add(ddm)
                ops = [a['operation'] for a in mod['db_access'] if a['ddm'] == ddm]
                fields = []
                for a in mod['db_access']:
                    if a['ddm'] == ddm:
                        fields.extend(a.get('fields', []))
                fields = sorted(set(fields))[:10]
                lines.append(f"| {ddm} | {', '.join(set(ops))} | {', '.join(fields) if fields else 'N/A'} |")
        lines.append(f"")
    else:
        lines.append(f"No direct database access detected.")
        lines.append(f"")

    # Section 4: Process Flow (functional, non-technical)
    lines.append(f"## 4. Process Flow")
    lines.append(f"")
    lines.append(f"### 4.1 Called By (Upstream)")
    callers = mod.get('called_by', [])
    if callers:
        lines.append(f"This function is invoked by:")
        for caller in callers:
            caller_mod = graph['modules'].get(caller, {})
            lines.append(f"- **{caller}** ({caller_mod.get('type', 'unknown')})")
    else:
        lines.append(f"This is a top-level entry point (not called by other programs).")
    lines.append(f"")

    lines.append(f"### 4.2 Calls (Downstream)")
    calls = mod.get('calls', [])
    if calls:
        lines.append(f"This function delegates work to:")
        for call in calls:
            target = call['target']
            target_mod = graph['modules'].get(target, {})
            target_desc = generate_functional_description(target_mod, graph) if target_mod else "External dependency"
            lines.append(f"- **{target}** — {target_desc[:100]}")
    else:
        lines.append(f"This is a leaf function (does not call other programs).")
    lines.append(f"")

    # Section 5: Functional Tree (non-technical)
    lines.append(f"## 5. Functional Decomposition Tree")
    lines.append(f"")
    lines.append(f"```")
    _render_tree(lines, downstream[0] if downstream else {'name': program_name, 'children': []}, graph, indent=0)
    lines.append(f"```")
    lines.append(f"")

    # Section 6: Reference Tables
    if mod.get('ref_tables'):
        lines.append(f"## 6. Reference Data")
        lines.append(f"")
        lines.append(f"| Reference Table | Lookup Field | Usage |")
        lines.append(f"|---|---|---|")
        for ref in mod['ref_tables']:
            lines.append(f"| {ref['table']} | {ref['field']} | Code/value lookup |")
        lines.append(f"")

    # Section 7: Business Rules Summary
    lines.append(f"## 7. Business Rules (Inferred)")
    lines.append(f"")
    lines.append(f"The following business rules are inferred from the code structure:")
    lines.append(f"")
    rule_num = 1
    for access in mod.get('db_access', []):
        if access['operation'] == 'STORE':
            lines.append(f"- **BR-{rule_num:03d}**: New records can be created in {access['ddm']}")
            rule_num += 1
        elif access['operation'] == 'UPDATE':
            lines.append(f"- **BR-{rule_num:03d}**: Existing records in {access['ddm']} can be modified")
            rule_num += 1
        elif access['operation'] == 'DELETE':
            lines.append(f"- **BR-{rule_num:03d}**: Records can be removed from {access['ddm']}")
            rule_num += 1
    if mod.get('ref_tables'):
        for ref in mod['ref_tables']:
            lines.append(f"- **BR-{rule_num:03d}**: Values are validated against reference table {ref['table']}")
            rule_num += 1
    if rule_num == 1:
        lines.append(f"- No data modification rules detected (read-only module)")
    lines.append(f"")

    return '\n'.join(lines)


def generate_frd_for_ddm(graph, ddm_name):
    """Generate FRD focused on a specific data entity (DDM/Adabas file)."""
    adabas = graph.get('adabas_index', {}).get(ddm_name)
    if not adabas:
        return f"# ERROR: DDM '{ddm_name}' not found in graph.\n"

    lines = []
    lines.append(f"# Functional Requirements Document — Data Entity")
    lines.append(f"## {ddm_name}")
    lines.append(f"")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Type:** Adabas Data Entity (DDM)")
    lines.append(f"")

    lines.append(f"## 1. Overview")
    lines.append(f"")
    lines.append(f"This data entity is accessed by **{len(adabas['programs'])}** program(s).")
    lines.append(f"Known fields: {', '.join(adabas['fields'][:30])}")
    lines.append(f"")

    # Group by operation
    ops = defaultdict(list)
    for prog in adabas['programs']:
        ops[prog['operation']].append(prog)

    lines.append(f"## 2. Access Pattern Summary")
    lines.append(f"")
    lines.append(f"| Operation | Count | Programs |")
    lines.append(f"|---|---|---|")
    for op in ['READ', 'FIND', 'GET', 'STORE', 'UPDATE', 'DELETE', 'HISTOGRAM']:
        if op in ops:
            progs = sorted(set(p['program'] for p in ops[op]))
            lines.append(f"| {op} | {len(ops[op])} | {', '.join(progs[:10])} |")
    lines.append(f"")

    lines.append(f"## 3. Programs Accessing This Entity")
    lines.append(f"")
    lines.append(f"| Program | Operation | Fields Used |")
    lines.append(f"|---|---|---|")
    seen = set()
    for prog in adabas['programs']:
        key = (prog['program'], prog['operation'])
        if key not in seen:
            seen.add(key)
            fields = ', '.join(prog.get('fields', [])[:8])
            lines.append(f"| {prog['program']} | {prog['operation']} | {fields or 'N/A'} |")
    lines.append(f"")

    lines.append(f"## 4. Field Usage Matrix")
    lines.append(f"")
    # Build field-to-program matrix
    field_usage = defaultdict(lambda: defaultdict(set))
    for prog in adabas['programs']:
        for field in prog.get('fields', []):
            field_usage[field][prog['operation']].add(prog['program'])

    if field_usage:
        lines.append(f"| Field | Read By | Written By | Search Key In |")
        lines.append(f"|---|---|---|---|")
        for field in sorted(field_usage.keys()):
            readers = field_usage[field].get('READ', set()) | field_usage[field].get('FIND', set()) | field_usage[field].get('GET', set())
            writers = field_usage[field].get('STORE', set()) | field_usage[field].get('UPDATE', set())
            searchers = field_usage[field].get('FIND', set())
            lines.append(f"| {field} | {', '.join(sorted(readers)[:5])} | {', '.join(sorted(writers)[:5])} | {', '.join(sorted(searchers)[:5])} |")

    lines.append(f"")
    return '\n'.join(lines)


def generate_frd_for_field(graph, ddm_name, field_name):
    """Generate FRD for a specific field."""
    adabas = graph.get('adabas_index', {}).get(ddm_name)
    if not adabas:
        return f"# ERROR: DDM '{ddm_name}' not found.\n"

    lines = []
    lines.append(f"# Functional Requirements Document — Field Lineage")
    lines.append(f"## {ddm_name}.{field_name}")
    lines.append(f"")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"")

    lines.append(f"## 1. Field Overview")
    lines.append(f"")
    lines.append(f"- **Field:** {field_name}")
    lines.append(f"- **Entity:** {ddm_name}")
    lines.append(f"")

    # Find all programs referencing this field
    readers = []
    writers = []
    searchers = []
    for prog in adabas['programs']:
        if field_name in prog.get('fields', []):
            if prog['operation'] in ('READ', 'FIND', 'GET', 'HISTOGRAM'):
                readers.append(prog['program'])
            if prog['operation'] in ('STORE', 'UPDATE'):
                writers.append(prog['program'])
            if prog['operation'] == 'FIND':
                searchers.append(prog['program'])

    lines.append(f"## 2. Where This Field Is Read")
    if readers:
        for p in sorted(set(readers)):
            mod = graph['modules'].get(p, {})
            lines.append(f"- **{p}** ({mod.get('type','unknown')}) — {generate_functional_description(mod, graph)[:80]}")
    else:
        lines.append(f"No read references found for this field.")
    lines.append(f"")

    lines.append(f"## 3. Where This Field Is Written")
    if writers:
        for p in sorted(set(writers)):
            mod = graph['modules'].get(p, {})
            lines.append(f"- **{p}** ({mod.get('type','unknown')}) — {generate_functional_description(mod, graph)[:80]}")
    else:
        lines.append(f"No write references found for this field.")
    lines.append(f"")

    lines.append(f"## 4. Where This Field Is Used as Search Key")
    if searchers:
        for p in sorted(set(searchers)):
            lines.append(f"- **{p}** — uses this field to locate records")
    else:
        lines.append(f"Not used as a search key.")
    lines.append(f"")

    # Trace upstream from each writer to find data origin
    lines.append(f"## 5. Data Origin Trace")
    lines.append(f"")
    if writers:
        for writer in sorted(set(writers)):
            upstream = trace_upstream(graph, writer)
            if upstream and upstream[0].get('callers'):
                lines.append(f"**{writer}** receives data from:")
                for caller in upstream[0]['callers']:
                    lines.append(f"  - {caller}")
            else:
                lines.append(f"**{writer}** is a top-level entry (data originates here)")
        lines.append(f"")

    return '\n'.join(lines)


def _render_tree(lines, node, graph, indent=0):
    """Render a functional tree with indentation."""
    prefix = '  ' * indent
    connector = '├── ' if indent > 0 else ''
    mod = graph['modules'].get(node['name'], {})

    # Create functional label (non-technical)
    name = node['name']
    mod_type = mod.get('type', node.get('type', 'unknown'))
    ddms = set(a['ddm'] for a in mod.get('db_access', [])) if mod else set()
    maps = mod.get('maps', []) if mod else []

    label = f"{name}"
    if maps:
        label += f" [Screen: {', '.join(maps[:2])}]"
    if ddms:
        label += f" [Data: {', '.join(sorted(ddms)[:3])}]"

    lines.append(f"{prefix}{connector}{label}")

    for child in node.get('children', []):
        _render_tree(lines, child, graph, indent + 1)


# ── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='MFREA FRD Generator')
    parser.add_argument('--graph', required=True, help='Path to graph.json from scanner')
    parser.add_argument('--program', help='Program name to generate FRD for')
    parser.add_argument('--ddm', help='DDM/Adabas file name to generate FRD for')
    parser.add_argument('--field', help='Field name (requires --ddm)')
    parser.add_argument('--output', default='frd_output.md', help='Output markdown file')
    args = parser.parse_args()

    graph = load_graph(args.graph)

    if args.field and args.ddm:
        content = generate_frd_for_field(graph, args.ddm.upper(), args.field.upper())
    elif args.ddm:
        content = generate_frd_for_ddm(graph, args.ddm.upper())
    elif args.program:
        content = generate_frd_for_program(graph, args.program.upper())
    else:
        print("ERROR: Specify --program, --ddm, or --ddm + --field")
        return

    with open(args.output, 'w') as f:
        f.write(content)
    print(f"FRD generated: {args.output}")


if __name__ == '__main__':
    main()
