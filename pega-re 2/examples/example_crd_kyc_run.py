"""
example_crd_kyc_run.py — Example for your CRD KYC mainframe modernization program.

This shows how to integrate PegaRE into your existing program workflow,
especially alongside MFREA (Mainframe Reverse Engineering Agent) outputs.
"""
from pathlib import Path
from pega_re.agents import PegaREAgentSuite


def run_crd_kyc_analysis():
    """
    Example run for your CRD KYC application.
    Adjust paths and parameters to match your environment.
    """
    
    # Your extracted Pega JAR directories (manifests + bin files already extracted)
    pega_extracted_dir = "/path/to/your/extracted_pega_content"
    
    # Output alongside your existing MFREA outputs
    output_dir = "/path/to/program_analysis/pega_analysis"
    
    # Application name for executive reporting
    app_name = "CRD KYC Platform"
    
    print("🏦 Starting PegaRE analysis for CRD KYC Platform")
    print(f"📂 Extracted Pega content: {pega_extracted_dir}")
    print(f"📁 Output: {output_dir}")
    print("ℹ️  Working with extracted JAR contents (manifest + bin files)")
    print("🤖 Powered by GitHub Copilot + deterministic Python modules")
    
    # Initialize the agent suite
    suite = PegaREAgentSuite()
    
    # Option 1: Run the complete pipeline deterministically (no AI needed)
    print("\n📊 Option 1: Direct Python execution (no AI required)")
    results = suite.execute_full_pipeline(
        input_dir=pega_extracted_dir,  # Point to your extracted directory
        workdir=output_dir,
        app_name=app_name
    )
    
    # Report results for your steering committee
    successful_steps = [r for r in results if r.success]
    
    if len(successful_steps) == len(results):
        print("\n✅ PegaRE analysis completed successfully!")
        
        # Key deliverables for your executive reporting
        output_path = Path(output_dir)
        deliverables = {
            "Executive Summary": output_path / "executive_summary.md",
            "Full Program Documentation": output_path / "program_doc.html", 
            "Task Generation Ledger": output_path / "task_ledger.html",
            "UI Inventory": output_path / "ui" / "index.html",
            "Class Hierarchy": output_path / "hierarchy.html"
        }
        
        print("\n📋 Generated deliverables for C-Suite reporting:")
        for name, path in deliverables.items():
            if path.exists():
                print(f"   📄 {name}: {path}")
                
                # Integration suggestions for your existing workflow
                if "executive_summary" in path.name:
                    print(f"       💡 Include in monthly steering committee deck")
                elif "program_doc.html" in path.name:
                    print(f"       💡 Link from your Confluence program workspace")
                elif "task_ledger.html" in path.name:
                    print(f"       💡 Use for workstream capacity planning")
        
        # Show integration with your MFREA outputs
        print(f"\n🔗 Integration with MFREA:")
        print(f"   • MFREA analyzes Natural/ADABAS dependencies")
        print(f"   • PegaRE analyzes Pega task flows and UI")
        print(f"   • Both feed into your modernization roadmap")
        print(f"   • Task ledger shows which Pega workflows to prioritize")
        
        # Option 2: GitHub Copilot workflow for interactive analysis
        print(f"\n🤖 Alternative: GitHub Copilot Chat workflow")
        print(f"   For interactive step-by-step analysis with Copilot:")
        print(f"   python -c \"from pega_re.agents import create_copilot_chat_workflow, PegaREAgentSuite; create_copilot_chat_workflow(PegaREAgentSuite(), '{pega_extracted_dir}', '{output_dir}', '{app_name}')\"")
        print(f"   ✅ Perfect for learning the system or customizing analysis")
        print(f"   ✅ No external API keys required - pure GitHub Copilot")
        
        # Stats for your executive summary
        extractor_result = successful_steps[0].outputs
        parser_result = successful_steps[1].outputs
        tasks_result = next((r.outputs for r in successful_steps if r.agent_name == "pega-task-extractor"), {})
        
        print(f"\n📊 Key metrics for executive reporting:")
        print(f"   • Total Pega rules analyzed: {parser_result.get('total', '?'):,}")
        print(f"   • User-facing tasks identified: {tasks_result.get('assignment_count', '?'):,}")
        print(f"   • Case types (business processes): {getattr(tasks_result, 'case_type_count', '?')}")
        print(f"   • UI screens to modernize: {getattr(tasks_result, 'harness_count', '?')}")
        
    else:
        print(f"\n❌ Analysis incomplete: {len(successful_steps)}/{len(results)} steps successful")
        for result in results:
            if not result.success:
                print(f"   • {result.agent_name}: {result.error}")


def integrate_with_existing_tooling():
    """
    Example of integrating PegaRE outputs with your existing program tooling.
    """
    print("\n🔧 Integration suggestions for your program:")
    
    print("\n📊 Excel workbooks (your existing deliverables):")
    print("   • Import task_ledger.csv into your capacity planning workbook")
    print("   • Add Pega metrics to your monthly KPI dashboard")
    print("   • Include case type inventory in architecture documentation")
    
    print("\n📋 PowerPoint decks (your steering committee updates):")
    print("   • Embed Mermaid diagrams from case_type_*.html files")
    print("   • Use executive_summary.md as input for slide content")
    print("   • Include UI screenshots from rendered harnesses")
    
    print("\n🔍 Confluence documentation:")
    print("   • Link to program_doc.html as the Pega analysis artifact")
    print("   • Embed hierarchy.html for stakeholder reference")
    print("   • Use task ledger for workstream planning")
    
    print("\n📅 Microsoft Project / planning tools:")
    print("   • Map case types to modernization workstream timelines")
    print("   • Use task complexity for effort estimation")
    print("   • Sequence UI modernization by harness dependency")


if __name__ == "__main__":
    # Run the analysis
    run_crd_kyc_analysis()
    
    # Show integration suggestions
    integrate_with_existing_tooling()
    
    print("\n🎯 Next steps for your modernization program:")
    print("   1. Review executive_summary.md with your steering committee")
    print("   2. Use task_ledger.html to prioritize which case types to modernize first")
    print("   3. Compare Pega UI inventory with MFREA mainframe screen analysis")
    print("   4. Feed both analyses into your 2025-2027 modernization roadmap")
    print("   5. Include metrics in your monthly C-Suite updates")
