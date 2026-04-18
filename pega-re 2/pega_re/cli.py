"""
cli.py - Convenient command line interfaces for common PegaRE operations
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from .auto_dispatcher import PegaAnalyzer


def analyze_command():
    """Command line interface for pegare-analyze command."""
    parser = argparse.ArgumentParser(
        description="Analyze Pega application - simplified interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pegare-analyze /path/to/extracted_jars
  pegare-analyze /path/to/jars --app-name "CRD KYC Platform"
  pegare-analyze /path/to/jars --tasks-only
  pegare-analyze /path/to/jars --ui-only --output ./ui_analysis
        """
    )
    
    parser.add_argument("input_dir", help="Directory with JAR files or extracted JAR contents")
    parser.add_argument("--app-name", default="Pega Application", help="Application name for documentation")
    parser.add_argument("--output", "-o", default="./pegare_output", help="Output directory")
    parser.add_argument("--tasks-only", action="store_true", help="Extract tasks and workflows only")
    parser.add_argument("--ui-only", action="store_true", help="Analyze UI screens only")
    parser.add_argument("--hierarchy-only", action="store_true", help="Build class hierarchy only")
    parser.add_argument("--executive-only", action="store_true", help="Generate executive summary only")
    parser.add_argument("--method", choices=["simple", "langgraph"], default="simple", help="Execution method")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--format", choices=["standard", "json"], default="standard", help="Output format")
    
    args = parser.parse_args()
    
    # Determine query based on flags
    if args.tasks_only:
        query = "extract all tasks and workflows"
    elif args.ui_only:
        query = "show me the UI screens and forms"
    elif args.hierarchy_only:
        query = "build class hierarchy and dependencies"
    elif args.executive_only:
        query = "generate executive summary for management"
    else:
        query = "analyze my pega application"
    
    # Run analysis
    analyzer = PegaAnalyzer()
    result = analyzer.analyze_from_text(
        query=query,
        input_dir=args.input_dir,
        output_dir=args.output,
        app_name=args.app_name,
        method=args.method,
        verbose=args.verbose
    )
    
    # Output results
    if args.format == "json":
        import json
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
        if result.success:
            print("✅ Analysis completed successfully!")
            print(f"⏱️  Execution time: {result.execution_time}")
            
            if result.primary_deliverable:
                print(f"📋 Primary deliverable: {result.primary_deliverable}")
            
            key_outputs = [
                ("Executive summary", result.executive_summary_path),
                ("Task ledger", result.task_ledger_path), 
                ("UI catalog", result.ui_catalog_path),
            ]
            
            for name, path in key_outputs:
                if path:
                    print(f"📄 {name}: {path}")
                    
            if result.metrics_summary:
                print(f"📈 Key metrics:")
                for key, value in result.metrics_summary.items():
                    print(f"   {key}: {value:,}" if isinstance(value, int) else f"   {key}: {value}")
        else:
            print("❌ Analysis failed!")
            for error in result.errors:
                print(f"   Error: {error}")
        
        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   {warning}")
    
    return 0 if result.success else 1


def validate_command():
    """Command line interface for pegare-validate command."""
    parser = argparse.ArgumentParser(
        description="Validate Pega input files and estimate analysis scope"
    )
    
    parser.add_argument("input_dir", help="Directory to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--format", choices=["standard", "json"], default="standard", help="Output format")
    
    args = parser.parse_args()
    
    analyzer = PegaAnalyzer()
    result = analyzer.analyze_from_text(
        query="validate my input",
        input_dir=args.input_dir,
        output_dir="./temp_validation",
        verbose=args.verbose
    )
    
    if args.format == "json":
        import json
        output_data = {
            "valid": result.success,
            "metrics": result.metrics_summary,
            "errors": result.errors,
            "warnings": result.warnings
        }
        print(json.dumps(output_data, indent=2))
    else:
        if result.success:
            print("✅ Input validation successful!")
            if result.metrics_summary:
                print("\n📊 Discovered content:")
                for key, value in result.metrics_summary.items():
                    if isinstance(value, int):
                        print(f"   {key}: {value:,}")
                    elif isinstance(value, list):
                        print(f"   {key}: {', '.join(value[:5])}" + (f" (+{len(value)-5} more)" if len(value) > 5 else ""))
                    else:
                        print(f"   {key}: {value}")
        else:
            print("❌ Input validation failed!")
            for error in result.errors:
                print(f"   {error}")
        
        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   {warning}")
    
    # Clean up temp validation directory
    import shutil
    temp_dir = Path("./temp_validation")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    return 0 if result.success else 1


if __name__ == "__main__":
    # This allows the CLI module to be run directly for testing
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        sys.argv = ["pegare-validate"] + sys.argv[2:]
        exit(validate_command())
    else:
        sys.argv = ["pegare-analyze"] + sys.argv[1:]
        exit(analyze_command())
