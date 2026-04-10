#!/usr/bin/env python3
"""
project_graph.py — Extract sparse projections from repo-graph.json.
Token-efficient: loads only the slice needed for each query.

Usage:
  python3 project_graph.py --graph repo-graph.json --mode index
  python3 project_graph.py --graph repo-graph.json --mode fan-in   --node shared-lib
  python3 project_graph.py --graph repo-graph.json --mode fan-out  --node service-a:core
  python3 project_graph.py --graph repo-graph.json --mode impact   --node shared-lib
  python3 project_graph.py --graph repo-graph.json --mode path     --from svc-a --to api-gw
  python3 project_graph.py --graph repo-graph.json --mode cycles
  python3 project_graph.py --graph repo-graph.json --mode dead
  python3 project_graph.py --graph repo-graph.json --mode subtree  --node service-a
  python3 project_graph.py --graph repo-graph.json --mode critical --top 10
  python3 project_graph.py --graph repo-graph.json --mode entry-points
  python3 project_graph.py --graph repo-graph.json --mode longest-path

Output: JSON projection to stdout (pipe to a file or read inline)
"""

import json
import sys
import argparse
from collections import defaultdict, deque


# ─── Lazy loader: stream-parse only what's needed ──────────────────────────

def load_graph(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def node_map(nodes: list) -> dict:
    return {n["id"]: n for n in nodes}


# ─── Projection functions ───────────────────────────────────────────────────

def proj_index(data: dict) -> dict:
    """Minimal index: id + label only. Cheapest possible load."""
    return {
        "mode": "index",
        "totalModules": data["meta"]["totalModules"],
        "totalEdges":   data["meta"]["totalEdges"],
        "buildSystem":  data["meta"]["buildSystem"],
        "nodes": [
            {"id": n["id"], "label": n.get("label", n["id"]),
             "parent": n.get("parent"), "type": n.get("type")}
            for n in data["nodes"]
        ]
    }


def proj_fan_in(data: dict, node_id: str) -> dict:
    nm = node_map(data["nodes"])
    if node_id not in nm:
        return {"error": f"Node '{node_id}' not found"}
    focal_node = slim_node(nm[node_id])
    edges_in = [e for e in data["edges"] if e["to"] == node_id]
    callers = [slim_node(nm[e["from"]]) for e in edges_in if e["from"] in nm]
    return {
        "mode": "fan-in", "focalNode": node_id,
        "nodes": [focal_node] + callers,
        "edges": edges_in,
        "summary": f"{len(callers)} modules depend directly on {node_id}"
    }


def proj_fan_out(data: dict, node_id: str) -> dict:
    nm = node_map(data["nodes"])
    if node_id not in nm:
        return {"error": f"Node '{node_id}' not found"}
    focal_node = slim_node(nm[node_id])
    edges_out = [e for e in data["edges"] if e["from"] == node_id]
    callees = [slim_node(nm[e["to"]]) for e in edges_out if e["to"] in nm]
    return {
        "mode": "fan-out", "focalNode": node_id,
        "nodes": [focal_node] + callees,
        "edges": edges_out,
        "summary": f"{node_id} declares {len(callees)} direct dependencies"
    }


def proj_impact(data: dict, node_id: str) -> dict:
    nm = node_map(data["nodes"])
    if node_id not in nm:
        return {"error": f"Node '{node_id}' not found"}
    impact_ids = data["analysis"]["impactMap"].get(node_id, [])
    # Truncate if huge — summarise instead
    truncated = len(impact_ids) > 40
    shown_ids = impact_ids[:40]
    nodes_out = [slim_node(nm[node_id])] + [
        slim_node(nm[i]) for i in shown_ids if i in nm
    ]
    return {
        "mode": "impact", "focalNode": node_id,
        "totalImpact": len(impact_ids),
        "truncated": truncated,
        "nodes": nodes_out,
        "summary": f"Changing {node_id} puts {len(impact_ids)} modules at risk"
                   + (" (showing first 40)" if truncated else "")
    }


def proj_path(data: dict, from_id: str, to_id: str) -> dict:
    nm = node_map(data["nodes"])
    adj = defaultdict(list)
    edge_lookup = defaultdict(dict)
    for e in data["edges"]:
        adj[e["from"]].append(e["to"])
        edge_lookup[(e["from"], e["to"])] = e

    # BFS shortest path
    queue = deque([[from_id]])
    visited = {from_id}
    while queue:
        path = queue.popleft()
        curr = path[-1]
        if curr == to_id:
            nodes_in_path = [slim_node(nm[n]) for n in path if n in nm]
            edges_in_path = [
                edge_lookup.get((path[i], path[i+1]), {"from": path[i], "to": path[i+1]})
                for i in range(len(path) - 1)
            ]
            return {
                "mode": "path", "from": from_id, "to": to_id,
                "path": path, "hops": len(path) - 1,
                "nodes": nodes_in_path, "edges": edges_in_path,
                "summary": f"Path found: {' → '.join(path)} ({len(path)-1} hops)"
            }
        for nxt in adj.get(curr, []):
            if nxt not in visited:
                visited.add(nxt)
                queue.append(path + [nxt])

    return {"mode": "path", "from": from_id, "to": to_id,
            "path": None, "summary": f"No dependency path from {from_id} to {to_id}"}


def proj_cycles(data: dict) -> dict:
    nm = node_map(data["nodes"])
    cycles = data["analysis"].get("circularDependencies", [])
    all_nodes = {n for c in cycles for n in c}
    return {
        "mode": "cycles",
        "totalCycles": len(cycles),
        "cycles": cycles,
        "nodesInCycles": list(all_nodes),
        "nodes": [slim_node(nm[n]) for n in all_nodes if n in nm],
        "summary": f"{len(cycles)} circular dependency cycle(s) detected"
    }


def proj_dead(data: dict) -> dict:
    nm = node_map(data["nodes"])
    dead = data["analysis"].get("deadModules", [])
    return {
        "mode": "dead",
        "totalDead": len(dead),
        "nodes": [slim_node(nm[d]) for d in dead if d in nm],
        "summary": f"{len(dead)} potentially unused module(s) detected"
    }


def proj_subtree(data: dict, node_id: str) -> dict:
    """All nodes in the subtree rooted at node_id."""
    nm = node_map(data["nodes"])
    if node_id not in nm:
        return {"error": f"Node '{node_id}' not found"}
    subtree_ids = {node_id}
    # Find all descendants by parent relationship
    for n in data["nodes"]:
        parts = n["id"].split(":")
        for depth in range(1, len(parts)):
            ancestor = ":".join(parts[:depth])
            if ancestor == node_id:
                subtree_ids.add(n["id"])
                break
    subtree_edges = [
        e for e in data["edges"]
        if e["from"] in subtree_ids or e["to"] in subtree_ids
    ]
    return {
        "mode": "subtree", "root": node_id,
        "nodeCount": len(subtree_ids),
        "nodes": [slim_node(nm[i]) for i in subtree_ids if i in nm],
        "edges": subtree_edges,
        "summary": f"Subtree of {node_id}: {len(subtree_ids)} modules"
    }


def proj_critical(data: dict, top: int = 10) -> dict:
    nm = node_map(data["nodes"])
    critical = data["analysis"].get("criticalNodes", [])[:top]
    return {
        "mode": "critical",
        "nodes": [slim_node(nm[c["id"]]) | {"fanIn": c["fanIn"]} for c in critical if c["id"] in nm],
        "summary": f"Top {len(critical)} highest-impact modules"
    }


def proj_entry_points(data: dict) -> dict:
    ENTRY_HINTS = {"app", "application", "main", "boot", "server", "gateway",
                   "frontend", "webapp", "web", "ui", "cli", "runner"}
    nm = node_map(data["nodes"])
    entries = [
        n for n in data["nodes"]
        if any(hint in n.get("label","").lower() or hint in n.get("path","").lower()
               for hint in ENTRY_HINTS)
    ]
    return {
        "mode": "entry-points",
        "nodes": [slim_node(n) for n in entries],
        "summary": f"{len(entries)} probable entry-point module(s)"
    }


def proj_longest_path(data: dict) -> dict:
    """Find the longest dependency chain (critical path for latency)."""
    nm = node_map(data["nodes"])
    adj = defaultdict(list)
    for e in data["edges"]:
        if e.get("type") not in ("test",):
            adj[e["from"]].append(e["to"])

    memo = {}

    def longest_from(node, visiting=None):
        if visiting is None:
            visiting = set()
        if node in memo:
            return memo[node]
        if node in visiting:  # cycle guard
            return [node]
        visiting.add(node)
        best = [node]
        for nxt in adj.get(node, []):
            candidate = [node] + longest_from(nxt, visiting.copy())
            if len(candidate) > len(best):
                best = candidate
        memo[node] = best
        return best

    all_paths = [longest_from(n["id"]) for n in data["nodes"]]
    top5 = sorted(all_paths, key=len, reverse=True)[:5]

    return {
        "mode": "longest-path",
        "longestChains": [
            {"length": len(p), "path": p}
            for p in top5
        ],
        "summary": f"Longest chain: {len(top5[0])} hops" if top5 else "No paths found"
    }


# ─── Slim node: strip bulky impactSet to save tokens ───────────────────────

def slim_node(n: dict) -> dict:
    """Return node without impactSet (large array — loaded separately on demand)."""
    return {k: v for k, v in n.items() if k != "impactSet"}


# ─── CLI entrypoint ─────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Sparse graph projection extractor")
    p.add_argument("--graph",  required=True, help="Path to repo-graph.json")
    p.add_argument("--mode",   required=True,
                   choices=["index","fan-in","fan-out","impact","path",
                             "cycles","dead","subtree","critical","entry-points","longest-path"])
    p.add_argument("--node",   help="Focal node ID (fan-in/fan-out/impact/subtree)")
    p.add_argument("--from",   dest="from_node", help="Source node (path mode)")
    p.add_argument("--to",     dest="to_node",   help="Target node (path mode)")
    p.add_argument("--top",    type=int, default=10, help="Top N for critical mode")
    args = p.parse_args()

    data = load_graph(args.graph)

    dispatch = {
        "index":        lambda: proj_index(data),
        "fan-in":       lambda: proj_fan_in(data, args.node),
        "fan-out":      lambda: proj_fan_out(data, args.node),
        "impact":       lambda: proj_impact(data, args.node),
        "path":         lambda: proj_path(data, args.from_node, args.to_node),
        "cycles":       lambda: proj_cycles(data),
        "dead":         lambda: proj_dead(data),
        "subtree":      lambda: proj_subtree(data, args.node),
        "critical":     lambda: proj_critical(data, args.top),
        "entry-points": lambda: proj_entry_points(data),
        "longest-path": lambda: proj_longest_path(data),
    }

    result = dispatch[args.mode]()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
