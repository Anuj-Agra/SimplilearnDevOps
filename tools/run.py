#!/usr/bin/env python3
"""
tools/run.py

Command-line entry point for the PEGA KYC recursive analysis engine.

Usage examples:
  # Run full pipeline from scratch
  python tools/run.py analyse \
    --rules-dir ./my-pega-export/rules \
    --workspace ./workspaces/kyc-cdd-v1 \
    --root-casetype KYC-Work-CDD \
    --role ba

  # Resume a previous session (picks up where it left off)
  python tools/run.py analyse \
    --workspace ./workspaces/kyc-cdd-v1

  # Phase 1 only (build graph, no LLM calls) — useful for inspection
  python tools/run.py graph \
    --rules-dir ./my-pega-export/rules \
    --workspace ./workspaces/kyc-cdd-v1

  # Show progress of an existing workspace
  python tools/run.py status \
    --workspace ./workspaces/kyc-cdd-v1

  # Aggregate outputs from a completed (or partial) workspace
  python tools/run.py aggregate \
    --workspace ./workspaces/kyc-cdd-v1

  # Dry run (parse + build graph, no LLM calls, saves placeholder outputs)
  python tools/run.py analyse \
    --rules-dir ./my-pega-export/rules \
    --workspace ./workspaces/kyc-cdd-v1 \
    --dry-run

  # Reset a workspace and start over
  python tools/run.py reset \
    --workspace ./workspaces/kyc-cdd-v1
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("pega-kyc")


# ─── Path helpers ─────────────────────────────────────────────────────────────

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


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_analyse(args):
    """Run full recursive analysis (or resume)."""
    from runner.recursive_analyser import RecursiveAnalyser

    workspace = Path(args.workspace)

    # If rules_dir not specified, check if graph already exists in workspace
    rules_dir = Path(args.rules_dir) if args.rules_dir else None
    if not rules_dir:
        graph_path = workspace / "rule_graph.json"
        if not graph_path.exists():
            print("ERROR: --rules-dir is required when no existing graph is found in workspace.")
            sys.exit(1)
        rules_dir = workspace   # graph will be loaded, not rebuilt

    analyser = RecursiveAnalyser(
        workspace=workspace,
        rules_dir=rules_dir or workspace,
        root_casetype=args.root_casetype,
        model=args.model,
        max_rules_per_session=args.max_rules,
        token_budget_per_rule=args.token_budget,
        skill_files=DEFAULT_SKILLS,
        role_adapter_path=ROLE_ADAPTERS.get(args.role),
        dry_run=args.dry_run,
    )

    overwrite = args.reset

    if rules_dir and (workspace / "rule_graph.json").exists() and not overwrite:
        logger.info("Existing graph found — skipping Phase 1 (use --reset to rebuild)")
    elif rules_dir:
        logger.info("Phase 1: Building rule graph...")
        analyser.phase1_build_graph(overwrite=overwrite)

    logger.info("Phase 2: Recursive analysis...")
    report = analyser.phase2_analyse(max_rules=args.max_rules)

    if report.get("pending", 0) == 0:
        logger.info("Phase 3: Aggregating outputs...")
        analyser.phase3_aggregate()
        print("\n✓ Analysis complete. All outputs saved to:", workspace / "aggregated")
    else:
        remaining = report.get("pending", 0)
        print(f"\n⏸  Session complete. {remaining} rules remaining.")
        print(f"   Re-run the same command to continue from where you left off.")

    print(json.dumps(report, indent=2))


def cmd_graph(args):
    """Phase 1 only: build rule graph and print stats."""
    from runner.recursive_analyser import RecursiveAnalyser

    analyser = RecursiveAnalyser(
        workspace=Path(args.workspace),
        rules_dir=Path(args.rules_dir),
        root_casetype=args.root_casetype,
        dry_run=True,
    )
    graph = analyser.phase1_build_graph(overwrite=getattr(args, "reset", False))
    stats = graph.stats()

    print("\n=== Rule Graph Statistics ===")
    print(json.dumps(stats, indent=2))

    # Print analysis queue order
    queue = graph.analysis_queue()
    print(f"\n=== Analysis Queue ({len(queue)} rules) ===")
    for i, node in enumerate(queue[:30], 1):
        print(f"  {i:>3}. [{node.rule_type:<25}] {node.rule_name}  (depth={node.depth}, priority={node.priority})")
    if len(queue) > 30:
        print(f"  ... and {len(queue) - 30} more rules")

    missing = graph.missing_references()
    if missing:
        print(f"\n=== Missing References ({len(missing)}) ===")
        for src, ref in missing[:20]:
            print(f"  {src} → {ref.rule_name} ({ref.rule_type})")


def cmd_status(args):
    """Show progress of an existing workspace."""
    from checkpoint.checkpoint_manager import CheckpointManager

    cp = CheckpointManager(Path(args.workspace))
    cp.load()
    cp.print_progress()
    report = cp.progress_report()
    print(json.dumps(report, indent=2))


def cmd_aggregate(args):
    """Aggregate all available analysis outputs into documents."""
    from runner.recursive_analyser import RecursiveAnalyser

    analyser = RecursiveAnalyser(
        workspace=Path(args.workspace),
        rules_dir=Path(args.workspace),   # not used for aggregation
        dry_run=True,
    )
    analyser.checkpoint.load()
    outputs = analyser.phase3_aggregate()
    print("\n✓ Aggregated outputs:")
    for k, v in outputs.items():
        print(f"   {k}: {v}")


def cmd_reset(args):
    """Reset a workspace (delete manifest + queue, keep rule files)."""
    import shutil
    workspace = Path(args.workspace)

    files_to_delete = [
        workspace / "manifest.json",
        workspace / "queue.json",
        workspace / "rule_graph.json",
        workspace / "session_log.jsonl",
    ]
    dirs_to_clean = [
        workspace / "analysis",
        workspace / "context",
        workspace / "aggregated",
    ]

    confirm = input(f"Reset workspace '{workspace}'? This deletes all analysis outputs. [y/N] ")
    if confirm.lower() != "y":
        print("Cancelled.")
        return

    for f in files_to_delete:
        if f.exists():
            f.unlink()
            print(f"  Deleted {f.name}")

    for d in dirs_to_clean:
        if d.exists():
            shutil.rmtree(d)
            print(f"  Deleted {d.name}/")

    print("✓ Workspace reset. Rules directory preserved.")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PEGA KYC Recursive Analyser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── analyse ──
    p_analyse = sub.add_parser("analyse", help="Run full recursive analysis (or resume)")
    p_analyse.add_argument("--workspace",      required=True,  help="Path to workspace directory")
    p_analyse.add_argument("--rules-dir",      default=None,   help="Path to directory containing rule JSON files")
    p_analyse.add_argument("--root-casetype",  default=None,   help="Name of the root Rule-Obj-CaseType rule")
    p_analyse.add_argument("--role",           default="ba",   choices=["ba","po","dev","qa"],
                           help="Output audience (default: ba)")
    p_analyse.add_argument("--model",          default="claude-sonnet-4-20250514")
    p_analyse.add_argument("--max-rules",      type=int, default=50,
                           help="Max rules to process per session (default: 50)")
    p_analyse.add_argument("--token-budget",   type=int, default=6000,
                           help="Token budget per rule context (default: 6000)")
    p_analyse.add_argument("--reset",          action="store_true",
                           help="Rebuild graph and restart analysis from scratch")
    p_analyse.add_argument("--dry-run",        action="store_true",
                           help="Build graph only, no LLM calls")
    p_analyse.set_defaults(func=cmd_analyse)

    # ── graph ──
    p_graph = sub.add_parser("graph", help="Phase 1 only: build rule graph and print stats")
    p_graph.add_argument("--workspace",     required=True)
    p_graph.add_argument("--rules-dir",     required=True)
    p_graph.add_argument("--root-casetype", default=None)
    p_graph.add_argument("--reset",         action="store_true")
    p_graph.set_defaults(func=cmd_graph)

    # ── status ──
    p_status = sub.add_parser("status", help="Show progress of an existing workspace")
    p_status.add_argument("--workspace", required=True)
    p_status.set_defaults(func=cmd_status)

    # ── aggregate ──
    p_agg = sub.add_parser("aggregate", help="Aggregate outputs from a workspace")
    p_agg.add_argument("--workspace", required=True)
    p_agg.set_defaults(func=cmd_aggregate)

    # ── reset ──
    p_reset = sub.add_parser("reset", help="Reset a workspace (keeps rule files)")
    p_reset.add_argument("--workspace", required=True)
    p_reset.set_defaults(func=cmd_reset)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    # Make tools/ importable when run from repo root
    sys.path.insert(0, str(Path(__file__).parent))
    main()
