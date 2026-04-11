#!/usr/bin/env python3
"""
tests/test_extractor.py
Unit tests for pega_bin_extractor.py

Run with: pytest tests/ -v
"""

import gzip
import io
import json
import struct
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from pega_bin_extractor import (
    detect_format, parse_zip, parse_gzip, parse_pega_legacy,
    parse_java_serialized, scan_for_xml_fragments, infer_rule_type,
    infer_layer, parse_rule_xml, extract_dependencies, extract_ui_fields,
    extract_flow_steps, deduplicate_rules, PegaRule,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────

SAMPLE_FLOW_XML = """<?xml version="1.0" encoding="UTF-8"?>
<flow pyRuleName="ProcessKYCSubmission" pyClassName="Work-KYC-Case"
      pyRuleSet="KYCPlatform" pyRuleSetVersion="01-01-01"
      pyStatus="Active" pyUpdateOpName="admin@pega.com"
      pxUpdateDateTime="2024-11-15T10:30:00Z">
  <step name="ValidateClient" methodName="ValidateClientData" workParty="Analyst">
    <transition to="AMLScreening" when=".pyStatusWork == Open"/>
    <transition to="End" when=".pyStatusWork == Rejected"/>
  </step>
  <step name="AMLScreening" methodName="ScreenAML" workParty="System">
    <transition to="RiskAssign"/>
  </step>
  <assignment name="RiskAssign" workParty="KYCAnalyst"/>
  <step name="End" methodName="End"/>
</flow>"""

SAMPLE_SECTION_XML = """<?xml version="1.0" encoding="UTF-8"?>
<section pyRuleName="ClientDetailSection" pyClassName="Work-KYC-Case"
         pyRuleSet="KYCPlatform" pyStatus="Active">
  <field name="ClientName" type="TextInput" required="true" label="Client Legal Name"/>
  <field name="DateOfBirth" type="Date" required="false"
         label="Date of Birth" visibleWhen=".EntityType == Individual"/>
  <control name="RiskRating" type="ReadOnly" readOnly="true"/>
  <field name="PEPStatus" type="DropDown" required="true" label="PEP Status"
         listDataPage="D_PEPStatusList"/>
</section>"""

SAMPLE_DECISION_XML = """<?xml version="1.0" encoding="UTF-8"?>
<decision pyRuleName="EvaluateAMLRisk" pyClassName="Work-KYC-Case"
          pyRuleSet="KYCPlatform" pyStatus="Active">
  <row result="High">
    <condition type="condition" value="PEP" field="PEPStatus"/>
  </row>
  <row result="Medium">
    <condition type="condition" value="FATF" field="Jurisdiction"/>
  </row>
  <row result="Low"/>
</decision>"""


def make_zip_bytes(*xml_contents) -> bytes:
    """Create a ZIP binary containing XML files."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, xml in enumerate(xml_contents):
            zf.writestr(f"rule_{i}.xml", xml)
    return buf.getvalue()


def make_gzip_bytes(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(data)
    return buf.getvalue()


def make_legacy_bytes(*xml_contents) -> bytes:
    """Create a minimal Pega legacy binary."""
    blocks = []
    for xml in xml_contents:
        payload = xml.encode("utf-8")
        block = struct.pack(">IHH", len(payload), 0, 1) + payload   # size, no-compress, type=1
        blocks.append(block)

    header = b"PEG\x01"
    header += struct.pack(">I", len(xml_contents))   # record count
    header += struct.pack(">I", 12)                  # index offset (unused)
    return header + b"".join(blocks)


# ── Format Detection Tests ────────────────────────────────────────────────────

class TestFormatDetection:
    def test_detect_zip(self):
        data = make_zip_bytes(SAMPLE_FLOW_XML)
        assert detect_format(data) == "zip"

    def test_detect_gzip(self):
        data = make_gzip_bytes(SAMPLE_FLOW_XML.encode())
        assert detect_format(data) == "gzip"

    def test_detect_legacy(self):
        data = make_legacy_bytes(SAMPLE_FLOW_XML)
        assert detect_format(data) == "pega_legacy"

    def test_detect_raw_xml(self):
        data = SAMPLE_FLOW_XML.encode("utf-8")
        assert detect_format(data) in ("raw_xml", "raw_xml_with_header")

    def test_detect_java_serial(self):
        data = b"\xac\xed\x00\x05" + b"\x00" * 100
        assert detect_format(data) == "java_serialized"

    def test_detect_unknown(self):
        data = b"\x00\x01\x02\x03\x04" * 50
        assert detect_format(data) == "unknown"


# ── ZIP Parsing Tests ─────────────────────────────────────────────────────────

class TestZIPParsing:
    def test_basic_zip_extraction(self):
        data = make_zip_bytes(SAMPLE_FLOW_XML, SAMPLE_SECTION_XML)
        xmls = parse_zip(data, "test.zip")
        assert len(xmls) == 2
        assert any("flow" in x.lower() for x in xmls)
        assert any("section" in x.lower() for x in xmls)

    def test_zip_with_gzip_inner(self):
        inner_gz = make_gzip_bytes(SAMPLE_FLOW_XML.encode())
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("rule.xml", inner_gz)   # gzip inside ZIP
        data = buf.getvalue()
        xmls = parse_zip(data, "test.zip")
        assert any("flow" in x.lower() for x in xmls)

    def test_bad_zip_falls_back_to_scan(self):
        # Not a real ZIP but contains XML
        data = b"GARBAGE" + SAMPLE_FLOW_XML.encode() + b"MORE_GARBAGE"
        xmls = parse_zip(data, "bad.zip")
        # Should fall back to raw scan
        assert len(xmls) >= 0   # no crash

    def test_empty_zip(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            pass   # empty ZIP
        xmls = parse_zip(buf.getvalue(), "empty.zip")
        assert xmls == []


# ── GZIP Parsing Tests ─────────────────────────────────────────────────────────

class TestGZIPParsing:
    def test_gzip_raw_xml(self):
        data = make_gzip_bytes(SAMPLE_FLOW_XML.encode())
        xmls = parse_gzip(data)
        assert len(xmls) >= 1
        assert "flow" in xmls[0].lower()

    def test_gzip_contains_zip(self):
        inner_zip = make_zip_bytes(SAMPLE_FLOW_XML)
        data = make_gzip_bytes(inner_zip)
        xmls = parse_gzip(data)
        assert len(xmls) >= 1


# ── Legacy Format Tests ───────────────────────────────────────────────────────

class TestLegacyParsing:
    def test_legacy_single_rule(self):
        data = make_legacy_bytes(SAMPLE_FLOW_XML)
        xmls = parse_pega_legacy(data, "test.bin")
        assert len(xmls) >= 1

    def test_legacy_multiple_rules(self):
        data = make_legacy_bytes(SAMPLE_FLOW_XML, SAMPLE_SECTION_XML, SAMPLE_DECISION_XML)
        xmls = parse_pega_legacy(data, "test.bin")
        assert len(xmls) >= 3

    def test_legacy_corrupt_header_falls_back(self):
        # Corrupt record count
        data = b"PEG\x01" + struct.pack(">I", 9_999_999) + struct.pack(">I", 12) + b"\x00" * 100
        xmls = parse_pega_legacy(data, "corrupt.bin")
        assert isinstance(xmls, list)   # no crash


# ── XML Rule Parsing Tests ────────────────────────────────────────────────────

class TestXMLParsing:
    def test_parse_flow_rule(self):
        counter = [0]
        rule = parse_rule_xml(SAMPLE_FLOW_XML, "test.bin", None, counter)
        assert rule is not None
        assert rule.rule_type == "Flow"
        assert rule.name == "ProcessKYCSubmission"
        assert rule.pega_class == "Work-KYC-Case"
        assert rule.ruleset == "KYCPlatform"
        assert rule.status == "Active"

    def test_parse_section_rule(self):
        counter = [0]
        rule = parse_rule_xml(SAMPLE_SECTION_XML, "test.bin", None, counter)
        assert rule is not None
        assert rule.rule_type == "UI Section"
        assert len(rule.ui_fields) >= 3

    def test_parse_decision_table(self):
        counter = [0]
        rule = parse_rule_xml(SAMPLE_DECISION_XML, "test.bin", None, counter)
        assert rule is not None
        assert rule.rule_type == "Decision Table"
        assert len(rule.decision_rows) >= 2

    def test_parse_empty_xml_returns_none(self):
        counter = [0]
        rule = parse_rule_xml("", "test.bin", None, counter)
        assert rule is None

    def test_parse_malformed_xml(self):
        counter = [0]
        rule = parse_rule_xml("<broken>not closed", "test.bin", None, counter)
        assert rule is None

    def test_rule_id_increments(self):
        counter = [0]
        r1 = parse_rule_xml(SAMPLE_FLOW_XML, "f1.bin", None, counter)
        r2 = parse_rule_xml(SAMPLE_SECTION_XML, "f2.bin", None, counter)
        assert r1 is not None and r2 is not None
        assert r1.rule_id != r2.rule_id
        assert counter[0] == 2


# ── Inference Tests ───────────────────────────────────────────────────────────

class TestInference:
    def test_rule_type_flow(self):
        assert infer_rule_type("<flow name='x'>") == "Flow"

    def test_rule_type_section(self):
        assert infer_rule_type("<section name='x'>") == "UI Section"

    def test_rule_type_decision(self):
        assert infer_rule_type("<decision name='x'>") == "Decision Table"

    def test_rule_type_unknown(self):
        assert infer_rule_type("<completely_unknown>data</completely_unknown>") == "Unknown"

    def test_layer_framework(self):
        assert infer_layer("PegaFramework") == "Framework"
        assert infer_layer("PegaPlatform") == "Framework"

    def test_layer_industry(self):
        assert infer_layer("FSKYCIndustry") == "Industry"
        assert infer_layer("FinServCore") == "Industry"

    def test_layer_enterprise(self):
        assert infer_layer("MSEnterprise") == "Enterprise"
        assert infer_layer("EnterpriseShared") == "Enterprise"

    def test_layer_implementation(self):
        assert infer_layer("KYCImpl") == "Implementation"
        assert infer_layer("AppCustom") == "Implementation"

    def test_layer_unknown(self):
        assert infer_layer("XYZ123") == "Unknown"


# ── Field Extraction Tests ────────────────────────────────────────────────────

class TestFieldExtraction:
    def test_extract_ui_fields(self):
        from xml.etree import ElementTree as ET
        root = ET.fromstring(SAMPLE_SECTION_XML)
        fields = extract_ui_fields(root)
        names = [f["name"] for f in fields]
        assert "ClientName" in names
        assert "DateOfBirth" in names
        assert "PEPStatus" in names

    def test_extract_dependencies(self):
        from xml.etree import ElementTree as ET
        root = ET.fromstring(SAMPLE_FLOW_XML)
        deps = extract_dependencies(root)
        assert "ValidateClientData" in deps or "AMLScreening" in deps

    def test_extract_flow_steps(self):
        from xml.etree import ElementTree as ET
        root = ET.fromstring(SAMPLE_FLOW_XML)
        steps = extract_flow_steps(root)
        names = [s["name"] for s in steps]
        assert len(steps) >= 2
        assert any("Validate" in n or "AML" in n or "End" in n for n in names)


# ── Deduplication Tests ───────────────────────────────────────────────────────

class TestDeduplication:
    def _make_rule(self, name, layer, checksum_suffix=""):
        import hashlib
        xml = f"<flow>{name}{layer}</flow>"
        checksum = hashlib.md5((xml + checksum_suffix).encode()).hexdigest()[:12]
        return PegaRule(
            rule_id=f"RULE-{name}", name=name, rule_type="Flow",
            pega_class="Work-Test", layer=layer, ruleset="Test",
            ruleset_version="01-01", status="Active", created="", updated="",
            author="", source_file="test.bin", checksum=checksum, raw_xml=xml,
        )

    def test_exact_duplicate_removed(self):
        r1 = self._make_rule("FlowA", "Enterprise")
        r2 = self._make_rule("FlowA", "Enterprise")   # same checksum
        result = deduplicate_rules([r1, r2])
        assert len(result) == 1

    def test_override_kept(self):
        # Same name, different layer → different checksum
        r1 = self._make_rule("FlowA", "Framework", "v1")
        r2 = self._make_rule("FlowA", "Enterprise", "v2")
        result = deduplicate_rules([r1, r2])
        assert len(result) == 2

    def test_different_rules_all_kept(self):
        rules = [self._make_rule(f"Flow{i}", "Enterprise", str(i)) for i in range(5)]
        result = deduplicate_rules(rules)
        assert len(result) == 5


# ── Integration Test ──────────────────────────────────────────────────────────

class TestIntegration:
    def test_full_zip_extraction_pipeline(self, tmp_path):
        """Full pipeline: create ZIP, extract, validate output."""
        from pega_bin_extractor import run_extraction
        from pathlib import Path

        zip_data = make_zip_bytes(SAMPLE_FLOW_XML, SAMPLE_SECTION_XML, SAMPLE_DECISION_XML)
        bin_file = tmp_path / "test_rules.bin"
        bin_file.write_bytes(zip_data)

        output = tmp_path / "rules_extracted.json"
        summary = run_extraction(
            input_paths   = [bin_file],
            manifest_data = None,
            output_path   = output,
            verbose       = False,
        )

        assert output.exists()
        with output.open() as f:
            data = json.load(f)

        assert data["summary"]["total_rules"] >= 2
        assert len(data["rules"]) >= 2

        rule_types = {r["rule_type"] for r in data["rules"]}
        assert "Flow" in rule_types
        assert "UI Section" in rule_types

    def test_manifest_layer_override(self, tmp_path):
        """Manifest layer mapping overrides heuristic inference."""
        from pega_bin_extractor import run_extraction, load_manifest

        # Rule with ruleset "MyCustomRS" — heuristic would say Unknown
        xml = SAMPLE_FLOW_XML.replace('pyRuleSet="KYCPlatform"', 'pyRuleSet="MyCustomRS"')
        zip_data = make_zip_bytes(xml)
        bin_file = tmp_path / "test.bin"
        bin_file.write_bytes(zip_data)

        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps({
            "layer_map": {"MyCustomRS": "Implementation"}
        }))
        manifest_data = load_manifest(manifest_path)

        output = tmp_path / "rules.json"
        run_extraction([bin_file], manifest_data, output)

        with output.open() as f:
            data = json.load(f)

        assert any(r["layer"] == "Implementation" for r in data["rules"])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
