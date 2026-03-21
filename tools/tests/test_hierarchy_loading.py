"""
tools/tests/test_hierarchy_loading.py

Tests for:
  - config_loader: YAML parsing, manifest version resolution, path resolution
  - manifest_loader: record extraction, BIN matching, rule type filtering
  - bin_reader: string extraction, cross-reference detection
  - hierarchy_loader: most-specific-wins inheritance, tier ordering

Run with:  python -m pytest tools/tests/test_hierarchy_loading.py -v
           OR standalone: python tools/tests/test_hierarchy_loading.py
"""

import json
import os
import struct
import sys
import tempfile
from pathlib import Path

# ── Make tools/ importable ────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_manifest(rules: list[dict], version: str = "01-01-01",
                  ruleset_name: str = "TestRuleset") -> dict:
    """Build a minimal PEGA manifest dict."""
    return {
        "pyRuleSetName":    ruleset_name,
        "pyRuleSetVersion": version,
        "pxResults": rules,
    }


def make_rule_record(rule_name="TestFlow", class_name="Test-Work-CDD",
                     rule_type="Rule-Obj-Flow", availability="Available") -> dict:
    return {
        "pyRuleName":    rule_name,
        "pyClassName":   class_name,
        "pxObjClass":    rule_type,
        "pyAvailability":availability,
        "pyLabel":       f"Label for {rule_name}",
        "pyDescription": f"Description of {rule_name}",
    }


def write_manifest_file(folder: Path, filename: str, rules: list[dict],
                        version: str = "01-01-01") -> Path:
    fpath = folder / filename
    fpath.write_text(json.dumps(make_manifest(rules, version)), encoding="utf-8")
    return fpath


def make_fake_bin(strings: list[str]) -> bytes:
    """
    Create a fake BIN file containing readable strings in Java short-string format
    (2-byte big-endian length prefix + UTF-8 bytes), mixed with random binary garbage.
    """
    data = bytearray()
    for s in strings:
        enc = s.encode("utf-8")
        data += struct.pack(">H", len(enc)) + enc
        # Add some binary garbage between strings
        data += bytes([0x00, 0xAC, 0xED, 0x00, 0x05])
    return bytes(data)


# ─── config_loader tests ──────────────────────────────────────────────────────

class TestConfigLoader:

    def _write_config(self, tmp: Path, overrides: dict = None) -> Path:
        """Write a minimal valid config YAML to tmp and return path."""
        import yaml

        cob_dir  = tmp / "COB";       cob_dir.mkdir()
        crdfw_dir= tmp / "CRDFWApp";  crdfw_dir.mkdir()
        msfw_dir = tmp / "MSFWApp";   msfw_dir.mkdir()
        pega_dir = tmp / "PegaRules"; pega_dir.mkdir()

        # Write a manifest in each folder so version resolution works
        for folder, ver in [(cob_dir, "01-02-00"), (crdfw_dir, "01-01-05"),
                            (msfw_dir, "01-01-04"), (pega_dir, "08-07-01")]:
            write_manifest_file(folder, f"manifest-{ver}.json",
                                [make_rule_record()], version=ver)

        cfg_data = {
            "hierarchy": [
                {"name": "COB",       "tier": 0, "folder": str(cob_dir),   "manifest_version": "latest", "include_in_analysis": True},
                {"name": "CRDFWApp",  "tier": 1, "folder": str(crdfw_dir), "manifest_version": "latest", "include_in_analysis": True},
                {"name": "MSFWApp",   "tier": 2, "folder": str(msfw_dir),  "manifest_version": "latest", "include_in_analysis": False},
                {"name": "PegaRules", "tier": 3, "folder": str(pega_dir),  "manifest_version": "latest", "include_in_analysis": False},
            ],
            "analysis": {
                "root_casetype": "KYC-Work-CDD",
                "role": "ba",
                "model": "claude-sonnet-4-20250514",
                "max_rules_per_session": 30,
                "token_budget_per_rule": 5000,
            },
            "workspace": str(tmp / "workspace"),
        }
        if overrides:
            cfg_data.update(overrides)

        cfg_path = tmp / "config.yaml"
        cfg_path.write_text(yaml.dump(cfg_data), encoding="utf-8")
        return cfg_path

    def test_loads_all_4_apps(self):
        from config.config_loader import load_config
        with tempfile.TemporaryDirectory() as td:
            cfg = load_config(self._write_config(Path(td)))
            assert len(cfg.hierarchy) == 4
            names = [a.name for a in cfg.hierarchy]
            assert "COB" in names
            assert "CRDFWApp" in names
            assert "MSFWApp" in names
            assert "PegaRules" in names

    def test_tier_order(self):
        from config.config_loader import load_config
        with tempfile.TemporaryDirectory() as td:
            cfg = load_config(self._write_config(Path(td)))
            tiers = [a.tier for a in cfg.hierarchy]
            assert tiers == sorted(tiers), "Apps should be sorted by tier (0→3)"

    def test_analysis_settings(self):
        from config.config_loader import load_config
        with tempfile.TemporaryDirectory() as td:
            cfg = load_config(self._write_config(Path(td)))
            assert cfg.root_casetype == "KYC-Work-CDD"
            assert cfg.role == "ba"
            assert cfg.max_rules_per_session == 30
            assert cfg.token_budget_per_rule == 5000

    def test_include_in_analysis_flag(self):
        from config.config_loader import load_config
        with tempfile.TemporaryDirectory() as td:
            cfg = load_config(self._write_config(Path(td)))
            analysable = [a for a in cfg.hierarchy if a.include_in_analysis]
            context_only = [a for a in cfg.hierarchy if not a.include_in_analysis]
            assert len(analysable) == 2    # COB + CRDFWApp
            assert len(context_only) == 2  # MSFWApp + PegaRules

    def test_manifest_latest_resolved(self):
        from config.config_loader import load_config
        with tempfile.TemporaryDirectory() as td:
            cfg = load_config(self._write_config(Path(td)))
            for app in cfg.hierarchy:
                assert app.resolved_manifest is not None, \
                    f"{app.name} manifest should be resolved"
                assert app.resolved_manifest.exists(), \
                    f"Resolved manifest should exist: {app.resolved_manifest}"

    def test_manifest_exact_version(self):
        """Test that an exact version string resolves correctly."""
        import yaml
        from config.config_loader import load_config
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            cob_dir = td / "COB"; cob_dir.mkdir()
            # Create two manifests with different versions
            write_manifest_file(cob_dir, "manifest-old.json",
                                [make_rule_record()], version="01-01-00")
            write_manifest_file(cob_dir, "manifest-new.json",
                                [make_rule_record()], version="01-02-00")

            cfg_path = td / "config.yaml"
            cfg_data = {
                "hierarchy": [{"name": "COB", "tier": 0, "folder": str(cob_dir),
                               "manifest_version": "01-01-00", "include_in_analysis": True}],
                "analysis":  {"root_casetype": None},
                "workspace": str(td / "ws"),
            }
            cfg_path.write_text(yaml.dump(cfg_data))
            cfg = load_config(cfg_path)
            assert cfg.hierarchy[0].resolved_manifest is not None
            assert "old" in cfg.hierarchy[0].resolved_manifest.name

    def test_multiple_manifests_latest_picks_highest(self):
        """Latest should pick the manifest with the highest version."""
        import yaml
        from config.config_loader import load_config
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            cob_dir = td / "COB"; cob_dir.mkdir()
            write_manifest_file(cob_dir, "manifest-v1.json",
                                [make_rule_record()], version="01-01-00")
            write_manifest_file(cob_dir, "manifest-v2.json",
                                [make_rule_record()], version="01-03-00")
            write_manifest_file(cob_dir, "manifest-v3.json",
                                [make_rule_record()], version="01-02-00")

            cfg_path = td / "config.yaml"
            cfg_data = {
                "hierarchy": [{"name": "COB", "tier": 0, "folder": str(cob_dir),
                               "manifest_version": "latest", "include_in_analysis": True}],
                "analysis": {"root_casetype": None},
                "workspace": str(td / "ws"),
            }
            cfg_path.write_text(yaml.dump(cfg_data))
            cfg = load_config(cfg_path)
            # Should pick v2 (01-03-00) — highest version
            assert "v2" in cfg.hierarchy[0].resolved_manifest.name


# ─── manifest_loader tests ────────────────────────────────────────────────────

class TestManifestLoader:

    def test_loads_rules_from_pxresults(self):
        from parser.manifest_loader import ManifestLoader
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            manifest_path = write_manifest_file(td, "manifest.json", [
                make_rule_record("Flow_A", "TestApp", "Rule-Obj-Flow"),
                make_rule_record("Flow_B", "TestApp", "Rule-Obj-Flow"),
                make_rule_record("Act_A",  "TestApp", "Rule-Obj-Activity"),
            ])
            loader = ManifestLoader("COB", 0, td, manifest_path)
            rules  = loader.load()
            assert len(rules) == 3
            names = [r.rule_name for r in rules]
            assert "Flow_A" in names
            assert "Flow_B" in names
            assert "Act_A"  in names

    def test_rule_type_filter(self):
        from parser.manifest_loader import ManifestLoader
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            manifest_path = write_manifest_file(td, "manifest.json", [
                make_rule_record("Flow_A", rule_type="Rule-Obj-Flow"),
                make_rule_record("When_A", rule_type="Rule-Obj-When"),
                make_rule_record("Act_A",  rule_type="Rule-Obj-Activity"),
            ])
            loader = ManifestLoader("COB", 0, td, manifest_path)
            filter_only_flows = {
                "Rule-Obj-Flow": True,
                "Rule-Obj-When": False,
                "Rule-Obj-Activity": False,
            }
            rules = loader.load(rule_type_filter=filter_only_flows)
            assert len(rules) == 1
            assert rules[0].rule_name == "Flow_A"

    def test_blocked_rules_excluded(self):
        from parser.manifest_loader import ManifestLoader
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            manifest_path = write_manifest_file(td, "manifest.json", [
                make_rule_record("ActiveRule", availability="Available"),
                make_rule_record("BlockedRule", availability="Blocked"),
                make_rule_record("WithdrawnRule", availability="Withdrawn"),
            ])
            loader = ManifestLoader("COB", 0, td, manifest_path)
            rules  = loader.load()
            names  = [r.rule_name for r in rules]
            assert "ActiveRule"    in names
            assert "BlockedRule"   not in names
            assert "WithdrawnRule" not in names

    def test_app_name_and_tier_set(self):
        from parser.manifest_loader import ManifestLoader
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            mp = write_manifest_file(td, "m.json", [make_rule_record("R1")])
            loader = ManifestLoader("CRDFWApp", 1, td, mp)
            rules  = loader.load()
            assert rules[0].app_name == "CRDFWApp"
            assert rules[0].tier     == 1

    def test_bin_file_matching(self):
        """A BIN file named after the rule should be matched."""
        from parser.manifest_loader import ManifestLoader
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            # Create a manifest entry
            mp = write_manifest_file(td, "m.json", [make_rule_record("MyFlow")])
            # Create a BIN file with the same name
            (td / "myflow.bin").write_bytes(b"\x00\x01\x02")
            loader = ManifestLoader("COB", 0, td, mp)
            rules  = loader.load()
            assert rules[0].bin_file is not None
            assert rules[0].bin_file.name == "myflow.bin"

    def test_empty_manifest(self):
        from parser.manifest_loader import ManifestLoader
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            mp = write_manifest_file(td, "empty.json", [])
            loader = ManifestLoader("COB", 0, td, mp)
            rules  = loader.load()
            assert rules == []


# ─── bin_reader tests ─────────────────────────────────────────────────────────

class TestBinReader:

    def test_extracts_readable_strings(self):
        from parser.bin_reader import read_bin_file
        with tempfile.TemporaryDirectory() as td:
            td  = Path(td)
            bin_path = td / "myflow.bin"
            # Write a BIN with known strings
            bin_path.write_bytes(
                make_fake_bin(["Rule-Obj-Flow", "KYC_CDDOnboarding", "KYC-Work-CDD"])
            )
            result = read_bin_file(bin_path)
            assert result["_bin_source"] is True
            assert len(result["_raw_strings"]) > 0

    def test_detects_rule_type(self):
        from parser.bin_reader import read_bin_file
        with tempfile.TemporaryDirectory() as td:
            bin_path = Path(td) / "testflow.bin"
            bin_path.write_bytes(
                make_fake_bin(["Rule-Obj-Flow", "SomeFlowName", "SomeClass"])
            )
            result = read_bin_file(bin_path)
            assert result.get("pxObjClass") == "Rule-Obj-Flow"

    def test_fallback_rule_name_from_filename(self):
        from parser.bin_reader import read_bin_file
        with tempfile.TemporaryDirectory() as td:
            bin_path = Path(td) / "KYC_CDDOnboarding.bin"
            bin_path.write_bytes(b"\x00\x01\x02\x03")   # no readable strings
            result = read_bin_file(bin_path)
            assert result["pyRuleName"] == "KYC_CDDOnboarding"

    def test_extracts_cross_references(self):
        from parser.bin_reader import read_bin_file
        with tempfile.TemporaryDirectory() as td:
            bin_path = Path(td) / "flow.bin"
            # Embed a reference field followed by a value
            bin_path.write_bytes(
                make_fake_bin([
                    "Rule-Obj-Flow",
                    "pyActivityName",
                    "KYC_CalculateRiskScore",
                    "pySubFlowName",
                    "KYC_EDDProcess",
                ])
            )
            result = read_bin_file(bin_path)
            # At least one reference should have been picked up
            has_ref = (
                bool(result.get("pyActivityName")) or
                bool(result.get("pySubFlowName"))  or
                bool(result.get("_all_pyActivityName")) or
                bool(result.get("_all_pySubFlowName"))
            )
            assert has_ref, f"Expected at least one cross-reference. Got: {result}"

    def test_handles_unreadable_file(self):
        from parser.bin_reader import read_bin_file
        with tempfile.TemporaryDirectory() as td:
            bin_path = Path(td) / "broken.bin"
            bin_path.write_bytes(bytes(range(256)) * 4)  # pure binary garbage
            result = read_bin_file(bin_path)
            assert result is not None
            assert "_bin_source" in result


# ─── hierarchy_loader tests ───────────────────────────────────────────────────

class TestHierarchyLoader:

    def _setup_apps(self, tmp: Path) -> list:
        """Create 3 app folders with manifests and return AppConfig list.
        SharedFlow uses the SAME class name across all apps to test most-specific-wins.
        """
        from config.config_loader import AppConfig
        apps = []
        for tier, name in [(0, "COB"), (1, "CRDFWApp"), (2, "MSFWApp")]:
            folder = tmp / name
            folder.mkdir()
            mp = write_manifest_file(
                folder, "manifest.json",
                [
                    make_rule_record("SharedFlow",     "SharedApp-Work", "Rule-Obj-Flow"),
                    make_rule_record(f"UniqueIn{name}", f"{name}-Work",   "Rule-Obj-Flow"),
                ],
                version=f"01-0{tier+1}-00"
            )
            app = AppConfig(
                name               = name,
                tier               = tier,
                folder             = folder,
                manifest_version   = "latest",
                include_in_analysis= tier < 2,
            )
            app.resolved_manifest = mp
            apps.append(app)
        return apps

    def test_most_specific_wins(self):
        """SharedFlow exists in all tiers — COB (tier 0) should win."""
        from parser.hierarchy_loader import HierarchyLoader
        with tempfile.TemporaryDirectory() as td:
            apps  = self._setup_apps(Path(td))
            hl    = HierarchyLoader(apps, {
                "Rule-Obj-Flow": True,
                "Rule-Obj-Activity": True,
            })
            rules = hl.load()

            # There should be exactly one SharedFlow (not 3)
            shared_flows = [r for r in rules if r.rule_name == "SharedFlow"]
            assert len(shared_flows) == 1, \
                f"Expected 1 SharedFlow (most-specific-wins), got {len(shared_flows)}"
            # It should come from COB (tier 0)
            assert shared_flows[0].tier == 0
            assert shared_flows[0].app_name == "COB"

    def test_unique_rules_all_present(self):
        """Each app's unique rule should appear in the result."""
        from parser.hierarchy_loader import HierarchyLoader
        with tempfile.TemporaryDirectory() as td:
            apps  = self._setup_apps(Path(td))
            hl    = HierarchyLoader(apps, {"Rule-Obj-Flow": True})
            rules = hl.load()
            names = {r.rule_name for r in rules}
            assert "UniqueInCOB"      in names
            assert "UniqueInCRDFWApp" in names
            assert "UniqueInMSFWApp"  in names

    def test_include_in_analysis_propagated(self):
        """Rules from MSFWApp (tier 2, include_in_analysis=False) should be context-only."""
        from parser.hierarchy_loader import HierarchyLoader
        with tempfile.TemporaryDirectory() as td:
            apps  = self._setup_apps(Path(td))
            hl    = HierarchyLoader(apps, {"Rule-Obj-Flow": True})
            rules = hl.load()

            msfw_rules = [r for r in rules if r.app_name == "MSFWApp"]
            for r in msfw_rules:
                assert r.include_in_analysis is False, \
                    f"MSFWApp rule {r.rule_name} should be context-only"

    def test_empty_folder_no_crash(self):
        """An app with no manifest should be skipped gracefully."""
        from config.config_loader import AppConfig
        from parser.hierarchy_loader import HierarchyLoader
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            empty_folder = td / "EmptyApp"
            empty_folder.mkdir()
            app = AppConfig("EmptyApp", 0, empty_folder, "latest", True)
            app.resolved_manifest = None  # not resolved — no manifest found
            hl  = HierarchyLoader([app], {"Rule-Obj-Flow": True})
            rules = hl.load()   # should not raise
            assert rules == []


# ─── Integration test ─────────────────────────────────────────────────────────

class TestFullHierarchyIntegration:
    """
    End-to-end test: YAML config → manifest loading → hierarchy merging → rule graph.
    Uses only in-memory temp files (no real PEGA export needed).
    """

    def test_full_pipeline_dry_run(self):
        """
        Build a rule graph from a synthetic 4-tier hierarchy.
        Verifies that most-specific-wins is applied and the graph is built correctly.
        """
        import yaml
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from config.config_loader import load_config
        from traversal.rule_graph import RuleGraph

        with tempfile.TemporaryDirectory() as td:
            td = Path(td)

            # Create 4 app folders with manifests
            for tier, name, version in [
                (0, "COB",       "02-00-01"),
                (1, "CRDFWApp",  "01-05-03"),
                (2, "MSFWApp",   "01-04-00"),
                (3, "PegaRules", "08-07-01"),
            ]:
                folder = td / name
                folder.mkdir()
                # SharedFlow exists in all tiers
                # UniqueName exists only in this tier
                write_manifest_file(folder, f"manifest-{version}.json", [
                    make_rule_record("SharedFlow",     "KYCShared-Work", "Rule-Obj-Flow"),
                    make_rule_record(f"Only{name}Flow", f"{name}-Work",  "Rule-Obj-Flow"),
                    make_rule_record("KYCCaseType",     "KYCShared-Work","Rule-Obj-CaseType"),
                ], version=version)

            cfg_path = td / "config.yaml"
            cfg_data = {
                "hierarchy": [
                    {"name": "COB",       "tier": 0, "folder": str(td/"COB"),       "manifest_version": "latest", "include_in_analysis": True},
                    {"name": "CRDFWApp",  "tier": 1, "folder": str(td/"CRDFWApp"),  "manifest_version": "latest", "include_in_analysis": True},
                    {"name": "MSFWApp",   "tier": 2, "folder": str(td/"MSFWApp"),   "manifest_version": "latest", "include_in_analysis": False},
                    {"name": "PegaRules", "tier": 3, "folder": str(td/"PegaRules"), "manifest_version": "latest", "include_in_analysis": False},
                ],
                "analysis": {
                    "root_casetype": "KYCCaseType",
                    "role": "ba",
                    "max_rules_per_session": 20,
                    "token_budget_per_rule": 5000,
                },
                "workspace": str(td / "workspace"),
                "rule_type_filter": {
                    "Rule-Obj-CaseType": True,
                    "Rule-Obj-Flow": True,
                },
            }
            cfg_path.write_text(yaml.dump(cfg_data))
            cfg = load_config(cfg_path)

            # Build graph
            graph = RuleGraph.from_hierarchy_config(cfg)

            # SharedFlow should appear exactly once — from COB (tier 0)
            shared = [n for n in graph if n.rule_name == "SharedFlow"]
            assert len(shared) == 1, f"Expected 1 SharedFlow, got {len(shared)}"
            assert shared[0].app_name == "COB"

            # Each app's unique flow should exist
            unique_names = {n.rule_name for n in graph}
            assert "OnlyCOBFlow"       in unique_names
            assert "OnlyCRDFWAppFlow"  in unique_names
            assert "OnlyMSFWAppFlow"   in unique_names
            assert "OnlyPegaRulesFlow" in unique_names

            # Analysis queue should only include COB + CRDFWApp rules
            queue = graph.analysis_queue()
            queue_apps = {n.app_name for n in queue}
            assert "MSFWApp"   not in queue_apps, "MSFWApp should be context-only"
            assert "PegaRules" not in queue_apps, "PegaRules should be context-only"

            print(
                f"\n  Integration test ✓  —  {len(list(graph))} total nodes, "
                f"{len(queue)} in analysis queue"
            )


# ─── Simple standalone runner ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running tests inline (no pytest needed)...\n")

    test_classes = [
        TestConfigLoader(),
        TestManifestLoader(),
        TestBinReader(),
        TestHierarchyLoader(),
        TestFullHierarchyIntegration(),
    ]

    total = 0
    passed = 0
    failed = 0

    for tc in test_classes:
        cls_name = type(tc).__name__
        methods  = [m for m in dir(tc) if m.startswith("test_")]
        for method_name in methods:
            total += 1
            method = getattr(tc, method_name)
            try:
                method()
                print(f"  ✓  {cls_name}.{method_name}")
                passed += 1
            except Exception as e:
                print(f"  ✗  {cls_name}.{method_name}  →  {type(e).__name__}: {e}")
                failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed  |  {failed} failed")
    if failed == 0:
        print("All tests passed ✓")
    else:
        print("Some tests failed — check output above")
        sys.exit(1)
