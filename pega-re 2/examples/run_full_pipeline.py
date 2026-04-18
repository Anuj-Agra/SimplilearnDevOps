"""
run_full_pipeline.py — Complete example of running PegaRE end-to-end.

This script demonstrates three ways to run the reverse engineering pipeline:
1. Simple synchronous execution using the agent suite
2. LangGraph orchestration with checkpointing
3. GitHub Copilot Chat workflow generation
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

# Add the parent directory to Python path so we can import pega_re
sys.path.insert(0, str(Path(__file__).parent.parent))

from pega_re.agents import PegaREAgentSuite, create_copilot_chat_workflow
from pega_re.graph import run_full_pipeline as run_langgraph_pipeline


def run_simple_pipeline(input_dir: str, output_dir: str, app_name: str, verbose: bool = False):
    """
    Run the pipeline using the simple agent suite (no LangGraph).
    Good for testing and when you don't need checkpointing.
    """
    print(f"🚀 Starting PegaRE pipeline: {app_name}")
    print(f"📂 Input: {input_dir}")
    print(f"📁 Output: {output_dir}")
    print()
    
    suite = PegaREAgentSuite()
    results = suite.execute_full_pipeline(input_dir, output_dir, app_name)
    
    print("Pipeline Execution Summary:")
    print("=" * 50)
    
    success_count = 0
    for i, result in enumerate(results, 1):
        status = "✅" if result.success else "❌"
        print(f"{status} Step {i}: {result.agent_name}")
        
        if verbose and result.success:
            print(f"   Outputs: {list(result.outputs.keys())}")
        elif not result.success:
            print(f"   Error: {result.error}")
        
        if result.success:
            success_count += 1
    
    print()
    print(f"Completed: {success_count}/{len(results)} steps successful")
    
    if success_count == len(results):
        print("\n🎉 Pipeline completed successfully!")
        print("\n📋 Generated outputs:")
        output_path = Path(output_dir)
        
        key_files = [
            ("Program Documentation", "program_doc.html"),
            ("Executive Summary", "executive_summary.md"),
            ("Task Ledger", "task_ledger.html"),
            ("UI Catalog", "ui/index.html"),
            ("Class Hierarchy", "hierarchy.html"),
            ("SQLite Catalog", "catalog.sqlite")
        ]
        
        for name, file_path in key_files:
            full_path = output_path / file_path
            if full_path.exists():
                print(f"   📄 {name}: {full_path}")
            else:
                print(f"   ⚠️  {name}: {file_path} (not found)")
    
    return success_count == len(results)


def run_langgraph_pipeline_wrapper(input_dir: str, output_dir: str, app_name: str, 
                                  resume_checkpoint: Optional[str] = None):
    """
    Run the pipeline using LangGraph orchestration.
    Supports checkpointing and resumption.
    """
    print(f"🚀 Starting PegaRE LangGraph pipeline: {app_name}")
    if resume_checkpoint:
        print(f"🔄 Resuming from checkpoint: {resume_checkpoint}")
    print()
    
    result = run_langgraph_pipeline(
        input_dir=input_dir,
        workdir=output_dir,
        app_name=app_name,
        llm_agent=None,  # Could integrate actual LLM here
        resume_from_checkpoint=resume_checkpoint
    )
    
    if result.success:
        print("🎉 LangGraph pipeline completed successfully!")
        print("\n📋 Key outputs:")
        if result.program_doc_html:
            print(f"   📄 Program Documentation: {result.program_doc_html}")
        if result.task_ledger_html:
            print(f"   📊 Task Ledger: {result.task_ledger_html}")
        if result.ui_index_html:
            print(f"   🖼️  UI Catalog: {result.ui_index_html}")
        if result.hierarchy_html:
            print(f"   🌳 Hierarchy: {result.hierarchy_html}")
        
        if result.state["warnings"]:
            print(f"\n⚠️  Warnings ({len(result.state['warnings'])}):")
            for warning in result.state["warnings"]:
                print(f"   • {warning}")
    else:
        print("❌ LangGraph pipeline failed!")
        if result.state["warnings"]:
            print("\nErrors and warnings:")
            for warning in result.state["warnings"]:
                print(f"   • {warning}")
    
    return result.success


def generate_copilot_workflow(input_dir: str, output_dir: str, app_name: str):
    """Generate step-by-step prompts for GitHub Copilot Chat."""
    suite = PegaREAgentSuite()
    create_copilot_chat_workflow(suite, input_dir, output_dir, app_name)


def validate_inputs(input_dir: str) -> bool:
    """Validate that input directory contains Pega JAR files or extracted content."""
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Input directory does not exist: {input_dir}")
        return False
    
    # Check for JAR files
    jar_files = list(input_path.glob("*.jar"))
    if jar_files:
        print(f"✅ Found {len(jar_files)} JAR files in {input_dir}")
        return True
    
    # Check for already-extracted directories
    extracted_dirs = [d for d in input_path.iterdir() if d.is_dir() and (d / "META-INF").exists()]
    if extracted_dirs:
        print(f"✅ Found {len(extracted_dirs)} extracted JAR directories in {input_dir}")
        return True
    
    print(f"❌ No JAR files or extracted JAR directories found in {input_dir}")
    print("   Expected: *.jar files OR directories containing META-INF/pega.xml")
    return False


def estimate_scale(input_dir: str):
    """Provide a rough estimate of the workload based on input files."""
    input_path = Path(input_dir)
    
    # Count potential rule files
    xml_files = list(input_path.rglob("*.xml"))
    pegarules_files = list(input_path.rglob("*.pegarules"))
    total_files = len(xml_files) + len(pegarules_files)
    
    if total_files > 0:
        print(f"📊 Estimated scale: ~{total_files:,} rule files detected")
        
        if total_files < 10_000:
            print("   💨 Small application - should complete in minutes")
        elif total_files < 100_000:
            print("   ⏱️  Medium application - may take 15-30 minutes")
        else:
            print("   ⏳ Large application - could take 1+ hours")
        
        # Estimate memory usage
        estimated_mb = total_files * 0.05  # Very rough: ~50KB average per rule
        if estimated_mb > 500:
            print(f"   💾 Estimated memory usage: ~{estimated_mb:.0f}MB")
            print("   💡 Tip: Use LangGraph pipeline for better memory management")
    else:
        print("   📊 No rule files found - may be binary-only or pre-parsed content")


def main():
    parser = argparse.ArgumentParser(
        description="PegaRE — Reverse engineer Pega applications from JAR exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with 4 extracted JAR files
  python run_full_pipeline.py /path/to/extracted_jars --output ./output --app-name "KYC Application"
  
  # Use LangGraph orchestration (supports checkpointing)
  python run_full_pipeline.py /path/to/jars --method langgraph --app-name "CRD System"
  
  # Generate prompts for GitHub Copilot Chat
  python run_full_pipeline.py /path/to/jars --method copilot --app-name "My App"
  
  # Resume from a checkpoint
  python run_full_pipeline.py /path/to/jars --method langgraph --resume checkpoint-123
        """
    )
    
    parser.add_argument("input_dir", help="Directory containing JAR files or extracted JAR contents")
    parser.add_argument("--output", "-o", default="./pegare_output", 
                       help="Output directory for generated documentation (default: ./pegare_output)")
    parser.add_argument("--app-name", default="Pega Application", 
                       help="Application name for documentation (default: Pega Application)")
    parser.add_argument("--method", choices=["simple", "langgraph", "copilot"], default="simple",
                       help="Execution method (default: simple)")
    parser.add_argument("--resume", help="Resume LangGraph pipeline from checkpoint ID")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Only validate inputs and estimate scale, don't run pipeline")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not validate_inputs(args.input_dir):
        return 1
    
    # Estimate scale
    estimate_scale(args.input_dir)
    print()
    
    if args.validate_only:
        print("✅ Validation complete. Use --help for execution options.")
        return 0
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Execute based on method
    success = False
    
    if args.method == "simple":
        success = run_simple_pipeline(args.input_dir, args.output, args.app_name, args.verbose)
    
    elif args.method == "langgraph":
        try:
            success = run_langgraph_pipeline_wrapper(
                args.input_dir, args.output, args.app_name, args.resume
            )
        except ImportError:
            print("❌ LangGraph not available. Install with: pip install langgraph")
            print("💡 Use --method simple as alternative")
            return 1
    
    elif args.method == "copilot":
        print("Generating GitHub Copilot Chat workflow...")
        generate_copilot_workflow(args.input_dir, args.output, args.app_name)
        print("\n✅ Copilot workflow generated. Follow the prompts above in GitHub Copilot Chat.")
        return 0
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
