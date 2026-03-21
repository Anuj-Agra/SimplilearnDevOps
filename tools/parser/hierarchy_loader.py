"""
tools/parser/hierarchy_loader.py

Orchestrates loading all 4 application tiers (COB → CRDFWApp → MSFWApp → PegaRules)
and applying PEGA's "most specific wins" inheritance rule.

How it works:
  1. Load each app's selected manifest JSON (via ManifestLoader)
  2. For each rule discovered: if the same rule_id already exists from a
     more-specific tier, keep the more-specific one (lower tier number wins)
  3. Match BIN files to manifest entries for detail extraction
  4. Return a flat list of LoadedRule objects ready for graph construction

The "most specific wins" rule mirrors PEGA's class hierarchy resolution:
  COB (tier 0) overrides CRDFWApp (tier 1) overrides MSFWApp (tier 2) overrides PegaRules (tier 3)

Output summary (logged):
  ✓ COB       : 42 rules loaded  (12 unique, 0 overridden)
  ✓ CRDFWApp  : 87 rules loaded  (61 unique, 26 overridden by COB)
  ✓ MSFWApp   : 203 rules loaded (139 unique, 64 overridden by higher tiers)
  ✓ PegaRules : 1,240 rules loaded (980 unique, 260 overridden by higher tiers)
  Total unique rules: 1,192
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .manifest_loader import ManifestLoader, ManifestRule
from .bin_reader import read_bin_file, extract_cross_references

logger = logging.getLogger(__name__)


# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class LoadedRule:
    """
    A fully resolved rule from the hierarchy — manifest metadata merged with
    any BIN-extracted content.  This is what the graph builder consumes.
    """
    rule_name:       str
    rule_class:      str
    rule_type:       str
    app_name:        str              # which app this rule came from (after inheritance)
    tier:            int              # 0=COB, 1=CRDFWApp, 2=MSFWApp, 3=PegaRules
    ruleset_name:    str = ""
    ruleset_version: str = ""
    label:           str = ""
    description:     str = ""
    bin_file:        Optional[Path] = None
    bin_content:     Optional[dict] = None    # extracted BIN dict (may be None)
    overridden_by:   str = ""         # app name that overrides this rule (if any)
    include_in_analysis: bool = True

    @property
    def node_id(self) -> str:
        return f"{self.rule_class}::{self.rule_name}"

    @property
    def has_detail(self) -> bool:
        """True if we have some rule content (BIN extraction succeeded)."""
        return self.bin_content is not None and bool(self.bin_content.get("pxObjClass"))

    def to_pseudo_json(self) -> dict:
        """
        Return a dict that looks like the rule's JSON export.
        Merges manifest metadata with BIN-extracted content.
        Used as the 'parsed' payload for the graph node.
        """
        pseudo = {
            "pyRuleName":       self.rule_name,
            "pyClassName":      self.rule_class,
            "pxObjClass":       self.rule_type,
            "pyRuleSetName":    self.ruleset_name,
            "pyRuleSetVersion": self.ruleset_version,
            "pyLabel":          self.label,
            "pyDescription":    self.description,
            "_source_app":      self.app_name,
            "_source_tier":     self.tier,
            "_bin_source":      self.bin_file is not None,
        }
        # Merge in BIN-extracted fields (don't overwrite identity fields)
        if self.bin_content:
            for k, v in self.bin_content.items():
                if k not in pseudo and not k.startswith("_raw"):
                    pseudo[k] = v
        return pseudo


# ─── Hierarchy loader ─────────────────────────────────────────────────────────

class HierarchyLoader:
    """
    Loads all application tiers and applies the most-specific-wins rule.
    """

    def __init__(self, apps_config, rule_type_filter: dict[str, bool],
                 bin_extraction_config=None):
        """
        apps_config      : list[AppConfig] from config_loader — in tier order
        rule_type_filter : dict mapping pxObjClass → bool (True = include)
        bin_extraction_config : BinExtractionConfig from config_loader
        """
        self.apps_config    = sorted(apps_config, key=lambda a: a.tier)
        self.rule_filter    = rule_type_filter
        self.bin_cfg        = bin_extraction_config

    def load(self) -> list[LoadedRule]:
        """
        Load all tiers and return the final merged list of unique rules.
        """
        # rule_id → LoadedRule (the most specific version we've seen)
        registry: dict[str, LoadedRule] = {}
        stats: dict[str, dict] = {}

        for app_cfg in self.apps_config:
            if app_cfg.resolved_manifest is None:
                logger.warning(
                    "[%s] Skipping — no manifest resolved.", app_cfg.name
                )
                continue

            loader = ManifestLoader(
                app_name      = app_cfg.name,
                tier          = app_cfg.tier,
                folder        = app_cfg.folder,
                manifest_path = app_cfg.resolved_manifest,
            )
            manifest_rules = loader.load(rule_type_filter=self.rule_filter)

            app_stats = {"loaded": len(manifest_rules), "new": 0, "overridden": 0}

            for mr in manifest_rules:
                loaded = self._to_loaded_rule(mr, app_cfg.include_in_analysis)

                existing = registry.get(loaded.node_id)
                if existing is None:
                    # New rule — not seen in any higher-tier app
                    registry[loaded.node_id] = loaded
                    app_stats["new"] += 1
                else:
                    # Rule exists from a more-specific (lower-tier) app
                    # Keep the existing more-specific one; mark this one as overridden
                    existing.overridden_by = ""   # already the winner
                    app_stats["overridden"] += 1
                    logger.debug(
                        "Rule %s from [%s] overridden by [%s] (tier %d vs %d)",
                        loaded.node_id, app_cfg.name, existing.app_name,
                        app_cfg.tier, existing.tier
                    )

            stats[app_cfg.name] = app_stats
            logger.info(
                "[%s] tier=%d  loaded=%d  new=%d  overridden=%d",
                app_cfg.name, app_cfg.tier,
                app_stats["loaded"], app_stats["new"], app_stats["overridden"]
            )

        # Now enrich rules with BIN content (if extraction is enabled)
        if self.bin_cfg and self.bin_cfg.enabled:
            self._enrich_with_bin(list(registry.values()))

        result = list(registry.values())
        self._print_summary(result, stats)
        return result

    def _to_loaded_rule(self, mr: ManifestRule, include_in_analysis: bool) -> LoadedRule:
        return LoadedRule(
            rule_name           = mr.rule_name,
            rule_class          = mr.rule_class,
            rule_type           = mr.rule_type,
            app_name            = mr.app_name,
            tier                = mr.tier,
            ruleset_name        = mr.ruleset_name,
            ruleset_version     = mr.ruleset_version,
            label               = mr.label,
            description         = mr.description,
            bin_file            = mr.bin_file,
            include_in_analysis = include_in_analysis,
        )

    def _enrich_with_bin(self, rules: list[LoadedRule]):
        """
        For each rule that has a matched BIN file, extract content and attach
        it to the LoadedRule as bin_content.
        """
        enriched = 0
        no_bin   = 0

        for rule in rules:
            if rule.bin_file and rule.bin_file.exists():
                try:
                    content = read_bin_file(
                        rule.bin_file,
                        min_string_length  = self.bin_cfg.min_string_length,
                        reference_patterns = self.bin_cfg.reference_patterns,
                    )
                    rule.bin_content = content
                    enriched += 1
                except Exception as e:
                    logger.debug("BIN extraction failed for %s: %s", rule.bin_file, e)
            else:
                no_bin += 1

        logger.info(
            "BIN enrichment: %d rules enriched, %d rules have no matching BIN file",
            enriched, no_bin
        )

    def _print_summary(self, rules: list[LoadedRule], stats: dict):
        total = len(rules)
        by_app: dict[str, int] = {}
        by_type: dict[str, int] = {}
        analysable = 0
        has_bin = 0

        for r in rules:
            by_app[r.app_name]    = by_app.get(r.app_name, 0) + 1
            by_type[r.rule_type]  = by_type.get(r.rule_type, 0) + 1
            if r.include_in_analysis:
                analysable += 1
            if r.bin_file:
                has_bin += 1

        logger.info("=" * 60)
        logger.info("Hierarchy load complete: %d unique rules", total)
        logger.info("  Queued for analysis (LLM): %d", analysable)
        logger.info("  Context-only (no LLM):     %d", total - analysable)
        logger.info("  Rules with BIN file:        %d / %d", has_bin, total)
        logger.info("")
        logger.info("  By application (winning tier):")
        for app in sorted(by_app, key=lambda a: next((x.tier for x in self.apps_config if x.name == a), 99)):
            logger.info("    %-14s %d rules", app, by_app[app])
        logger.info("")
        logger.info("  By rule type:")
        for rtype in sorted(by_type):
            logger.info("    %-30s %d", rtype, by_type[rtype])
        logger.info("=" * 60)
