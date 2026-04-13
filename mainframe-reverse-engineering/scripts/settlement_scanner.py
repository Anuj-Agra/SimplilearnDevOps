#!/usr/bin/env python3
"""
Settlement Instruction Override Scanner
========================================
Analyses 52K+ Natural modules and 13K+ JCL to find fields where:
  - The value is NOT received from the upstream caller
  - The value IS overridden/enriched from reference tables or Adabas files
  - The override has business meaning (settlement instruction for cash & securities)

Builds a knowledge graph of:
  Field → Override Source → Business Rule → Downstream Consumer

Usage:
  python settlement_scanner.py \\
    --natural /path/to/natural \\
    --jcl /path/to/jcl \\
    --output settlement_knowledge_graph.json \\
    --workers 8
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
# SETTLEMENT DOMAIN KEYWORDS
# Fields and terms commonly found in settlement instruction
# processing for cash and securities
# ═══════════════════════════════════════════════════════════════

SETTLEMENT_KEYWORDS = {
    # Settlement instruction fields
    'SETTLE', 'SETTLEMENT', 'SSI', 'INSTRUCT', 'INSTRUCTION',
    'CLEARING', 'CUSTODIAN', 'DEPOSITORY', 'SUBCUSTODIAN',
    'AGENT', 'CORRESPONDENT', 'INTERMEDIARY', 'BENEFICIARY',
    'ACCOUNT', 'ACCT', 'ACC-', 'NOSTRO', 'VOSTRO', 'LORO',
    # Cash settlement
    'CASH', 'PAYMENT', 'PAY-', 'AMOUNT', 'CURRENCY', 'CCY',
    'SWIFT', 'BIC', 'IBAN', 'ROUTING', 'SORT-CODE', 'ABA',
    'FED-WIRE', 'FEDWIRE', 'CHIPS', 'TARGET', 'RTGS',
    'CREDIT', 'DEBIT', 'TRANSFER', 'REMITTANCE',
    # Securities settlement
    'SECURITY', 'SECURITIES', 'ISIN', 'CUSIP', 'SEDOL',
    'PLACE-OF-SETTLE', 'PSET', 'MARKET', 'EXCHANGE',
    'CSD', 'DTCC', 'EUROCLEAR', 'CLEARSTREAM', 'CREST',
    'DELIVERY', 'RECEIVE', 'DVP', 'RVP', 'FOP', 'DWP',
    'TRADE', 'POSITION', 'HOLDING', 'SAFEKEEP', 'CUSTODY',
    # Reference data
    'COUNTRY', 'PARTY', 'COUNTERPARTY', 'CPTY', 'BROKER',
    'STATUS', 'TYPE', 'CODE', 'INDICATOR', 'IND-', 'FLAG',
    'DEFAULT', 'OVERRIDE', 'ENRICH', 'LOOKUP', 'DERIVE',
    'STANDING', 'INSTRUCTION', 'TEMPLATE', 'RULE',
}

# Terms indicating a field override (not from upstream)
OVERRIDE_INDICATORS = {
    'DEFAULT', 'OVERRIDE', 'ENRICH', 'LOOKUP', 'DERIVE',
    'POPULATE', 'SET-UP', 'SETUP', 'STANDING', 'TEMPLATE',
    'FALLBACK', 'REPLACE', 'SUBSTITUTE', 'APPLY',
}

# ═══════════════════════════════════════════════════════════════
# REGEX PATTERNS
# ═══════════════════════════════════════════════════════════════

# DEFINE DATA — VIEW OF (DDM reference)
RE_VIEW = re.compile(
    r"^\s*\d+\s+([A-Za-z0-9_#@$-]+)\s+VIEW\s+OF\s+([A-Za-z0-9_#@$-]+)",
    re.IGNORECASE | re.MULTILINE
)

# DEFINE DATA — field with format
RE_DEFINE_FIELD = re.compile(
    r"^\s*(\d+)\s+([#A-Za-z0-9_@$-]+)\s+\(([ANPBCDTL][\d.]*)\)",
    re.MULTILINE
)

# DEFINE DATA PARAMETER (incoming fields from caller)
RE_PARAMETER_BLOCK = re.compile(
    r"PARAMETER(.*?)(?=LOCAL|GLOBAL|END-DEFINE)",
    re.IGNORECASE | re.DOTALL
)

# CALLNAT with params
RE_CALLNAT = re.compile(
    r"CALLNAT\s+'([A-Za-z0-9_#@$-]+)'\s*(.*?)(?:\n|$)", re.IGNORECASE
)

# Assignment: MOVE source TO target
RE_MOVE = re.compile(
    r"MOVE\s+(.+?)\s+TO\s+([A-Za-z0-9_#@$.-]+)", re.IGNORECASE
)

# Assignment: target := source
RE_ASSIGN = re.compile(
    r"([A-Za-z0-9_#@$.-]+)\s*:=\s*(.+?)(?:\n|$)", re.IGNORECASE
)

# COMPUTE
RE_COMPUTE = re.compile(
    r"COMPUTE\s+([A-Za-z0-9_#@$.-]+)\s*=\s*(.+?)(?:\n|$)", re.IGNORECASE
)

# COMPRESS INTO
RE_COMPRESS = re.compile(
    r"COMPRESS\s+(.+?)\s+INTO\s+([A-Za-z0-9_#@$.-]+)", re.IGNORECASE
)

# Database READ/FIND (populates fields from Adabas)
RE_DB_READ = re.compile(
    r"\b(READ|FIND|GET|HISTOGRAM)\s+(?:\(\d+\)\s+)?([A-Za-z0-9_#@$-]+)",
    re.IGNORECASE
)

# Database STORE/UPDATE (writes fields to Adabas)
RE_DB_WRITE = re.compile(
    r"\b(STORE|UPDATE)\s+([A-Za-z0-9_#@$-]+)", re.IGNORECASE
)

# FIND/READ WITH (search criteria — reveals lookup key)
RE_SEARCH_CRIT = re.compile(
    r"(?:WITH|WHERE|BY)\s+([A-Za-z0-9_#@$-]+)\s*=\s*([A-Za-z0-9_#@$.'\"*]+)",
    re.IGNORECASE
)

# IF condition (reveals business rules)
RE_IF_CONDITION = re.compile(
    r"IF\s+([A-Za-z0-9_#@$.-]+)\s*([=<>!]+|EQ|NE|LT|GT|LE|GE|NOT\s*=)\s*(.+?)(?:\n|THEN|$)",
    re.IGNORECASE
)

# DECIDE ON EVERY VALUE
RE_DECIDE = re.compile(
    r"DECIDE\s+ON\s+EVERY\s+VALUE\s+OF\s+([A-Za-z0-9_#@$.-]+)",
    re.IGNORECASE
)

# MAP interactions
RE_MAP = re.compile(
    r"(?:INPUT|WRITE|REINPUT)\s+(?:USING\s+)?MAP\s+'([A-Za-z0-9_#@$-]+)'",
    re.IGNORECASE
)

# System variables
RE_SYSVAR = re.compile(r'\*[A-Z][A-Z0-9-]+')

# Natural file extensions
NATURAL_EXTENSIONS = {
    '.nsp', '.nsn', '.nsl', '.nsg', '.nsa', '.nsh',
    '.nsm', '.nsc', '.nss', '.ns7', '.ns4', '.nat', '.txt', '.src',
}


# ═══════════════════════════════════════════════════════════════
# OVERRIDE DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════

def is_settlement_related(field_name):
    """Check if a field name relates to settlement instruction domain."""
    upper = field_name.upper()
    return any(kw in upper for kw in SETTLEMENT_KEYWORDS)


def classify_override_source(source_expr, views, program_context):
    """Classify WHERE a value comes from and whether it's an override."""
    source = source_expr.strip().upper()

    # System variable
    if source.startswith('*'):
        return {
            'category': 'SYSTEM-VARIABLE',
            'source': source,
            'is_override': True,
            'override_type': 'system-derived',
            'business_meaning': f'Value set by system ({source})',
        }

    # Literal/hardcoded
    if source.startswith("'") or source.startswith('"') or re.match(r'^-?\d+\.?\d*$', source):
        return {
            'category': 'LITERAL',
            'source': source.strip("'\""),
            'is_override': True,
            'override_type': 'hardcoded-default',
            'business_meaning': f'Default value: {source}',
        }

    # Constants
    if source in ('SPACES', 'ZEROS', 'ZERO', 'BLANK', 'TRUE', 'FALSE'):
        return {
            'category': 'CONSTANT',
            'source': source,
            'is_override': True,
            'override_type': 'reset-to-default',
            'business_meaning': f'Field cleared to {source}',
        }

    # Another field — is it from a VIEW (i.e., from Adabas/ref table)?
    # Check if source field belongs to any VIEW (= read from database)
    for alias, ddm in views.items():
        if source.startswith(alias + '.') or source == alias:
            return {
                'category': 'DATABASE-FIELD',
                'source': f'{ddm}.{source}',
                'ddm': ddm,
                'is_override': True,
                'override_type': 'enriched-from-database',
                'business_meaning': f'Value looked up from {ddm}',
            }

    # Check if source field name contains override indicators
    if any(ind in source for ind in OVERRIDE_INDICATORS):
        return {
            'category': 'OVERRIDE-FIELD',
            'source': source,
            'is_override': True,
            'override_type': 'explicit-override',
            'business_meaning': f'Explicitly overridden via {source}',
        }

    # Check if source field is settlement-related (cross-reference enrichment)
    if is_settlement_related(source):
        return {
            'category': 'SETTLEMENT-FIELD',
            'source': source,
            'is_override': False,
            'override_type': 'field-copy',
            'business_meaning': f'Copied from settlement field {source}',
        }

    # Expression with operators (calculated)
    if any(op in source for op in ['+', '-', '*', '/', '**']):
        return {
            'category': 'CALCULATED',
            'source': source_expr.strip(),
            'is_override': True,
            'override_type': 'calculated-value',
            'business_meaning': 'Value derived from calculation',
        }

    # Plain field copy (could be from parameter = upstream)
    return {
        'category': 'FIELD-COPY',
        'source': source,
        'is_override': False,
        'override_type': 'upstream-passthrough',
        'business_meaning': f'Value received from {source} (likely upstream)',
    }


# ═══════════════════════════════════════════════════════════════
# PROGRAM ANALYZER
# ═══════════════════════════════════════════════════════════════

def analyze_program(filepath):
    """Analyse a single Natural program for settlement field overrides."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return None

    name = Path(filepath).stem.upper()
    lib = _infer_library(filepath)

    # Strip comments
    lines = content.split('\n')
    clean_lines = [l for l in lines if not l.strip().startswith('*') and not l.strip().startswith('/*')]
    clean = '\n'.join(clean_lines)

    # Extract VIEWS (DDM references)
    views = {}
    for m in RE_VIEW.finditer(clean):
        views[m.group(1).upper()] = m.group(2).upper()

    # Extract PARAMETER fields (these come from upstream)
    param_fields = set()
    pm = RE_PARAMETER_BLOCK.search(clean)
    if pm:
        for fm in RE_DEFINE_FIELD.finditer(pm.group(1)):
            param_fields.add(fm.group(2).upper())

    # Extract all defined fields
    all_fields = {}
    for fm in RE_DEFINE_FIELD.finditer(clean):
        fname = fm.group(2).upper()
        all_fields[fname] = {
            'format': fm.group(3).upper(),
            'level': int(fm.group(1)),
            'is_parameter': fname in param_fields,
            'is_settlement': is_settlement_related(fname),
        }

    # Tag VIEW fields with their DDM
    for alias, ddm in views.items():
        pattern = re.compile(
            rf"^\s*\d+\s+{re.escape(alias)}\s+VIEW\s+OF\s+{re.escape(ddm)}\s*$(.*?)(?=^\s*\d+\s+\S+\s+VIEW|\bEND-DEFINE\b)",
            re.IGNORECASE | re.MULTILINE | re.DOTALL
        )
        vm = pattern.search(clean)
        if vm:
            for line in vm.group(1).split('\n'):
                fm = re.match(r'^\s*\d+\s+([A-Za-z0-9_#@$-]+)\s*$', line)
                if fm:
                    vfield = fm.group(1).upper()
                    if vfield in all_fields:
                        all_fields[vfield]['ddm'] = ddm
                        all_fields[vfield]['scope'] = 'VIEW'

    # ── Track all assignments ──
    overrides = []
    all_assignments = []

    def process_assignment(target, source_expr, context_type):
        target = target.upper().strip()
        classification = classify_override_source(source_expr, views, name)

        entry = {
            'target_field': target,
            'source_expression': source_expr.strip(),
            'context': context_type,
            'program': name,
            'library': lib,
            'is_settlement_field': is_settlement_related(target),
            **classification,
        }

        all_assignments.append(entry)

        # Is this an override? (value NOT from upstream parameter)
        if classification['is_override'] and target not in param_fields:
            overrides.append(entry)
        # Or: upstream parameter is being OVERWRITTEN by a non-parameter source
        elif target in param_fields and classification['is_override']:
            entry['override_type'] = 'upstream-overridden'
            entry['business_meaning'] = f'Upstream value for {target} is OVERRIDDEN by {classification["source"]}'
            entry['is_override'] = True
            overrides.append(entry)

    # MOVE source TO target
    for m in RE_MOVE.finditer(clean):
        process_assignment(m.group(2), m.group(1), 'MOVE')

    # target := source
    for m in RE_ASSIGN.finditer(clean):
        process_assignment(m.group(1), m.group(2), 'ASSIGN')

    # COMPUTE target = expression
    for m in RE_COMPUTE.finditer(clean):
        process_assignment(m.group(1), m.group(2), 'COMPUTE')

    # COMPRESS sources INTO target
    for m in RE_COMPRESS.finditer(clean):
        process_assignment(m.group(2), m.group(1), 'COMPRESS')

    # Database READ/FIND (populates VIEW fields = override from Adabas)
    db_reads = []
    for m in RE_DB_READ.finditer(clean):
        op = m.group(1).upper()
        view_ref = m.group(2).upper()
        ddm = views.get(view_ref, view_ref)

        # Extract search criteria (reveals the lookup key)
        pos = m.start()
        context = clean[pos:pos+400]
        criteria = []
        for cm in RE_SEARCH_CRIT.finditer(context):
            criteria.append({'field': cm.group(1).upper(), 'value': cm.group(2).strip()})

        db_reads.append({
            'operation': op,
            'view': view_ref,
            'ddm': ddm,
            'criteria': criteria,
            'program': name,
        })

        # All VIEW fields under this alias are now populated from Adabas
        for fname, finfo in all_fields.items():
            if finfo.get('ddm') == ddm:
                override_entry = {
                    'target_field': fname,
                    'source_expression': f'{ddm}.{fname}',
                    'context': f'{op} {view_ref}',
                    'program': name,
                    'library': lib,
                    'is_settlement_field': is_settlement_related(fname),
                    'category': 'DATABASE-READ',
                    'source': f'{ddm}.{fname}',
                    'ddm': ddm,
                    'is_override': True,
                    'override_type': 'enriched-from-database',
                    'business_meaning': f'Value read from {ddm} (lookup key: {criteria[0]["field"] if criteria else "ISN"})',
                    'lookup_criteria': criteria,
                }
                overrides.append(override_entry)

    # Database STORE/UPDATE
    db_writes = []
    for m in RE_DB_WRITE.finditer(clean):
        view_ref = m.group(2).upper()
        ddm = views.get(view_ref, view_ref)
        db_writes.append({
            'operation': m.group(1).upper(),
            'view': view_ref,
            'ddm': ddm,
            'program': name,
        })

    # Extract business rules (IF conditions on settlement fields)
    business_rules = []
    for m in RE_IF_CONDITION.finditer(clean):
        field = m.group(1).upper()
        operator = m.group(2).strip()
        value = m.group(3).strip()
        if is_settlement_related(field):
            business_rules.append({
                'field': field,
                'condition': f'{field} {operator} {value}',
                'program': name,
                'type': 'conditional-logic',
            })

    for m in RE_DECIDE.finditer(clean):
        field = m.group(1).upper()
        if is_settlement_related(field):
            business_rules.append({
                'field': field,
                'condition': f'DECIDE ON {field}',
                'program': name,
                'type': 'value-routing',
            })

    # Extract CALLNAT (downstream calls)
    calls = []
    for m in RE_CALLNAT.finditer(clean):
        calls.append({
            'target': m.group(1).upper(),
            'params': m.group(2).strip(),
        })

    # Maps
    maps = [m.group(1).upper() for m in RE_MAP.finditer(clean)]

    # Settlement relevance score (higher = more relevant)
    settlement_field_count = sum(1 for f in all_fields.values() if f.get('is_settlement'))
    override_count = len([o for o in overrides if o.get('is_settlement_field')])

    return {
        'program': name,
        'library': lib,
        'filepath': str(filepath),
        'line_count': len(lines),
        'settlement_relevance': settlement_field_count + override_count * 2,
        'fields': all_fields,
        'parameter_fields': list(param_fields),
        'overrides': overrides,
        'settlement_overrides': [o for o in overrides if o.get('is_settlement_field')],
        'db_reads': db_reads,
        'db_writes': db_writes,
        'business_rules': business_rules,
        'calls': calls,
        'maps': maps,
        'views': views,
    }


def _infer_library(filepath):
    parts = Path(filepath).parts
    for i, part in enumerate(parts):
        if part.lower() in ('natural', 'jcl', 'cobol', 'maps', 'ddm'):
            if i > 0:
                return parts[i-1].upper()
    return Path(filepath).parent.name.upper()


# ═══════════════════════════════════════════════════════════════
# KNOWLEDGE GRAPH BUILDER
# ═══════════════════════════════════════════════════════════════

def build_knowledge_graph(all_results):
    """Build the settlement instruction knowledge graph."""

    # Node types: PROGRAM, FIELD, DDM, REF-TABLE, BUSINESS-RULE, SCREEN
    nodes = {}
    edges = []

    # Index: field → programs that override it
    field_override_index = defaultdict(list)
    # Index: DDM → fields read from it
    ddm_field_index = defaultdict(set)
    # Index: program → programs it calls
    call_graph = defaultdict(list)
    # Reverse call graph
    called_by = defaultdict(list)

    for result in all_results:
        if not result or result['settlement_relevance'] == 0:
            continue

        pgm = result['program']

        # Program node
        nodes[f'PGM:{pgm}'] = {
            'id': f'PGM:{pgm}',
            'type': 'PROGRAM',
            'name': pgm,
            'library': result['library'],
            'settlement_relevance': result['settlement_relevance'],
            'override_count': len(result['settlement_overrides']),
            'maps': result['maps'],
        }

        # Call graph
        for call in result['calls']:
            call_graph[pgm].append(call['target'])
            called_by[call['target']].append(pgm)

        # DDM nodes
        for alias, ddm in result['views'].items():
            if f'DDM:{ddm}' not in nodes:
                nodes[f'DDM:{ddm}'] = {
                    'id': f'DDM:{ddm}',
                    'type': 'DDM',
                    'name': ddm,
                    'accessed_by': [],
                    'fields_used': set(),
                }
            nodes[f'DDM:{ddm}']['accessed_by'].append(pgm)

        # Process overrides
        for override in result['settlement_overrides']:
            field = override['target_field']
            field_id = f'FIELD:{field}'

            # Field node
            if field_id not in nodes:
                nodes[field_id] = {
                    'id': field_id,
                    'type': 'FIELD',
                    'name': field,
                    'overridden_in': [],
                    'override_sources': [],
                    'business_rules': [],
                    'displayed_on': [],
                }

            nodes[field_id]['overridden_in'].append(pgm)
            nodes[field_id]['override_sources'].append({
                'program': pgm,
                'source': override['source'],
                'override_type': override['override_type'],
                'category': override['category'],
                'business_meaning': override['business_meaning'],
                'lookup_criteria': override.get('lookup_criteria', []),
            })

            field_override_index[field].append(override)

            # Edge: PROGRAM --overrides--> FIELD
            edges.append({
                'from': f'PGM:{pgm}',
                'to': field_id,
                'type': 'OVERRIDES',
                'override_type': override['override_type'],
                'source': override['source'],
            })

            # Edge: DDM --provides--> FIELD (if from database)
            if override.get('ddm'):
                ddm = override['ddm']
                ddm_field_index[ddm].add(field)
                edges.append({
                    'from': f'DDM:{ddm}',
                    'to': field_id,
                    'type': 'PROVIDES',
                    'via': f'PGM:{pgm}',
                })

        # Business rules
        for rule in result['business_rules']:
            rule_id = f'RULE:{pgm}:{rule["field"]}'
            nodes[rule_id] = {
                'id': rule_id,
                'type': 'BUSINESS-RULE',
                'name': f'{rule["field"]} check in {pgm}',
                'condition': rule['condition'],
                'program': pgm,
                'field': rule['field'],
            }
            edges.append({
                'from': f'FIELD:{rule["field"]}',
                'to': rule_id,
                'type': 'VALIDATED-BY',
            })

        # Screen/Map nodes
        for map_name in result['maps']:
            map_id = f'MAP:{map_name}'
            if map_id not in nodes:
                nodes[map_id] = {
                    'id': map_id,
                    'type': 'SCREEN',
                    'name': map_name,
                    'used_by': [],
                }
            nodes[map_id]['used_by'].append(pgm)

    # Convert sets to lists for JSON
    for nid in nodes:
        for key in nodes[nid]:
            if isinstance(nodes[nid][key], set):
                nodes[nid][key] = sorted(nodes[nid][key])

    # Build override summary (the key deliverable)
    override_summary = {}
    for field, overrides in field_override_index.items():
        sources_by_type = defaultdict(list)
        for o in overrides:
            sources_by_type[o['override_type']].append({
                'program': o['program'],
                'source': o['source'],
                'business_meaning': o['business_meaning'],
                'category': o['category'],
            })

        override_summary[field] = {
            'field': field,
            'total_overrides': len(overrides),
            'programs_overriding': sorted(set(o['program'] for o in overrides)),
            'override_types': dict(sources_by_type),
            'is_from_upstream': False,
            'primary_source': _determine_primary_source(overrides),
        }

    # Stats
    stats = {
        'total_programs_scanned': len(all_results),
        'settlement_relevant_programs': sum(1 for r in all_results if r and r['settlement_relevance'] > 0),
        'total_settlement_overrides': sum(len(r['settlement_overrides']) for r in all_results if r),
        'unique_overridden_fields': len(field_override_index),
        'unique_ddms_used': len(ddm_field_index),
        'total_business_rules': sum(len(r['business_rules']) for r in all_results if r),
        'total_nodes': len(nodes),
        'total_edges': len(edges),
    }

    return {
        'metadata': {
            'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'domain': 'Settlement Instructions — Cash & Securities',
            'stats': stats,
        },
        'nodes': nodes,
        'edges': edges,
        'override_summary': override_summary,
        'field_override_index': {k: [_serialize(o) for o in v] for k, v in field_override_index.items()},
        'ddm_field_index': {k: sorted(v) for k, v in ddm_field_index.items()},
        'call_graph': dict(call_graph),
        'called_by': dict(called_by),
        'programs': {r['program']: {
            'program': r['program'],
            'library': r['library'],
            'settlement_relevance': r['settlement_relevance'],
            'override_count': len(r['settlement_overrides']),
            'parameter_fields': r['parameter_fields'],
            'maps': r['maps'],
            'views': r['views'],
            'calls': [c['target'] for c in r['calls']],
        } for r in all_results if r and r['settlement_relevance'] > 0},
    }


def _determine_primary_source(overrides):
    """Determine the primary source of a field's value."""
    # Priority: database > calculated > literal > system > field-copy
    for cat in ['DATABASE-READ', 'DATABASE-FIELD', 'CALCULATED', 'LITERAL', 'SYSTEM-VARIABLE', 'OVERRIDE-FIELD']:
        matches = [o for o in overrides if o.get('category') == cat]
        if matches:
            return {
                'category': cat,
                'source': matches[0]['source'],
                'business_meaning': matches[0]['business_meaning'],
                'programs': sorted(set(m['program'] for m in matches)),
            }
    return {'category': 'UNKNOWN', 'source': '', 'business_meaning': 'Source could not be determined'}


def _serialize(obj):
    """Make an object JSON-serializable."""
    if isinstance(obj, set):
        return sorted(obj)
    return obj


# ═══════════════════════════════════════════════════════════════
# FRD GENERATOR (non-technical)
# ═══════════════════════════════════════════════════════════════

def generate_settlement_frd(knowledge_graph):
    """Generate a non-technical Functional Requirements Document."""
    kg = knowledge_graph
    stats = kg['metadata']['stats']
    overrides = kg['override_summary']

    lines = []
    lines.append("# Functional Requirements Document")
    lines.append("# Settlement Instruction Processing — Cash & Securities")
    lines.append("")
    lines.append(f"**Generated:** {kg['metadata']['generated']}")
    lines.append(f"**Domain:** {kg['metadata']['domain']}")
    lines.append(f"**Programs Analysed:** {stats['settlement_relevant_programs']:,} (settlement-relevant)")
    lines.append(f"**Fields with Override Logic:** {stats['unique_overridden_fields']:,}")
    lines.append("")

    # Executive Summary
    lines.append("## 1. Executive Summary")
    lines.append("")
    lines.append("This document describes the settlement instruction processing system's data enrichment logic. "
                 "When a settlement instruction is received, certain fields are NOT passed through from the "
                 "upstream source. Instead, the system overrides or enriches these fields by looking up values "
                 "from reference tables and standing data stored in the database.")
    lines.append("")
    lines.append(f"The analysis identified **{stats['unique_overridden_fields']}** fields where values are "
                 f"derived from internal reference data rather than received from upstream. These overrides "
                 f"occur across **{stats['settlement_relevant_programs']}** programs and reference "
                 f"**{stats['unique_ddms_used']}** database tables.")
    lines.append("")

    # Group overrides by business category
    cash_fields = {k: v for k, v in overrides.items()
                   if any(kw in k.upper() for kw in ['CASH', 'PAYMENT', 'PAY-', 'AMOUNT', 'CCY', 'CURRENCY',
                                                      'BIC', 'SWIFT', 'IBAN', 'ROUTING', 'SORT-CODE',
                                                      'NOSTRO', 'VOSTRO', 'CORRESPONDENT', 'REMIT'])}
    sec_fields = {k: v for k, v in overrides.items()
                  if any(kw in k.upper() for kw in ['SECURITY', 'SECURITIES', 'ISIN', 'CUSIP', 'SEDOL',
                                                     'PSET', 'CSD', 'DELIVERY', 'DVP', 'FOP', 'CUSTODY',
                                                     'SAFEKEEP', 'DEPOSITORY', 'CLEARSTREAM', 'EUROCLEAR'])}
    ssi_fields = {k: v for k, v in overrides.items()
                  if any(kw in k.upper() for kw in ['SSI', 'SETTLE', 'INSTRUCTION', 'STANDING',
                                                     'AGENT', 'CUSTODIAN', 'SUBCUSTODIAN', 'INTERMEDIARY',
                                                     'BENEFICIARY', 'TEMPLATE', 'DEFAULT'])}
    other_fields = {k: v for k, v in overrides.items()
                    if k not in cash_fields and k not in sec_fields and k not in ssi_fields}

    # Section 2: Cash Settlement Overrides
    lines.append("## 2. Cash Settlement — Overridden Fields")
    lines.append("")
    if cash_fields:
        lines.append("These fields relate to cash payment routing. Their values are NOT received from the "
                     "trade instruction but are looked up from standing payment instructions and reference data.")
        lines.append("")
        lines.append("| Field | What It Represents | Where Value Comes From | Business Rule |")
        lines.append("|---|---|---|---|")
        for field, info in sorted(cash_fields.items()):
            ps = info['primary_source']
            lines.append(f"| {field} | {_infer_business_name(field)} | {ps['business_meaning']} | "
                        f"Looked up in {', '.join(ps.get('programs', [])[:3])} |")
        lines.append("")
    else:
        lines.append("No cash settlement override fields detected.")
        lines.append("")

    # Section 3: Securities Settlement Overrides
    lines.append("## 3. Securities Settlement — Overridden Fields")
    lines.append("")
    if sec_fields:
        lines.append("These fields relate to securities delivery and custody. Their values are derived from "
                     "market rules, depository standing instructions, and securities reference data.")
        lines.append("")
        lines.append("| Field | What It Represents | Where Value Comes From | Business Rule |")
        lines.append("|---|---|---|---|")
        for field, info in sorted(sec_fields.items()):
            ps = info['primary_source']
            lines.append(f"| {field} | {_infer_business_name(field)} | {ps['business_meaning']} | "
                        f"Looked up in {', '.join(ps.get('programs', [])[:3])} |")
        lines.append("")
    else:
        lines.append("No securities settlement override fields detected.")
        lines.append("")

    # Section 4: SSI / Standing Instructions
    lines.append("## 4. Standing Settlement Instructions (SSI) — Overridden Fields")
    lines.append("")
    if ssi_fields:
        lines.append("These fields represent standing settlement instructions — pre-configured routing "
                     "information that the system applies automatically based on counterparty, market, "
                     "and instrument type. They replace any upstream values with the correct standing instruction.")
        lines.append("")
        lines.append("| Field | What It Represents | Where Value Comes From | Override Type |")
        lines.append("|---|---|---|---|")
        for field, info in sorted(ssi_fields.items()):
            ps = info['primary_source']
            otype = list(info['override_types'].keys())[0] if info['override_types'] else 'unknown'
            lines.append(f"| {field} | {_infer_business_name(field)} | {ps['business_meaning']} | {otype} |")
        lines.append("")
    else:
        lines.append("No SSI override fields detected.")
        lines.append("")

    # Section 5: Other Overridden Fields
    if other_fields:
        lines.append("## 5. Other Overridden Fields")
        lines.append("")
        lines.append("| Field | Where Value Comes From | Programs | Override Type |")
        lines.append("|---|---|---|---|")
        for field, info in sorted(other_fields.items()):
            ps = info['primary_source']
            lines.append(f"| {field} | {ps['business_meaning']} | "
                        f"{', '.join(info['programs_overriding'][:3])} | {ps['category']} |")
        lines.append("")

    # Section 6: Data Sources (reference tables)
    lines.append("## 6. Reference Data Sources")
    lines.append("")
    lines.append("The following database tables provide the override/enrichment values:")
    lines.append("")
    lines.append("| Database Table (DDM) | Fields Provided | Used By Programs |")
    lines.append("|---|---|---|")
    for ddm, fields in sorted(kg['ddm_field_index'].items()):
        ddm_node = kg['nodes'].get(f'DDM:{ddm}', {})
        progs = ddm_node.get('accessed_by', [])
        lines.append(f"| {ddm} | {', '.join(sorted(fields)[:6])} | {', '.join(progs[:4])} |")
    lines.append("")

    # Section 7: Business Rules
    lines.append("## 7. Business Rules (Conditions That Control Overrides)")
    lines.append("")
    rules = [n for n in kg['nodes'].values() if n['type'] == 'BUSINESS-RULE']
    if rules:
        lines.append("These conditions determine WHEN and HOW override values are applied:")
        lines.append("")
        lines.append("| Rule | Field | Condition | Program |")
        lines.append("|---|---|---|---|")
        for i, rule in enumerate(rules[:50], 1):
            lines.append(f"| BR-{i:03d} | {rule['field']} | {rule['condition']} | {rule['program']} |")
        lines.append("")
    else:
        lines.append("No conditional business rules detected on settlement fields.")
        lines.append("")

    # Section 8: Process Flow Summary
    lines.append("## 8. Settlement Instruction Processing Flow")
    lines.append("")
    lines.append("The system processes settlement instructions through these stages:")
    lines.append("")
    lines.append("1. **Receive instruction** — Trade or payment instruction arrives from upstream")
    lines.append("2. **Identify counterparty and market** — Determine which standing instructions apply")
    lines.append("3. **Look up reference data** — Query standing settlement instructions (SSI), "
                 "counterparty details, market rules, and custodian information from reference tables")
    lines.append("4. **Override/enrich fields** — Replace upstream values with standing instruction values "
                 "for fields like payment agent, custodian, BIC codes, account numbers")
    lines.append("5. **Validate** — Check that all required fields are populated and consistent")
    lines.append("6. **Route** — Send the enriched instruction to the appropriate settlement system "
                 "(SWIFT, clearing house, CSD)")
    lines.append("")

    # Section 9: Key Findings
    lines.append("## 9. Key Findings")
    lines.append("")
    lines.append(f"- **{stats['unique_overridden_fields']}** fields have their values overridden "
                 f"(not received from upstream)")
    lines.append(f"- **{stats['unique_ddms_used']}** reference tables are used as override sources")
    lines.append(f"- **{stats['total_business_rules']}** business rules control the override logic")
    lines.append(f"- **{stats['settlement_relevant_programs']}** programs participate in the "
                 f"settlement enrichment process")
    lines.append("")

    # Identify highest-risk fields (most overrides = most complex)
    top_fields = sorted(overrides.items(), key=lambda x: x[1]['total_overrides'], reverse=True)[:10]
    if top_fields:
        lines.append("**Highest complexity fields** (most override sources):")
        lines.append("")
        for field, info in top_fields:
            lines.append(f"- **{field}** — overridden in {info['total_overrides']} places "
                        f"across {len(info['programs_overriding'])} programs")
        lines.append("")

    return '\n'.join(lines)


def _infer_business_name(field):
    """Infer a non-technical business name from a field name."""
    f = field.upper().replace('#', '').replace('-', ' ').replace('_', ' ')
    mappings = {
        'BIC': 'Bank identifier code (SWIFT)',
        'IBAN': 'International bank account number',
        'SWIFT': 'SWIFT code',
        'NOSTRO': 'Our account at their bank',
        'VOSTRO': 'Their account at our bank',
        'CUSTODIAN': 'Securities custodian bank',
        'SUBCUSTODIAN': 'Local sub-custodian',
        'SSI': 'Standing settlement instruction',
        'PSET': 'Place of settlement',
        'CSD': 'Central securities depository',
        'DVP': 'Delivery versus payment',
        'FOP': 'Free of payment delivery',
        'CCY': 'Currency code',
        'ISIN': 'International securities identifier',
        'CUSIP': 'US securities identifier',
        'SEDOL': 'UK securities identifier',
        'CPTY': 'Counterparty',
    }
    for key, desc in mappings.items():
        if key in field.upper():
            return desc
    return f.title().strip()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def scan_files(dir_path, max_workers=8):
    dir_path = Path(dir_path)
    files = []
    for root, dirs, filenames in os.walk(dir_path):
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in NATURAL_EXTENSIONS or not ext:
                files.append(os.path.join(root, fname))

    total = len(files)
    print(f"Scanning {total:,} files...")

    results = []
    processed = 0
    if total > 500 and max_workers > 1:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(analyze_program, fp): fp for fp in files}
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
            r = analyze_program(fp)
            if r:
                results.append(r)

    print(f"  Done: {len(results):,} programs analysed")
    return results


def main():
    parser = argparse.ArgumentParser(description='Settlement Instruction Override Scanner')
    parser.add_argument('--natural', required=True, help='Path to Natural modules')
    parser.add_argument('--jcl', help='Path to JCL files (optional)')
    parser.add_argument('--output', default='settlement_knowledge_graph.json', help='Output JSON')
    parser.add_argument('--frd', default='Settlement_FRD.md', help='Output FRD markdown')
    parser.add_argument('--workers', type=int, default=8, help='Parallel workers')
    args = parser.parse_args()

    print("=" * 60)
    print("Settlement Instruction Override Scanner")
    print("Domain: Cash & Securities Settlement")
    print("=" * 60)

    start = time.time()

    print(f"\n[1/4] Scanning Natural modules...")
    results = scan_files(args.natural, args.workers)

    if args.jcl:
        print(f"\n[2/4] Scanning JCL files...")
        jcl_results = scan_files(args.jcl, args.workers)
        results.extend(jcl_results)

    print(f"\n[3/4] Building knowledge graph...")
    kg = build_knowledge_graph(results)

    # Write knowledge graph
    with open(args.output, 'w') as f:
        json.dump(kg, f, indent=2, default=str)

    print(f"\n[4/4] Generating FRD...")
    frd = generate_settlement_frd(kg)
    with open(args.frd, 'w') as f:
        f.write(frd)

    elapsed = time.time() - start
    s = kg['metadata']['stats']
    print(f"\n{'=' * 60}")
    print(f"COMPLETE in {elapsed:.1f}s")
    print(f"  Settlement-relevant programs: {s['settlement_relevant_programs']:>6,}")
    print(f"  Fields with overrides:        {s['unique_overridden_fields']:>6,}")
    print(f"  Reference tables used:        {s['unique_ddms_used']:>6,}")
    print(f"  Business rules found:         {s['total_business_rules']:>6,}")
    print(f"  Knowledge graph nodes:        {s['total_nodes']:>6,}")
    print(f"  Knowledge graph edges:        {s['total_edges']:>6,}")
    print(f"  Output: {args.output}")
    print(f"  FRD:    {args.frd}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
