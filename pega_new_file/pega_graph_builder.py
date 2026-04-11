#!/usr/bin/env python3
"""
pega_graph_builder.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREA — Pega Rule Dependency Graph Builder

Builds a directed dependency graph from extracted Pega rules and produces:
  1. rule_graph.json — graph data for downstream use (nodes + edges)
  2. rule_graph.html — interactive D3.js force-directed visualisation
  3. graph_metrics.json — centrality, clustering, hub/leaf analysis

Uses NetworkX for graph algorithms (PageRank, betweenness centrality,
connected components, cycle detection).

Usage:
    python pega_graph_builder.py --rules rules_extracted.json
                                  --output-graph rule_graph.json
                                  --output-html rule_graph.html

    python pega_graph_builder.py --rules rules_extracted.json
                                  --layer-filter Enterprise,Implementation
                                  --type-filter Flow,"Data Transform"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

log = logging.getLogger("prea.graph")
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")

# Optional deps
try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False
    log.warning("networkx not installed — graph metrics will be limited. pip install networkx")

# Rule type colours (matches PREA UI)
TYPE_COLORS: Dict[str, str] = {
    "Flow":                "#00c2ff",
    "Activity":            "#f87171",
    "UI Section":          "#fbbf24",
    "Harness":             "#fbbf24",
    "Decision Table":      "#34d399",
    "Data Transform":      "#a78bfa",
    "Declare Expression":  "#ff6b35",
    "When Rule":           "#22d3ee",
    "Validate Rule":       "#fb923c",
    "Correspondence":      "#64748b",
    "Report Definition":   "#94a3b8",
    "Data Page":           "#818cf8",
    "Service REST":        "#e879f9",
    "Connector REST":      "#e879f9",
    "Unknown":             "#475569",
}

LAYER_COLORS: Dict[str, str] = {
    "Framework":      "#00c2ff",
    "Industry":       "#a78bfa",
    "Enterprise":     "#34d399",
    "Implementation": "#fbbf24",
    "Unknown":        "#475569",
}


# ── Graph Building ───────────────────────────────────────────────────────────

def load_rules(rules_path: Path) -> List[Dict]:
    with rules_path.open(encoding="utf-8") as f:
        data = json.load(f)
    # Support both {"rules": [...]} and bare list
    if isinstance(data, list):
        return data
    return data.get("rules", [])


def build_graph(rules: List[Dict],
                layer_filter: Optional[Set[str]] = None,
                type_filter:  Optional[Set[str]] = None) -> Tuple[List[Dict], List[Dict]]:
    """
    Build node and edge lists from rule records.

    Returns:
        nodes: list of node dicts {id, label, type, layer, color, ...}
        edges: list of edge dicts {source, target, type}
    """
    # Build lookup: name → rule_id
    name_to_id: Dict[str, str] = {}
    id_to_rule: Dict[str, Dict] = {}

    filtered = rules
    if layer_filter:
        filtered = [r for r in filtered if r.get("layer") in layer_filter]
    if type_filter:
        filtered = [r for r in filtered if r.get("rule_type") in type_filter]

    for r in filtered:
        rid  = r.get("rule_id") or r.get("name", "")
        name = r.get("name", "")
        name_to_id[name] = rid
        id_to_rule[rid]  = r

    nodes = []
    edges = []
    seen_edges: Set[Tuple[str, str]] = set()

    for r in filtered:
        rid       = r.get("rule_id") or r.get("name", "")
        rule_type = r.get("rule_type", "Unknown")
        layer     = r.get("layer", "Unknown")
        deps      = r.get("dependencies", [])
        flow_steps= r.get("flow_steps", [])

        # Node
        nodes.append({
            "id":       rid,
            "label":    r.get("name", rid),
            "type":     rule_type,
            "layer":    layer,
            "class":    r.get("pega_class", ""),
            "ruleset":  r.get("ruleset", ""),
            "status":   r.get("status", "Active"),
            "color":    TYPE_COLORS.get(rule_type, TYPE_COLORS["Unknown"]),
            "layer_color": LAYER_COLORS.get(layer, LAYER_COLORS["Unknown"]),
            "size":     _node_size(rule_type, deps),
            "notes":    r.get("notes", ""),
            "dep_count": len(deps),
            "field_count": len(r.get("ui_fields", [])),
            "step_count": len(flow_steps),
        })

        # Edges from dependency list
        for dep_name in deps:
            dep_id = name_to_id.get(dep_name)
            if dep_id and dep_id != rid:
                edge_key = (rid, dep_id)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append({
                        "source": rid,
                        "target": dep_id,
                        "type":   "calls",
                    })

        # Edges from flow steps (more precise than generic deps)
        for step in flow_steps:
            for trans in step.get("transition", []):
                to_name = trans.get("to", "")
                to_id   = name_to_id.get(to_name)
                if to_id and to_id != rid:
                    edge_key = (rid, to_id)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append({
                            "source": rid,
                            "target": to_id,
                            "type":   "flow_transition",
                        })

    log.info("Graph built: %d nodes, %d edges", len(nodes), len(edges))
    return nodes, edges


def _node_size(rule_type: str, deps: List) -> int:
    """Compute node display size based on type and connectivity."""
    base_sizes = {
        "Flow": 14, "Activity": 12, "Data Transform": 11,
        "Decision Table": 11, "UI Section": 9, "Harness": 9,
    }
    base = base_sizes.get(rule_type, 8)
    # Bump up for highly-connected nodes
    if len(deps) > 20:
        base += 4
    elif len(deps) > 10:
        base += 2
    return base


# ── Graph Metrics (NetworkX) ─────────────────────────────────────────────────

def compute_metrics(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
    """Compute graph metrics using NetworkX."""
    if not HAS_NX:
        return {"error": "networkx not available"}

    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
    for e in edges:
        G.add_edge(e["source"], e["target"], type=e.get("type", "calls"))

    metrics: Dict[str, Any] = {
        "node_count":     G.number_of_nodes(),
        "edge_count":     G.number_of_edges(),
        "density":        round(nx.density(G), 6),
        "is_dag":         nx.is_directed_acyclic_graph(G),
    }

    # Weakly connected components
    wcc = list(nx.weakly_connected_components(G))
    metrics["connected_components"] = len(wcc)
    metrics["largest_component_size"] = max(len(c) for c in wcc) if wcc else 0

    # Cycles (potential circular dependencies — problematic in Pega)
    try:
        cycles = list(nx.simple_cycles(G))
        metrics["cycle_count"] = len(cycles)
        metrics["cycles_sample"] = [list(c) for c in cycles[:5]]
    except Exception:
        metrics["cycle_count"] = -1

    # PageRank (rule importance)
    try:
        pr = nx.pagerank(G, alpha=0.85, max_iter=200)
        top_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:20]
        metrics["top_pagerank"] = [{"id": nid, "score": round(score, 6)} for nid, score in top_pr]
    except Exception:
        metrics["top_pagerank"] = []

    # In-degree / out-degree centrality (hub rules)
    in_deg  = dict(G.in_degree())
    out_deg = dict(G.out_degree())

    hub_rules  = sorted(in_deg.items(),  key=lambda x: x[1], reverse=True)[:20]
    leaf_rules = [nid for nid, deg in in_deg.items() if deg == 0]
    orphan_rules = [nid for nid, deg in out_deg.items() if deg == 0 and in_deg.get(nid, 0) == 0]

    metrics["hub_rules"]    = [{"id": nid, "dependents": deg} for nid, deg in hub_rules]
    metrics["leaf_count"]   = len(leaf_rules)
    metrics["leaf_rules"]   = leaf_rules[:50]
    metrics["orphan_count"] = len(orphan_rules)
    metrics["orphan_rules"] = orphan_rules[:50]

    # Layer-to-layer dependency flow (override chain analysis)
    layer_flows: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for u, v in G.edges():
        u_layer = G.nodes[u].get("layer", "Unknown")
        v_layer = G.nodes[v].get("layer", "Unknown")
        layer_flows[u_layer][v_layer] += 1
    metrics["layer_dependency_matrix"] = {k: dict(v) for k, v in layer_flows.items()}

    log.info("Metrics computed: %d nodes, %d edges, %d cycles", 
             G.number_of_nodes(), G.number_of_edges(), metrics.get("cycle_count", 0))
    return metrics


# ── HTML Visualisation ───────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>PREA Rule Dependency Graph — {app_name}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0a0c10; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; overflow: hidden; }}
  #canvas {{ width: 100vw; height: 100vh; }}
  .tooltip {{
    position: absolute; background: #111318; border: 1px solid #2e3445;
    border-radius: 8px; padding: 12px 16px; font-size: 12px; pointer-events: none;
    max-width: 280px; opacity: 0; transition: opacity 0.15s;
  }}
  .tooltip.visible {{ opacity: 1; }}
  .tt-name {{ font-weight: 700; font-size: 14px; color: #e2e8f0; margin-bottom: 4px; }}
  .tt-type {{ font-size: 11px; color: #94a3b8; margin-bottom: 8px; }}
  .tt-row {{ display: flex; justify-content: space-between; gap: 16px; font-size: 11px; margin-bottom: 3px; }}
  .tt-row span {{ color: #64748b; }}
  .tt-row strong {{ color: #94a3b8; }}
  #controls {{
    position: absolute; top: 16px; right: 16px;
    background: #111318; border: 1px solid #232733;
    border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 10px;
    width: 220px;
  }}
  .ctrl-title {{ font-size: 10px; color: #64748b; letter-spacing: 1px; text-transform: uppercase; }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; font-size: 11px; color: #94a3b8; cursor: pointer; }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  #stats {{
    position: absolute; bottom: 16px; left: 16px;
    background: #111318; border: 1px solid #232733;
    border-radius: 8px; padding: 12px 16px; font-size: 11px; color: #64748b;
    font-family: monospace;
  }}
  #search {{
    position: absolute; top: 16px; left: 16px;
    display: flex; gap: 8px;
  }}
  #search input {{
    background: #111318; border: 1px solid #232733; border-radius: 6px;
    padding: 8px 12px; color: #e2e8f0; font-size: 13px; outline: none; width: 240px;
  }}
  #search input:focus {{ border-color: #00c2ff; }}
  .link {{ stroke: #1e2433; stroke-width: 1; stroke-opacity: 0.6; marker-end: url(#arrow); }}
  .link.flow_transition {{ stroke: #00c2ff44; stroke-width: 1.5; }}
  .node {{ cursor: pointer; transition: opacity 0.2s; }}
  .node:hover circle {{ stroke-width: 3; }}
  .node-label {{ font-size: 9px; fill: #94a3b8; pointer-events: none; }}
  .highlighted circle {{ stroke-width: 3 !important; stroke: white !important; }}
</style>
</head>
<body>
<svg id="canvas"></svg>
<div class="tooltip" id="tooltip"></div>
<div id="search">
  <input type="text" id="searchInput" placeholder="Search rule name..." oninput="searchNode(this.value)"/>
</div>
<div id="controls">
  <div class="ctrl-title">Rule Types</div>
  {legend_html}
  <div class="ctrl-title" style="margin-top:8px">Layer Filter</div>
  {layer_legend_html}
</div>
<div id="stats" id="stats">
  Nodes: {node_count} &nbsp;|&nbsp; Edges: {edge_count}
</div>
<script>
const graphData = {graph_json};
const W = window.innerWidth, H = window.innerHeight;

const svg = d3.select("#canvas").attr("width", W).attr("height", H);
const defs = svg.append("defs");
defs.append("marker").attr("id","arrow").attr("viewBox","0 -5 10 10")
    .attr("refX",20).attr("refY",0).attr("markerWidth",6).attr("markerHeight",6)
    .attr("orient","auto")
    .append("path").attr("d","M0,-5L10,0L0,5").attr("fill","#2e3445");

const g = svg.append("g");
svg.call(d3.zoom().scaleExtent([0.05,5]).on("zoom", e => g.attr("transform", e.transform)));

const sim = d3.forceSimulation(graphData.nodes)
  .force("link", d3.forceLink(graphData.edges).id(d=>d.id).distance(80).strength(0.3))
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(W/2, H/2))
  .force("collision", d3.forceCollide().radius(d => d.size + 4));

const link = g.append("g").selectAll("line")
  .data(graphData.edges).join("line")
  .attr("class", d => "link " + (d.type || ""))
  .attr("stroke", d => d.type === "flow_transition" ? "#00c2ff44" : "#1e2433");

const node = g.append("g").selectAll("g")
  .data(graphData.nodes).join("g")
  .attr("class","node")
  .call(d3.drag()
    .on("start", (e,d) => {{ if(!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; }})
    .on("drag",  (e,d) => {{ d.fx=e.x; d.fy=e.y; }})
    .on("end",   (e,d) => {{ if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }}));

node.append("circle")
  .attr("r", d => d.size)
  .attr("fill", d => d.color + "33")
  .attr("stroke", d => d.color)
  .attr("stroke-width", 1.5);

node.filter(d => d.size >= 11).append("text")
  .attr("class","node-label")
  .attr("dy", d => d.size + 11)
  .attr("text-anchor","middle")
  .text(d => d.label.substring(0,18));

const tt = document.getElementById("tooltip");
node.on("mouseover", (e,d) => {{
  tt.innerHTML = `
    <div class="tt-name">${{d.label}}</div>
    <div class="tt-type" style="color:${{d.color}}">${{d.type}}</div>
    <div class="tt-row"><span>Layer</span><strong>${{d.layer}}</strong></div>
    <div class="tt-row"><span>Class</span><strong>${{d.class}}</strong></div>
    <div class="tt-row"><span>Ruleset</span><strong>${{d.ruleset}}</strong></div>
    <div class="tt-row"><span>Status</span><strong>${{d.status}}</strong></div>
    <div class="tt-row"><span>Dependencies</span><strong>${{d.dep_count}}</strong></div>
    ${{d.notes ? `<div style="margin-top:8px;font-size:10px;color:#64748b">${{d.notes}}</div>` : ''}}
  `;
  tt.classList.add("visible");
}})
.on("mousemove", e => {{ tt.style.left = (e.pageX+14)+"px"; tt.style.top = (e.pageY-10)+"px"; }})
.on("mouseout",  () => tt.classList.remove("visible"))
.on("click",     (e,d) => highlightNeighbours(d));

sim.on("tick", () => {{
  link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y)
      .attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  node.attr("transform",d=>`translate(${{d.x}},${{d.y}})`);
}});

function highlightNeighbours(d) {{
  const connected = new Set([d.id]);
  graphData.edges.forEach(e => {{
    if(e.source.id===d.id || e.source===d.id) connected.add(e.target.id||e.target);
    if(e.target.id===d.id || e.target===d.id) connected.add(e.source.id||e.source);
  }});
  node.style("opacity", n => connected.has(n.id) ? 1 : 0.15);
  link.style("opacity", e => {{
    const s = e.source.id||e.source, t = e.target.id||e.target;
    return connected.has(s) && connected.has(t) ? 1 : 0.05;
  }});
}}

svg.on("click", (e) => {{
  if(e.target === svg.node()) {{
    node.style("opacity",1); link.style("opacity",0.6);
  }}
}});

function searchNode(q) {{
  if(!q) {{ node.style("opacity",1); link.style("opacity",0.6); return; }}
  const lq = q.toLowerCase();
  node.style("opacity", d => d.label.toLowerCase().includes(lq) ? 1 : 0.1);
}}

// Layer filter toggles
const hiddenLayers = new Set();
document.querySelectorAll(".layer-toggle").forEach(el => {{
  el.addEventListener("click", () => {{
    const layer = el.dataset.layer;
    if(hiddenLayers.has(layer)) {{ hiddenLayers.delete(layer); el.style.opacity=1; }}
    else {{ hiddenLayers.add(layer); el.style.opacity=0.3; }}
    node.style("display", d => hiddenLayers.has(d.layer) ? "none" : null);
  }});
}});
</script>
</body>
</html>"""


def build_legend_html(type_colors: Dict[str, str]) -> str:
    return "\n".join(
        f'<div class="legend-item">'
        f'<div class="legend-dot" style="background:{color}"></div>{rtype}'
        f'</div>'
        for rtype, color in type_colors.items() if rtype != "Unknown"
    )


def build_layer_legend_html(layer_colors: Dict[str, str]) -> str:
    return "\n".join(
        f'<div class="legend-item layer-toggle" data-layer="{layer}" style="cursor:pointer">'
        f'<div class="legend-dot" style="background:{color}"></div>{layer}'
        f'</div>'
        for layer, color in layer_colors.items() if layer != "Unknown"
    )


def write_html(nodes: List[Dict], edges: List[Dict],
               output_path: Path, app_name: str = "Pega Application") -> None:
    """Write an interactive D3.js HTML visualisation."""
    graph_json = json.dumps({"nodes": nodes, "edges": edges}, default=str)

    html = HTML_TEMPLATE.format(
        app_name        = app_name,
        graph_json      = graph_json,
        legend_html     = build_legend_html(TYPE_COLORS),
        layer_legend_html = build_layer_legend_html(LAYER_COLORS),
        node_count      = len(nodes),
        edge_count      = len(edges),
    )

    output_path.write_text(html, encoding="utf-8")
    log.info("HTML graph written: %s", output_path)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PREA Graph Builder")
    parser.add_argument("--rules",         required=True, help="rules_extracted.json")
    parser.add_argument("--output-graph",  default="rule_graph.json")
    parser.add_argument("--output-html",   default="rule_graph.html")
    parser.add_argument("--output-metrics",default="graph_metrics.json")
    parser.add_argument("--layer-filter",  help="Comma-separated layers to include")
    parser.add_argument("--type-filter",   help="Comma-separated rule types to include")
    parser.add_argument("--app-name",      default="Pega Application")
    args = parser.parse_args()

    rules = load_rules(Path(args.rules))
    log.info("Loaded %d rules", len(rules))

    layer_filter = set(args.layer_filter.split(",")) if args.layer_filter else None
    type_filter  = set(args.type_filter.split(","))  if args.type_filter  else None

    nodes, edges = build_graph(rules, layer_filter, type_filter)

    # Write graph JSON
    graph_out = Path(args.output_graph)
    graph_out.parent.mkdir(parents=True, exist_ok=True)
    with graph_out.open("w") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=2)
    log.info("Graph JSON written: %s", graph_out)

    # Write HTML
    write_html(nodes, edges, Path(args.output_html), args.app_name)

    # Write metrics
    metrics = compute_metrics(nodes, edges)
    metrics_out = Path(args.output_metrics)
    with metrics_out.open("w") as f:
        json.dump(metrics, f, indent=2)
    log.info("Metrics written: %s", metrics_out)

    print(f"\n{'═'*50}")
    print(f"  Graph: {len(nodes)} nodes, {len(edges)} edges")
    print(f"  Cycles: {metrics.get('cycle_count', 'N/A')}")
    print(f"  Components: {metrics.get('connected_components', 'N/A')}")
    if metrics.get("hub_rules"):
        print(f"  Top Hub: {metrics['hub_rules'][0]['id']} ({metrics['hub_rules'][0]['dependents']} dependents)")
    print(f"{'═'*50}")


if __name__ == "__main__":
    main()
