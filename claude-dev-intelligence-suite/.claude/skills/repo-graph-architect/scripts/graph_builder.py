#!/usr/bin/env python3
"""
graph_builder.py — Assemble repo-graph.json from collected scan data.

Usage:
    python3 graph_builder.py \
        --nodes nodes.jsonl \
        --edges edges.jsonl \
        --repo-root /path/to/repo \
        --output repo-graph.json

Input formats:
  nodes.jsonl — one JSON object per line:
    {"id":"service-a:core","label":"core","parent":"service-a",
     "type":"submodule","path":"service-a/core","language":"java",
     "linesOfCode":2400,"fileCount":34}

  edges.jsonl — one JSON object per line:
    {"from":"service-a:core","to":"shared-lib","type":"compile",
     "declaredIn":"service-a/core/pom.xml","version":"2.1.0"}
"""

import json
import sys
import argparse
from collections import defaultdict
from datetime import datetime, timezone


def load_jsonl(path: str) -> list:
    items = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def compute_metrics(nodes: list, edges: list) -> dict:
    """Compute fan-in, fan-out, instability per node."""
    fan_in  = defaultdict(int)
    fan_out = defaultdict(int)

    for e in edges:
        if e.get("type") != "test":
            fan_out[e["from"]] += 1
            fan_in[e["to"]]    += 1

    metrics = {}
    for n in nodes:
        nid = n["id"]
        fo = fan_out[nid]
        fi = fan_in[nid]
        total = fi + fo
        metrics[nid] = {
            "fanIn":       fi,
            "fanOut":      fo,
            "instability": round(fo / total, 3) if total > 0 else 0.0,
        }
    return metrics


def build_impact_map(nodes: list, edges: list) -> dict:
    """For each node, compute its full reverse-dependency (impact) set."""
    # Reverse adjacency: who depends on me?
    rev_adj = defaultdict(set)
    for e in edges:
        if e.get("type") != "test":
            rev_adj[e["to"]].add(e["from"])

    node_ids = {n["id"] for n in nodes}

    def bfs_reverse(start: str) -> list[str]:
        visited = set()
        queue = [start]
        while queue:
            curr = queue.pop(0)
            for dep in rev_adj.get(curr, []):
                if dep not in visited and dep in node_ids:
                    visited.add(dep)
                    queue.append(dep)
        return sorted(visited)

    return {n["id"]: bfs_reverse(n["id"]) for n in nodes}


def detect_dead_modules(nodes: list, edges: list) -> list[str]:
    """Modules with fan-in=0 that are not likely entry-points."""
    ENTRY_POINT_HINTS = {
        "app", "application", "main", "boot", "server", "gateway",
        "frontend", "webapp", "web", "ui", "cli", "runner"
    }
    depended_on = {e["to"] for e in edges}
    dead = []
    for n in nodes:
        if n["id"] not in depended_on:
            label_lower = n.get("label", "").lower()
            path_lower  = n.get("path", "").lower()
            is_entry = any(hint in label_lower or hint in path_lower
                          for hint in ENTRY_POINT_HINTS)
            if not is_entry and n.get("type") != "repo":
                dead.append(n["id"])
    return sorted(dead)


def detect_critical_nodes(metrics: dict, top_n: int = 10) -> list[dict]:
    """Return top N nodes by fan-in (most depended upon)."""
    ranked = sorted(metrics.items(), key=lambda x: x[1]["fanIn"], reverse=True)
    return [{"id": nid, "fanIn": m["fanIn"]} for nid, m in ranked[:top_n]
            if m["fanIn"] > 0]


def detect_cycles(nodes: list, edges: list) -> list[list]:
    """Simple DFS cycle detection."""
    adj = defaultdict(set)
    ids = {n["id"] for n in nodes}
    for e in edges:
        if e.get("type") != "test" and e["from"] in ids and e["to"] in ids:
            adj[e["from"]].add(e["to"])

    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in ids}
    cycles, stack = [], []

    def dfs(node):
        color[node] = GREY
        stack.append(node)
        for nb in adj.get(node, []):
            if color.get(nb) == GREY:
                idx = stack.index(nb)
                cycles.append(stack[idx:] + [nb])
            elif color.get(nb) == WHITE:
                dfs(nb)
        stack.pop()
        color[node] = BLACK

    for node in list(ids):
        if color[node] == WHITE:
            dfs(node)

    # Deduplicate
    seen, unique = set(), []
    for c in cycles:
        core = c[:-1]
        if not core:
            continue
        min_idx = core.index(min(core))
        key = tuple(core[min_idx:] + core[:min_idx])
        if key not in seen:
            seen.add(key)
            unique.append(list(key) + [key[0]])
    return unique


def main():
    parser = argparse.ArgumentParser(description="Build repo-graph.json")
    parser.add_argument("--nodes",     required=True)
    parser.add_argument("--edges",     required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--build-system", default="unknown")
    parser.add_argument("--output",    default="repo-graph.json")
    args = parser.parse_args()

    nodes = load_jsonl(args.nodes)
    edges = load_jsonl(args.edges)

    print(f"  Loaded {len(nodes)} nodes, {len(edges)} edges")

    metrics    = compute_metrics(nodes, edges)
    impact_map = build_impact_map(nodes, edges)
    dead       = detect_dead_modules(nodes, edges)
    critical   = detect_critical_nodes(metrics)
    cycles     = detect_cycles(nodes, edges)

    # Enrich nodes with metrics
    for n in nodes:
        n["metrics"] = metrics.get(n["id"], {"fanIn":0,"fanOut":0,"instability":0})
        n["impactSet"] = impact_map.get(n["id"], [])

    total_loc = sum(n.get("linesOfCode", 0) for n in nodes)

    graph = {
        "meta": {
            "repoRoot":      args.repo_root,
            "generatedAt":   datetime.now(timezone.utc).isoformat(),
            "buildSystem":   args.build_system,
            "totalModules":  len(nodes),
            "totalEdges":    len(edges),
            "totalLinesOfCode": total_loc,
        },
        "nodes": nodes,
        "edges": edges,
        "analysis": {
            "circularDependencies": cycles,
            "deadModules":          dead,
            "criticalNodes":        critical,
            "impactMap":            impact_map,
        }
    }

    with open(args.output, "w") as f:
        json.dump(graph, f, indent=2)

    print(f"\n  ✅ repo-graph.json written ({len(nodes)} nodes, {len(edges)} edges)")
    print(f"  🔴 Circular deps: {len(cycles)}")
    print(f"  ⚫ Dead modules:  {len(dead)}")
    print(f"  ⚠️  Critical nodes: {[c['id'] for c in critical[:3]]}")


if __name__ == "__main__":
    main()
