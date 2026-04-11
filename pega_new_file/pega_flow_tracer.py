#!/usr/bin/env python3
"""
pega_flow_tracer.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREA — Pega Flow Rule Tracer

Traces the execution path of Pega Flow rules, following:
  - Flow step transitions (when conditions)
  - Subprocess calls (embedded flows)
  - Activity calls from flow steps
  - Decision Table evaluations within flow connectors
  - Assignment steps with actor/work party resolution
  - Split/Join parallel branches

Outputs a structured flow trace JSON and a human-readable Markdown report.

Usage:
    python pega_flow_tracer.py --rules rules_extracted.json
                                --flow "ProcessKYCSubmission"
                                --output flow_trace.json

    python pega_flow_tracer.py --rules rules_extracted.json
                                --all-flows
                                --output-dir ./flow_traces/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import argparse
import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple

log = logging.getLogger("prea.flow_tracer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")

# Step type icons for Markdown output
STEP_ICONS: Dict[str, str] = {
    "Start":       "🚀",
    "End":         "🏁",
    "Assignment":  "👤",
    "Utility":     "⚙️",
    "Decision":    "🔀",
    "Subprocess":  "📦",
    "Split":       "⑂",
    "Join":        "⊕",
    "Wait":        "⏳",
    "Error":       "❌",
    "Notify":      "📬",
    "Connector":   "🔗",
    "Activity":    "⚡",
    "Unknown":     "◈",
}

# Pega step type inference from method names and element tags
STEP_TYPE_INFERENCE: Dict[str, str] = {
    "begin":        "Start",
    "end":          "End",
    "assignment":   "Assignment",
    "utility":      "Utility",
    "split":        "Split",
    "join":         "Join",
    "wait":         "Wait",
    "subprocess":   "Subprocess",
    "notify":       "Notify",
    "connector":    "Connector",
    "decision":     "Decision",
    "error":        "Error",
    "localflow":    "Subprocess",
}


@dataclass
class FlowStep:
    step_id:      str
    name:         str
    step_type:    str
    method:       str
    actor:        str
    description:  str
    conditions:   List[Dict[str, str]] = field(default_factory=list)
    transitions:  List[Dict[str, str]] = field(default_factory=list)
    sub_flow:     Optional[str] = None
    sub_activity: Optional[str] = None
    decision_ref: Optional[str] = None
    notes:        str = ""

    def icon(self) -> str:
        return STEP_ICONS.get(self.step_type, STEP_ICONS["Unknown"])


@dataclass
class FlowTrace:
    flow_name:    str
    flow_class:   str
    flow_layer:   str
    flow_ruleset: str
    description:  str
    steps:        List[FlowStep] = field(default_factory=list)
    sub_flows:    List["FlowTrace"] = field(default_factory=list)
    actors:       List[str] = field(default_factory=list)
    conditions:   List[str] = field(default_factory=list)
    warnings:     List[str] = field(default_factory=list)
    max_depth:    int = 0


def infer_step_type(raw_type: str, method: str) -> str:
    """Infer canonical step type from raw XML tag and method name."""
    for key, stype in STEP_TYPE_INFERENCE.items():
        if key in raw_type.lower() or key in method.lower():
            return stype
    return "Unknown"


def load_rules(rules_path: Path) -> Dict[str, Dict]:
    """Load rules into a lookup dict keyed by name."""
    with rules_path.open(encoding="utf-8") as f:
        data = json.load(f)
    rules_list = data.get("rules", data) if isinstance(data, dict) else data
    # Build multi-key lookup: name, rule_id, and name::class
    lookup = {}
    for r in rules_list:
        name = r.get("name", "")
        rid  = r.get("rule_id", "")
        cls  = r.get("pega_class", "")
        if name:
            lookup[name] = r
        if rid:
            lookup[rid] = r
        if name and cls:
            lookup[f"{name}::{cls}"] = r
    return lookup


def build_flow_step(raw_step: Dict, step_idx: int) -> FlowStep:
    """Convert a raw step dict (from rule extraction) into a FlowStep."""
    raw_type = raw_step.get("type", "")
    method   = raw_step.get("method", "")
    actor    = raw_step.get("actor", "")
    name     = raw_step.get("name", f"Step-{step_idx+1}")
    when     = raw_step.get("when", "")
    transitions = raw_step.get("transition", [])

    step_type = infer_step_type(raw_type, method)

    # Normalise transitions
    norm_transitions = []
    for t in transitions:
        norm_transitions.append({
            "to":   t.get("to") or t.get("name") or "",
            "when": t.get("when") or t.get("condition") or "",
            "label": t.get("label") or ("Default" if not t.get("when") else "Conditional"),
        })

    # Detect sub-flow / activity references
    sub_flow     = None
    sub_activity = None
    decision_ref = None

    if step_type in ("Subprocess", "Connector"):
        sub_flow = method or name
    elif step_type == "Activity":
        sub_activity = method
    elif step_type == "Decision":
        decision_ref = method or name

    # Build human-readable description
    description = _build_step_description(step_type, name, method, actor, when)

    return FlowStep(
        step_id      = f"STEP-{step_idx+1:03d}",
        name         = name,
        step_type    = step_type,
        method       = method,
        actor        = actor,
        description  = description,
        conditions   = [{"expression": when, "outcome": ""}] if when else [],
        transitions  = norm_transitions,
        sub_flow     = sub_flow,
        sub_activity = sub_activity,
        decision_ref = decision_ref,
    )


def _build_step_description(step_type: str, name: str, method: str, 
                             actor: str, when: str) -> str:
    """Generate a plain-English description of a flow step."""
    parts = []
    type_descriptions = {
        "Start":       "The flow begins.",
        "End":         "The flow reaches a terminal state.",
        "Assignment":  f"A task is assigned to {actor or 'the work queue'} for action.",
        "Utility":     f"The system executes the utility method '{method}'." if method else "A system utility step executes.",
        "Decision":    f"A decision is evaluated using '{method}'." if method else "A branching decision is evaluated.",
        "Subprocess":  f"The sub-flow '{method or name}' is called." if (method or name) else "A subprocess is invoked.",
        "Split":       "The flow splits into parallel branches.",
        "Join":        "Parallel branches re-converge.",
        "Wait":        "The flow pauses, waiting for an event or time trigger.",
        "Notify":      "A notification or correspondence is sent.",
        "Error":       "An error condition is raised.",
    }
    desc = type_descriptions.get(step_type, f"Step '{name}' executes.")
    if when:
        desc += f" Condition: {when}."
    return desc


def trace_flow(flow_name: str, rules: Dict[str, Dict],
               visited: Optional[Set[str]] = None,
               depth: int = 0,
               max_depth: int = 8) -> Optional[FlowTrace]:
    """
    Recursively trace a flow rule and its subflows.

    Args:
        flow_name:  Name of the flow to trace
        rules:      Lookup dict of all extracted rules
        visited:    Set of already-visited flow names (cycle prevention)
        depth:      Current recursion depth
        max_depth:  Maximum recursion depth

    Returns:
        FlowTrace or None if flow not found
    """
    if visited is None:
        visited = set()

    if flow_name in visited:
        log.debug("Cycle detected: %s (already visited)", flow_name)
        return None

    if depth > max_depth:
        log.debug("Max depth reached at %s", flow_name)
        return None

    rule = rules.get(flow_name)
    if not rule:
        log.debug("Flow not found: %s", flow_name)
        return None

    if rule.get("rule_type") not in ("Flow", "Activity", "Subprocess", None, ""):
        # Allow tracing into activities too
        if rule.get("rule_type") not in ("Activity", "Flow"):
            log.debug("Not a flow/activity: %s (type=%s)", flow_name, rule.get("rule_type"))

    visited.add(flow_name)

    raw_steps  = rule.get("flow_steps", [])
    raw_actors = rule.get("actors", [])

    # Build steps
    steps: List[FlowStep] = []
    for i, raw_step in enumerate(raw_steps):
        step = build_flow_step(raw_step, i)
        steps.append(step)

    # Synthesise Start/End if not present (some Pega flows omit these)
    if steps and steps[0].step_type != "Start":
        steps.insert(0, FlowStep(
            step_id="STEP-000", name="Flow Start", step_type="Start",
            method="", actor="", description="The flow begins.",
        ))
    if steps and steps[-1].step_type not in ("End", "Error"):
        steps.append(FlowStep(
            step_id=f"STEP-{len(steps)+1:03d}", name="Flow End", step_type="End",
            method="", actor="", description="The flow reaches a terminal state.",
        ))

    # If no steps extracted (binary not fully parsed), generate from dependencies
    if not steps or len(steps) <= 2:
        deps = rule.get("dependencies", [])
        steps = _synthesise_steps_from_deps(rule, deps)

    # Collect all actors
    all_actors = list(set(raw_actors + [s.actor for s in steps if s.actor]))

    # Collect all conditions
    all_conditions = [
        cond["expression"]
        for step in steps
        for cond in step.conditions
        if cond.get("expression")
    ]

    trace = FlowTrace(
        flow_name    = flow_name,
        flow_class   = rule.get("pega_class", ""),
        flow_layer   = rule.get("layer", ""),
        flow_ruleset = rule.get("ruleset", ""),
        description  = _infer_flow_description(flow_name, rule),
        steps        = steps,
        actors       = all_actors,
        conditions   = all_conditions,
        max_depth    = depth,
    )

    # Recurse into sub-flows
    for step in steps:
        if step.sub_flow and step.sub_flow != flow_name:
            sub_trace = trace_flow(step.sub_flow, rules, visited.copy(), depth+1, max_depth)
            if sub_trace:
                trace.sub_flows.append(sub_trace)
                trace.warnings.extend(sub_trace.warnings)

    return trace


def _synthesise_steps_from_deps(rule: Dict, deps: List[str]) -> List[FlowStep]:
    """
    When flow step XML is sparse (binary not fully decoded), synthesise
    a plausible step chain from dependency references.
    """
    steps = [FlowStep(step_id="STEP-000", name="Flow Start", step_type="Start",
                      method="", actor="", description="The flow begins.")]

    # Classify dependencies by likely type
    for i, dep in enumerate(deps[:15]):   # cap at 15 synthetic steps
        stype = "Utility"
        if any(x in dep.lower() for x in ["validate", "check"]):
            stype = "Utility"
        elif any(x in dep.lower() for x in ["approve", "reject", "review", "assign"]):
            stype = "Assignment"
        elif any(x in dep.lower() for x in ["decision", "evaluate", "score", "risk"]):
            stype = "Decision"
        elif any(x in dep.lower() for x in ["flow", "process", "sub"]):
            stype = "Subprocess"
        elif any(x in dep.lower() for x in ["notify", "send", "mail", "correspondence"]):
            stype = "Notify"
        elif any(x in dep.lower() for x in ["transform", "map", "convert"]):
            stype = "Utility"

        steps.append(FlowStep(
            step_id=f"STEP-{i+1:03d}",
            name=dep,
            step_type=stype,
            method=dep,
            actor="",
            description=f"{'Referenced rule' if stype == 'Utility' else 'Step'}: {dep}",
            notes="Synthesised from dependency reference — run full binary decode for exact step details",
        ))

    steps.append(FlowStep(
        step_id=f"STEP-{len(steps):03d}", name="Flow End", step_type="End",
        method="", actor="", description="The flow reaches a terminal state.",
    ))
    return steps


def _infer_flow_description(flow_name: str, rule: Dict) -> str:
    """Generate a plain-English description for a flow."""
    cls = rule.get("pega_class", "")
    layer = rule.get("layer", "")
    n_steps = len(rule.get("flow_steps", []))
    actors = rule.get("actors", [])

    desc = f"Flow rule '{flow_name}'"
    if cls:
        desc += f" on class {cls}"
    if layer:
        desc += f" ({layer} layer)"
    desc += "."
    if n_steps:
        desc += f" Contains {n_steps} steps."
    if actors:
        desc += f" Actors: {', '.join(actors[:3])}."
    return desc


# ── Markdown Report ──────────────────────────────────────────────────────────

def trace_to_markdown(trace: FlowTrace, indent: int = 0) -> str:
    """Convert a FlowTrace to a human-readable Markdown document."""
    lines = []
    prefix = "#" * (2 + indent)

    lines.append(f"{prefix} {trace.icon() if hasattr(trace, 'icon') else '⚡'} {trace.flow_name}")
    lines.append(f"")
    lines.append(f"**Class:** `{trace.flow_class}`  ")
    lines.append(f"**Layer:** {trace.flow_layer}  ")
    lines.append(f"**Ruleset:** {trace.flow_ruleset}  ")
    lines.append(f"")
    lines.append(f"{trace.description}")
    lines.append(f"")

    if trace.actors:
        lines.append(f"**Actors:** {', '.join(trace.actors)}")
        lines.append(f"")

    lines.append(f"### Steps")
    lines.append(f"")

    for i, step in enumerate(trace.steps):
        icon = step.icon()
        lines.append(f"**{i+1}. {icon} {step.name}** `[{step.step_type}]`")
        lines.append(f"")
        lines.append(f"{step.description}")

        if step.conditions:
            for cond in step.conditions:
                if cond.get("expression"):
                    lines.append(f"  - 📐 *When:* `{cond['expression']}`")

        if step.transitions:
            for t in step.transitions:
                arrow = "→"
                label = t.get("when") or t.get("label") or "Default"
                to    = t.get("to") or ""
                if to:
                    lines.append(f"  - {arrow} **{label}**: `{to}`")

        if step.sub_flow:
            lines.append(f"  - 📦 *Calls sub-flow:* `{step.sub_flow}`")
        if step.sub_activity:
            lines.append(f"  - ⚡ *Calls activity:* `{step.sub_activity}`")
        if step.notes:
            lines.append(f"  - ⚠️ _{step.notes}_")

        lines.append(f"")

    if trace.sub_flows:
        lines.append(f"### Sub-Flows")
        lines.append(f"")
        for sub in trace.sub_flows:
            lines.extend(trace_to_markdown(sub, indent+1).split("\n"))

    if trace.warnings:
        lines.append(f"### ⚠️ Warnings")
        for w in trace.warnings:
            lines.append(f"- {w}")
        lines.append(f"")

    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PREA Flow Tracer")
    parser.add_argument("--rules",        required=True, help="rules_extracted.json")
    parser.add_argument("--flow",         help="Name of the flow to trace")
    parser.add_argument("--all-flows",    action="store_true", help="Trace all flow rules")
    parser.add_argument("--output",       default="flow_trace.json")
    parser.add_argument("--output-dir",   help="Directory for multiple flow traces (--all-flows)")
    parser.add_argument("--output-md",    default="flow_trace.md", help="Markdown report output")
    parser.add_argument("--max-depth",    type=int, default=8, help="Maximum recursion depth")
    args = parser.parse_args()

    rules = load_rules(Path(args.rules))
    log.info("Loaded %d rules", len(rules))

    if args.all_flows:
        # Find all flow rules
        flow_names = [
            r.get("name") for r in
            (list(rules.values()) if isinstance(list(rules.values())[0], dict) else [])
            if r.get("rule_type") == "Flow" and r.get("name")
        ]
        # Deduplicate (lookup has multiple keys per rule)
        flow_names = list(dict.fromkeys(flow_names))
        log.info("Found %d flow rules", len(flow_names))

        out_dir = Path(args.output_dir or "flow_traces")
        out_dir.mkdir(parents=True, exist_ok=True)

        for fn in flow_names:
            trace = trace_flow(fn, rules, max_depth=args.max_depth)
            if trace:
                out = out_dir / f"{fn.replace('/', '_')}_trace.json"
                with out.open("w") as f:
                    json.dump(asdict(trace), f, indent=2)
                log.info("Traced: %s → %s steps", fn, len(trace.steps))

        log.info("All flow traces written to %s", out_dir)
        return

    if not args.flow:
        parser.error("Provide --flow <name> or --all-flows")

    trace = trace_flow(args.flow, rules, max_depth=args.max_depth)
    if not trace:
        log.error("Flow '%s' not found in rule set", args.flow)
        return

    # Write JSON
    with open(args.output, "w") as f:
        json.dump(asdict(trace), f, indent=2)
    log.info("Flow trace written: %s", args.output)

    # Write Markdown
    md = trace_to_markdown(trace)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(f"# PREA Flow Trace Report\n\n")
        f.write(f"Generated by PREA — Pega Reverse Engineering Agent\n\n")
        f.write("---\n\n")
        f.write(md)
    log.info("Markdown report written: %s", args.output_md)

    # Print summary
    print(f"\n{'═'*55}")
    print(f"  Flow: {trace.flow_name}")
    print(f"  Class: {trace.flow_class} | Layer: {trace.flow_layer}")
    print(f"  Steps: {len(trace.steps)}")
    print(f"  Sub-flows: {len(trace.sub_flows)}")
    print(f"  Actors: {', '.join(trace.actors) or 'None detected'}")
    if trace.warnings:
        print(f"  ⚠ Warnings: {len(trace.warnings)}")
    print(f"{'═'*55}")


if __name__ == "__main__":
    main()
