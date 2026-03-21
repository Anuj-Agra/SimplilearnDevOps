# Workspace directories are created at runtime by tools/run.py
# Each workspace contains checkpoint state and LLM outputs for one analysis session
# These are gitignored by default — commit only if you want to share analysis results

# To share analysis results, commit:
#   workspaces/{name}/aggregated/full_flow_narrative.md
#   workspaces/{name}/aggregated/frd_fragments.md
#
# Do NOT commit:
#   workspaces/{name}/rules/*.json      (may contain sensitive rule data)
#   workspaces/{name}/context/*.json    (large debug files)
#   workspaces/{name}/session_log.jsonl (may contain LLM inputs with rule data)
