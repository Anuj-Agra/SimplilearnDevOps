"""
auto_dispatcher.py — Intelligent agent dispatcher that automatically selects agents based on natural language queries.

This module provides a natural language interface to PegaRE. Users can describe what they want
in plain English, and the system automatically determines which agents to run.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

from .agents import PegaREAgentSuite
from .graph import run_full_pipeline as run_langgraph_pipeline


class AnalysisIntent(Enum):
    """Different types of analysis the user might want."""
    FULL_ANALYSIS = "full"
    TASK_EXTRACTION = "tasks"
    UI_ANALYSIS = "ui" 
    HIERARCHY_ANALYSIS = "hierarchy"
    FLOW_ANALYSIS = "flows"
    EXECUTIVE_SUMMARY = "executive"
    VALIDATION = "validation"
    COPILOT_WORKFLOW = "copilot"
    RESUME_ANALYSIS = "resume"
    TROUBLESHOOTING = "troubleshoot"


@dataclass
class AnalysisRequest:
    """Parsed user request with detected intent and parameters."""
    intent: AnalysisIntent
    confidence: float
    agents_needed: List[str]
    output_focus: List[str]
    estimated_time: str
    user_query: str
    detected_keywords: Set[str]


@dataclass
class AnalysisResult:
    """Result of running the analysis."""
    success: bool
    outputs_generated: List[str]
    primary_deliverable: Optional[str]
    executive_summary_path: Optional[str]
    task_ledger_path: Optional[str]
    ui_catalog_path: Optional[str]
    errors: List[str]
    warnings: List[str]
    execution_time: str
    metrics_summary: dict


class QueryAnalyzer:
    """Analyzes natural language queries to determine analysis intent."""
    
    # Keyword patterns for different analysis types
    INTENT_PATTERNS = {
        AnalysisIntent.FULL_ANALYSIS: {
            "keywords": ["analyze", "analysis", "complete", "full", "everything", "entire", "comprehensive", "all"],
            "phrases": ["full analysis", "complete analysis", "analyze everything", "entire application"],
            "agents": ["extractor", "parser", "hierarchy", "flow", "tasks", "ui", "doc_synthesizer"],
            "time_estimate": "30-60 minutes for 100K+ rules"
        },
        AnalysisIntent.TASK_EXTRACTION: {
            "keywords": ["task", "tasks", "assignment", "assignments", "workflow", "workflows", "sla", "routing", "workbasket"],
            "phrases": ["extract tasks", "show tasks", "task generation", "assignment routing", "workflow analysis"],
            "agents": ["extractor", "parser", "flow", "tasks"],
            "time_estimate": "15-30 minutes"
        },
        AnalysisIntent.UI_ANALYSIS: {
            "keywords": ["ui", "interface", "screen", "screens", "form", "forms", "harness", "section", "portal", "page"],
            "phrases": ["ui analysis", "show screens", "user interface", "forms analysis"],
            "agents": ["extractor", "parser", "ui"],
            "time_estimate": "10-20 minutes"
        },
        AnalysisIntent.HIERARCHY_ANALYSIS: {
            "keywords": ["hierarchy", "class", "classes", "inheritance", "dependencies", "structure", "organization", "ruleset"],
            "phrases": ["class hierarchy", "show structure", "dependencies analysis", "ruleset organization"],
            "agents": ["extractor", "parser", "hierarchy"],
            "time_estimate": "5-15 minutes"
        },
        AnalysisIntent.FLOW_ANALYSIS: {
            "keywords": ["flow", "flows", "process", "processes", "case", "cases", "stage", "stages", "step", "steps"],
            "phrases": ["process flow", "case types", "business process", "flow analysis"],
            "agents": ["extractor", "parser", "flow"],
            "time_estimate": "10-25 minutes"
        },
        AnalysisIntent.EXECUTIVE_SUMMARY: {
            "keywords": ["executive", "summary", "report", "overview", "management", "steering", "committee", "presentation"],
            "phrases": ["executive summary", "management report", "steering committee", "high level"],
            "agents": ["extractor", "parser", "hierarchy", "flow", "tasks", "ui", "doc_synthesizer"],
            "time_estimate": "30-45 minutes (full pipeline for summary)"
        },
        AnalysisIntent.VALIDATION: {
            "keywords": ["validate", "check", "verify", "test", "scan", "diagnose", "inspect"],
            "phrases": ["validate input", "check files", "diagnose issues", "scan for problems"],
            "agents": ["extractor"],
            "time_estimate": "2-5 minutes"
        },
        AnalysisIntent.COPILOT_WORKFLOW: {
            "keywords": ["copilot", "github", "prompts", "workflow", "step", "manual", "guided"],
            "phrases": ["copilot workflow", "github copilot", "generate prompts", "step by step"],
            "agents": [],  # Special case - generates prompts instead of running agents
            "time_estimate": "Instant (generates prompts)"
        },
        AnalysisIntent.RESUME_ANALYSIS: {
            "keywords": ["resume", "continue", "checkpoint", "restart", "recover"],
            "phrases": ["resume analysis", "continue from checkpoint", "pick up where left off"],
            "agents": [],  # Determined by checkpoint state
            "time_estimate": "Varies (depends on checkpoint)"
        },
        AnalysisIntent.TROUBLESHOOTING: {
            "keywords": ["troubleshoot", "debug", "error", "problem", "issue", "fix", "help"],
            "phrases": ["troubleshoot issues", "debug problems", "what's wrong", "fix errors"],
            "agents": ["extractor", "parser"],  # Basic validation
            "time_estimate": "5-10 minutes"
        }
    }
    
    def analyze_query(self, query: str) -> AnalysisRequest:
        """Analyze a natural language query and determine intent."""
        query_lower = query.lower()
        detected_keywords = set()
        intent_scores = {}
        
        # Score each intent based on keyword and phrase matches
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            matched_keywords = set()
            
            # Check keyword matches
            for keyword in patterns["keywords"]:
                if keyword in query_lower:
                    score += 1
                    matched_keywords.add(keyword)
            
            # Check phrase matches (higher weight)
            for phrase in patterns["phrases"]:
                if phrase in query_lower:
                    score += 3
                    matched_keywords.update(phrase.split())
            
            if score > 0:
                intent_scores[intent] = score
                detected_keywords.update(matched_keywords)
        
        # Determine the highest scoring intent
        if not intent_scores:
            # Default to full analysis if no keywords matched
            best_intent = AnalysisIntent.FULL_ANALYSIS
            confidence = 0.3
        else:
            best_intent = max(intent_scores, key=intent_scores.get)
            max_score = intent_scores[best_intent]
            confidence = min(max_score / 5.0, 1.0)  # Normalize to 0-1 range
        
        patterns = self.INTENT_PATTERNS[best_intent]
        
        return AnalysisRequest(
            intent=best_intent,
            confidence=confidence,
            agents_needed=patterns["agents"],
            output_focus=self._determine_output_focus(best_intent, query_lower),
            estimated_time=patterns["time_estimate"],
            user_query=query,
            detected_keywords=detected_keywords
        )
    
    def _determine_output_focus(self, intent: AnalysisIntent, query: str) -> List[str]:
        """Determine what outputs the user is most interested in."""
        focus = []
        
        if "csv" in query or "excel" in query or "spreadsheet" in query:
            focus.append("csv_export")
        if "html" in query or "browser" in query or "web" in query:
            focus.append("html_catalog")
        if "json" in query or "api" in query or "data" in query:
            focus.append("json_export")
        if "executive" in query or "management" in query or "summary" in query:
            focus.append("executive_summary")
        if "detailed" in query or "comprehensive" in query or "full" in query:
            focus.append("detailed_documentation")
        
        # Default focus based on intent
        if not focus:
            if intent == AnalysisIntent.TASK_EXTRACTION:
                focus = ["task_ledger", "csv_export"]
            elif intent == AnalysisIntent.UI_ANALYSIS:
                focus = ["ui_catalog", "html_catalog"]
            elif intent == AnalysisIntent.EXECUTIVE_SUMMARY:
                focus = ["executive_summary", "program_documentation"]
            else:
                focus = ["program_documentation"]
        
        return focus


class PegaAnalyzer:
    """Main analyzer class that coordinates the entire process."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.query_analyzer = QueryAnalyzer()
        self.agent_suite = PegaREAgentSuite(project_root)
        self.project_root = project_root or Path(__file__).parent.parent
    
    def analyze_from_text(self, query: str, input_dir: str, output_dir: str = "./pegare_output",
                         app_name: str = "Pega Application", method: str = "simple",
                         resume_checkpoint: Optional[str] = None, verbose: bool = False) -> AnalysisResult:
        """
        Main entry point - analyze a Pega application based on natural language query.
        """
        # Parse the user's intent
        request = self.query_analyzer.analyze_query(query)
        
        if verbose:
            print(f"🎯 Detected intent: {request.intent.value}")
            print(f"📊 Confidence: {request.confidence:.1%}")
            print(f"🔍 Keywords found: {', '.join(request.detected_keywords)}")
            print(f"⏱️  Estimated time: {request.estimated_time}")
            print(f"🔧 Agents needed: {', '.join(request.agents_needed)}")
            print()
        
        # Handle special cases
        if request.intent == AnalysisIntent.COPILOT_WORKFLOW:
            return self._generate_copilot_workflow(input_dir, output_dir, app_name)
        
        if request.intent == AnalysisIntent.VALIDATION:
            return self._validate_input(input_dir, output_dir, verbose)
        
        if request.intent == AnalysisIntent.TROUBLESHOOTING:
            return self._troubleshoot_issues(input_dir, output_dir, verbose)
        
        # Run the appropriate analysis
        return self._run_analysis(request, input_dir, output_dir, app_name, method, resume_checkpoint, verbose)
    
    def _run_analysis(self, request: AnalysisRequest, input_dir: str, output_dir: str,
                     app_name: str, method: str, resume_checkpoint: Optional[str], verbose: bool) -> AnalysisResult:
        """Run the actual analysis based on the parsed request."""
        import time
        start_time = time.time()
        
        try:
            if method == "langgraph":
                # Use LangGraph orchestration
                result = run_langgraph_pipeline(input_dir, output_dir, app_name, resume_from_checkpoint=resume_checkpoint)
                success = result.success
                errors = result.state.get("warnings", [])
                warnings = []
            else:
                # Use simple agent suite
                if request.intent == AnalysisIntent.FULL_ANALYSIS or request.intent == AnalysisIntent.EXECUTIVE_SUMMARY:
                    # Run all agents
                    results = self.agent_suite.execute_full_pipeline(input_dir, output_dir, app_name)
                else:
                    # Run only specific agents
                    results = self._run_partial_pipeline(request.agents_needed, input_dir, output_dir, app_name)
                
                success = all(r.success for r in results)
                errors = [r.error for r in results if not r.success and r.error]
                warnings = []
            
            # Collect output files
            output_path = Path(output_dir)
            outputs = []
            for file_path in output_path.rglob("*.html"):
                outputs.append(str(file_path))
            for file_path in output_path.rglob("*.csv"):
                outputs.append(str(file_path))
            
            # Identify key deliverables
            primary_deliverable = str(output_path / "program_doc.html") if (output_path / "program_doc.html").exists() else None
            exec_summary = str(output_path / "executive_summary.md") if (output_path / "executive_summary.md").exists() else None
            task_ledger = str(output_path / "task_ledger.html") if (output_path / "task_ledger.html").exists() else None
            ui_catalog = str(output_path / "ui" / "index.html") if (output_path / "ui" / "index.html").exists() else None
            
            # Generate metrics summary
            metrics = self._collect_metrics(output_path)
            
            execution_time = f"{time.time() - start_time:.1f} seconds"
            
            return AnalysisResult(
                success=success,
                outputs_generated=outputs,
                primary_deliverable=primary_deliverable,
                executive_summary_path=exec_summary,
                task_ledger_path=task_ledger,
                ui_catalog_path=ui_catalog,
                errors=errors,
                warnings=warnings,
                execution_time=execution_time,
                metrics_summary=metrics
            )
            
        except Exception as e:
            execution_time = f"{time.time() - start_time:.1f} seconds"
            return AnalysisResult(
                success=False,
                outputs_generated=[],
                primary_deliverable=None,
                executive_summary_path=None,
                task_ledger_path=None,
                ui_catalog_path=None,
                errors=[str(e)],
                warnings=[],
                execution_time=execution_time,
                metrics_summary={}
            )
    
    def _run_partial_pipeline(self, agent_names: List[str], input_dir: str, output_dir: str, app_name: str):
        """Run only a subset of agents based on the analysis request."""
        results = []
        
        # Always need extractor and parser as prerequisites
        base_agents = ["extractor", "parser"]
        all_agents = base_agents + [a for a in agent_names if a not in base_agents]
        
        catalog_path = str(Path(output_dir) / "catalog.sqlite")
        unpacked_dir = str(Path(output_dir) / "unpacked")
        
        # Run agents in dependency order
        for agent_name in all_agents:
            if agent_name == "extractor":
                result = self.agent_suite.extractor.extract_jars(input_dir, output_dir)
            elif agent_name == "parser":
                result = self.agent_suite.parser.parse_rules(catalog_path, unpacked_dir)
            elif agent_name == "hierarchy":
                result = self.agent_suite.hierarchy.build_hierarchy(catalog_path, output_dir)
            elif agent_name == "flow":
                result = self.agent_suite.flow.analyze_flows(catalog_path, output_dir)
            elif agent_name == "tasks":
                result = self.agent_suite.tasks.extract_tasks(catalog_path, output_dir)
            elif agent_name == "ui":
                result = self.agent_suite.ui.render_ui(catalog_path, output_dir)
            elif agent_name == "doc_synthesizer":
                result = self.agent_suite.doc_synthesizer.synthesize_documentation(catalog_path, output_dir, app_name)
            else:
                continue
            
            results.append(result)
            
            # Stop on first failure for prerequisite agents
            if not result.success and agent_name in ["extractor", "parser"]:
                break
        
        return results
    
    def _validate_input(self, input_dir: str, output_dir: str, verbose: bool) -> AnalysisResult:
        """Validate input directory and provide diagnostics."""
        input_path = Path(input_dir)
        issues = []
        
        if not input_path.exists():
            issues.append(f"Input directory does not exist: {input_dir}")
        else:
            jar_files = list(input_path.glob("*.jar"))
            extracted_dirs = [d for d in input_path.iterdir() if d.is_dir() and (d / "META-INF").exists()]
            
            if not jar_files and not extracted_dirs:
                issues.append("No JAR files or extracted JAR directories found")
                issues.append("Expected: *.jar files OR directories containing META-INF/pega.xml")
                issues.append("For extracted JARs, ensure each directory has META-INF/pega.xml inside")
            elif extracted_dirs and not jar_files:
                # This is for users who already extracted their JARs
                if verbose:
                    print(f"✅ Found {len(extracted_dirs)} extracted JAR directories (no re-extraction needed)")
            elif jar_files:
                if verbose:
                    print(f"✅ Found {len(jar_files)} JAR files")
                    if extracted_dirs:
                        print(f"ℹ️  Also found {len(extracted_dirs)} extracted directories")
            
            # Run extractor to get detailed validation
            if not issues:
                try:
                    result = self.agent_suite.extractor.extract_jars(input_dir, output_dir)
                    if result.success:
                        outputs = result.outputs
                        validation_summary = {
                            "jars_found": outputs.get("jars_found", 0),
                            "files_cataloged": outputs.get("files_cataloged", 0),
                            "rule_files": outputs.get("rule_files", 0),
                            "rulesets": outputs.get("rulesets", [])
                        }
                        return AnalysisResult(
                            success=True,
                            outputs_generated=[],
                            primary_deliverable=None,
                            executive_summary_path=None,
                            task_ledger_path=None,
                            ui_catalog_path=None,
                            errors=[],
                            warnings=outputs.get("warnings", []),
                            execution_time="validation",
                            metrics_summary=validation_summary
                        )
                    else:
                        issues.append(result.error or "Validation failed")
                except Exception as e:
                    issues.append(f"Validation error: {e}")
        
        return AnalysisResult(
            success=False,
            outputs_generated=[],
            primary_deliverable=None,
            executive_summary_path=None,
            task_ledger_path=None,
            ui_catalog_path=None,
            errors=issues,
            warnings=[],
            execution_time="validation",
            metrics_summary={}
        )
    
    def _generate_copilot_workflow(self, input_dir: str, output_dir: str, app_name: str) -> AnalysisResult:
        """Generate prompts for GitHub Copilot Chat workflow."""
        from .agents import create_copilot_chat_workflow
        
        try:
            # This function prints the workflow - capture it to a file
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            workflow_file = output_path / "copilot_workflow.md"
            
            # Generate the workflow (this currently prints to stdout)
            create_copilot_chat_workflow(self.agent_suite, input_dir, output_dir, app_name)
            
            # Create a simple workflow file
            workflow_content = f"""# GitHub Copilot Chat Workflow for {app_name}

Generated for input directory: `{input_dir}`
Output directory: `{output_dir}`

Use the auto-dispatcher with `--method copilot` to see detailed step-by-step prompts.

```bash
python -m pega_re.auto_dispatcher "generate copilot workflow" \\
    --input {input_dir} \\
    --output {output_dir} \\
    --app-name "{app_name}"
```
"""
            workflow_file.write_text(workflow_content)
            
            return AnalysisResult(
                success=True,
                outputs_generated=[str(workflow_file)],
                primary_deliverable=str(workflow_file),
                executive_summary_path=None,
                task_ledger_path=None,
                ui_catalog_path=None,
                errors=[],
                warnings=[],
                execution_time="instant",
                metrics_summary={"workflow_type": "copilot_chat"}
            )
            
        except Exception as e:
            return AnalysisResult(
                success=False,
                outputs_generated=[],
                primary_deliverable=None,
                executive_summary_path=None,
                task_ledger_path=None,
                ui_catalog_path=None,
                errors=[str(e)],
                warnings=[],
                execution_time="instant",
                metrics_summary={}
            )
    
    def _troubleshoot_issues(self, input_dir: str, output_dir: str, verbose: bool) -> AnalysisResult:
        """Run basic troubleshooting diagnostics."""
        # Start with validation
        validation_result = self._validate_input(input_dir, output_dir, verbose)
        
        if not validation_result.success:
            return validation_result
        
        # Try parsing a sample of rules to identify issues
        try:
            # Run extractor and parser only
            extractor_result = self.agent_suite.extractor.extract_jars(input_dir, output_dir)
            if not extractor_result.success:
                return AnalysisResult(
                    success=False,
                    outputs_generated=[],
                    primary_deliverable=None,
                    executive_summary_path=None,
                    task_ledger_path=None,
                    ui_catalog_path=None,
                    errors=[extractor_result.error or "Extractor failed"],
                    warnings=[],
                    execution_time="troubleshooting",
                    metrics_summary={}
                )
            
            catalog_path = str(Path(output_dir) / "catalog.sqlite")
            unpacked_dir = str(Path(output_dir) / "unpacked")
            
            parser_result = self.agent_suite.parser.parse_rules(catalog_path, unpacked_dir)
            
            # Collect troubleshooting info
            troubleshooting_info = {
                "extraction_successful": extractor_result.success,
                "parsing_successful": parser_result.success,
                "total_files": extractor_result.outputs.get("files_cataloged", 0),
                "rule_files": extractor_result.outputs.get("rule_files", 0),
                "parse_success_rate": 0
            }
            
            if parser_result.success:
                outputs = parser_result.outputs
                total_rules = outputs.get("total", 0)
                parsed_ok = outputs.get("parsed_ok", 0)
                troubleshooting_info["parse_success_rate"] = parsed_ok / total_rules if total_rules > 0 else 0
                troubleshooting_info["unknown_rule_types"] = len(outputs.get("unknown_types", []))
            
            return AnalysisResult(
                success=True,
                outputs_generated=[catalog_path],
                primary_deliverable=None,
                executive_summary_path=None,
                task_ledger_path=None,
                ui_catalog_path=None,
                errors=[],
                warnings=extractor_result.outputs.get("warnings", []),
                execution_time="troubleshooting",
                metrics_summary=troubleshooting_info
            )
            
        except Exception as e:
            return AnalysisResult(
                success=False,
                outputs_generated=[],
                primary_deliverable=None,
                executive_summary_path=None,
                task_ledger_path=None,
                ui_catalog_path=None,
                errors=[f"Troubleshooting failed: {e}"],
                warnings=[],
                execution_time="troubleshooting",
                metrics_summary={}
            )
    
    def _collect_metrics(self, output_path: Path) -> dict:
        """Collect metrics from generated outputs."""
        metrics = {}
        
        # Try to read SQLite catalog for metrics
        catalog_path = output_path / "catalog.sqlite"
        if catalog_path.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(catalog_path))
                cur = conn.cursor()
                
                # Basic counts
                metrics["total_rules"] = cur.execute("SELECT COUNT(*) FROM rules WHERE parsed_ok=1").fetchone()[0]
                metrics["case_types"] = cur.execute("SELECT COUNT(*) FROM case_types").fetchone()[0] if self._table_exists(cur, "case_types") else 0
                metrics["assignments"] = cur.execute("SELECT COUNT(*) FROM assignments").fetchone()[0] if self._table_exists(cur, "assignments") else 0
                metrics["ui_rules"] = cur.execute("SELECT COUNT(*) FROM ui_rules").fetchone()[0] if self._table_exists(cur, "ui_rules") else 0
                
                conn.close()
            except Exception:
                pass
        
        return metrics
    
    def _table_exists(self, cursor, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            return cursor.fetchone() is not None
        except Exception:
            return False


def main():
    """Command line interface for the auto-dispatcher."""
    parser = argparse.ArgumentParser(
        description="PegaRE Auto-Dispatcher - Intelligent agent selection based on natural language queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Natural Language Examples:
  "analyze my pega application"
  "extract all tasks and workflows"  
  "show me the UI screens and forms"
  "build class hierarchy and dependencies"
  "generate executive summary for steering committee"
  "validate my input files"
  "troubleshoot parsing issues"
  "generate copilot workflow"

The system automatically selects the appropriate agents based on your query.
        """
    )
    
    parser.add_argument("query", help="Natural language description of what you want to analyze")
    parser.add_argument("--input", "-i", required=True, help="Input directory with JAR files")
    parser.add_argument("--output", "-o", default="./pegare_output", help="Output directory")
    parser.add_argument("--app-name", default="Pega Application", help="Application name for documentation")
    parser.add_argument("--method", choices=["simple", "langgraph"], default="simple", help="Execution method")
    parser.add_argument("--resume", help="Resume from checkpoint (langgraph only)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--format", choices=["standard", "json"], default="standard", help="Output format")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = PegaAnalyzer()
    
    # Run analysis
    result = analyzer.analyze_from_text(
        query=args.query,
        input_dir=args.input,
        output_dir=args.output,
        app_name=args.app_name,
        method=args.method,
        resume_checkpoint=args.resume,
        verbose=args.verbose
    )
    
    # Output results
    if args.format == "json":
        output_data = {
            "success": result.success,
            "execution_time": result.execution_time,
            "primary_deliverable": result.primary_deliverable,
            "outputs_generated": result.outputs_generated,
            "metrics": result.metrics_summary,
            "errors": result.errors,
            "warnings": result.warnings
        }
        print(json.dumps(output_data, indent=2))
    else:
        # Standard output
        if result.success:
            print("✅ Analysis completed successfully!")
            print(f"⏱️  Execution time: {result.execution_time}")
            
            if result.primary_deliverable:
                print(f"📋 Primary deliverable: {result.primary_deliverable}")
            
            if result.executive_summary_path:
                print(f"📄 Executive summary: {result.executive_summary_path}")
            
            if result.task_ledger_path:
                print(f"📊 Task ledger: {result.task_ledger_path}")
            
            if result.ui_catalog_path:
                print(f"🖼️  UI catalog: {result.ui_catalog_path}")
            
            if result.metrics_summary:
                print(f"📈 Metrics: {result.metrics_summary}")
        else:
            print("❌ Analysis failed!")
            for error in result.errors:
                print(f"   Error: {error}")
        
        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   {warning}")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    exit(main())
