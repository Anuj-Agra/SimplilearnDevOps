"""
graph.py — LangGraph orchestration of the seven PegaRE agents.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.sqlite import SqliteSaver
    _HAS_LANGGRAPH = True
except ImportError:
    _HAS_LANGGRAPH = False

from . import extractor, parser, hierarchy, flow, tasks, ui, docgen


class PegaREState(TypedDict):
    """State object that flows through the graph."""
    input_dir: str
    workdir: str
    app_name: str
    catalog_path: str
    unpacked_dir: str
    progress: dict[str, str]  # agent_name → "pending" | "running" | "done" | "failed"
    outputs: dict[str, Any]  # agent_name → result object
    warnings: list[str]
    llm_enabled: bool


@dataclass
class PegaREResult:
    success: bool
    state: PegaREState
    program_doc_html: str | None
    task_ledger_html: str | None
    ui_index_html: str | None
    hierarchy_html: str | None


def build_graph(llm_agent=None, checkpoints_enabled=True):
    """
    Build the LangGraph workflow.
    
    Args:
        llm_agent: Optional LLM agent for generating natural-language summaries.
                   If None, deterministic templates are used.
        checkpoints_enabled: If True, enables SQLite checkpointing for resumability.
    """
    if not _HAS_LANGGRAPH:
        raise ImportError("langgraph is required. pip install langgraph")
    
    graph = StateGraph(PegaREState)
    
    # Add all agent nodes
    graph.add_node("extractor", _extractor_node)
    graph.add_node("parser", _parser_node)
    graph.add_node("hierarchy", _hierarchy_node)
    graph.add_node("flow", _flow_node)
    graph.add_node("ui", _ui_node)
    graph.add_node("tasks", _tasks_node)
    graph.add_node("doc_synthesizer", lambda state: _doc_synthesizer_node(state, llm_agent))
    
    # Define the workflow edges
    graph.set_entry_point("extractor")
    graph.add_edge("extractor", "parser")
    
    # Fan-out after parsing
    graph.add_edge("parser", "hierarchy")
    graph.add_edge("parser", "flow")
    graph.add_edge("parser", "ui")
    
    # Tasks depends on flow results
    graph.add_edge("flow", "tasks")
    
    # Fan-in: doc synthesizer waits for hierarchy, tasks, and ui
    graph.add_conditional_edges(
        "hierarchy",
        _check_all_specialists_done,
        {"continue": "doc_synthesizer", "wait": END}
    )
    graph.add_conditional_edges(
        "tasks", 
        _check_all_specialists_done,
        {"continue": "doc_synthesizer", "wait": END}
    )
    graph.add_conditional_edges(
        "ui",
        _check_all_specialists_done,
        {"continue": "doc_synthesizer", "wait": END}
    )
    
    graph.add_edge("doc_synthesizer", END)
    
    # Compile with optional checkpointing
    if checkpoints_enabled:
        memory = SqliteSaver.from_conn_string(":memory:")
        return graph.compile(checkpointer=memory)
    else:
        return graph.compile()


def run_full_pipeline(input_dir: str | Path, workdir: str | Path, app_name: str,
                      llm_agent=None, resume_from_checkpoint=None) -> PegaREResult:
    """
    Run the complete PegaRE pipeline.
    
    Args:
        input_dir: Directory containing extracted JAR files
        workdir: Working directory for outputs
        app_name: Application name for documentation
        llm_agent: Optional LLM agent for summaries
        resume_from_checkpoint: Optional checkpoint thread ID to resume from
    
    Returns:
        PegaREResult with success status and output paths
    """
    input_dir = Path(input_dir)
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    
    initial_state = PegaREState(
        input_dir=str(input_dir),
        workdir=str(workdir),
        app_name=app_name,
        catalog_path=str(workdir / "catalog.sqlite"),
        unpacked_dir=str(workdir / "unpacked"),
        progress={
            "extractor": "pending", "parser": "pending", "hierarchy": "pending",
            "flow": "pending", "ui": "pending", "tasks": "pending", "doc_synthesizer": "pending"
        },
        outputs={},
        warnings=[],
        llm_enabled=llm_agent is not None
    )
    
    graph = build_graph(llm_agent)
    
    try:
        config = {"configurable": {"thread_id": resume_from_checkpoint}} if resume_from_checkpoint else {}
        final_state = graph.invoke(initial_state, config=config)
        
        return PegaREResult(
            success=final_state["progress"].get("doc_synthesizer") == "done",
            state=final_state,
            program_doc_html=str(workdir / "program_doc.html"),
            task_ledger_html=str(workdir / "task_ledger.html"),
            ui_index_html=str(workdir / "ui" / "index.html"),
            hierarchy_html=str(workdir / "hierarchy.html")
        )
    except Exception as e:
        return PegaREResult(
            success=False,
            state=initial_state,
            program_doc_html=None,
            task_ledger_html=None,
            ui_index_html=None,
            hierarchy_html=None
        )


# Agent node implementations
def _extractor_node(state: PegaREState) -> PegaREState:
    state["progress"]["extractor"] = "running"
    try:
        result = extractor.extract_and_catalog(state["input_dir"], state["workdir"])
        state["outputs"]["extractor"] = result
        state["warnings"].extend(result.warnings)
        state["progress"]["extractor"] = "done"
    except Exception as e:
        state["warnings"].append(f"Extractor failed: {e}")
        state["progress"]["extractor"] = "failed"
    return state


def _parser_node(state: PegaREState) -> PegaREState:
    if state["progress"]["extractor"] != "done":
        return state
    
    state["progress"]["parser"] = "running"
    try:
        result = parser.parse_all(state["catalog_path"], state["unpacked_dir"])
        state["outputs"]["parser"] = result
        if result.unknown_types:
            state["warnings"].append(f"Found {len(result.unknown_types)} unknown rule types")
        state["progress"]["parser"] = "done"
    except Exception as e:
        state["warnings"].append(f"Parser failed: {e}")
        state["progress"]["parser"] = "failed"
    return state


def _hierarchy_node(state: PegaREState) -> PegaREState:
    if state["progress"]["parser"] != "done":
        return state
    
    state["progress"]["hierarchy"] = "running"
    try:
        result = hierarchy.build(state["catalog_path"], state["workdir"])
        state["outputs"]["hierarchy"] = result
        state["progress"]["hierarchy"] = "done"
    except Exception as e:
        state["warnings"].append(f"Hierarchy mapper failed: {e}")
        state["progress"]["hierarchy"] = "failed"
    return state


def _flow_node(state: PegaREState) -> PegaREState:
    if state["progress"]["parser"] != "done":
        return state
    
    state["progress"]["flow"] = "running"
    try:
        result = flow.analyse(state["catalog_path"], state["workdir"])
        state["outputs"]["flow"] = result
        if result.broken_refs:
            state["warnings"].extend(result.broken_refs)
        state["progress"]["flow"] = "done"
    except Exception as e:
        state["warnings"].append(f"Flow analyzer failed: {e}")
        state["progress"]["flow"] = "failed"
    return state


def _ui_node(state: PegaREState) -> PegaREState:
    if state["progress"]["parser"] != "done":
        return state
    
    state["progress"]["ui"] = "running"
    try:
        result = ui.render_all(state["catalog_path"], state["workdir"])
        state["outputs"]["ui"] = result
        if result.stub_fidelity > 0:
            state["warnings"].append(f"{result.stub_fidelity} UI rules rendered as stubs")
        state["progress"]["ui"] = "done"
    except Exception as e:
        state["warnings"].append(f"UI renderer failed: {e}")
        state["progress"]["ui"] = "failed"
    return state


def _tasks_node(state: PegaREState) -> PegaREState:
    if state["progress"]["flow"] != "done":
        return state
    
    state["progress"]["tasks"] = "running"
    try:
        result = tasks.extract(state["catalog_path"], state["workdir"])
        state["outputs"]["tasks"] = result
        state["progress"]["tasks"] = "done"
    except Exception as e:
        state["warnings"].append(f"Task extractor failed: {e}")
        state["progress"]["tasks"] = "failed"
    return state


def _doc_synthesizer_node(state: PegaREState, llm_agent) -> PegaREState:
    required = ["hierarchy", "tasks", "ui"]
    if not all(state["progress"][agent] == "done" for agent in required):
        return state
    
    state["progress"]["doc_synthesizer"] = "running"
    try:
        result = docgen.synthesize(
            state["catalog_path"], 
            state["workdir"], 
            state["app_name"],
            llm_agent
        )
        state["outputs"]["doc_synthesizer"] = result
        state["progress"]["doc_synthesizer"] = "done"
    except Exception as e:
        state["warnings"].append(f"Doc synthesizer failed: {e}")
        state["progress"]["doc_synthesizer"] = "failed"
    return state


def _check_all_specialists_done(state: PegaREState) -> str:
    """Check if hierarchy, tasks, and ui are all done to trigger doc synthesis."""
    required = ["hierarchy", "tasks", "ui"]
    if all(state["progress"][agent] == "done" for agent in required):
        return "continue"
    return "wait"


# Simple CLI interface for the graph
def main():
    import argparse
    parser = argparse.ArgumentParser(description="PegaRE — Pega Reverse Engineering")
    parser.add_argument("input_dir", help="Directory with extracted JAR files")
    parser.add_argument("--output", "-o", default="./pegare_output", help="Output directory")
    parser.add_argument("--app-name", default="Pega Application", help="Application name")
    parser.add_argument("--llm", action="store_true", help="Enable LLM summaries (requires API setup)")
    parser.add_argument("--resume", help="Resume from checkpoint thread ID")
    
    args = parser.parse_args()
    
    llm_agent = None
    if args.llm:
        # This would need actual LLM integration - placeholder for now
        print("Warning: LLM integration not implemented in this example")
    
    result = run_full_pipeline(
        args.input_dir,
        args.output,
        args.app_name,
        llm_agent,
        args.resume
    )
    
    if result.success:
        print(f"✅ Pipeline completed successfully!")
        print(f"📋 Program documentation: {result.program_doc_html}")
        print(f"📊 Task ledger: {result.task_ledger_html}")
        print(f"🖼️  UI catalog: {result.ui_index_html}")
        print(f"🌳 Hierarchy: {result.hierarchy_html}")
    else:
        print(f"❌ Pipeline failed. Check logs and warnings.")
        if result.state["warnings"]:
            for w in result.state["warnings"]:
                print(f"⚠️  {w}")


if __name__ == "__main__":
    main()
