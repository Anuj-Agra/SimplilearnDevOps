"""
tools/parser/manifest_loader.py

Reads a PEGA manifest JSON file and returns the inventory of rules it contains.

A PEGA manifest is the metadata export for a RuleSet — it lists every rule
in the application with its name, class, type, and version, but NOT the
rule's internal logic (flow steps, activity steps, etc.).  The logic lives
in the .bin files alongside the manifest.

Supported manifest formats:
  1. Standard PEGA export  — top-level "pxResults" array of rule records
  2. Simplified export     — top-level "rules" array
  3. Flat list             — top-level JSON array of rule records
  4. Single rule           — a single rule dict (treated as a 1-rule manifest)

Each rule record in the manifest is expected to have at minimum:
  pyRuleName   → the rule name
  pyClassName  → the PEGA class the rule belongs to
  pxObjClass   → the rule type (Rule-Obj-Flow, Rule-Obj-Activity, etc.)

Optional fields (used when present):
  pyRuleSetVersion, pyLabel, pyDescription, pyAvailability, pxCommittedByName
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ─── Rule record ─────────────────────────────────────────────────────────────

@dataclass
class ManifestRule:
    """One rule entry parsed from a manifest JSON."""
    rule_name:       str
    rule_class:      str
    rule_type:       str              # pxObjClass value
    app_name:        str              # which application this came from
    tier:            int              # 0 = COB (most specific), 3 = PegaRules
    ruleset_name:    str = ""
    ruleset_version: str = ""
    label:           str = ""
    description:     str = ""
    availability:    str = "Available"
    bin_file:        Optional[Path] = None   # matched .bin file, if found

    @property
    def node_id(self) -> str:
        return f"{self.rule_class}::{self.rule_name}"

    @property
    def safe_filename(self) -> str:
        return self.node_id.replace("::", "__").replace("/", "_")


# ─── Loader ───────────────────────────────────────────────────────────────────

class ManifestLoader:
    """
    Loads a manifest JSON and resolves BIN file paths for each rule entry.
    """

    def __init__(self, app_name: str, tier: int, folder: Path, manifest_path: Path):
        self.app_name      = app_name
        self.tier          = tier
        self.folder        = folder
        self.manifest_path = manifest_path
        self._bin_index: dict[str, Path] = {}   # lower(safe_key) → Path

    def load(self, rule_type_filter: dict[str, bool] | None = None) -> list[ManifestRule]:
        """
        Parse the manifest file and return a list of ManifestRule objects.
        Only includes rules whose pxObjClass passes rule_type_filter (if provided).
        Resolves BIN file paths for each rule.
        """
        logger.info("[%s] Loading manifest: %s", self.app_name, self.manifest_path.name)

        try:
            raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.error("[%s] Could not read manifest %s: %s", self.app_name, self.manifest_path, e)
            return []

        records = self._extract_records(raw)
        if not records:
            logger.warning("[%s] No rule records found in manifest %s", self.app_name, self.manifest_path.name)
            return []

        # Build BIN index once
        self._build_bin_index()

        ruleset_name    = _extract_top_level(raw, ["pyRuleSetName", "ruleSetName"], "")
        ruleset_version = _extract_top_level(raw, ["pyRuleSetVersion", "ruleSetVersion", "version"], "")

        rules: list[ManifestRule] = []
        skipped_type  = 0
        skipped_avail = 0

        for rec in records:
            if not isinstance(rec, dict):
                continue

            rule_type = str(rec.get("pxObjClass", "")).strip()
            rule_name = str(rec.get("pyRuleName", "")).strip()
            rule_cls  = str(rec.get("pyClassName", "")).strip()

            if not rule_name or not rule_cls or not rule_type:
                continue

            # Apply rule type filter
            if rule_type_filter is not None:
                if not rule_type_filter.get(rule_type, False):
                    skipped_type += 1
                    continue

            # Skip unavailable rules
            avail = str(rec.get("pyAvailability", "Available")).strip()
            if avail in ("Blocked", "Withdrawn"):
                skipped_avail += 1
                continue

            mr = ManifestRule(
                rule_name       = rule_name,
                rule_class      = rule_cls,
                rule_type       = rule_type,
                app_name        = self.app_name,
                tier            = self.tier,
                ruleset_name    = str(rec.get("pyRuleSetName",    ruleset_name)).strip(),
                ruleset_version = str(rec.get("pyRuleSetVersion", ruleset_version)).strip(),
                label           = str(rec.get("pyLabel",       "")).strip(),
                description     = str(rec.get("pyDescription", "")).strip(),
                availability    = avail,
                bin_file        = self._find_bin(rule_name, rule_cls, rule_type),
            )
            rules.append(mr)

        logger.info(
            "[%s] Manifest loaded: %d rules  (%d type-filtered, %d unavailable)",
            self.app_name, len(rules), skipped_type, skipped_avail
        )
        return rules

    # ── Record extraction ─────────────────────────────────────────────────────

    def _extract_records(self, raw) -> list:
        """Normalise all manifest formats to a flat list of rule dicts."""
        if isinstance(raw, list):
            return raw

        if isinstance(raw, dict):
            # Standard PEGA export: { "pxResults": [...] }
            for key in ("pxResults", "rules", "ruleList", "pyResults"):
                val = raw.get(key)
                if isinstance(val, list):
                    return val

            # Single rule record
            if "pyRuleName" in raw and "pxObjClass" in raw:
                return [raw]

        return []

    # ── BIN file matching ─────────────────────────────────────────────────────

    def _build_bin_index(self):
        """
        Index all .bin files in the folder by multiple key patterns so we can
        match them to manifest rule entries.

        PEGA BIN file naming conventions vary by version and export method:
          {RuleName}.bin
          {ClassName}-{RuleName}.bin
          {RuleType}-{RuleName}.bin
          {RuleName}-{Version}.bin
          {SafeRuleName}.bin   (spaces → underscores)

        We normalise all names to lowercase for matching.
        """
        self._bin_index = {}
        if not self.folder.exists():
            return

        for fpath in self.folder.glob("**/*.bin"):
            stem = fpath.stem.lower()
            # Index by stem as-is
            self._bin_index[stem] = fpath
            # Also index by stem with hyphens removed
            self._bin_index[stem.replace("-", "_").replace(" ", "_")] = fpath

        logger.debug("[%s] BIN index: %d files", self.app_name, len(self._bin_index))

    def _find_bin(self, rule_name: str, rule_class: str, rule_type: str) -> Optional[Path]:
        """
        Try to match a manifest rule to a BIN file using several naming patterns.
        Returns the first match found, or None.
        """
        def norm(s: str) -> str:
            return s.lower().replace(" ", "_").replace("-", "_")

        candidates = [
            norm(rule_name),
            norm(f"{rule_class}_{rule_name}"),
            norm(f"{rule_type}_{rule_name}"),
            norm(f"{rule_name}_{rule_class}"),
        ]

        for key in candidates:
            if key in self._bin_index:
                return self._bin_index[key]

        # Partial match: rule_name is a substring of a BIN filename
        n = norm(rule_name)
        for key, fpath in self._bin_index.items():
            if n in key:
                return fpath

        return None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _extract_top_level(data: dict, keys: list[str], default: str) -> str:
    for k in keys:
        v = data.get(k)
        if v:
            return str(v).strip()
    return default
