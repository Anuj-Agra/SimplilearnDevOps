"""
pega_re — Pega Reverse Engineering toolkit.

Intelligent agent system for analyzing Pega applications from JAR/manifest exports.
Natural language interface automatically selects appropriate agents and generates
executive-ready documentation.

Quick Start:
    from pega_re import PegaAnalyzer
    
    analyzer = PegaAnalyzer()
    result = analyzer.analyze_from_text(
        "analyze my pega application",
        input_dir="/path/to/extracted_jars"
    )

Agent System:
    from pega_re.agents import PegaREAgentSuite
    
    suite = PegaREAgentSuite()
    results = suite.execute_full_pipeline(
        input_dir="/path/to/jars", 
        workdir="./output",
        app_name="My App"
    )

Command Line:
    from pega_re.auto_dispatcher import main
    main()  # Or use: python -m pega_re.auto_dispatcher

Individual Modules:
    from pega_re import extractor, parser, hierarchy, flow, tasks, ui, docgen
"""

__version__ = "1.0.0"
__author__ = "Claude (Anthropic)"

# Main entry points for importing into existing projects
from .auto_dispatcher import PegaAnalyzer, QueryAnalyzer, AnalysisIntent, AnalysisRequest, AnalysisResult
from .agents import (
    PegaREAgentSuite, 
    PegaExtractorAgent,
    PegaRuleParserAgent, 
    PegaHierarchyMapperAgent,
    PegaFlowAnalyzerAgent,
    PegaTaskExtractorAgent,
    PegaUIRendererAgent,
    PegaDocSynthesizerAgent,
    SkillExecution
)

# Deterministic modules for advanced usage
from . import extractor, parser, hierarchy, flow, tasks, ui, docgen

# Optional graph orchestration (requires langgraph)
try:
    from .graph import run_full_pipeline, build_graph, PegaREResult
    _HAS_LANGGRAPH = True
except ImportError:
    _HAS_LANGGRAPH = False
    run_full_pipeline = None
    build_graph = None
    PegaREResult = None

__all__ = [
    # Main classes for integration
    "PegaAnalyzer",
    "PegaREAgentSuite", 
    "QueryAnalyzer",
    
    # Individual agents
    "PegaExtractorAgent",
    "PegaRuleParserAgent", 
    "PegaHierarchyMapperAgent",
    "PegaFlowAnalyzerAgent",
    "PegaTaskExtractorAgent", 
    "PegaUIRendererAgent",
    "PegaDocSynthesizerAgent",
    
    # Data classes
    "AnalysisRequest",
    "AnalysisResult", 
    "AnalysisIntent",
    "SkillExecution",
    
    # Deterministic modules
    "extractor",
    "parser", 
    "hierarchy",
    "flow",
    "tasks",
    "ui", 
    "docgen",
    
    # Optional graph orchestration
    "run_full_pipeline",
    "build_graph", 
    "PegaREResult",
]

# Helper function for checking optional dependencies
def has_langgraph() -> bool:
    """Check if LangGraph is available for orchestration."""
    return _HAS_LANGGRAPH

def get_version() -> str:
    """Get the package version."""
    return __version__
