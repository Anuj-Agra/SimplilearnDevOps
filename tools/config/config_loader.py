"""
tools/config/config_loader.py

Loads analysis_config.yaml, validates required fields, resolves "latest"
manifest version to an actual file path per application folder, and
returns a typed AnalysisConfig object consumed by the rest of the engine.

Usage:
    from config.config_loader import load_config
    cfg = load_config(Path("config/analysis_config.yaml"))
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class AppConfig:
    """Configuration for one application tier (COB, CRDFWApp, MSFWApp, PegaRules)."""
    name:                 str
    tier:                 int           # 0 = most specific (COB), 3 = least (PegaRules)
    folder:               Path          # resolved absolute path to the app folder
    manifest_version:     str           # "latest" or exact version string "01-02-03"
    include_in_analysis:  bool          # True = queue for LLM; False = graph context only
    resolved_manifest:    Optional[Path] = None   # filled in after version resolution


@dataclass
class BinExtractionConfig:
    enabled:             bool = True
    min_string_length:   int  = 4
    reference_patterns:  list[str] = field(default_factory=lambda: [
        "pyFlowActionName", "pyActivityName", "pySubFlowName",
        "pyConnectorName", "pyDataTransformName", "pySLAName",
        "pyWhenName", "pyDecisionName", "pyRouterName",
    ])


@dataclass
class AnalysisConfig:
    """Complete, validated configuration for one analysis run."""
    hierarchy:            list[AppConfig]
    root_casetype:        Optional[str]
    role:                 str
    model:                str
    max_rules_per_session: int
    token_budget_per_rule: int
    workspace:            Path
    rule_type_filter:     dict[str, bool]
    bin_extraction:       BinExtractionConfig

    # ── Derived helpers ───────────────────────────────────────────────────────

    def apps_for_analysis(self) -> list[AppConfig]:
        """Apps to queue for LLM analysis (include_in_analysis=True), ordered tier 0→3."""
        return [a for a in self.hierarchy if a.include_in_analysis]

    def all_apps(self) -> list[AppConfig]:
        """All apps in tier order."""
        return sorted(self.hierarchy, key=lambda a: a.tier)

    def app_by_name(self, name: str) -> Optional[AppConfig]:
        return next((a for a in self.hierarchy if a.name == name), None)


# ─── Loader ───────────────────────────────────────────────────────────────────

def load_config(config_path: Path) -> AnalysisConfig:
    """
    Load, validate and fully resolve analysis_config.yaml.
    Raises ValueError with a clear message on any problem.
    Returns a ready-to-use AnalysisConfig.
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required. Run:  pip install pyyaml"
        )

    config_path = Path(config_path).resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Config file is empty or not valid YAML: {config_path}")

    config_dir = config_path.parent

    # ── Hierarchy ──────────────────────────────────────────────────────────────
    raw_hier = raw.get("hierarchy", [])
    if not raw_hier:
        raise ValueError("Config must have at least one entry under 'hierarchy:'")

    _validate_required_apps(raw_hier)
    apps = []
    for entry in raw_hier:
        app = _build_app_config(entry, config_dir)
        app.resolved_manifest = _resolve_manifest(app)
        apps.append(app)

    # sort by tier so COB (0) is first
    apps.sort(key=lambda a: a.tier)
    logger.info("Hierarchy loaded: %s", " → ".join(a.name for a in apps))
    for app in apps:
        logger.info(
            "  [tier %d] %-12s  manifest=%s  analyse=%s",
            app.tier, app.name,
            app.resolved_manifest.name if app.resolved_manifest else "NOT FOUND",
            app.include_in_analysis
        )

    # ── Analysis settings ─────────────────────────────────────────────────────
    an = raw.get("analysis", {})
    role  = str(an.get("role", "ba")).lower()
    if role not in ("ba", "po", "dev", "qa"):
        logger.warning("Unknown role '%s' — defaulting to 'ba'", role)
        role = "ba"

    # ── Rule type filter ──────────────────────────────────────────────────────
    default_filter = {
        "Rule-Obj-CaseType":    True,
        "Rule-Obj-Flow":        True,
        "Rule-Obj-Activity":    True,
        "Rule-Obj-Flowsection": True,
        "Rule-HTML-Section":    True,
        "Rule-Obj-When":        True,
        "Rule-Obj-DataTransform": False,
        "Rule-Obj-Decision":    False,
    }
    raw_filter = raw.get("rule_type_filter", {})
    rule_filter = {**default_filter, **{k: bool(v) for k, v in raw_filter.items()}}

    # ── BIN extraction ────────────────────────────────────────────────────────
    raw_bin = raw.get("bin_extraction", {})
    bin_cfg = BinExtractionConfig(
        enabled           = bool(raw_bin.get("enabled", True)),
        min_string_length = int(raw_bin.get("min_string_length", 4)),
        reference_patterns= list(raw_bin.get("reference_patterns", BinExtractionConfig().reference_patterns)),
    )

    # ── Workspace ─────────────────────────────────────────────────────────────
    raw_ws = raw.get("workspace", "./workspaces/analysis")
    workspace = _resolve_path(raw_ws, config_dir)

    cfg = AnalysisConfig(
        hierarchy             = apps,
        root_casetype         = an.get("root_casetype") or None,
        role                  = role,
        model                 = str(an.get("model", "claude-sonnet-4-20250514")),
        max_rules_per_session = int(an.get("max_rules_per_session", 50)),
        token_budget_per_rule = int(an.get("token_budget_per_rule", 6000)),
        workspace             = workspace,
        rule_type_filter      = rule_filter,
        bin_extraction        = bin_cfg,
    )

    _warn_missing_manifests(cfg)
    return cfg


# ─── Manifest version resolution ─────────────────────────────────────────────

def _resolve_manifest(app: AppConfig) -> Optional[Path]:
    """
    Find the correct manifest JSON file in app.folder.

    Manifest files are identified as JSON files whose content contains any of:
      - a top-level key "pxResults" (PEGA standard export format)
      - a top-level key "rules"
      - a top-level key "ruleSetName"
      - a pyRuleSetVersion field at the top level

    If manifest_version == "latest": pick the file with the highest version.
    If manifest_version == "01-02-03": pick the file whose resolved version
      exactly matches (dashes OR dots treated the same).
    """
    folder = app.folder
    if not folder.exists():
        logger.warning("[%s] Folder does not exist: %s", app.name, folder)
        return None

    candidates = _find_manifest_candidates(folder)
    if not candidates:
        logger.warning("[%s] No manifest JSON files found in %s", app.name, folder)
        return None

    if app.manifest_version == "latest":
        chosen = max(candidates, key=lambda x: x[1])
        logger.info("[%s] Resolved manifest (latest): %s  (version=%s)", app.name, chosen[0].name, chosen[1])
        return chosen[0]

    # Exact version match — normalise dashes ↔ dots
    target = _normalise_version(app.manifest_version)
    for fpath, ver in candidates:
        if _normalise_version(ver) == target:
            logger.info("[%s] Resolved manifest (exact %s): %s", app.name, target, fpath.name)
            return fpath

    # Fallback: try filename match
    for fpath, ver in candidates:
        if target in fpath.name.replace(".", "-"):
            logger.warning(
                "[%s] Exact version '%s' not found in content — matched by filename: %s",
                app.name, app.manifest_version, fpath.name
            )
            return fpath

    logger.error(
        "[%s] Could not resolve manifest version '%s'. Available: %s",
        app.name, app.manifest_version,
        ", ".join(f"{f.name}({v})" for f, v in candidates)
    )
    return None


def _find_manifest_candidates(folder: Path) -> list[tuple[Path, str]]:
    """
    Scan folder for JSON files that look like PEGA manifests.
    Returns list of (path, version_string) tuples.
    """
    candidates = []

    for fpath in folder.glob("*.json"):
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        if not isinstance(data, dict):
            continue

        # Must look like a manifest
        is_manifest = (
            "pxResults" in data
            or "rules" in data
            or "ruleSetName" in data
            or "pyRuleSetName" in data
        )
        if not is_manifest:
            # Try array of rules at top level
            if isinstance(data, list) and data and isinstance(data[0], dict):
                if "pyRuleName" in data[0]:
                    is_manifest = True

        if not is_manifest:
            continue

        version = _extract_version_from_manifest(data, fpath)
        candidates.append((fpath, version))

    return candidates


def _extract_version_from_manifest(data: dict, fpath: Path) -> str:
    """
    Extract a sortable version string from manifest content or filename.
    Priority: content field > filename.
    """
    # Try common PEGA version fields
    for key in ("pyRuleSetVersion", "ruleSetVersion", "version", "pyVersion"):
        val = data.get(key, "")
        if val:
            return str(val)

    # Try first entry in pxResults array
    results = data.get("pxResults", data.get("rules", []))
    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, dict):
            for key in ("pyRuleSetVersion", "ruleSetVersion"):
                val = first.get(key, "")
                if val:
                    return str(val)

    # Fall back to version in filename: name-01-02-03.json → "01-02-03"
    m = re.search(r"(\d{2}[.\-]\d{2}[.\-]\d{2})", fpath.stem)
    if m:
        return m.group(1)

    # Use mtime as last resort (higher = newer)
    return f"mtime-{fpath.stat().st_mtime:.0f}"


def _normalise_version(v: str) -> str:
    """Normalise version string: "01.02.03" → "01-02-03"."""
    return str(v).replace(".", "-").strip()


# ─── Validation helpers ───────────────────────────────────────────────────────

_REQUIRED_APP_NAMES = {"COB", "CRDFWApp", "MSFWApp", "PegaRules"}

def _validate_required_apps(raw_hier: list[dict]):
    """Warn (but don't error) if any of the 4 expected app names are missing."""
    found = {str(e.get("name", "")).strip() for e in raw_hier}
    missing = _REQUIRED_APP_NAMES - found
    if missing:
        logger.warning(
            "Expected hierarchy apps not found in config: %s. "
            "Analysis will proceed with the apps that are configured.",
            ", ".join(sorted(missing))
        )


def _build_app_config(entry: dict, config_dir: Path) -> AppConfig:
    name = str(entry.get("name", "")).strip()
    if not name:
        raise ValueError(f"Each hierarchy entry must have a 'name' field. Got: {entry}")

    folder_raw = entry.get("folder", f"./{name}")
    folder = _resolve_path(str(folder_raw), config_dir)

    return AppConfig(
        name                = name,
        tier                = int(entry.get("tier", 99)),
        folder              = folder,
        manifest_version    = str(entry.get("manifest_version", "latest")).strip(),
        include_in_analysis = bool(entry.get("include_in_analysis", True)),
    )


def _resolve_path(raw: str, base: Path) -> Path:
    """Resolve a path relative to the config file's directory."""
    p = Path(raw)
    return (base / p).resolve() if not p.is_absolute() else p.resolve()


def _warn_missing_manifests(cfg: AnalysisConfig):
    for app in cfg.hierarchy:
        if app.resolved_manifest is None:
            logger.warning(
                "[%s] No manifest resolved — rules from this app will be SKIPPED. "
                "Check that the folder path is correct and contains manifest JSON files.",
                app.name
            )
