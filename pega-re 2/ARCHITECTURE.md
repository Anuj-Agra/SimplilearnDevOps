# PegaRE — Architecture

## 1. Design principles

1. **Stream, don't load.** 200K rules × typical XML size (5–50 KB) = 1–10 GB. The pipeline parses rule-by-rule, writing structured records to a local SQLite catalog. Only the catalog is held in memory; raw XML is re-opened on demand.
2. **Deterministic core, LLM edges.** Parsing, hierarchy building, and dependency graphing are pure Python — reproducible and auditable. LLM agents are used only for (a) classification of ambiguous rules, (b) natural-language summaries, and (c) the final documentation synthesis. This keeps hallucination risk bounded.
3. **Skill files are the contract.** Every agent has a `SKILL.md` defining its inputs, outputs, and instructions. The same skill file works with Claude, GitHub Copilot Chat, or a local LLM.
4. **Hierarchy is first-class.** The Product Owner needs to see "what is this app?" at Case Type level and "what fires when?" at Assignment level. The schema separates these concerns into distinct tables.

## 2. Input shape

Each of your 4 JARs, once extracted, contains:

```
jar_N_extracted/
├── META-INF/
│   ├── MANIFEST.MF                 ← standard jar manifest
│   └── pega.xml                    ← Pega archive manifest (rule index)
└── <ruleset>/<major>-<minor>/
    └── <ClassName>/
        └── <RuleType>/
            └── <RuleName>.xml      ← individual rule
```

Rule XML typically has:
```xml
<pagedata pxObjClass="Rule-Obj-Flow"
          pyRuleName="pyStartCase"
          pyClassName="MyCo-App-Work-KYCReview"
          pyRuleSet="MyCoKYC"
          pyRuleSetVersion="01-05-12"
          pyAppliesTo="..."
          pxInsName="...">
  <!-- rule-type-specific payload -->
</pagedata>
```

## 3. Rule types we handle

| Pega class (`pxObjClass`) | What it represents | Agent that owns it |
|---|---|---|
| `Rule-Obj-Class` | Data/work class definition | HierarchyMapper |
| `Rule-Obj-Property` | Field on a class | HierarchyMapper |
| `Rule-Obj-CaseType` | Top-level case blueprint | FlowAnalyzer |
| `Rule-Obj-Flow` | Process diagram | FlowAnalyzer |
| `Rule-Obj-FlowAction` | User action on an assignment | TaskExtractor |
| `Rule-Obj-Activity` | Imperative logic | FlowAnalyzer (for called activities) |
| `Rule-HTML-Section` | UI fragment | UIRenderer |
| `Rule-HTML-Harness` | Full page / portal | UIRenderer |
| `Rule-Declare-Expression` | Declarative computation | HierarchyMapper |
| `Rule-Decision-Table` / `-Map` / `-Tree` | Business rules | FlowAnalyzer |
| `Rule-Obj-When` | Boolean condition | FlowAnalyzer |
| `Rule-Obj-ServiceLevel` | SLA definition | TaskExtractor |
| `Rule-Access-Role-Obj` / `-Privilege` | Security | HierarchyMapper |
| `Data-Admin-Operator-ID` | Operator / workbasket | TaskExtractor |

## 4. Data model (SQLite catalog)

```
rules(rule_id PK, obj_class, name, class_name, applies_to,
      ruleset, version, file_path, parsed_ok, raw_xml_offset)

classes(class_id PK, class_name, parent_class, is_work_class, ruleset)

case_types(case_type_id PK, class_name, label, starting_flow, stages_json)

flows(flow_id PK, rule_id FK, flow_name, class_name, shapes_json, edges_json)

assignments(assignment_id PK, flow_id FK, shape_name, flow_action,
            router_type, router_target, sla_rule, task_label,
            triggered_when, step_order)

ui_rules(ui_id PK, rule_id FK, ui_type, layout_json, rendered_html_path)

dependencies(src_rule_id, dst_rule_name, dst_rule_type, ref_kind)
```

## 5. Agent orchestration graph

```
                          ┌──────────────────┐
                          │   ExtractorAgent │
                          │  (JAR → catalog) │
                          └────────┬─────────┘
                                   ▼
                          ┌──────────────────┐
                          │ RuleParserAgent  │
                          │ (XML → records)  │
                          └────────┬─────────┘
                                   ▼
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
 ┌───────────────────┐  ┌──────────────────┐   ┌──────────────────┐
 │ HierarchyMapper   │  │  FlowAnalyzer    │   │   UIRenderer     │
 │ (classes, rulesets│  │ (cases, flows,   │   │ (Section/Harness │
 │ , properties)     │  │  decisions)      │   │  → HTML)         │
 └─────────┬─────────┘  └────────┬─────────┘   └─────────┬────────┘
           │                     ▼                       │
           │            ┌──────────────────┐             │
           │            │ TaskExtractor    │             │
           │            │ (assignments,    │             │
           │            │  routers, SLAs)  │             │
           │            └────────┬─────────┘             │
           └─────────────────────┼───────────────────────┘
                                 ▼
                       ┌──────────────────┐
                       │ DocSynthesizer   │
                       │ (Program Doc)    │
                       └──────────────────┘
```

## 6. Hierarchy view the PO/TL will consume

```
Application
 └─ Ruleset (e.g. MyCoKYC:01-05-12)
     └─ Work Class (e.g. MyCo-App-Work-KYCReview)
         └─ Case Type
             └─ Stage (Intake / Review / Decision / Closure)
                 └─ Step
                     └─ Flow / FlowAction
                         └─ Assignment  ← "a task is generated here"
                             ├─ Router  (worklist | workbasket | skill)
                             ├─ SLA     (goal/deadline/passed-deadline)
                             └─ UI      (Harness + Sections rendered)
```

Every node in this tree is queryable. Every Assignment row in the `assignments` table answers your core question: **which task, generated when, by what trigger, routed to whom, with what SLA.**

## 7. Why LangGraph

- Fan-out / fan-in over typed state is native.
- Each agent is a node; failures in one branch don't kill the others.
- The state object is a `dataclass` containing `catalog_path`, `progress`, `warnings`, `outputs` — inspectable at any checkpoint.
- Runs incrementally: re-running after a new JAR drop only reparses changed rules.

## 8. Failure modes we design around

| Risk | Mitigation |
|---|---|
| Rule XML is malformed or uses newer schema | `parsed_ok=False` flag, quarantine folder, LLM asked only to classify — never to invent content |
| Custom rule types we don't know | Generic `Rule-*` handler logs and surfaces them in a "Review Queue" section of the doc |
| Circular flow references | `networkx` cycle detection; cycles are annotated, not followed |
| UI sections reference CSS/JS assets not in the JAR | Rendered HTML uses a fallback stylesheet; missing assets logged |
| LLM cost at 200K rules | LLM is **never** called per-rule — only per Case Type (~tens to low hundreds) and for final synthesis |
