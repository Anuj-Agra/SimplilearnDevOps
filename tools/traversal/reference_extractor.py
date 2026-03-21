"""
tools/traversal/reference_extractor.py

Extracts all cross-rule references from a parsed PEGA rule JSON.
Returns a list of RuleRef objects that the traversal engine will queue for analysis.

Handles:
  Rule-Obj-CaseType
  Rule-Obj-Flow
  Rule-Obj-Activity
  Rule-Obj-Flowsection
  Rule-HTML-Section
  Rule-Obj-When
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuleRef:
    """A reference from one PEGA rule to another."""
    rule_name:  str           # pyRuleName of the referenced rule
    rule_class: str           # pyClassName of the referenced rule
    rule_type:  str           # pxObjClass of the referenced rule
    source_rule: str          # pyRuleName of the rule that contains this reference
    source_field: str         # JSON path in source rule where reference was found
    is_async: bool = False    # True for Spinoff steps (lower analysis priority)
    priority: int = 5         # 1=highest, 10=lowest; CaseType=1, SubFlow=2, etc.


# ─── Dispatcher ──────────────────────────────────────────────────────────────

def extract_references(rule: dict) -> list[RuleRef]:
    """
    Main entry point. Given a parsed rule dict, return all cross-rule references.
    Dispatches to the correct extractor based on pxObjClass.
    """
    obj_class = rule.get("pxObjClass", "").strip()
    source = rule.get("pyRuleName", "unknown")

    extractors = {
        "Rule-Obj-CaseType":    _extract_casetype,
        "Rule-Obj-Flow":        _extract_flow,
        "Rule-Obj-Activity":    _extract_activity,
        "Rule-Obj-Flowsection": _extract_flowsection,
        "Rule-HTML-Section":    _extract_html_section,
        "Rule-Obj-When":        _extract_when,
    }

    extractor = extractors.get(obj_class)
    if extractor is None:
        logger.warning("No extractor for rule type '%s' in rule '%s'", obj_class, source)
        return []

    refs = extractor(rule, source)
    logger.debug("Extracted %d references from %s (%s)", len(refs), source, obj_class)
    return refs


# ─── CaseType extractor ───────────────────────────────────────────────────────

def _extract_casetype(rule: dict, source: str) -> list[RuleRef]:
    refs = []
    cls  = rule.get("pyClassName", "")

    # Entry flows
    for field_name in ("pyStartingFlow", "pyCreateFlow"):
        flow_name = rule.get(field_name, "").strip()
        if flow_name:
            refs.append(RuleRef(
                rule_name=flow_name, rule_class=cls,
                rule_type="Rule-Obj-Flow", source_rule=source,
                source_field=field_name, priority=1
            ))

    # Stage process flows
    for stage in rule.get("pyStages", []):
        for process in stage.get("pyProcesses", []):
            flow_name  = process.get("pyFlowName", "").strip()
            flow_class = process.get("pyFlowClass", cls).strip() or cls
            if flow_name:
                refs.append(RuleRef(
                    rule_name=flow_name, rule_class=flow_class,
                    rule_type="Rule-Obj-Flow", source_rule=source,
                    source_field=f"pyStages[{stage.get('pyStageName','')}].pyProcesses",
                    priority=2
                ))

    # Action flows
    for action in rule.get("pyActionFlows", []):
        flow_name = action.get("pyFlowName", "").strip()
        if flow_name:
            refs.append(RuleRef(
                rule_name=flow_name, rule_class=cls,
                rule_type="Rule-Obj-Flow", source_rule=source,
                source_field="pyActionFlows", priority=4
            ))

    # Child case types
    for rel in rule.get("pyCaseRelationships", []):
        child_class = rel.get("pyChildClass", "").strip()
        if child_class:
            refs.append(RuleRef(
                rule_name=child_class, rule_class=child_class,
                rule_type="Rule-Obj-CaseType", source_rule=source,
                source_field="pyCaseRelationships", priority=3
            ))

    return refs


# ─── Flow extractor ───────────────────────────────────────────────────────────

def _extract_flow(rule: dict, source: str) -> list[RuleRef]:
    refs = []
    cls  = rule.get("pyClassName", "")

    STEP_TYPE_DISPATCH = {
        "Assignment": _flow_step_assignment,
        "Utility":    _flow_step_utility,
        "SubFlow":    _flow_step_subflow,
        "Spinoff":    _flow_step_spinoff,
        "Decision":   _flow_step_decision,
        "Split-ForAll": _flow_step_split_forall,
    }

    for step in rule.get("pyFlowSteps", []):
        step_type = step.get("pyStepType", "").strip()
        handler   = STEP_TYPE_DISPATCH.get(step_type)
        if handler:
            refs.extend(handler(step, source, cls))

    # Connector-level When conditions (branch conditions)
    for connector in rule.get("pyConnectors", []):
        when_name = connector.get("pyWhenName", "").strip()
        if when_name:
            refs.append(RuleRef(
                rule_name=when_name, rule_class=cls,
                rule_type="Rule-Obj-When", source_rule=source,
                source_field="pyConnectors[].pyWhenName", priority=7
            ))

    return refs


def _flow_step_assignment(step: dict, source: str, cls: str) -> list[RuleRef]:
    refs = []
    action_name  = step.get("pyFlowActionName", "").strip()
    action_class = step.get("pyFlowActionClass", cls).strip() or cls
    if action_name:
        refs.append(RuleRef(
            rule_name=action_name, rule_class=action_class,
            rule_type="Rule-Obj-Flowsection", source_rule=source,
            source_field=f"pyFlowSteps[{step.get('pyStepName','')}].pyFlowActionName",
            priority=3
        ))
    return refs


def _flow_step_utility(step: dict, source: str, cls: str) -> list[RuleRef]:
    refs = []
    step_label = step.get("pyStepName", "")

    activity_name = step.get("pyActivityName", "").strip()
    if activity_name:
        refs.append(RuleRef(
            rule_name=activity_name, rule_class=cls,
            rule_type="Rule-Obj-Activity", source_rule=source,
            source_field=f"pyFlowSteps[{step_label}].pyActivityName",
            priority=4
        ))
    return refs


def _flow_step_subflow(step: dict, source: str, cls: str) -> list[RuleRef]:
    refs = []
    sub_name  = step.get("pySubFlowName", "").strip()
    sub_class = step.get("pySubFlowClass", cls).strip() or cls
    if sub_name:
        refs.append(RuleRef(
            rule_name=sub_name, rule_class=sub_class,
            rule_type="Rule-Obj-Flow", source_rule=source,
            source_field=f"pyFlowSteps[{step.get('pyStepName','')}].pySubFlowName",
            priority=2
        ))
    return refs


def _flow_step_spinoff(step: dict, source: str, cls: str) -> list[RuleRef]:
    refs = []
    sub_name  = step.get("pySubFlowName", "").strip()
    sub_class = step.get("pySubFlowClass", cls).strip() or cls
    if sub_name:
        refs.append(RuleRef(
            rule_name=sub_name, rule_class=sub_class,
            rule_type="Rule-Obj-Flow", source_rule=source,
            source_field=f"pyFlowSteps[{step.get('pyStepName','')}].pySubFlowName (Spinoff)",
            is_async=True, priority=6
        ))
    return refs


def _flow_step_decision(step: dict, source: str, cls: str) -> list[RuleRef]:
    refs = []
    when_name = step.get("pyWhenName", "").strip()
    if when_name:
        refs.append(RuleRef(
            rule_name=when_name, rule_class=cls,
            rule_type="Rule-Obj-When", source_rule=source,
            source_field=f"pyFlowSteps[{step.get('pyStepName','')}].pyWhenName",
            priority=7
        ))
    return refs


def _flow_step_split_forall(step: dict, source: str, cls: str) -> list[RuleRef]:
    refs = []
    sub_name = step.get("pySubFlowName", "").strip()
    if sub_name:
        refs.append(RuleRef(
            rule_name=sub_name, rule_class=cls,
            rule_type="Rule-Obj-Flow", source_rule=source,
            source_field=f"pyFlowSteps[{step.get('pyStepName','')}].pySubFlowName (Split-ForAll)",
            priority=5
        ))
    return refs


# ─── Activity extractor ───────────────────────────────────────────────────────

def _extract_activity(rule: dict, source: str) -> list[RuleRef]:
    refs = []
    cls  = rule.get("pyClassName", "")

    for step in rule.get("pySteps", []):
        method = step.get("pyStepMethod", "").strip()

        # Recursive activity call
        if method == "CallActivity":
            called = step.get("pyStepParam_ActivityName", "").strip()
            if called:
                refs.append(RuleRef(
                    rule_name=called, rule_class=cls,
                    rule_type="Rule-Obj-Activity", source_rule=source,
                    source_field=f"pySteps[{step.get('pyStepIndex','')}].CallActivity",
                    priority=4
                ))

        # When condition on step
        when_name = step.get("pyWhenName", "").strip()
        if when_name:
            refs.append(RuleRef(
                rule_name=when_name, rule_class=cls,
                rule_type="Rule-Obj-When", source_rule=source,
                source_field=f"pySteps[{step.get('pyStepIndex','')}].pyWhenName",
                priority=7
            ))

    return refs


# ─── Flowsection extractor ────────────────────────────────────────────────────

def _extract_flowsection(rule: dict, source: str) -> list[RuleRef]:
    refs = []
    cls  = rule.get("pyClassName", "")

    # Screen section
    screen_name  = rule.get("pyScreenName", "").strip()
    screen_class = rule.get("pyScreenClass", cls).strip() or cls
    if screen_name:
        refs.append(RuleRef(
            rule_name=screen_name, rule_class=screen_class,
            rule_type="Rule-HTML-Section", source_rule=source,
            source_field="pyScreenName", priority=3
        ))

    # Pre / post / validate activities
    for field_name in ("pyPreActivity", "pyPostActivity", "pyValidateActivity"):
        act_name = rule.get(field_name, "").strip()
        if act_name:
            refs.append(RuleRef(
                rule_name=act_name, rule_class=cls,
                rule_type="Rule-Obj-Activity", source_rule=source,
                source_field=field_name, priority=5
            ))

    # When conditions on fields
    for wc in rule.get("pyWhenConditions", []):
        when_name = wc.get("pyWhenName", "").strip()
        if when_name:
            refs.append(RuleRef(
                rule_name=when_name, rule_class=cls,
                rule_type="Rule-Obj-When", source_rule=source,
                source_field="pyWhenConditions[].pyWhenName", priority=8
            ))

    return refs


# ─── HTML Section extractor ───────────────────────────────────────────────────

def _extract_html_section(rule: dict, source: str) -> list[RuleRef]:
    refs = []
    cls  = rule.get("pyClassName", "")

    # Section-level visibility
    when_visible = rule.get("pyWhenVisible", "").strip()
    if when_visible:
        refs.append(RuleRef(
            rule_name=when_visible, rule_class=cls,
            rule_type="Rule-Obj-When", source_rule=source,
            source_field="pyWhenVisible", priority=8
        ))

    # Field-level conditions
    for f in rule.get("pyFields", []):
        when_name = f.get("pyWhen", "").strip()
        if when_name:
            refs.append(RuleRef(
                rule_name=when_name, rule_class=cls,
                rule_type="Rule-Obj-When", source_rule=source,
                source_field=f"pyFields[{f.get('pyPropertyReference','')}].pyWhen",
                priority=8
            ))

    # Embedded sections
    for emb in rule.get("pyEmbeddedSections", []):
        sect_name  = emb.get("pySectionName", "").strip()
        sect_class = emb.get("pySectionClass", cls).strip() or cls
        if sect_name:
            refs.append(RuleRef(
                rule_name=sect_name, rule_class=sect_class,
                rule_type="Rule-HTML-Section", source_rule=source,
                source_field="pyEmbeddedSections[].pySectionName",
                priority=4
            ))
        # Embedded section When condition
        when_name = emb.get("pyWhen", "").strip()
        if when_name:
            refs.append(RuleRef(
                rule_name=when_name, rule_class=cls,
                rule_type="Rule-Obj-When", source_rule=source,
                source_field="pyEmbeddedSections[].pyWhen", priority=8
            ))

    # Repeating layout row template
    repeating = rule.get("pyRepeatingLayout", {})
    if isinstance(repeating, dict):
        row_sect = repeating.get("pySectionName", "").strip()
        if row_sect:
            refs.append(RuleRef(
                rule_name=row_sect, rule_class=cls,
                rule_type="Rule-HTML-Section", source_rule=source,
                source_field="pyRepeatingLayout.pySectionName", priority=5
            ))

    return refs


# ─── When extractor ───────────────────────────────────────────────────────────

def _extract_when(rule: dict, source: str) -> list[RuleRef]:
    """When rules are terminal — no references to follow."""
    return []
