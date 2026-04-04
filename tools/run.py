#!/usr/bin/env python3
"""
tools/run.py

Command-line entry point for the PEGA KYC recursive analysis engine.

─── TWO OPERATING MODES ──────────────────────────────────────────────────────

  MODE 1 — Hierarchy mode (for real PEGA exports with BIN + manifest files)
  ─────────────────────────────────────────────────────────────────────────────
  Edit config/analysis_config.yaml to set your 4 folder paths and manifest
  version preferences, then run:

    python tools/run.py analyse --config config/analysis_config.yaml

  Folder structure expected:
    pega-export/
      COB/          ← most specific (client overrides)   [tier 0]
      CRDFWApp/     ← framework application               [tier 1]
      MSFWApp/      ← shared framework                    [tier 2]
      PegaRules/    ← base PEGA rules                     [tier 3]

  Each folder contains:
    - One or more manifest .json files  (which one to use is set in config)
    - Multiple .bin files               (native PEGA rule content)

  Resume after interruption (same command — workspace stored in config):
    python tools/run.py analyse --config config/analysis_config.yaml

  Inspect what was resolved before any LLM calls:
    python tools/run.py validate-config --config config/analysis_config.yaml
    python tools/run.py graph           --config config/analysis_config.yaml


  MODE 2 — Legacy mode (flat directory of exported JSON rule files)
  ─────────────────────────────────────────────────────────────────
    python tools/run.py analyse \\
      --rules-dir ./my-pega-export \\
      --workspace ./workspaces/kyc-cdd-v1 \\
      --root-casetype KYC-Work-CDD \\
      --role ba

    python tools/run.py analyse --workspace ./workspaces/kyc-cdd-v1  # resume


─── OTHER COMMANDS ───────────────────────────────────────────────────────────

  python tools/run.py status    --workspace ./workspaces/kyc-cdd-v1
  python tools/run.py aggregate --workspace ./workspaces/kyc-cdd-v1
  python tools/run.py reset     --workspace ./workspaces/kyc-cdd-v1
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# ─── Logging setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("pega-kyc")


# ─── Repo-relative paths ──────────────────────────────────────────────────────

REPO_ROOT  = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills" / "pega-knowledge"

DEFAULT_SKILLS = [
    SKILLS_DIR / "rule-schemas" / "rule-obj-casetype.md",
    SKILLS_DIR / "rule-schemas" / "rule-obj-flow.md",
    SKILLS_DIR / "rule-schemas" / "rule-obj-activity-flowsection-htmlsection-when.md",
    SKILLS_DIR / "rule-types.md",
    SKILLS_DIR / "json-bin-structure.md",
    SKILLS_DIR / "class-hierarchy.md",
    REPO_ROOT  / "skills" / "kyc-domain" / "regulatory-framework.md",
    REPO_ROOT  / "skills" / "kyc-domain" / "risk-scoring.md",
]

ROLE_ADAPTERS = {
    "ba":  REPO_ROOT / "skills" / "role-adapters" / "business-analyst.md",
    "po":  REPO_ROOT / "skills" / "role-adapters" / "product-owner.md",
    "dev": REPO_ROOT / "skills" / "role-adapters" / "pega-developer.md",
    "qa":  REPO_ROOT / "skills" / "role-adapters" / "qa-tester.md",
}


# ─── Config helpers ───────────────────────────────────────────────────────────

def _load_cfg(config_path: str):
    """Load an AnalysisConfig from a YAML file."""
    sys.path.insert(0, str(Path(__file__).parent))
    from config.config_loader import load_config
    cfg = load_config(Path(config_path))
    logger.info(
        "Config loaded — %d apps | root=%s | workspace=%s",
        len(cfg.hierarchy), cfg.root_casetype or "(not set)", cfg.workspace,
    )
    return cfg


def _workspace(args, cfg=None) -> Path:
    """Resolve workspace: CLI flag > config > error."""
    if getattr(args, "workspace", None):
        return Path(args.workspace)
    if cfg is not None:
        return cfg.workspace
    print("ERROR: provide --workspace or use --config.", file=sys.stderr)
    sys.exit(1)


def _role(args, cfg=None) -> str:
    """Resolve role: CLI flag > config > default ba."""
    r = getattr(args, "role", None)
    if r:
        return r
    if cfg is not None:
        return cfg.role
    return "ba"


# ─── analyse command ──────────────────────────────────────────────────────────

def cmd_analyse(args):
    from runner.recursive_analyser import RecursiveAnalyser

    cfg       = _load_cfg(args.config) if getattr(args, "config", None) else None
    workspace = _workspace(args, cfg)
    role      = _role(args, cfg)
    overwrite = getattr(args, "reset", False)

    if cfg is not None:
        # ── Hierarchy mode ────────────────────────────────────────────────────
        # CLI --max-rules overrides config only when explicitly changed from default
        max_rules = args.max_rules if args.max_rules != 50 else cfg.max_rules_per_session
        analyser  = RecursiveAnalyser(
            analysis_config   = cfg,
            skill_files       = DEFAULT_SKILLS,
            role_adapter_path = ROLE_ADAPTERS.get(role),
            dry_run           = args.dry_run,
        )
    else:
        # ── Legacy mode ───────────────────────────────────────────────────────
        max_rules = args.max_rules
        rules_dir = Path(args.rules_dir) if getattr(args, "rules_dir", None) else None
        if not rules_dir:
            gp = workspace / "rule_graph.json"
            if not gp.exists():
                print(
                    "ERROR: --rules-dir is required for the first run "
                    "when not using --config.",
                    file=sys.stderr,
                )
                sys.exit(1)
            rules_dir = workspace
        analyser  = RecursiveAnalyser(
            workspace         = workspace,
            rules_dir         = rules_dir,
            root_casetype     = getattr(args, "root_casetype", None),
            max_rules_per_session = max_rules,
            skill_files       = DEFAULT_SKILLS,
            role_adapter_path = ROLE_ADAPTERS.get(role),
            dry_run           = args.dry_run,
        )

    graph_path = workspace / "rule_graph.json"
    if graph_path.exists() and not overwrite:
        logger.info("Existing graph found — loading (use --reset to rebuild)")
    else:
        logger.info("Phase 1: Building rule graph...")
        analyser.phase1_build_graph(overwrite=overwrite)

    logger.info("Phase 2: Recursive LLM analysis (max %d rules this session)...", max_rules)
    report = analyser.phase2_analyse(max_rules=max_rules)

    pending = report.get("pending", 0)
    if pending == 0:
        logger.info("Phase 3: Aggregating outputs...")
        analyser.phase3_aggregate()
        print("\n✓ Analysis complete. Outputs saved to:", workspace / "aggregated")
    else:
        print(f"\n⏸  Session complete. {pending} rules remaining.")
        print("   Re-run the same command to continue from where you left off.")

    print(json.dumps(report, indent=2))


# ─── graph command ────────────────────────────────────────────────────────────

def cmd_graph(args):
    from runner.recursive_analyser import RecursiveAnalyser

    cfg       = _load_cfg(args.config) if getattr(args, "config", None) else None
    workspace = _workspace(args, cfg)

    if cfg is not None:
        analyser = RecursiveAnalyser(analysis_config=cfg, dry_run=True)
    else:
        analyser = RecursiveAnalyser(
            workspace     = workspace,
            rules_dir     = Path(args.rules_dir),
            root_casetype = getattr(args, "root_casetype", None),
            dry_run       = True,
        )

    graph = analyser.phase1_build_graph(overwrite=getattr(args, "reset", False))
    stats = graph.stats()

    print("\n=== Rule Graph Statistics ===")
    print(json.dumps(stats, indent=2))

    queue = graph.analysis_queue()
    print(f"\n=== Analysis Queue ({len(queue)} rules will be analysed) ===")
    for i, node in enumerate(queue[:40], 1):
        app_tag = f"[{node.app_name}]" if node.app_name else ""
        print(
            f"  {i:>3}. [{node.rule_type:<25}]  {node.rule_name:<45}"
            f" depth={node.depth}  {app_tag}"
        )
    if len(queue) > 40:
        print(f"  ... and {len(queue) - 40} more")

    # Context-only count (hierarchy mode only)
    ctx_only = [n for n in graph if not n.include_in_analysis and n.parsed]
    if ctx_only:
        print(f"\n  Context-only nodes (not queued for LLM): {len(ctx_only)}")

    # Missing references
    missing = graph.missing_references()
    if missing:
        print(f"\n=== Unresolved References ({len(missing)}) ===")
        for src, ref in missing[:20]:
            print(f"  {src}  →  {ref.rule_name}  ({ref.rule_type})")


# ─── status command ───────────────────────────────────────────────────────────

def cmd_status(args):
    from checkpoint.checkpoint_manager import CheckpointManager

    workspace = _workspace(args)
    cp = CheckpointManager(workspace)
    cp.load()
    cp.print_progress()
    print(json.dumps(cp.progress_report(), indent=2))


# ─── aggregate command ────────────────────────────────────────────────────────

def cmd_aggregate(args):
    from runner.recursive_analyser import RecursiveAnalyser

    workspace = _workspace(args)
    analyser  = RecursiveAnalyser(workspace=workspace, rules_dir=workspace, dry_run=True)
    analyser.checkpoint.load()
    outputs = analyser.phase3_aggregate()
    print("\n✓ Aggregated outputs:")
    for k, v in outputs.items():
        print(f"   {k}: {v}")


# ─── reset command ────────────────────────────────────────────────────────────

def cmd_reset(args):
    import shutil
    workspace = _workspace(args)

    to_delete = [
        workspace / "manifest.json",
        workspace / "queue.json",
        workspace / "rule_graph.json",
        workspace / "session_log.jsonl",
    ]
    to_clean = [
        workspace / "analysis",
        workspace / "context",
        workspace / "aggregated",
    ]

    confirm = input(
        f"Reset workspace '{workspace}'?\n"
        "This deletes all analysis outputs. BIN and rule files are preserved. [y/N] "
    )
    if confirm.strip().lower() != "y":
        print("Cancelled.")
        return

    for f in to_delete:
        if f.exists():
            f.unlink()
            print(f"  Deleted {f.name}")

    for d in to_clean:
        if d.exists():
            shutil.rmtree(d)
            print(f"  Deleted {d.name}/")

    print("✓ Workspace reset.")


# ─── validate-config command ──────────────────────────────────────────────────

def cmd_validate_config(args):
    """
    Load the config, resolve all paths and manifests, and print a full
    diagnostic without touching the workspace or running any analysis.
    """
    cfg = _load_cfg(args.config)

    print("\n" + "=" * 68)
    print("  Config validation report")
    print("=" * 68)
    print(f"  Config file    : {Path(args.config).resolve()}")
    print(f"  Workspace      : {cfg.workspace}")
    print(f"  Root CaseType  : {cfg.root_casetype or '(not set — all CaseTypes loaded)'}")
    print(f"  Role           : {cfg.role}")
    print(f"  Model          : {cfg.model}")
    print(f"  Max rules/sess : {cfg.max_rules_per_session}")
    print(f"  Token budget   : {cfg.token_budget_per_rule}")

    print("\n  Application hierarchy:")
    print(f"  {'Tier':<6} {'Name':<14} {'Folder':<8} {'BINs':>5} {'Manifests':>9}  {'Selected manifest':<30}  {'Analyse?'}")
    print("  " + "-" * 96)

    all_ok = True
    for app in cfg.hierarchy:
        folder_exists = app.folder.exists()
        bin_count     = len(list(app.folder.glob("**/*.bin"))) if folder_exists else 0
        json_count    = len(list(app.folder.glob("*.json")))   if folder_exists else 0
        manifest_name = app.resolved_manifest.name if app.resolved_manifest else "✗ NOT FOUND"
        folder_flag   = "✓" if folder_exists else "✗"

        if not folder_exists or not app.resolved_manifest:
            all_ok = False

        print(
            f"  [{app.tier}]    {app.name:<14} {folder_flag:<8} {bin_count:>5} {json_count:>9}"
            f"  {manifest_name:<30}  {app.include_in_analysis}"
        )

    print()
    if all_ok:
        print("  ✓ All folders and manifests resolved — ready to run")
    else:
        print("  ✗ One or more issues found — fix paths in config before analysing")

    print("\n  Rule type filter:")
    for rt, enabled in sorted(cfg.rule_type_filter.items()):
        print(f"    {'✓' if enabled else '✗'}  {rt}")

    print("\n  BIN extraction:")
    print(f"    Enabled            : {cfg.bin_extraction.enabled}")
    print(f"    Min string length  : {cfg.bin_extraction.min_string_length}")
    print(f"    Reference patterns : {len(cfg.bin_extraction.reference_patterns)} patterns")
    print("=" * 68)


# ─── CLI wiring ───────────────────────────────────────────────────────────────

def _add_config_or_rules_dir(p):
    """Add --config / --rules-dir as mutually exclusive options."""
    group = p.add_mutually_exclusive_group()
    group.add_argument(
        "--config", default=None,
        metavar="FILE",
        help="Path to analysis_config.yaml (hierarchy mode: COB/CRDFWApp/MSFWApp/PegaRules)",
    )
    group.add_argument(
        "--rules-dir", default=None,
        metavar="DIR",
        help="Path to flat directory of JSON rule files (legacy mode)",
    )
    p.add_argument(
        "--workspace", default=None,
        metavar="DIR",
        help="Workspace directory (overrides config file value)",
    )
    p.add_argument(
        "--root-casetype", default=None,
        help="Root CaseType pyRuleName (overrides config file value)",
    )


def main():
    parser = argparse.ArgumentParser(
        description="PEGA KYC Recursive Analyser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── analyse ───────────────────────────────────────────────────────────────
    p_an = sub.add_parser("analyse", help="Run recursive analysis (or resume)")
    _add_config_or_rules_dir(p_an)
    p_an.add_argument("--role",      default=None, choices=["ba","po","dev","qa"],
                      help="Output audience: ba (default), po, dev, qa")
    p_an.add_argument("--max-rules", type=int, default=50,
                      help="Max rules per session (default 50)")
    p_an.add_argument("--reset",     action="store_true",
                      help="Rebuild graph and restart from scratch")
    p_an.add_argument("--dry-run",   action="store_true",
                      help="Build graph only — no LLM calls")
    p_an.set_defaults(func=cmd_analyse)

    # ── graph ─────────────────────────────────────────────────────────────────
    p_gr = sub.add_parser("graph", help="Phase 1 only — build graph, print stats (no LLM)")
    _add_config_or_rules_dir(p_gr)
    p_gr.add_argument("--reset", action="store_true")
    p_gr.set_defaults(func=cmd_graph)

    # ── status ────────────────────────────────────────────────────────────────
    p_st = sub.add_parser("status", help="Show progress of an existing workspace")
    p_st.add_argument("--workspace", required=True)
    p_st.set_defaults(func=cmd_status)

    # ── aggregate ─────────────────────────────────────────────────────────────
    p_ag = sub.add_parser("aggregate", help="Concatenate all outputs into documents")
    p_ag.add_argument("--workspace", required=True)
    p_ag.set_defaults(func=cmd_aggregate)

    # ── reset ─────────────────────────────────────────────────────────────────
    p_re = sub.add_parser("reset", help="Reset workspace (keeps BIN/rule files)")
    p_re.add_argument("--workspace", required=True)
    p_re.set_defaults(func=cmd_reset)

    # ── validate-config ───────────────────────────────────────────────────────
    p_vc = sub.add_parser(
        "validate-config",
        help="Validate config file and show resolved paths — no analysis performed",
    )
    p_vc.add_argument("--config", required=True, metavar="FILE",
                      help="Path to analysis_config.yaml")
    p_vc.set_defaults(func=cmd_validate_config)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    main()
