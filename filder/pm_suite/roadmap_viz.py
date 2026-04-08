"""
roadmap_viz.py — Plotly-based roadmap and dependency visualizations.
Import and call directly, or used by app.py.
"""

import json
from pathlib import Path
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx

RAG_COLORS = {"G": "#1D9E75", "A": "#EF9F27", "R": "#E24B4A"}
RAG_LABELS = {"G": "On Track", "A": "At Risk", "R": "Off Track"}
STATUS_OPACITY = {"done": 0.55, "active": 1.0, "planned": 0.70}


def load_roadmap(path: str | Path = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "data" / "roadmap.json"
    with open(path) as f:
        return json.load(f)


def _flat_milestones(data: dict) -> list[dict]:
    """Flatten nested roadmap structure into a list of milestone records."""
    rows = []
    for prog in data["programs"]:
        for ws in prog["workstreams"]:
            for m in ws["milestones"]:
                rows.append({
                    **m,
                    "program_id":   prog["id"],
                    "program_name": prog["name"],
                    "program_color": prog["color"],
                    "ws_id":        ws["id"],
                    "ws_name":      ws["name"],
                    "label": f"{ws['name']} › {m['name']}",
                })
    return rows


def build_gantt(data: dict, filter_program: str = "All") -> go.Figure:
    """
    Build a Plotly Gantt chart from roadmap data.

    Args:
        data:           Parsed roadmap dict (from load_roadmap).
        filter_program: "All" or a program id to filter.

    Returns:
        Plotly Figure.
    """
    milestones = _flat_milestones(data)
    if filter_program != "All":
        milestones = [m for m in milestones if m["program_id"] == filter_program]

    today = date.today().isoformat()

    fig = go.Figure()

    # Group by workstream for y-axis ordering
    ws_order = []
    seen = set()
    for m in milestones:
        key = (m["program_id"], m["ws_id"])
        if key not in seen:
            ws_order.append((m["ws_name"], m["program_name"], m["program_color"]))
            seen.add(key)

    y_labels = [f"<b>{ws}</b><br><span style='font-size:10px;color:#888'>{prog}</span>"
                for ws, prog, _ in ws_order]
    y_map = {ws: i for i, (ws, _, _) in enumerate(ws_order)}

    for m in milestones:
        y_idx  = y_map[m["ws_name"]]
        color  = RAG_COLORS.get(m["rag"], "#888")
        opacity = STATUS_OPACITY.get(m["status"], 0.8)
        border_color = "#333" if m["status"] == "active" else color

        fig.add_trace(go.Bar(
            name=m["name"],
            x=[(datetime.fromisoformat(m["end"]) - datetime.fromisoformat(m["start"])).days],
            y=[y_idx],
            base=[m["start"]],
            orientation="h",
            marker=dict(
                color=color,
                opacity=opacity,
                line=dict(color=border_color, width=1.5 if m["status"] == "active" else 0.5),
            ),
            hovertemplate=(
                f"<b>{m['name']}</b><br>"
                f"Workstream: {m['ws_name']}<br>"
                f"Start: {m['start']}<br>"
                f"End:   {m['end']}<br>"
                f"Status: {m['status'].title()}<br>"
                f"RAG: {RAG_LABELS.get(m['rag'], m['rag'])}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    # Today line
    fig.add_vline(
        x=today,
        line=dict(color="#E24B4A", width=1.5, dash="dot"),
        annotation_text="Today",
        annotation_position="top",
        annotation_font_size=11,
        annotation_font_color="#E24B4A",
    )

    # RAG legend traces
    for rag, color in RAG_COLORS.items():
        fig.add_trace(go.Bar(
            name=RAG_LABELS[rag],
            x=[None], y=[None],
            marker_color=color,
            showlegend=True,
        ))

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            type="date",
            tickformat="%b %Y",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.06)",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            tickvals=list(range(len(y_labels))),
            ticktext=y_labels,
            tickfont=dict(size=11),
            showgrid=False,
        ),
        height=max(320, len(ws_order) * 68 + 80),
        margin=dict(l=240, r=24, t=48, b=48),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
            font=dict(size=11),
        ),
        font=dict(family="system-ui, sans-serif"),
        title=dict(text="Program Roadmap", font=dict(size=15, color="#333"), x=0.5),
    )
    return fig


def build_dependency_graph(data: dict, filter_rag: str = "All") -> go.Figure:
    """
    Build a Plotly network graph showing milestone dependencies.

    Args:
        data:       Parsed roadmap dict.
        filter_rag: "All", "R", "A", or "G" to filter dependency edges.

    Returns:
        Plotly Figure.
    """
    milestones = {m["id"]: m for m in _flat_milestones(data)}
    deps = data["dependencies"]

    if filter_rag != "All":
        deps = [d for d in deps if d["rag"] == filter_rag]

    G = nx.DiGraph()
    for mid, m in milestones.items():
        G.add_node(mid, **m)

    for d in deps:
        G.add_edge(d["from_milestone"], d["to_milestone"], **d)

    # Only keep nodes that appear in filtered edges
    active_nodes = set()
    for d in deps:
        active_nodes.add(d["from_milestone"])
        active_nodes.add(d["to_milestone"])

    if not active_nodes:
        fig = go.Figure()
        fig.update_layout(
            title="No dependencies match the current filter.",
            height=400,
            paper_bgcolor="white",
        )
        return fig

    subG = G.subgraph(active_nodes)
    pos = nx.spring_layout(subG, seed=42, k=2.2)

    # Edges
    edge_traces = []
    for u, v, attr in subG.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        color = RAG_COLORS.get(attr.get("rag", "G"), "#888")
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode="lines",
            line=dict(width=2, color=color),
            hoverinfo="none",
            showlegend=False,
        ))

        # Arrow annotation midpoint label
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        edge_traces.append(go.Scatter(
            x=[mx], y=[my],
            mode="markers+text",
            marker=dict(color=color, size=8, symbol="arrow", angleref="previous"),
            text=[attr.get("type", "")],
            textfont=dict(size=9, color=color),
            textposition="top center",
            hovertemplate=f"<b>{attr.get('description','')}</b><br>Type: {attr.get('type','')}<extra></extra>",
            showlegend=False,
        ))

    # Nodes
    node_x, node_y, node_text, node_color, node_hover = [], [], [], [], []
    for node in subG.nodes():
        m = milestones[node]
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        short = m["name"] if len(m["name"]) <= 22 else m["name"][:20] + "…"
        node_text.append(short)
        node_color.append(RAG_COLORS.get(m["rag"], "#888"))
        node_hover.append(
            f"<b>{m['name']}</b><br>"
            f"{m['ws_name']}<br>"
            f"{m['program_name']}<br>"
            f"RAG: {RAG_LABELS.get(m['rag'], m['rag'])}<br>"
            f"{m['start']} → {m['end']}"
        )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=18, color=node_color, line=dict(width=1.5, color="white")),
        text=node_text,
        textposition="bottom center",
        textfont=dict(size=10),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=node_hover,
        showlegend=False,
    )

    # RAG legend
    legend_traces = [
        go.Scatter(x=[None], y=[None], mode="markers",
                   marker=dict(size=10, color=c),
                   name=RAG_LABELS[r], showlegend=True)
        for r, c in RAG_COLORS.items()
    ]

    fig = go.Figure(data=edge_traces + [node_trace] + legend_traces)
    fig.update_layout(
        title=dict(text="Dependency Network", font=dict(size=15, color="#333"), x=0.5),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=520,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=16, r=16, t=56, b=16),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="system-ui, sans-serif"),
    )
    return fig


def build_dependency_table(data: dict) -> list[dict]:
    """Return a flat list of dependency records for display in a table."""
    milestones = {m["id"]: m for m in _flat_milestones(data)}
    rows = []
    for d in data["dependencies"]:
        frm = milestones.get(d["from_milestone"], {})
        to  = milestones.get(d["to_milestone"],   {})
        rows.append({
            "ID":          d["id"],
            "From":        frm.get("name", d["from_milestone"]),
            "From Stream": frm.get("ws_name", ""),
            "To":          to.get("name",  d["to_milestone"]),
            "To Stream":   to.get("ws_name", ""),
            "Type":        d["type"],
            "Description": d["description"],
            "RAG":         d["rag"],
        })
    return rows
