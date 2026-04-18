#!/usr/bin/env python3
"""
copilot_workflow_example.py - Generate GitHub Copilot Chat prompts for your Pega analysis

This is the simplest way to get started with PegaRE using GitHub Copilot.
No external API keys needed - just GitHub Copilot Chat.
"""
from pega_re.agents import create_copilot_chat_workflow, PegaREAgentSuite

def main():
    """Generate Copilot workflow for analyzing your extracted Pega JARs."""
    
    # UPDATE THESE PATHS FOR YOUR SETUP
    input_dir = "/path/to/your/extracted_pega_jars"  # Your manifest + bin files
    output_dir = "./pega_analysis_output"             # Where to put results
    app_name = "CRD KYC Platform"                     # Your application name
    
    print("🤖 Generating GitHub Copilot Chat workflow for Pega analysis...")
    print(f"📂 Input: {input_dir}")
    print(f"📁 Output: {output_dir}")  
    print(f"🏷️  App: {app_name}")
    print()
    
    # Generate the step-by-step workflow
    suite = PegaREAgentSuite()
    create_copilot_chat_workflow(suite, input_dir, output_dir, app_name)
    
    print("\n" + "="*60)
    print("🎯 Next Steps:")
    print("1. Copy each prompt above into GitHub Copilot Chat")
    print("2. Wait for each step to complete before proceeding")
    print("3. Your analysis results will be in:", output_dir)
    print("4. Key deliverable: task_ledger.html (who does what when)")
    print("="*60)

if __name__ == "__main__":
    main()
