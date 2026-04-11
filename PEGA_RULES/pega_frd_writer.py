#!/usr/bin/env python3
"""
pega_frd_writer.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREA — Functional Requirements Document Writer

Generates a professional Word (.docx) Functional Requirements Document
from the extracted Pega rule inventory, dependency graph, and flow traces.

Pipeline:
  1. Load rules, graph, and flow traces
  2. Group rules into business modules using AI clustering + heuristics
  3. For each module: extract user stories, business rules, data requirements
  4. Call Claude API to write plain-English FRD sections
  5. Assemble and write the .docx using the docx npm package

Usage:
    python pega_frd_writer.py --rules rules_extracted.json
                               --graph rule_graph.json
                               --output FRD_KYCPlatform.docx
                               --system-name "KYC Platform"
                               --version "2.0"
                               --api-key sk-ant-...

    # Without API key (template-only mode):
    python pega_frd_writer.py --rules rules_extracted.json
                               --output FRD_KYCPlatform.docx
                               --no-ai
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

log = logging.getLogger("prea.frd_writer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")

# Optional deps
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ── Module Grouping ──────────────────────────────────────────────────────────

# Heuristic class-name → business module mappings
MODULE_PATTERNS: List[Tuple[str, str]] = [
    (r"(?i)(kyc|know.your.customer|onboard|intake|client.lifecycle)", "KYC & Client Onboarding"),
    (r"(?i)(aml|anti.money|money.launder|suspicious|sar|screen)", "AML & Financial Crime"),
    (r"(?i)(document|doc\b|upload|attachment|evidence|file)", "Document Management"),
    (r"(?i)(risk|score|rating|classify|classify|pep|sanction)", "Risk Classification"),
    (r"(?i)(review|periodic|refresh|renewal|ongoing|monitor)", "Periodic Review & Monitoring"),
    (r"(?i)(report|regulatory|regul|filing|compliance|audit)", "Regulatory Reporting"),
    (r"(?i)(notif|correspond|email|alert|message|communicat)", "Notifications & Correspondence"),
    (r"(?i)(party|client|customer|counterparty|entity|person)", "Client Data Management"),
    (r"(?i)(account|product|entitle|access|privilege)", "Account & Entitlement"),
    (r"(?i)(workflow|task|queue|assignment|work.item|case)", "Workflow & Task Management"),
    (r"(?i)(ui|form|section|harness|portal|screen|display|render)", "User Interface"),
    (r"(?i)(data|transform|map|convert|integrat|connect|api|service)", "Data Integration"),
]


def classify_to_module(rule: Dict) -> str:
    """Classify a rule into a business module using class name and rule name."""
    text = f"{rule.get('pega_class','')} {rule.get('name','')} {rule.get('ruleset','')}"
    for pattern, module in MODULE_PATTERNS:
        if re.search(pattern, text):
            return module
    return "General / Cross-Cutting"


def group_rules_by_module(rules: List[Dict]) -> Dict[str, List[Dict]]:
    """Group rules into business modules."""
    modules: Dict[str, List[Dict]] = defaultdict(list)
    for r in rules:
        module = classify_to_module(r)
        modules[module].append(r)
    return dict(modules)


# ── Business Rule Extraction ─────────────────────────────────────────────────

def extract_business_rules(rules: List[Dict]) -> List[str]:
    """
    Extract business rules from when/validate/decision rules in plain English.
    Returns a list of rule statements.
    """
    statements = []
    for r in rules:
        if r.get("rule_type") in ("When Rule", "Validate Rule", "Decision Table"):
            name = r.get("name", "")
            # Convert camelCase to words
            words = re.sub(r"([A-Z])", r" \1", name).strip()
            statements.append(f"Business rule: {words}")

        for cond in r.get("conditions", []):
            expr = cond.get("expression", "")
            if expr and len(expr) > 5:
                statements.append(f"Condition: {expr}")

        for row in r.get("decision_rows", []):
            result = row.get("result", "")
            conds  = row.get("conditions", {})
            if result and conds:
                cond_str = ", ".join(f"{k}={v}" for k, v in conds.items())
                statements.append(f"When {cond_str} → {result}")

    return statements[:30]   # cap for prompt length


def extract_ui_fields_for_module(rules: List[Dict]) -> List[Dict]:
    """Extract all UI field definitions across rules in a module."""
    all_fields = []
    seen = set()
    for r in rules:
        for field in r.get("ui_fields", []):
            name = field.get("name", "")
            if name and name not in seen:
                seen.add(name)
                all_fields.append(field)
    return all_fields[:50]


def extract_actors_for_module(rules: List[Dict]) -> List[str]:
    """Extract unique actors/work parties from a module's rules."""
    actors = set()
    for r in rules:
        for actor in r.get("actors", []):
            if actor and len(actor) < 60:
                actors.add(actor)
    return sorted(actors)


# ── AI Section Generation ────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are PREA — Pega Reverse Engineering Agent. 
You generate Functional Requirements Documents (FRDs) from extracted Pega rule metadata.

Rules:
- Write ONLY in plain business English. Zero technical jargon (no class names, no attribute paths, 
  no Pega-specific terms like pxWorkPage, pyRuleName, @baseclass, etc.)
- Every requirement must be testable and specific
- Use "the system" for automated steps, named roles for human steps
- Write user stories as: "As a [role], I can [action] so that [benefit]."
- Business rules as: "The system [verb] when [condition]."
- For data fields: state the field name in business English, whether required/optional, and any format constraints
- Keep each section concise — 150-300 words per module overview
- Output valid JSON only, with no preamble or markdown fencing"""

MODULE_PROMPT_TEMPLATE = """Analyse this Pega module and generate FRD content.

Module: {module_name}
Rule count: {rule_count}
Rule types present: {rule_types}
Actors/work parties detected: {actors}
Business rules detected: {business_rules}
UI fields detected: {ui_fields}
Sample rule names: {sample_names}

Generate a JSON object with these exact keys:
{{
  "overview": "2-3 sentence business overview of what this module enables",
  "user_stories": ["As a ... I can ... so that ...", ...],  // 3-6 stories
  "business_rules": ["The system ... when ...", ...],       // 3-8 rules  
  "data_requirements": [
    {{"field": "plain English name", "required": "Yes/No", "format": "constraint", "visible_when": "condition or Always"}}
  ],  // top 5-8 fields
  "error_scenarios": [
    {{"trigger": "what the user does", "message": "what the user sees", "resolution": "what to do"}}
  ]  // 2-4 scenarios
}}"""


def call_claude_for_module(module_name: str, rules: List[Dict], api_key: str) -> Optional[Dict]:
    """Call Claude API to generate FRD content for a module."""
    if not HAS_ANTHROPIC:
        log.warning("anthropic package not installed — using template mode")
        return None

    rule_types = list(set(r.get("rule_type", "") for r in rules))
    actors     = extract_actors_for_module(rules)
    biz_rules  = extract_business_rules(rules)
    ui_fields  = [f.get("name", "") for f in extract_ui_fields_for_module(rules)]
    sample_names = [r.get("name", "") for r in rules[:20]]

    prompt = MODULE_PROMPT_TEMPLATE.format(
        module_name  = module_name,
        rule_count   = len(rules),
        rule_types   = ", ".join(rule_types[:8]),
        actors       = ", ".join(actors[:10]) or "None detected",
        business_rules = json.dumps(biz_rules[:10]),
        ui_fields    = ", ".join(ui_fields[:15]),
        sample_names = ", ".join(sample_names),
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 1500,
            system     = SYSTEM_PROMPT,
            messages   = [{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        # Strip any markdown fences if present
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"```\s*$", "", text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        log.warning("JSON parse error for module %s: %s", module_name, e)
        return None
    except Exception as e:
        log.warning("Claude API error for module %s: %s", module_name, e)
        return None


def generate_template_content(module_name: str, rules: List[Dict]) -> Dict:
    """Generate template FRD content when AI is unavailable."""
    rule_types = list(set(r.get("rule_type", "") for r in rules))
    actors     = extract_actors_for_module(rules)
    ui_fields  = extract_ui_fields_for_module(rules)
    sample_names = [r.get("name", "") for r in rules[:5]]

    return {
        "overview": (
            f"The {module_name} module provides {len(rules)} rules across "
            f"{', '.join(rule_types[:3])} types. "
            f"Key rule names include: {', '.join(sample_names[:3])}. "
            f"[Replace with business description — run with --api-key for AI generation.]"
        ),
        "user_stories": [
            f"As a user, I can perform actions in the {module_name} module so that I can complete my work.",
            "[Add specific user stories — run with --api-key for AI generation.]",
        ],
        "business_rules": extract_business_rules(rules)[:5] or [
            f"[Business rules for {module_name} — run with --api-key for AI generation.]"
        ],
        "data_requirements": [
            {"field": f.get("name", ""), "required": f.get("required", "Unknown"),
             "format": f.get("type", "Text"), "visible_when": f.get("visible_when", "Always")}
            for f in ui_fields[:8]
        ],
        "error_scenarios": [
            {"trigger": "Invalid data entry", "message": "[Error message]", "resolution": "[User action]"}
        ],
    }


# ── DOCX Generation (Node.js) ────────────────────────────────────────────────

DOCX_TEMPLATE = """
const {{
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, NumberFormat
}} = require('docx');
const fs = require('fs');

const frdData = {frd_data_json};
const systemName = {system_name_json};
const version = {version_json};
const today = new Date().toLocaleDateString('en-GB', {{day:'numeric',month:'long',year:'numeric'}});

const NAVY  = "1B2A4A";
const GOLD  = "C9A84C";
const WHITE = "FFFFFF";
const LIGHT = "F0F4FA";
const BORDER_SINGLE = {{style: BorderStyle.SINGLE, size: 1, color: "D0D8E8"}};
const TABLE_BORDERS = {{top: BORDER_SINGLE, bottom: BORDER_SINGLE, left: BORDER_SINGLE, right: BORDER_SINGLE}};

function heading1(text) {{
  return new Paragraph({{
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({{ text, bold: true, font: "Arial", size: 36, color: NAVY }})],
    spacing: {{before: 400, after: 200}},
    border: {{bottom: {{style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 1}}}},
  }});
}}

function heading2(text) {{
  return new Paragraph({{
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({{ text, bold: true, font: "Arial", size: 28, color: NAVY }})],
    spacing: {{before: 300, after: 120}},
  }});
}}

function heading3(text) {{
  return new Paragraph({{
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({{ text, bold: true, font: "Arial", size: 24, color: "2E4F8A" }})],
    spacing: {{before: 200, after: 80}},
  }});
}}

function para(text, opts={{}}) {{
  return new Paragraph({{
    children: [new TextRun({{ text, font: "Arial", size: 22, ...opts }})],
    spacing: {{after: 100}},
  }});
}}

function bullet(text) {{
  return new Paragraph({{
    numbering: {{reference: "bullets", level: 0}},
    children: [new TextRun({{ text, font: "Arial", size: 22 }})],
    spacing: {{after: 80}},
  }});
}}

function numberItem(text) {{
  return new Paragraph({{
    numbering: {{reference: "numbers", level: 0}},
    children: [new TextRun({{ text, font: "Arial", size: 22 }})],
    spacing: {{after: 80}},
  }});
}}

function headerCell(text, width) {{
  return new TableCell({{
    borders: TABLE_BORDERS,
    width: {{size: width, type: WidthType.DXA}},
    shading: {{fill: NAVY, type: ShadingType.CLEAR}},
    margins: {{top: 80, bottom: 80, left: 120, right: 120}},
    children: [new Paragraph({{
      children: [new TextRun({{text, bold: true, font:"Arial", size:20, color:WHITE}})],
    }})],
  }});
}}

function dataCell(text, width, shade) {{
  return new TableCell({{
    borders: TABLE_BORDERS,
    width: {{size: width, type: WidthType.DXA}},
    shading: shade ? {{fill: LIGHT, type: ShadingType.CLEAR}} : undefined,
    margins: {{top: 60, bottom: 60, left: 120, right: 120}},
    children: [new Paragraph({{
      children: [new TextRun({{text: String(text||''), font:"Arial", size:20}})],
    }})],
  }});
}}

function dataRow(cells, shade) {{
  return new TableRow({{children: cells.map((c,i) => dataCell(c.text, c.width, shade))}});
}}

// ── Title Page ──
const titlePage = [
  new Paragraph({{spacing:{{before:1440}}}}),
  new Paragraph({{
    alignment: AlignmentType.CENTER,
    children: [new TextRun({{text: systemName, font:"Arial", size:72, bold:true, color:NAVY}})],
    spacing: {{after:240}},
  }}),
  new Paragraph({{
    alignment: AlignmentType.CENTER,
    children: [new TextRun({{text:"Functional Requirements Document", font:"Arial", size:36, color:GOLD}})],
    spacing: {{after:120}},
  }}),
  new Paragraph({{
    alignment: AlignmentType.CENTER,
    children: [new TextRun({{text:`Version ${{version}}  ·  Generated by PREA  ·  ${{today}}`, font:"Arial", size:22, color:"555555"}})],
    spacing: {{after:1440}},
  }}),
  new Paragraph({{
    border: {{bottom: {{style:BorderStyle.SINGLE, size:6, color:NAVY, space:1}}}},
    spacing: {{after:240}},
  }}),
  new Paragraph({{
    children: [
      new TextRun({{text:"Prepared by:  ", font:"Arial", size:22, bold:true}}),
      new TextRun({{text:"PREA — Pega Reverse Engineering Agent", font:"Arial", size:22}}),
    ],
    spacing: {{after:100}},
  }}),
  new Paragraph({{
    children: [
      new TextRun({{text:"Classification:  ", font:"Arial", size:22, bold:true}}),
      new TextRun({{text:"Confidential — Programme Leadership", font:"Arial", size:22}}),
    ],
    spacing: {{after:100}},
  }}),
  new Paragraph({{
    children: [
      new TextRun({{text:"Source:  ", font:"Arial", size:22, bold:true}}),
      new TextRun({{text:`${{frdData.summary.total_rules.toLocaleString()}} rules extracted across ${{frdData.summary.layer_count}} layers`, font:"Arial", size:22}}),
    ],
  }}),
];

// ── Executive Summary ──
const summarySection = [
  heading1("1. Executive Summary"),
  para(`This Functional Requirements Document describes the business capabilities of ${{systemName}}, a Pega Platform-based application deployed across ${{frdData.summary.layer_count}} architectural layers containing ${{frdData.summary.total_rules.toLocaleString()}} rule definitions.`),
  para("This document is auto-generated by PREA from binary rule extractions and is intended for business stakeholders, programme management, and regulatory review. It describes what the system does from a user perspective — not how it is built internally."),
  para(`The application delivers ${{frdData.modules.length}} primary functional modules, described in detail in Section 4.`),
];

// ── Layers & Architecture ──
const archSection = [
  heading1("2. Application Architecture"),
  para("The application is structured across four architectural layers, each building on the one below:"),
  ...Object.entries(frdData.summary.by_layer).map(([layer, count]) =>
    bullet(`${{layer}} Layer — ${{count.toLocaleString()}} rules`)
  ),
  new Paragraph({{spacing:{{after:200}}}}),
  para("Layer override precedence (highest to lowest): Implementation > Enterprise > Industry > Framework."),
];

// ── User Roles ──
const rolesTable = new Table({{
  width: {{size: 9360, type: WidthType.DXA}},
  columnWidths: [2800, 4160, 2400],
  rows: [
    new TableRow({{children:[headerCell("Role",2800), headerCell("Description",4160), headerCell("Access Level",2400)]}}),
    ...(frdData.roles||[]).map((role,i) => new TableRow({{
      children:[
        dataCell(role.name||"", 2800, i%2===1),
        dataCell(role.description||"", 4160, i%2===1),
        dataCell(role.access||"Standard", 2400, i%2===1),
      ],
    }})),
  ],
}});

const rolesSection = [
  heading1("3. User Roles & Actors"),
  para("The following roles interact with the system based on rule-level actor analysis:"),
  new Paragraph({{spacing:{{after:120}}}}),
  rolesTable,
  new Paragraph({{spacing:{{after:200}}}}),
];

// ── Functional Modules ──
const modulesSections = [];
modulesSections.push(heading1("4. Functional Requirements by Module"));

frdData.modules.forEach((mod, modIdx) => {{
  const mNum = modIdx + 1;
  modulesSections.push(heading2(`4.${{mNum}} ${{mod.name}}`));
  modulesSections.push(para(mod.content.overview || ""));

  if(mod.content.user_stories?.length) {{
    modulesSections.push(heading3("User Stories"));
    mod.content.user_stories.forEach(us => modulesSections.push(bullet(us)));
    modulesSections.push(new Paragraph({{spacing:{{after:120}}}}));
  }}

  if(mod.content.business_rules?.length) {{
    modulesSections.push(heading3("Business Rules"));
    mod.content.business_rules.forEach((br, i) => modulesSections.push(numberItem(`BR-${{String(i+1).padStart(3,'0')}}: ${{br}}`)));
    modulesSections.push(new Paragraph({{spacing:{{after:120}}}}));
  }}

  if(mod.content.data_requirements?.length) {{
    modulesSections.push(heading3("Data Requirements"));
    const drTable = new Table({{
      width: {{size: 9360, type: WidthType.DXA}},
      columnWidths: [2800, 1400, 2560, 2600],
      rows: [
        new TableRow({{children:[
          headerCell("Field",2800), headerCell("Required",1400),
          headerCell("Format / Constraint",2560), headerCell("Visible When",2600),
        ]}}),
        ...mod.content.data_requirements.map((dr,i) => new TableRow({{
          children:[
            dataCell(dr.field||"", 2800, i%2===1),
            dataCell(dr.required||"", 1400, i%2===1),
            dataCell(dr.format||"", 2560, i%2===1),
            dataCell(dr.visible_when||"Always", 2600, i%2===1),
          ],
        }})),
      ],
    }});
    modulesSections.push(drTable);
    modulesSections.push(new Paragraph({{spacing:{{after:160}}}}));
  }}

  if(mod.content.error_scenarios?.length) {{
    modulesSections.push(heading3("Error Handling"));
    const erTable = new Table({{
      width: {{size: 9360, type: WidthType.DXA}},
      columnWidths: [2800, 3280, 3280],
      rows: [
        new TableRow({{children:[headerCell("Trigger",2800), headerCell("Message Shown",3280), headerCell("Resolution",3280)]}}),
        ...mod.content.error_scenarios.map((er,i) => new TableRow({{
          children:[
            dataCell(er.trigger||"", 2800, i%2===1),
            dataCell(er.message||"", 3280, i%2===1),
            dataCell(er.resolution||"", 3280, i%2===1),
          ],
        }})),
      ],
    }});
    modulesSections.push(erTable);
    modulesSections.push(new Paragraph({{spacing:{{after:200}}}}));
  }}
}});

// ── Business Rules Summary ──
const brSummary = [
  heading1("5. Business Rules Summary"),
  para("All business rules extracted from the application, consolidated for reference:"),
  new Paragraph({{spacing:{{after:120}}}}),
  ...(frdData.all_business_rules||[]).slice(0,50).map((br,i) => numberItem(`BR-${{String(i+1).padStart(3,'0')}}: ${{br}}`)),
];

// ── Assemble Document ──
const doc = new Document({{
  numbering: {{
    config: [
      {{ reference: "bullets", levels: [{{level:0, format:LevelFormat.BULLET, text:"•", alignment:AlignmentType.LEFT, style:{{paragraph:{{indent:{{left:720,hanging:360}}}}}}}}] }},
      {{ reference: "numbers", levels: [{{level:0, format:LevelFormat.DECIMAL, text:"%1.", alignment:AlignmentType.LEFT, style:{{paragraph:{{indent:{{left:720,hanging:360}}}}}}}}] }},
    ]
  }},
  styles: {{
    default: {{ document: {{ run: {{ font: "Arial", size: 22 }} }} }},
    paragraphStyles: [
      {{ id:"Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true,
         run:{{size:36,bold:true,font:"Arial",color:NAVY}}, paragraph:{{spacing:{{before:400,after:200}},outlineLevel:0}} }},
      {{ id:"Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true,
         run:{{size:28,bold:true,font:"Arial",color:NAVY}}, paragraph:{{spacing:{{before:300,after:120}},outlineLevel:1}} }},
      {{ id:"Heading3", name:"Heading 3", basedOn:"Normal", next:"Normal", quickFormat:true,
         run:{{size:24,bold:true,font:"Arial",color:"2E4F8A"}}, paragraph:{{spacing:{{before:200,after:80}},outlineLevel:2}} }},
    ]
  }},
  sections: [{{
    properties: {{
      page: {{
        size: {{width:12240, height:15840}},
        margin: {{top:1440, right:1440, bottom:1440, left:1440}},
      }},
    }},
    headers: {{
      default: {{
        children: [new Paragraph({{
          children: [
            new TextRun({{text:`${{systemName}} — Functional Requirements Document`, font:"Arial", size:18, color:"888888"}}),
          ],
          border: {{bottom:{{style:BorderStyle.SINGLE,size:4,color:"D0D8E8",space:1}}}},
        }})],
      }},
    }},
    footers: {{
      default: {{
        children: [new Paragraph({{
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({{text:`Version ${{version}}  ·  Generated ${{today}}  ·  Page `, font:"Arial", size:18, color:"888888"}}),
            new TextRun({{children:[new PageNumber()], font:"Arial", size:18, color:"888888"}}),
          ],
        }})],
      }},
    }},
    children: [
      ...titlePage,
      ...summarySection,
      ...archSection,
      ...rolesSection,
      ...modulesSections,
      ...brSummary,
    ],
  }}],
}});

Packer.toBuffer(doc).then(buf => {{
  fs.writeFileSync(process.argv[2], buf);
  console.log("FRD written:", process.argv[2]);
}});
"""


# ── FRD Assembly ─────────────────────────────────────────────────────────────

def build_frd_data(rules: List[Dict], modules_content: Dict[str, Dict],
                   system_name: str, version: str) -> Dict:
    """Assemble the full FRD data structure."""
    from collections import Counter

    type_counts  = Counter(r.get("rule_type","") for r in rules)
    layer_counts = Counter(r.get("layer","") for r in rules)

    all_actors = set()
    all_biz_rules = []
    for r in rules:
        all_actors.update(r.get("actors", []))
        all_biz_rules.extend(extract_business_rules([r]))

    # Derive roles from actors
    role_map = {
        "rm": ("Relationship Manager", "Initiates cases, views client data, receives notifications", "Standard"),
        "analyst": ("KYC Analyst", "Reviews cases, validates documents, makes approval decisions", "Operational"),
        "compliance": ("Compliance Officer", "Oversees AML alerts, approves SARs, accesses all cases", "Supervisory"),
        "operations": ("Operations", "Data entry, document collection, account provisioning", "Operational"),
        "manager": ("Compliance Manager", "Approves high-risk cases, manages team workload", "Management"),
        "operator": ("System Operator", "Administers system configuration and user access", "Administrative"),
    }
    roles = []
    for actor in sorted(all_actors)[:12]:
        for key, (name, desc, access) in role_map.items():
            if key in actor.lower():
                roles.append({"name": name, "description": desc, "access": access})
                break
        else:
            roles.append({"name": actor, "description": "Role extracted from rule analysis", "access": "Standard"})

    return {
        "system_name": system_name,
        "version": version,
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_rules": len(rules),
            "layer_count": len(set(r.get("layer","") for r in rules)),
            "by_layer": dict(layer_counts.most_common()),
            "by_type":  dict(type_counts.most_common(10)),
        },
        "roles": roles[:10],
        "modules": [
            {"name": module_name, "rule_count": len(mrules), "content": content}
            for module_name, content in modules_content.items()
            for mrules in [rules]   # placeholder — real module rules passed separately
        ],
        "all_business_rules": list(dict.fromkeys(all_biz_rules))[:80],
    }


def run_frd_pipeline(rules_path: Path, output_path: Path,
                     system_name: str, version: str,
                     api_key: Optional[str] = None,
                     graph_path: Optional[Path] = None) -> None:
    """Full FRD generation pipeline."""

    # Load rules
    with rules_path.open(encoding="utf-8") as f:
        data = json.load(f)
    rules = data.get("rules", data) if isinstance(data, dict) else data
    log.info("Loaded %d rules", len(rules))

    # Group into modules
    module_groups = group_rules_by_module(rules)
    log.info("Grouped into %d modules: %s", len(module_groups), list(module_groups.keys()))

    # Generate content for each module
    modules_content: Dict[str, Dict] = {}
    for module_name, module_rules in module_groups.items():
        log.info("Generating FRD content for: %s (%d rules)", module_name, len(module_rules))
        if api_key and HAS_ANTHROPIC:
            content = call_claude_for_module(module_name, module_rules, api_key)
            if not content:
                log.warning("AI generation failed for %s — using template", module_name)
                content = generate_template_content(module_name, module_rules)
        else:
            content = generate_template_content(module_name, module_rules)
        modules_content[module_name] = content

    # Build FRD data structure
    frd_data = build_frd_data(rules, modules_content, system_name, version)
    frd_data["modules"] = [
        {"name": mn, "rule_count": len(module_groups[mn]), "content": content}
        for mn, content in modules_content.items()
    ]

    # Write DOCX using Node.js docx package
    _write_docx(frd_data, output_path, system_name, version)


def _write_docx(frd_data: Dict, output_path: Path, system_name: str, version: str) -> None:
    """Generate the .docx using the docx npm package via Node.js subprocess."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write the JS generator script
        js_content = DOCX_TEMPLATE.format(
            frd_data_json    = json.dumps(frd_data),
            system_name_json = json.dumps(system_name),
            version_json     = json.dumps(version),
        )
        js_path = Path(tmpdir) / "generate_frd.js"
        js_path.write_text(js_content, encoding="utf-8")

        # Ensure docx is installed
        log.info("Checking docx npm package...")
        subprocess.run(["npm", "install", "-g", "docx"], capture_output=True)

        # Run Node.js
        log.info("Generating DOCX...")
        result = subprocess.run(
            ["node", str(js_path), str(output_path)],
            capture_output=True, text=True, cwd=tmpdir
        )

        if result.returncode != 0:
            log.error("Node.js error:\n%s", result.stderr)
            # Fallback: write FRD data as JSON
            fallback = output_path.with_suffix(".json")
            with fallback.open("w") as f:
                json.dump(frd_data, f, indent=2)
            log.info("Fallback: FRD data written to %s", fallback)
        else:
            log.info("DOCX written: %s", output_path)
            if result.stdout:
                log.info(result.stdout)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PREA FRD Writer")
    parser.add_argument("--rules",       required=True)
    parser.add_argument("--output",      default="FRD_output.docx")
    parser.add_argument("--graph",       help="rule_graph.json (optional, enriches FRD)")
    parser.add_argument("--system-name", default="Pega Application")
    parser.add_argument("--version",     default="1.0")
    parser.add_argument("--api-key",     help="Anthropic API key for AI section generation")
    parser.add_argument("--no-ai",       action="store_true", help="Skip AI, use templates only")
    args = parser.parse_args()

    api_key = None if args.no_ai else (args.api_key or os.environ.get("ANTHROPIC_API_KEY"))

    if not api_key:
        log.info("No API key — using template mode (pass --api-key or set ANTHROPIC_API_KEY for AI generation)")

    run_frd_pipeline(
        rules_path  = Path(args.rules),
        output_path = Path(args.output),
        system_name = args.system_name,
        version     = args.version,
        api_key     = api_key,
        graph_path  = Path(args.graph) if args.graph else None,
    )


if __name__ == "__main__":
    main()
