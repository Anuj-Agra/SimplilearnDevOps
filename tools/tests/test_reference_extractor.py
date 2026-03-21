"""
tools/tests/test_reference_extractor.py

Tests for the reference extractor — verifies all 6 rule types produce
the correct RuleRef objects.

Run with:  python -m pytest tools/tests/test_reference_extractor.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from traversal.reference_extractor import extract_references, RuleRef


# ─── CaseType ────────────────────────────────────────────────────────────────

CASETYPE_RULE = {
    "pyRuleName":  "KYC-Work-CDD",
    "pyClassName": "KYC-Work-CDD",
    "pxObjClass":  "Rule-Obj-CaseType",
    "pyStartingFlow": "pyStartCase",
    "pyCreateFlow":   "KYC_CDDCreate",
    "pyStages": [
        {
            "pyStageName": "Initiation",
            "pyProcesses": [
                {"pyFlowName": "KYC_CollectCDDDetails", "pyFlowClass": "KYC-Work-CDD"}
            ]
        },
        {
            "pyStageName": "Approval",
            "pyProcesses": [
                {"pyFlowName": "KYC_CDDApproval", "pyFlowClass": "KYC-Work-CDD"}
            ]
        },
    ],
    "pyActionFlows": [
        {"pyActionName": "Reopen", "pyFlowName": "pyReOpen"}
    ],
    "pyCaseRelationships": [
        {"pyRelationshipType": "Child", "pyChildClass": "KYC-Work-EDD"}
    ]
}

def test_casetype_entry_flows():
    refs = extract_references(CASETYPE_RULE)
    rule_names = [r.rule_name for r in refs]
    assert "pyStartCase"          in rule_names
    assert "KYC_CDDCreate"        in rule_names
    assert "KYC_CollectCDDDetails" in rule_names
    assert "KYC_CDDApproval"      in rule_names

def test_casetype_action_flows():
    refs = extract_references(CASETYPE_RULE)
    assert any(r.rule_name == "pyReOpen" for r in refs)

def test_casetype_child_case():
    refs = extract_references(CASETYPE_RULE)
    child = next((r for r in refs if r.rule_name == "KYC-Work-EDD"), None)
    assert child is not None
    assert child.rule_type == "Rule-Obj-CaseType"

def test_casetype_all_are_ruletype_flow_or_casetype():
    refs = extract_references(CASETYPE_RULE)
    for r in refs:
        assert r.rule_type in ("Rule-Obj-Flow", "Rule-Obj-CaseType"), \
            f"Unexpected rule type {r.rule_type} for {r.rule_name}"


# ─── Flow ─────────────────────────────────────────────────────────────────────

FLOW_RULE = {
    "pyRuleName":  "KYC_CDDOnboarding",
    "pyClassName": "KYC-Work-CDD",
    "pxObjClass":  "Rule-Obj-Flow",
    "pyFlowSteps": [
        {
            "pyStepName":       "CollectDetails",
            "pyStepType":       "Assignment",
            "pyFlowActionName": "KYC_CollectCDDDetails",
            "pyFlowActionClass":"KYC-Work-CDD",
        },
        {
            "pyStepName":      "CalcRisk",
            "pyStepType":      "Utility",
            "pyActivityName":  "KYC_CalculateRiskScore",
        },
        {
            "pyStepName":      "RiskDecision",
            "pyStepType":      "Decision",
            "pyWhenName":      "KYC_IsHighRisk",
        },
        {
            "pyStepName":      "SpawnEDD",
            "pyStepType":      "SubFlow",
            "pySubFlowName":   "KYC_EDDProcess",
            "pySubFlowClass":  "KYC-Work-EDD",
        },
        {
            "pyStepName":      "BackgroundAsync",
            "pyStepType":      "Spinoff",
            "pySubFlowName":   "KYC_BackgroundCheck",
            "pySubFlowClass":  "KYC-Work-CDD",
        },
        {
            "pyStepName":  "End",
            "pyStepType":  "End",
        }
    ],
    "pyConnectors": [
        {
            "pyConnectName": "HighRisk",
            "pyStepFrom":    "RiskDecision",
            "pyStepTo":      "SpawnEDD",
            "pyWhenName":    "KYC_IsHighRisk",
        }
    ]
}

def test_flow_assignment_ref():
    refs = extract_references(FLOW_RULE)
    assert any(r.rule_name == "KYC_CollectCDDDetails" and r.rule_type == "Rule-Obj-Flowsection"
               for r in refs)

def test_flow_utility_activity_ref():
    refs = extract_references(FLOW_RULE)
    assert any(r.rule_name == "KYC_CalculateRiskScore" and r.rule_type == "Rule-Obj-Activity"
               for r in refs)

def test_flow_decision_when_ref():
    refs = extract_references(FLOW_RULE)
    when_refs = [r for r in refs if r.rule_name == "KYC_IsHighRisk"]
    assert len(when_refs) >= 1   # appears in step AND connector
    assert all(r.rule_type == "Rule-Obj-When" for r in when_refs)

def test_flow_subflow_ref():
    refs = extract_references(FLOW_RULE)
    subflow = next((r for r in refs if r.rule_name == "KYC_EDDProcess"), None)
    assert subflow is not None
    assert subflow.rule_type == "Rule-Obj-Flow"
    assert subflow.is_async is False

def test_flow_spinoff_is_async():
    refs = extract_references(FLOW_RULE)
    spinoff = next((r for r in refs if r.rule_name == "KYC_BackgroundCheck"), None)
    assert spinoff is not None
    assert spinoff.is_async is True

def test_flow_end_step_not_a_ref():
    refs = extract_references(FLOW_RULE)
    # End steps should not produce references
    assert not any(r.rule_name == "End" for r in refs)


# ─── Activity ─────────────────────────────────────────────────────────────────

ACTIVITY_RULE = {
    "pyRuleName":  "KYC_CalculateRiskScore",
    "pyClassName": "KYC-Work-CDD",
    "pxObjClass":  "Rule-Obj-Activity",
    "pySteps": [
        {
            "pyStepIndex":  1,
            "pyStepMethod": "Property-Set",
            "pyWhenName":   "",
        },
        {
            "pyStepIndex":  2,
            "pyStepMethod": "CallActivity",
            "pyStepParam_ActivityName": "KYC_CheckPEPStatus",
            "pyWhenName":   "KYC_IsIndividualCustomer",
        },
        {
            "pyStepIndex":  3,
            "pyStepMethod": "Obj-Save",
            "pyWhenName":   "",
        }
    ]
}

def test_activity_call_activity_ref():
    refs = extract_references(ACTIVITY_RULE)
    called = next((r for r in refs if r.rule_name == "KYC_CheckPEPStatus"), None)
    assert called is not None
    assert called.rule_type == "Rule-Obj-Activity"

def test_activity_when_ref():
    refs = extract_references(ACTIVITY_RULE)
    assert any(r.rule_name == "KYC_IsIndividualCustomer" and r.rule_type == "Rule-Obj-When"
               for r in refs)

def test_activity_propertyset_no_ref():
    refs = extract_references(ACTIVITY_RULE)
    # Property-Set step with no WhenName should produce no refs
    step1_refs = [r for r in refs if r.source_field.startswith("pySteps[1]")]
    assert len(step1_refs) == 0


# ─── Flowsection ──────────────────────────────────────────────────────────────

FLOWSECTION_RULE = {
    "pyRuleName":        "KYC_CollectCDDDetails",
    "pyClassName":       "KYC-Work-CDD",
    "pxObjClass":        "Rule-Obj-Flowsection",
    "pyScreenName":      "CDDInitiation",
    "pyScreenClass":     "KYC-Work-CDD",
    "pyPreActivity":     "KYC_PreLoadCDD",
    "pyPostActivity":    "KYC_PostSubmitCDD",
    "pyValidateActivity":"KYC_ValidateCDD",
    "pyWhenConditions":  [{"pyWhenName": "KYC_IsReopened", "pyEffect": "ReadOnly"}]
}

def test_flowsection_screen_ref():
    refs = extract_references(FLOWSECTION_RULE)
    screen = next((r for r in refs if r.rule_name == "CDDInitiation"), None)
    assert screen is not None
    assert screen.rule_type == "Rule-HTML-Section"

def test_flowsection_activity_refs():
    refs = extract_references(FLOWSECTION_RULE)
    act_names = {r.rule_name for r in refs if r.rule_type == "Rule-Obj-Activity"}
    assert "KYC_PreLoadCDD"   in act_names
    assert "KYC_PostSubmitCDD" in act_names
    assert "KYC_ValidateCDD"  in act_names

def test_flowsection_when_condition():
    refs = extract_references(FLOWSECTION_RULE)
    assert any(r.rule_name == "KYC_IsReopened" and r.rule_type == "Rule-Obj-When"
               for r in refs)


# ─── HTML Section ─────────────────────────────────────────────────────────────

SECTION_RULE = {
    "pyRuleName":    "CDDInitiation",
    "pyClassName":   "KYC-Work-CDD",
    "pxObjClass":    "Rule-HTML-Section",
    "pyWhenVisible": "KYC_IsCDDStage",
    "pyFields": [
        {"pyPropertyReference": ".CustomerName", "pyWhen": ""},
        {"pyPropertyReference": ".TaxID",         "pyWhen": "KYC_IsTaxIDRequired"},
    ],
    "pyEmbeddedSections": [
        {"pySectionName": "CDDAddressSection", "pySectionClass": "KYC-Work-CDD", "pyWhen": ""},
        {"pySectionName": "UBOSection",        "pySectionClass": "KYC-Work-CDD", "pyWhen": "KYC_IsCorporate"},
    ],
    "pyRepeatingLayout": {
        "pyPageListProperty": ".DocList",
        "pySectionName": "DocRowSection",
    }
}

def test_section_visibility_when():
    refs = extract_references(SECTION_RULE)
    assert any(r.rule_name == "KYC_IsCDDStage" and r.rule_type == "Rule-Obj-When"
               for r in refs)

def test_section_field_when():
    refs = extract_references(SECTION_RULE)
    assert any(r.rule_name == "KYC_IsTaxIDRequired" and r.rule_type == "Rule-Obj-When"
               for r in refs)

def test_section_embedded_section_refs():
    refs = extract_references(SECTION_RULE)
    sect_names = {r.rule_name for r in refs if r.rule_type == "Rule-HTML-Section"}
    assert "CDDAddressSection" in sect_names
    assert "UBOSection"        in sect_names
    assert "DocRowSection"     in sect_names   # repeating layout

def test_section_embedded_when():
    refs = extract_references(SECTION_RULE)
    assert any(r.rule_name == "KYC_IsCorporate" and r.rule_type == "Rule-Obj-When"
               for r in refs)


# ─── When (terminal) ──────────────────────────────────────────────────────────

WHEN_RULE = {
    "pyRuleName":   "KYC_IsHighRisk",
    "pyClassName":  "KYC-Work-CDD",
    "pxObjClass":   "Rule-Obj-When",
    "pyExpression": ".RiskRating == \"HIGH\"",
}

def test_when_produces_no_refs():
    refs = extract_references(WHEN_RULE)
    assert refs == [], "When rules are terminal and should produce no references"


# ─── Unknown type ─────────────────────────────────────────────────────────────

def test_unknown_rule_type_returns_empty():
    rule = {"pyRuleName": "foo", "pyClassName": "bar", "pxObjClass": "Rule-Unknown-Type"}
    refs = extract_references(rule)
    assert refs == []


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
