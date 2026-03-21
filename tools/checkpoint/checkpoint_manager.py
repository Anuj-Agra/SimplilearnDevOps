"""
tools/checkpoint/checkpoint_manager.py

Saves and restores the complete analysis state for a workspace.
Enables resumption after LLM token limit is reached mid-analysis.

Workspace layout (created automatically):
  workspaces/{workflow_name}/
    manifest.json          — master list of all rules + their status
    rule_graph.json        — full rule dependency graph
    queue.json             — ordered list of rule_ids still to analyse
    session_log.jsonl      — one JSON line per completed LLM call
    rules/                 — one .parsed.json per rule (phase-1 output)
    analysis/              — one .md per rule per output type (phase-2 output)
      {rule_id}.narrative.md
      {rule_id}.frd-fragment.md
      {rule_id}.jira-fragment.md
      {rule_id}.ac-fragment.md
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ─── Manifest entry ───────────────────────────────────────────────────────────

@dataclass
class ManifestEntry:
    rule_id:      str               # "{class}::{rule_name}"
    rule_name:    str
    rule_class:   str
    rule_type:    str
    depth:        int
    priority:     int
    status:       str = "pending"   # pending | in_progress | done | failed | skipped
    agent_used:   str = ""
    started_at:   str = ""
    completed_at: str = ""
    error:        str = ""
    outputs:      list[str] = field(default_factory=list)  # list of output file paths

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ManifestEntry":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ─── Checkpoint manager ───────────────────────────────────────────────────────

class CheckpointManager:
    """
    Manages persistent checkpoint state for a single workflow workspace.
    Thread-safe for single-process use; does not support concurrent writers.
    """

    MANIFEST_FILE    = "manifest.json"
    QUEUE_FILE       = "queue.json"
    GRAPH_FILE       = "rule_graph.json"
    SESSION_LOG_FILE = "session_log.jsonl"

    def __init__(self, workspace_path: Path):
        self.workspace  = workspace_path
        self.rules_dir  = workspace_path / "rules"
        self.analysis_dir = workspace_path / "analysis"
        self.context_dir  = workspace_path / "context"

        self._manifest: dict[str, ManifestEntry] = {}
        self._queue:    list[str] = []               # ordered list of rule_ids
        self._session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

        self._ensure_dirs()

    def _ensure_dirs(self):
        for d in (self.workspace, self.rules_dir, self.analysis_dir, self.context_dir):
            d.mkdir(parents=True, exist_ok=True)

    # ── Initialisation ────────────────────────────────────────────────────────

    def initialise(self, nodes: list, overwrite: bool = False):
        """
        Populate manifest and queue from a list of RuleNode objects.
        Call once at the start of a new workflow (or with overwrite=True to reset).
        """
        manifest_path = self.workspace / self.MANIFEST_FILE
        if manifest_path.exists() and not overwrite:
            logger.info("Checkpoint exists — loading existing state (use overwrite=True to reset)")
            self.load()
            return

        self._manifest = {}
        self._queue    = []

        for node in nodes:
            entry = ManifestEntry(
                rule_id=node.node_id,
                rule_name=node.rule_name,
                rule_class=node.rule_class,
                rule_type=node.rule_type,
                depth=node.depth,
                priority=node.priority,
            )
            self._manifest[node.node_id] = entry
            self._queue.append(node.node_id)

        self.save()
        logger.info(
            "Checkpoint initialised: %d rules queued in %s",
            len(self._queue), self.workspace
        )

    # ── Save / load ───────────────────────────────────────────────────────────

    def save(self):
        """Persist manifest and queue to disk."""
        manifest_data = {rid: e.to_dict() for rid, e in self._manifest.items()}
        (self.workspace / self.MANIFEST_FILE).write_text(
            json.dumps(manifest_data, indent=2), encoding="utf-8"
        )
        (self.workspace / self.QUEUE_FILE).write_text(
            json.dumps(self._queue, indent=2), encoding="utf-8"
        )

    def load(self):
        """Load manifest and queue from disk."""
        manifest_path = self.workspace / self.MANIFEST_FILE
        queue_path    = self.workspace / self.QUEUE_FILE

        if manifest_path.exists():
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            self._manifest = {rid: ManifestEntry.from_dict(e) for rid, e in data.items()}

        if queue_path.exists():
            self._queue = json.loads(queue_path.read_text(encoding="utf-8"))

        logger.info(
            "Checkpoint loaded: %d rules, %d pending",
            len(self._manifest), len(self.pending_ids())
        )

    # ── Queue management ──────────────────────────────────────────────────────

    def next_rule(self) -> Optional[ManifestEntry]:
        """Return the next pending rule from the queue, or None if queue is empty."""
        for rule_id in self._queue:
            entry = self._manifest.get(rule_id)
            if entry and entry.status == "pending":
                return entry
        return None

    def peek_queue(self, n: int = 10) -> list[ManifestEntry]:
        """Return the next n pending rules without consuming them."""
        result = []
        for rule_id in self._queue:
            entry = self._manifest.get(rule_id)
            if entry and entry.status == "pending":
                result.append(entry)
                if len(result) >= n:
                    break
        return result

    def pending_ids(self) -> list[str]:
        return [
            rid for rid in self._queue
            if self._manifest.get(rid) and self._manifest[rid].status == "pending"
        ]

    def done_ids(self) -> list[str]:
        return [rid for rid, e in self._manifest.items() if e.status == "done"]

    def failed_ids(self) -> list[str]:
        return [rid for rid, e in self._manifest.items() if e.status == "failed"]

    # ── Status updates ────────────────────────────────────────────────────────

    def mark_in_progress(self, rule_id: str, agent: str = ""):
        entry = self._manifest.get(rule_id)
        if entry:
            entry.status     = "in_progress"
            entry.agent_used = agent
            entry.started_at = datetime.now(timezone.utc).isoformat()
            self.save()

    def mark_done(self, rule_id: str, output_paths: list[str] = None):
        entry = self._manifest.get(rule_id)
        if entry:
            entry.status       = "done"
            entry.completed_at = datetime.now(timezone.utc).isoformat()
            entry.outputs      = output_paths or []
            self.save()
            self._log_session_event(rule_id, "done", output_paths or [])

    def mark_failed(self, rule_id: str, error: str = ""):
        entry = self._manifest.get(rule_id)
        if entry:
            entry.status = "failed"
            entry.error  = error
            self.save()
            self._log_session_event(rule_id, "failed", [], error)

    def mark_skipped(self, rule_id: str, reason: str = ""):
        entry = self._manifest.get(rule_id)
        if entry:
            entry.status = "skipped"
            entry.error  = reason
            self.save()

    def reset_in_progress(self):
        """
        Reset any 'in_progress' rules back to 'pending'.
        Call at session start to recover from a crashed previous session.
        """
        reset_count = 0
        for entry in self._manifest.values():
            if entry.status == "in_progress":
                entry.status = "pending"
                reset_count += 1
        if reset_count:
            self.save()
            logger.info("Reset %d in-progress rules to pending", reset_count)

    # ── Output file management ────────────────────────────────────────────────

    def save_parsed_rule(self, rule_id: str, parsed: dict) -> Path:
        """Save a phase-1 parsed rule summary."""
        safe_id = _safe_filename(rule_id)
        path = self.rules_dir / f"{safe_id}.parsed.json"
        path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
        return path

    def load_parsed_rule(self, rule_id: str) -> Optional[dict]:
        safe_id = _safe_filename(rule_id)
        path = self.rules_dir / f"{safe_id}.parsed.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def save_analysis(self, rule_id: str, output_type: str, content: str) -> Path:
        """
        Save agent analysis output.
        output_type: 'narrative' | 'frd-fragment' | 'jira-fragment' | 'ac-fragment'
        """
        safe_id = _safe_filename(rule_id)
        path = self.analysis_dir / f"{safe_id}.{output_type}.md"
        path.write_text(content, encoding="utf-8")
        return path

    def load_analysis(self, rule_id: str, output_type: str) -> Optional[str]:
        safe_id = _safe_filename(rule_id)
        path = self.analysis_dir / f"{safe_id}.{output_type}.md"
        return path.read_text(encoding="utf-8") if path.exists() else None

    def save_context_bundle(self, rule_id: str, context: dict) -> Path:
        """
        Save the assembled LLM context bundle for a rule.
        This is what gets passed to the agent — rule content + dependency summaries.
        """
        safe_id = _safe_filename(rule_id)
        path = self.context_dir / f"{safe_id}.context.json"
        path.write_text(json.dumps(context, indent=2), encoding="utf-8")
        return path

    def load_context_bundle(self, rule_id: str) -> Optional[dict]:
        safe_id = _safe_filename(rule_id)
        path = self.context_dir / f"{safe_id}.context.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    # ── Aggregated outputs ───────────────────────────────────────────────────

    def aggregate_narratives(self) -> str:
        """Concatenate all narrative outputs into a single markdown document."""
        parts = [
            f"# KYC Codebase Analysis — Full Flow Narrative\n",
            f"Generated: {datetime.now().isoformat()}\n",
            f"Workspace: {self.workspace}\n\n---\n"
        ]
        for entry in sorted(self._manifest.values(), key=lambda e: (e.depth, e.priority)):
            if entry.status == "done":
                content = self.load_analysis(entry.rule_id, "narrative")
                if content:
                    parts.append(f"\n\n## {entry.rule_type}: {entry.rule_name}\n")
                    parts.append(content)
        return "\n".join(parts)

    def aggregate_frd_fragments(self) -> str:
        parts = ["# KYC Codebase Analysis — FRD Fragments\n\n---\n"]
        for entry in sorted(self._manifest.values(), key=lambda e: (e.depth, e.priority)):
            if entry.status == "done":
                content = self.load_analysis(entry.rule_id, "frd-fragment")
                if content:
                    parts.append(f"\n\n## {entry.rule_type}: {entry.rule_name}\n")
                    parts.append(content)
        return "\n".join(parts)

    # ── Progress reporting ────────────────────────────────────────────────────

    def progress_report(self) -> dict:
        total    = len(self._manifest)
        done     = len(self.done_ids())
        failed   = len(self.failed_ids())
        pending  = len(self.pending_ids())
        skipped  = sum(1 for e in self._manifest.values() if e.status == "skipped")

        by_type = {}
        for entry in self._manifest.values():
            t = entry.rule_type
            if t not in by_type:
                by_type[t] = {"total": 0, "done": 0, "pending": 0, "failed": 0}
            by_type[t]["total"] += 1
            if entry.status == "done":
                by_type[t]["done"] += 1
            elif entry.status == "pending":
                by_type[t]["pending"] += 1
            elif entry.status == "failed":
                by_type[t]["failed"] += 1

        return {
            "workspace":      str(self.workspace),
            "total":          total,
            "done":           done,
            "failed":         failed,
            "pending":        pending,
            "skipped":        skipped,
            "pct_complete":   round(done / total * 100, 1) if total else 0,
            "by_rule_type":   by_type,
            "next_pending":   self.next_rule().rule_id if self.next_rule() else None,
        }

    def print_progress(self):
        r = self.progress_report()
        print(f"\n{'='*60}")
        print(f"  Workspace: {r['workspace']}")
        print(f"  Progress:  {r['done']}/{r['total']} ({r['pct_complete']}% complete)")
        print(f"  Pending:   {r['pending']}  |  Failed: {r['failed']}  |  Skipped: {r['skipped']}")
        print(f"\n  By rule type:")
        for rtype, counts in sorted(r["by_rule_type"].items()):
            bar = "█" * counts["done"] + "░" * counts["pending"]
            print(f"    {rtype:<30} {counts['done']:>3}/{counts['total']:<3}  {bar}")
        if r["next_pending"]:
            print(f"\n  Next: {r['next_pending']}")
        print(f"{'='*60}\n")

    # ── Session log ───────────────────────────────────────────────────────────

    def _log_session_event(self, rule_id: str, status: str, outputs: list, error: str = ""):
        log_path = self.workspace / self.SESSION_LOG_FILE
        event = {
            "ts":         datetime.now(timezone.utc).isoformat(),
            "session_id": self._session_id,
            "rule_id":    rule_id,
            "status":     status,
            "outputs":    outputs,
            "error":      error,
        }
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _safe_filename(rule_id: str) -> str:
    """Convert a rule_id like 'KYC-Work-CDD::KYC_CDDOnboarding' to a safe filename."""
    return rule_id.replace("::", "__").replace("/", "_").replace("\\", "_")
