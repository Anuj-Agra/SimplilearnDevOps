"""
tools/traversal/rule_graph.py

Builds a directed dependency graph of all PEGA rules in a workspace.

  node  = a PEGA rule  (identified by pyRuleName + pyClassName)
  edge  = a reference from one rule to another

The graph enables:
  - BFS/DFS traversal in dependency order
  - Detection of circular references
  - Identification of orphaned rules
  - Priority-ordered analysis queue generation
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

from .reference_extractor import extract_references, RuleRef

logger = logging.getLogger(__name__)


# ─── Node ─────────────────────────────────────────────────────────────────────

@dataclass
class RuleNode:
    rule_name:  str
    rule_class: str
    rule_type:  str
    file_path:  Optional[Path] = None      # Path to raw JSON/BIN file
    parsed:     Optional[dict] = None      # Loaded and parsed rule dict
    status:     str = "pending"            # pending | in_progress | done | failed | skipped
    references: list[RuleRef] = field(default_factory=list)   # outbound refs
    referenced_by: list[str] = field(default_factory=list)    # inbound refs (rule_names)
    priority:   int = 5
    depth:      int = 0                    # depth from root CaseType node

    @property
    def node_id(self) -> str:
        return f"{self.rule_class}::{self.rule_name}"

    def to_dict(self) -> dict:
        return {
            "rule_name":     self.rule_name,
            "rule_class":    self.rule_class,
            "rule_type":     self.rule_type,
            "file_path":     str(self.file_path) if self.file_path else None,
            "status":        self.status,
            "priority":      self.priority,
            "depth":         self.depth,
            "referenced_by": self.referenced_by,
            "references":    [
                {
                    "rule_name":  r.rule_name,
                    "rule_class": r.rule_class,
                    "rule_type":  r.rule_type,
                    "source_field": r.source_field,
                    "is_async":   r.is_async,
                    "priority":   r.priority,
                }
                for r in self.references
            ],
        }


# ─── Graph ────────────────────────────────────────────────────────────────────

class RuleGraph:
    """
    Directed graph of PEGA rules.
    Nodes are keyed by node_id = "{class}::{rule_name}".
    """

    def __init__(self):
        self._nodes: dict[str, RuleNode] = {}
        self._root_id: Optional[str] = None

    # ── Construction ──────────────────────────────────────────────────────────

    def add_node(self, node: RuleNode) -> RuleNode:
        """Add or update a node. Returns the (possibly existing) node."""
        nid = node.node_id
        if nid not in self._nodes:
            self._nodes[nid] = node
        else:
            # Merge: update file_path and parsed if missing
            existing = self._nodes[nid]
            if node.file_path and not existing.file_path:
                existing.file_path = node.file_path
            if node.parsed and not existing.parsed:
                existing.parsed = node.parsed
            if node.rule_type and not existing.rule_type:
                existing.rule_type = node.rule_type
        return self._nodes[nid]

    def add_edge(self, ref: RuleRef):
        """Record a reference from source_rule to (rule_name, rule_class)."""
        target_node = self._get_or_create(
            ref.rule_name, ref.rule_class, ref.rule_type
        )
        source_id = f"{ref.rule_class}::{ref.source_rule}"

        if source_id in self._nodes:
            source_node = self._nodes[source_id]
            if ref not in source_node.references:
                source_node.references.append(ref)

        if ref.source_rule not in target_node.referenced_by:
            target_node.referenced_by.append(ref.source_rule)

    def _get_or_create(self, rule_name: str, rule_class: str, rule_type: str) -> RuleNode:
        nid = f"{rule_class}::{rule_name}"
        if nid not in self._nodes:
            self._nodes[nid] = RuleNode(
                rule_name=rule_name,
                rule_class=rule_class,
                rule_type=rule_type
            )
        return self._nodes[nid]

    def set_root(self, node_id: str):
        self._root_id = node_id

    # ── File loading ─────────────────────────────────────────────────────────

    @classmethod
    def from_directory(cls, rules_dir: Path, root_casetype: Optional[str] = None) -> "RuleGraph":
        """
        Load all .json rule files from rules_dir, build nodes, extract references.
        Optionally specify the root CaseType rule name to set traversal start.
        """
        graph = cls()
        files = list(rules_dir.glob("**/*.json"))
        logger.info("Loading %d rule files from %s", len(files), rules_dir)

        for fpath in files:
            try:
                rule = json.loads(fpath.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Could not load %s: %s", fpath, e)
                continue

            rule_name  = rule.get("pyRuleName", fpath.stem)
            rule_class = rule.get("pyClassName", "")
            rule_type  = rule.get("pxObjClass",  "")

            node = RuleNode(
                rule_name=rule_name,
                rule_class=rule_class,
                rule_type=rule_type,
                file_path=fpath,
                parsed=rule,
                priority=_priority_for_type(rule_type)
            )
            graph.add_node(node)

        # Second pass: extract all references and build edges
        for node in list(graph._nodes.values()):
            if node.parsed:
                refs = extract_references(node.parsed)
                node.references = refs
                for ref in refs:
                    graph.add_edge(ref)

        # Set root
        if root_casetype:
            for nid, node in graph._nodes.items():
                if node.rule_name == root_casetype and node.rule_type == "Rule-Obj-CaseType":
                    graph._root_id = nid
                    node.depth = 0
                    break
            graph._assign_depths()

        return graph

    def _assign_depths(self):
        """BFS from root to assign depth values."""
        if not self._root_id or self._root_id not in self._nodes:
            return
        visited = set()
        queue = deque([(self._root_id, 0)])
        while queue:
            nid, depth = queue.popleft()
            if nid in visited:
                continue
            visited.add(nid)
            if nid in self._nodes:
                self._nodes[nid].depth = depth
                for ref in self._nodes[nid].references:
                    child_id = f"{ref.rule_class}::{ref.rule_name}"
                    if child_id not in visited:
                        queue.append((child_id, depth + 1))

    # ── Traversal ─────────────────────────────────────────────────────────────

    def analysis_queue(self, include_async: bool = True) -> list[RuleNode]:
        """
        Return nodes in BFS order from root, sorted by (depth, priority).
        Excludes nodes without file_path (referenced but not found on disk).
        """
        if not self._root_id:
            # No root: return all nodes sorted by priority
            nodes = [n for n in self._nodes.values() if n.file_path]
            return sorted(nodes, key=lambda n: (n.priority, n.rule_name))

        visited:   set[str]   = set()
        queue:     deque[str] = deque([self._root_id])
        result:    list[RuleNode] = []

        while queue:
            nid = queue.popleft()
            if nid in visited:
                continue
            visited.add(nid)

            node = self._nodes.get(nid)
            if not node:
                continue

            if node.file_path:   # only include rules we have files for
                result.append(node)

            # Enqueue children sorted by (priority, async)
            children = sorted(
                node.references,
                key=lambda r: (r.is_async, r.priority, r.rule_name)
            )
            for ref in children:
                if not ref.is_async or include_async:
                    child_id = f"{ref.rule_class}::{ref.rule_name}"
                    if child_id not in visited:
                        queue.append(child_id)

        return result

    def pending_nodes(self) -> list[RuleNode]:
        """Return all nodes with status='pending' that have a file_path."""
        return [
            n for n in self._nodes.values()
            if n.status == "pending" and n.file_path
        ]

    def find_cycles(self) -> list[list[str]]:
        """Detect circular references using DFS. Returns list of cycle paths."""
        cycles  = []
        visited = set()
        path    = []

        def dfs(nid: str):
            if nid in path:
                cycle_start = path.index(nid)
                cycles.append(path[cycle_start:] + [nid])
                return
            if nid in visited:
                return
            visited.add(nid)
            path.append(nid)
            node = self._nodes.get(nid)
            if node:
                for ref in node.references:
                    dfs(f"{ref.rule_class}::{ref.rule_name}")
            path.pop()

        for nid in list(self._nodes.keys()):
            dfs(nid)

        return cycles

    def missing_references(self) -> list[tuple[str, RuleRef]]:
        """Return references where the target rule has no file_path (not found on disk)."""
        missing = []
        for node in self._nodes.values():
            for ref in node.references:
                target_id = f"{ref.rule_class}::{ref.rule_name}"
                target = self._nodes.get(target_id)
                if not target or not target.file_path:
                    missing.append((node.node_id, ref))
        return missing

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "root_id":    self._root_id,
            "node_count": len(self._nodes),
            "nodes":      {nid: node.to_dict() for nid, node in self._nodes.items()},
        }

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        logger.info("Rule graph saved to %s (%d nodes)", path, len(self._nodes))

    @classmethod
    def load(cls, path: Path) -> "RuleGraph":
        data = json.loads(path.read_text(encoding="utf-8"))
        graph = cls()
        graph._root_id = data.get("root_id")
        for nid, node_data in data.get("nodes", {}).items():
            fp = node_data.get("file_path")
            node = RuleNode(
                rule_name=node_data["rule_name"],
                rule_class=node_data["rule_class"],
                rule_type=node_data["rule_type"],
                file_path=Path(fp) if fp else None,
                status=node_data.get("status", "pending"),
                priority=node_data.get("priority", 5),
                depth=node_data.get("depth", 0),
                referenced_by=node_data.get("referenced_by", []),
            )
            graph._nodes[nid] = node
        logger.info("Rule graph loaded from %s (%d nodes)", path, len(graph._nodes))
        return graph

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        by_type   = defaultdict(int)
        by_status = defaultdict(int)
        for node in self._nodes.values():
            by_type[node.rule_type]   += 1
            by_status[node.status]    += 1
        return {
            "total_nodes":   len(self._nodes),
            "has_file":      sum(1 for n in self._nodes.values() if n.file_path),
            "by_type":       dict(by_type),
            "by_status":     dict(by_status),
            "cycles":        len(self.find_cycles()),
            "missing_refs":  len(self.missing_references()),
        }

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self) -> Iterator[RuleNode]:
        return iter(self._nodes.values())


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _priority_for_type(rule_type: str) -> int:
    """Lower number = higher analysis priority."""
    return {
        "Rule-Obj-CaseType":    1,
        "Rule-Obj-Flow":        2,
        "Rule-Obj-Activity":    4,
        "Rule-Obj-Flowsection": 3,
        "Rule-HTML-Section":    5,
        "Rule-Obj-When":        8,
    }.get(rule_type, 6)
