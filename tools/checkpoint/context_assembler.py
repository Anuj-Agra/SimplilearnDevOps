"""
tools/checkpoint/context_assembler.py

Assembles the bounded LLM context for analysing a single rule.

Problem: A complex PEGA flow references 20+ other rules. Passing all raw JSON
to the LLM at once would blow the token budget.

Solution: For each rule being analysed, build a TIERED context:
  Tier 1  — The rule itself (full parsed JSON) — always included
  Tier 2  — Direct dependencies (parsed summaries, not full JSON) — always included
  Tier 3  — Already-completed analysis of dependencies — included if space allows
  Tier 4  — CaseType overview (root orientation) — always included if available
  Tier 5  — Hierarchy context and KYC domain skills — always included

Token budget: configurable, default 6000 tokens (~24000 chars) for the context
bundle. The LLM call itself has 4000 output tokens.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from .checkpoint_manager import CheckpointManager

logger = logging.getLogger(__name__)

# Rough chars-per-token for PEGA JSON (JSON is ~3.5 chars/token; markdown ~4.5)
CHARS_PER_TOKEN      = 3.5
DEFAULT_TOKEN_BUDGET = 6000        # tokens reserved for context
MIN_RULE_CHARS       = 500         # minimum chars to include a dependency


class ContextAssembler:
    """
    Builds a bounded context bundle for a single rule's LLM analysis call.
    """

    def __init__(
        self,
        checkpoint: CheckpointManager,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        include_raw_json: bool = True,
    ):
        self.checkpoint    = checkpoint
        self.char_budget   = int(token_budget * CHARS_PER_TOKEN)
        self.include_raw   = include_raw_json

    def assemble(
        self,
        entry,                         # ManifestEntry of the rule being analysed
        rule_raw: dict,                # the rule's raw parsed JSON
        dep_entries: list,             # ManifestEntry list of direct dependencies
        casetype_summary: Optional[str] = None,
        skill_context: str = "",
        role_adapter: str = "",
    ) -> dict:
        """
        Returns a context bundle dict with keys:
          rule_id, rule_type, rule_name, rule_class,
          rule_json,              ← always included (Tier 1)
          dependency_summaries,   ← list of {rule_id, type, name, summary} (Tier 2+3)
          casetype_overview,      ← string (Tier 4)
          skill_context,          ← string (Tier 5)
          role_adapter,           ← string (Tier 5)
          token_budget_used,      ← estimated chars used
          truncated_deps,         ← list of dep rule_ids dropped due to budget
        """
        budget_remaining = self.char_budget
        truncated = []

        # ── Tier 1: the rule itself ───────────────────────────────────────────
        rule_json_str = json.dumps(rule_raw, indent=2)
        budget_remaining -= len(rule_json_str)

        # ── Tier 4: CaseType overview (orientation) ───────────────────────────
        casetype_chars = len(casetype_summary or "")
        if casetype_summary and casetype_chars < budget_remaining * 0.3:
            budget_remaining -= casetype_chars
        else:
            casetype_summary = self._truncate(casetype_summary or "", budget_remaining // 8)
            budget_remaining -= len(casetype_summary)

        # ── Tier 5: skills + role adapter ────────────────────────────────────
        skills_chars = len(skill_context) + len(role_adapter)
        budget_remaining -= min(skills_chars, budget_remaining // 4)

        # ── Tier 2+3: dependency summaries ────────────────────────────────────
        dep_summaries = []
        per_dep_budget = max(
            MIN_RULE_CHARS,
            (budget_remaining // max(len(dep_entries), 1))
        )

        for dep_entry in dep_entries:
            dep_text = self._get_dep_text(dep_entry, per_dep_budget)
            if dep_text:
                dep_summaries.append({
                    "rule_id":    dep_entry.rule_id,
                    "rule_type":  dep_entry.rule_type,
                    "rule_name":  dep_entry.rule_name,
                    "rule_class": dep_entry.rule_class,
                    "summary":    dep_text,
                })
                budget_remaining -= len(dep_text)
            else:
                truncated.append(dep_entry.rule_id)

        used = self.char_budget * CHARS_PER_TOKEN - budget_remaining

        bundle = {
            "rule_id":               entry.rule_id,
            "rule_type":             entry.rule_type,
            "rule_name":             entry.rule_name,
            "rule_class":            entry.rule_class,
            "depth":                 entry.depth,
            "rule_json":             rule_raw if self.include_raw else _summarise_rule(rule_raw),
            "dependency_count":      len(dep_entries),
            "dependency_summaries":  dep_summaries,
            "casetype_overview":     casetype_summary or "",
            "skill_context":         skill_context,
            "role_adapter":          role_adapter,
            "estimated_tokens_used": int(used / CHARS_PER_TOKEN),
            "truncated_deps":        truncated,
        }

        if truncated:
            logger.warning(
                "Context for %s: %d dependencies truncated due to token budget",
                entry.rule_id, len(truncated)
            )

        return bundle

    def _get_dep_text(self, dep_entry, budget: int) -> Optional[str]:
        """Get the best available text for a dependency — analysis first, then raw JSON."""

        # Prefer completed narrative (most informative, most compressed)
        narrative = self.checkpoint.load_analysis(dep_entry.rule_id, "narrative")
        if narrative:
            return self._truncate(narrative, budget)

        # Fall back to parsed rule summary
        parsed = self.checkpoint.load_parsed_rule(dep_entry.rule_id)
        if parsed:
            summary = _summarise_rule(parsed)
            return self._truncate(summary, budget)

        return None

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        if not text or max_chars <= 0:
            return ""
        if len(text) <= max_chars:
            return text
        cutoff = max(0, max_chars - 80)
        return text[:cutoff] + f"\n\n[... truncated — {len(text) - cutoff} chars omitted ...]"


def _summarise_rule(rule: dict) -> str:
    """
    Produce a compact text summary of a rule dict.
    Used when no LLM analysis is available for a dependency.
    """
    obj_class  = rule.get("pxObjClass", "")
    rule_name  = rule.get("pyRuleName", "")
    rule_class = rule.get("pyClassName", "")
    desc       = rule.get("pyDescription", "")
    label      = rule.get("pyLabel", "")

    lines = [
        f"Rule:  {rule_name}",
        f"Type:  {obj_class}",
        f"Class: {rule_class}",
    ]
    if label:  lines.append(f"Label: {label}")
    if desc:   lines.append(f"Desc:  {desc}")

    dispatchers = {
        "Rule-Obj-CaseType":    _summarise_casetype,
        "Rule-Obj-Flow":        _summarise_flow,
        "Rule-Obj-Activity":    _summarise_activity,
        "Rule-Obj-Flowsection": _summarise_flowsection,
        "Rule-HTML-Section":    _summarise_html_section,
        "Rule-Obj-When":        _summarise_when,
    }
    fn = dispatchers.get(obj_class)
    if fn:
        lines.extend(fn(rule))

    return "\n".join(lines)


def _summarise_casetype(rule: dict) -> list[str]:
    lines = []
    stages = rule.get("pyStages", [])
    if stages:
        lines.append(f"Stages ({len(stages)}): " + " → ".join(
            s.get("pyStageName", "?") for s in stages
        ))
    return lines


def _summarise_flow(rule: dict) -> list[str]:
    steps  = rule.get("pyFlowSteps", [])
    lines  = [f"Steps ({len(steps)}):"]
    for s in steps[:8]:  # cap at 8 for summary
        lines.append(f"  [{s.get('pyStepType','?')}] {s.get('pyStepName','?')}"
                     + (f" → {s.get('pyFlowActionName','') or s.get('pyActivityName','') or s.get('pySubFlowName','')}" if any([
                         s.get('pyFlowActionName'), s.get('pyActivityName'), s.get('pySubFlowName')
                     ]) else ""))
    if len(steps) > 8:
        lines.append(f"  ... and {len(steps) - 8} more steps")
    return lines


def _summarise_activity(rule: dict) -> list[str]:
    steps = rule.get("pySteps", [])
    params = rule.get("pyParameters", [])
    lines = []
    if params:
        lines.append("Params: " + ", ".join(
            f"{p.get('pyName')}({p.get('pyDirection','')})" for p in params
        ))
    lines.append(f"Steps ({len(steps)}): " + ", ".join(
        s.get("pyStepMethod", "?") for s in steps[:6]
    ))
    return lines


def _summarise_flowsection(rule: dict) -> list[str]:
    lines = []
    if rule.get("pyScreenName"):
        lines.append(f"Screen: {rule['pyScreenName']}")
    buttons = rule.get("pyActionButtons", [])
    if buttons:
        lines.append("Buttons: " + ", ".join(b.get("pyButtonLabel","?") for b in buttons))
    return lines


def _summarise_html_section(rule: dict) -> list[str]:
    fields = rule.get("pyFields", [])
    embedded = rule.get("pyEmbeddedSections", [])
    lines = [
        f"Fields ({len(fields)}): " + ", ".join(
            f.get("pyLabel", f.get("pyPropertyReference","?")) for f in fields[:6]
        )
    ]
    if embedded:
        lines.append(f"Embeds ({len(embedded)}): " + ", ".join(
            e.get("pySectionName","?") for e in embedded[:4]
        ))
    return lines


def _summarise_when(rule: dict) -> list[str]:
    expr = rule.get("pyExpression", "")
    return [f"Expression: {expr}"] if expr else []
