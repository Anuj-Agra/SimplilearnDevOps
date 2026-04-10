#!/usr/bin/env python3
"""
cycle_detector.py — Detect circular dependencies in repo-graph.json

Usage:
    python3 cycle_detector.py repo-graph.json
    python3 cycle_detector.py repo-graph.json --only-internal
    python3 cycle_detector.py repo-graph.json --output cycles.json
"""

import json
import sys
import argparse
from collections import defaultdict


def load_graph(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def build_adj(nodes: list, edges: list, skip_test: bool = True) -> dict:
    """Build adjacency list from nodes and edges."""
    adj = defaultdict(set)
    ids = {n["id"] for n in nodes}
    for e in edges:
        if skip_test and e.get("type") == "test":
            continue
        if e["from"] in ids and e["to"] in ids:
            adj[e["from"]].add(e["to"])
    return adj


def find_cycles(adj: dict) -> list[list[str]]:
    """Johnson's algorithm — find all simple cycles."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in adj}
    cycles = []
    stack = []

    def dfs(node):
        color[node] = GREY
        stack.append(node)
        for neighbour in adj.get(node, []):
            if color[neighbour] == GREY:
                # Found a cycle — extract it
                idx = stack.index(neighbour)
                cycle = stack[idx:] + [neighbour]
                cycles.append(cycle)
            elif color[neighbour] == WHITE:
                dfs(neighbour)
        stack.pop()
        color[node] = BLACK

    for node in list(adj.keys()):
        if color[node] == WHITE:
            dfs(node)

    # Deduplicate (normalise by rotating to smallest element)
    seen = set()
    unique = []
    for c in cycles:
        core = c[:-1]  # remove repeated first element at end
        min_idx = core.index(min(core))
        normalised = tuple(core[min_idx:] + core[:min_idx])
        if normalised not in seen:
            seen.add(normalised)
            unique.append(list(normalised) + [normalised[0]])  # close the loop
    return unique


def main():
    parser = argparse.ArgumentParser(description="Detect circular dependencies")
    parser.add_argument("graph", help="Path to repo-graph.json")
    parser.add_argument("--include-test", action="store_true",
                        help="Include test-scoped edges in cycle detection")
    parser.add_argument("--output", help="Write results to JSON file")
    args = parser.parse_args()

    data = load_graph(args.graph)
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    adj = build_adj(nodes, edges, skip_test=not args.include_test)
    cycles = find_cycles(adj)

    result = {
        "totalCycles": len(cycles),
        "cycles": [
            {
                "length": len(c) - 1,
                "path": c,
                "modules": list(set(c))
            }
            for c in sorted(cycles, key=lambda x: len(x), reverse=True)
        ],
        "nodesInAnyCycle": list({m for c in cycles for m in c})
    }

    print(f"\n🔴 Found {len(cycles)} circular dependency cycle(s)\n")
    for i, cycle in enumerate(result["cycles"], 1):
        print(f"  Cycle {i} (length {cycle['length']}): {' → '.join(cycle['path'])}")

    if not cycles:
        print("  ✅ No circular dependencies detected!")

    print(f"\n  Modules involved in cycles: {len(result['nodesInAnyCycle'])}")
    for m in sorted(result["nodesInAnyCycle"]):
        print(f"    - {m}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n  Results written to {args.output}")

    return result


if __name__ == "__main__":
    main()
