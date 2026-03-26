"""
tools/runner/recursive_analyser.py

Main analysis engine. Drives the recursive analysis loop:

  1. Load rule graph from workspace
  2. Pop next pending rule from checkpoint queue
  3. Assemble bounded context (rule + dependencies + skills)
  4. Call the appropriate agent via Anthropic API
  5. Save output to workspace
  6. Mark checkpoint done
  7. Repeat until queue empty OR token budget exceeded

Designed to be re-run safely after interruption — it always picks up
exactly where the last session left off.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

import anthropic

from ..traversal.rule_graph import RuleGraph
from ..checkpoint.checkpoint_manager import CheckpointManager, ManifestEntry
from ..checkpoint.context_assembler import ContextAssembler

logger = logging.getLogger(__name__)

# ─── Agent system prompt templates (inline — no file I/O needed) ─────────────

AGENT_PROMPTS = {
    "Rule-Obj-CaseType": """\
You are a PEGA Principal Architect analysing a KYC CaseType rule.
Produce a structured analysis with these sections:
1. Case overview (purpose, business function, regulatory context)
2. Lifecycle (stages in order, entry/exit conditions, final status)
3. Process inventory (all flows per stage, with business purpose)
4. Status transition map (all statuses and what triggers each)
5. Child cases (linked sub-cases and spawn conditions)
6. Access requirements (which roles interact with this case)
7. Gaps and anomalies (missing exit conditions, broken references, etc.)
Be concise but complete. Use tables where helpful.
""",
    "Rule-Obj-Flow": """\
You are a PEGA Principal Architect analysing a KYC Flow rule.
Produce a structured analysis with these sections:
1. Flow purpose (what business process this implements)
2. Step-by-step narrative (plain English, numbered, with actor/system for each step)
3. Decision inventory (all branches with conditions and destinations)
4. Assignment steps (human tasks: actor, SLA, screen, workbasket)
5. External service calls (connector steps with data exchanged)
6. Sub-flows called (synchronous and async)
7. When conditions used (list rule names and their business meaning)
8. Terminal states (all End steps with their case status values)
9. Compliance notes (which regulatory obligations this flow fulfils)
10. Gaps and risks (unhandled errors, missing timeouts, orphaned steps)
""",
    "Rule-Obj-Activity": """\
You are a PEGA Principal Architect analysing a KYC Activity rule.
Produce a structured analysis with these sections:
1. Purpose (what business logic this activity encapsulates)
2. Parameters (inputs and outputs with types)
3. Step walkthrough (each step: method, what it does, error handling)
4. External calls (any Connect-* steps)
5. Called activities (recursive chain — list all)
6. Side effects (what data is written or saved)
7. When conditions used (list and explain)
8. Issues (silent failures, missing error handling, risky patterns)
""",
    "Rule-Obj-Flowsection": """\
You are a PEGA UX Architect analysing a KYC Flow Action rule.
Produce a structured analysis with these sections:
1. Purpose (what user action this screen supports, at which stage)
2. Screen rendered (Rule-HTML-Section name and what it shows)
3. Pre-processing (what the pre-activity does before the screen loads)
4. Post-processing (what happens after the user submits)
5. Validation (what validation activity runs)
6. Action buttons (what each button does, which flow connector it triggers)
7. Conditional behaviour (field visibility / read-only conditions)
8. Gaps (missing validation, no cancel button, etc.)
""",
    "Rule-HTML-Section": """\
You are a PEGA UX Architect analysing a KYC Section rule.
Produce a structured analysis with these sections:
1. Purpose (what part of the KYC screen this section provides)
2. Field inventory (table: field label | property | type | required | validation | condition)
3. Conditional fields (fields shown/hidden based on When rules — list each)
4. Embedded sections (nested sections and their conditions)
5. Data sources (dropdowns sourced from Data Pages — list each)
6. Repeating layouts (Page List property + row template if present)
7. Gaps (missing required fields, accessibility issues, missing labels)
""",
    "Rule-Obj-When": """\
You are a PEGA Business Analyst analysing a KYC When condition rule.
Produce a short structured analysis:
1. Business meaning (plain English translation of the expression)
2. Expression (the full PEGA expression)
3. Properties evaluated (list every property reference used)
4. Used in (list the rules that reference this When condition)
5. Edge cases (what happens at boundary values, null values, etc.)
""",
}

OUTPUT_TYPES = {
    "Rule-Obj-CaseType":    ["narrative"],
    "Rule-Obj-Flow":        ["narrative", "frd-fragment"],
    "Rule-Obj-Activity":    ["narrative"],
    "Rule-Obj-Flowsection": ["narrative"],
    "Rule-HTML-Section":    ["narrative"],
    "Rule-Obj-When":        ["narrative"],
}


# ─── Recursive analyser ───────────────────────────────────────────────────────

class RecursiveAnalyser:
    """
    Drives the complete recursive analysis of a PEGA KYC rule graph.
    Safe to interrupt and resume — state is checkpointed after every rule.

    Two construction modes:
      Legacy mode  (--rules-dir):  rules_dir points to flat directory of JSON files.
      Hierarchy mode (--config):   analysis_config is an AnalysisConfig from
                                   config_loader.load_config() — handles COB/CRDFWApp/
                                   MSFWApp/PegaRules folders, manifest selection, and
                                   BIN file extraction automatically.
    """

    def __init__(
        self,
        workspace: Path = None,
        rules_dir: Path = None,
        root_casetype: Optional[str] = None,
        max_rules_per_session: int = 50,
        skill_files: list[Path] = None,
        role_adapter_path: Optional[Path] = None,
        dry_run: bool = False,
        analysis_config=None,   # AnalysisConfig from config_loader.load_config()
    ):
        # ── Hierarchy mode — config object drives everything ──────────────────
        if analysis_config is not None:
            self._analysis_config      = analysis_config
            self.workspace             = Path(analysis_config.workspace)
            self.rules_dir             = None
            self.root_casetype         = analysis_config.root_casetype
            self.model                 = analysis_config.model
            self.max_rules_per_session = analysis_config.max_rules_per_session
            self.dry_run               = dry_run
            token_budget_per_rule      = analysis_config.token_budget_per_rule
        else:
            # ── Legacy mode — flat rules_dir of JSON files ────────────────────
            self._analysis_config      = None
            self.workspace             = Path(workspace)
            self.rules_dir             = Path(rules_dir) if rules_dir else None
            self.root_casetype         = root_casetype
            self.model                 = model
            self.max_rules_per_session = max_rules_per_session
            self.dry_run               = dry_run

        self.checkpoint = CheckpointManager(self.workspace)
        self.assembler  = ContextAssembler(
            self.checkpoint,
            token_budget=token_budget_per_rule
        )
        self.graph: Optional[RuleGraph] = None
        self._client = anthropic.Anthropic() if not dry_run else None

        # Load optional skill and role adapter content
        self._skill_context  = _load_text_files(skill_files or [])
        self._role_adapter   = Path(role_adapter_path).read_text(encoding="utf-8") \
                               if role_adapter_path and Path(role_adapter_path).exists() else ""

    # ── Phase 1: Build graph and initialise checkpoint ────────────────────────

    def phase1_build_graph(self, overwrite: bool = False) -> RuleGraph:
        """
        Parse all rule files, build the dependency graph, initialise the checkpoint.
        Does NOT call the LLM. Safe to run multiple times (idempotent with overwrite=False).

        In hierarchy mode: loads COB → CRDFWApp → MSFWApp → PegaRules using the
        AnalysisConfig (manifest selection, BIN extraction, most-specific-wins).
        In legacy mode: scans a flat directory of JSON rule files.
        """
        graph_path = self.workspace / "rule_graph.json"

        if graph_path.exists() and not overwrite:
            logger.info("Loading existing rule graph from %s", graph_path)
            self.graph = RuleGraph.load(graph_path)
        elif self._analysis_config is not None:
            # ── Hierarchy mode ────────────────────────────────────────────────
            logger.info("Building rule graph from 4-tier hierarchy (COB/CRDFWApp/MSFWApp/PegaRules)")
            self.graph = RuleGraph.from_hierarchy_config(self._analysis_config)
            self.graph.save(graph_path)
        else:
            # ── Legacy mode ───────────────────────────────────────────────────
            logger.info("Building rule graph from directory: %s", self.rules_dir)
            self.graph = RuleGraph.from_directory(self.rules_dir, self.root_casetype)
            self.graph.save(graph_path)

        # Print graph stats
        stats = self.graph.stats()
        logger.info("Rule graph: %s", json.dumps(stats, indent=2))

        # Report cycles (circular references) — these need manual review
        cycles = self.graph.find_cycles()
        if cycles:
            logger.warning("Circular references detected (%d cycles):", len(cycles))
            for cycle in cycles:
                logger.warning("  %s", " → ".join(cycle))

        # Report missing references
        missing = self.graph.missing_references()
        if missing:
            logger.warning(
                "%d rule references could not be resolved (files not found):", len(missing)
            )
            for source_id, ref in missing[:20]:
                logger.warning("  %s → %s (%s)", source_id, ref.rule_name, ref.rule_type)

        # Initialise checkpoint from analysis queue
        queue = self.graph.analysis_queue(include_async=True)
        self.checkpoint.initialise(queue, overwrite=overwrite)

        return self.graph

    # ── Phase 2: Analyse rules (LLM calls) ────────────────────────────────────

    def phase2_analyse(self, max_rules: Optional[int] = None) -> dict:
        """
        Main analysis loop. Processes pending rules from the checkpoint queue.
        Returns a progress report dict.
        Resumes automatically from the last checkpoint.
        """
        if not self.graph:
            graph_path = self.workspace / "rule_graph.json"
            if not graph_path.exists():
                raise RuntimeError("Rule graph not found. Run phase1_build_graph() first.")
            self.graph = RuleGraph.load(graph_path)

        self.checkpoint.load()
        self.checkpoint.reset_in_progress()   # recover from previous crashed session

        limit         = max_rules or self.max_rules_per_session
        rules_done    = 0
        casetype_sum  = self._load_casetype_summary()

        self.checkpoint.print_progress()

        while rules_done < limit:
            entry = self.checkpoint.next_rule()
            if not entry:
                logger.info("Queue empty — analysis complete.")
                break

            logger.info(
                "[%d/%d] Analysing %s (%s) depth=%d",
                rules_done + 1, limit, entry.rule_name, entry.rule_type, entry.depth
            )

            success = self._analyse_one(entry, casetype_sum)

            if success:
                rules_done += 1
                # If we just analysed a CaseType, refresh the casetype summary
                if entry.rule_type == "Rule-Obj-CaseType":
                    casetype_sum = self.checkpoint.load_analysis(entry.rule_id, "narrative") or ""
            else:
                logger.warning("Failed to analyse %s — continuing", entry.rule_id)

            # Brief pause to respect rate limits
            if not self.dry_run:
                time.sleep(0.5)

        self.checkpoint.print_progress()
        return self.checkpoint.progress_report()

    def _analyse_one(self, entry: ManifestEntry, casetype_summary: str) -> bool:
        """Analyse a single rule. Returns True on success."""
        rule_id = entry.rule_id
        self.checkpoint.mark_in_progress(rule_id, agent=entry.rule_type)

        # Load the raw rule JSON
        raw_rule = self.checkpoint.load_parsed_rule(rule_id)
        if not raw_rule:
            # Try loading from the original file path
            node = self._find_node(rule_id)
            if node and node.file_path and node.file_path.exists():
                raw_rule = json.loads(node.file_path.read_text(encoding="utf-8"))
                self.checkpoint.save_parsed_rule(rule_id, raw_rule)
            else:
                self.checkpoint.mark_failed(rule_id, "Rule file not found")
                return False

        # Gather dependency entries
        node     = self._find_node(rule_id)
        dep_entries = []
        if node:
            for ref in node.references:
                dep_id    = f"{ref.rule_class}::{ref.rule_name}"
                dep_entry = self.checkpoint._manifest.get(dep_id)
                if dep_entry:
                    dep_entries.append(dep_entry)

        # Assemble bounded context
        context_bundle = self.assembler.assemble(
            entry=entry,
            rule_raw=raw_rule,
            dep_entries=dep_entries,
            casetype_summary=casetype_summary,
            skill_context=self._skill_context,
            role_adapter=self._role_adapter,
        )
        self.checkpoint.save_context_bundle(rule_id, context_bundle)

        if self.dry_run:
            logger.info("[DRY RUN] Would analyse %s — skipping LLM call", rule_id)
            # Save placeholder outputs
            for output_type in OUTPUT_TYPES.get(entry.rule_type, ["narrative"]):
                placeholder = f"# {entry.rule_type}: {entry.rule_name}\n\n[DRY RUN — no LLM call made]\n"
                self.checkpoint.save_analysis(rule_id, output_type, placeholder)
            self.checkpoint.mark_done(rule_id)
            return True

        # Call the LLM
        output_paths = []
        for output_type in OUTPUT_TYPES.get(entry.rule_type, ["narrative"]):
            try:
                content = self._call_llm(entry, context_bundle, output_type)
                path = self.checkpoint.save_analysis(rule_id, output_type, content)
                output_paths.append(str(path))
                logger.debug("Saved %s output to %s", output_type, path)
            except Exception as e:
                logger.error("LLM call failed for %s (%s): %s", rule_id, output_type, e)
                self.checkpoint.mark_failed(rule_id, str(e))
                return False

        self.checkpoint.mark_done(rule_id, output_paths)
        return True

    def _call_llm(self, entry: ManifestEntry, context_bundle: dict, output_type: str) -> str:
        """Make a single Anthropic API call and return the text response."""
        system_prompt = AGENT_PROMPTS.get(entry.rule_type, AGENT_PROMPTS["Rule-Obj-Flow"])

        # Build the user message
        user_message = _build_user_message(entry, context_bundle, output_type)

        response = self._client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def _find_node(self, rule_id: str):
        if not self.graph:
            return None
        for node in self.graph:
            if node.node_id == rule_id:
                return node
        return None

    def _load_casetype_summary(self) -> str:
        """Load the CaseType narrative if already analysed."""
        for entry in self.checkpoint._manifest.values():
            if entry.rule_type == "Rule-Obj-CaseType" and entry.status == "done":
                return self.checkpoint.load_analysis(entry.rule_id, "narrative") or ""
        return ""

    # ── Phase 3: Aggregate outputs ────────────────────────────────────────────

    def phase3_aggregate(self, output_dir: Optional[Path] = None) -> dict[str, Path]:
        """
        Concatenate all analysis outputs into aggregate documents.
        Returns dict of {output_type: file_path}.
        """
        out_dir = Path(output_dir) if output_dir else self.workspace / "aggregated"
        out_dir.mkdir(parents=True, exist_ok=True)

        outputs = {}

        narrative_path = out_dir / "full_flow_narrative.md"
        narrative_path.write_text(self.checkpoint.aggregate_narratives(), encoding="utf-8")
        outputs["narrative"] = narrative_path

        frd_path = out_dir / "frd_fragments.md"
        frd_path.write_text(self.checkpoint.aggregate_frd_fragments(), encoding="utf-8")
        outputs["frd"] = frd_path

        logger.info("Aggregated outputs written to %s", out_dir)
        return outputs

    # ── Convenience: run full pipeline ────────────────────────────────────────

    def run_full_pipeline(
        self,
        overwrite_graph: bool = False,
        max_rules: Optional[int] = None,
    ) -> dict:
        """Phase 1 → Phase 2 → Phase 3 in sequence. Returns final progress report."""
        self.phase1_build_graph(overwrite=overwrite_graph)
        report = self.phase2_analyse(max_rules=max_rules)
        if report.get("pending", 0) == 0:
            self.phase3_aggregate()
        return report


# ─── Helper: build LLM user message ──────────────────────────────────────────

def _build_user_message(entry: ManifestEntry, ctx: dict, output_type: str) -> str:
    parts = []

    # Header
    parts.append(f"# Analyse this PEGA rule: {entry.rule_type}")
    parts.append(f"Rule: {entry.rule_name}  |  Class: {entry.rule_class}  |  Depth: {entry.depth}")
    parts.append(f"Output requested: {output_type}\n")

    # CaseType orientation
    if ctx.get("casetype_overview"):
        parts.append("## Case type context (orientation)")
        parts.append(ctx["casetype_overview"])
        parts.append("")

    # The rule itself
    parts.append("## Rule JSON (full)")
    parts.append("```json")
    parts.append(json.dumps(ctx.get("rule_json", {}), indent=2))
    parts.append("```\n")

    # Dependencies
    deps = ctx.get("dependency_summaries", [])
    if deps:
        parts.append(f"## Referenced rules ({len(deps)} available)")
        for dep in deps:
            parts.append(f"\n### {dep['rule_type']}: {dep['rule_name']}")
            parts.append(dep["summary"])

    # Truncated deps warning
    truncated = ctx.get("truncated_deps", [])
    if truncated:
        parts.append(f"\n⚠ {len(truncated)} referenced rules omitted (token budget): {', '.join(truncated[:5])}")

    # Skill context
    if ctx.get("skill_context"):
        parts.append("\n## PEGA & KYC knowledge")
        parts.append(ctx["skill_context"])

    # Role adapter
    if ctx.get("role_adapter"):
        parts.append("\n## Output audience")
        parts.append(ctx["role_adapter"])

    return "\n".join(parts)


def _load_text_files(paths: list[Path]) -> str:
    """Concatenate multiple text files into one string."""
    parts = []
    for p in paths:
        p = Path(p)
        if p.exists():
            parts.append(f"### {p.name}\n{p.read_text(encoding='utf-8')}")
        else:
            logger.warning("Skill file not found: %s", p)
    return "\n\n".join(parts)
