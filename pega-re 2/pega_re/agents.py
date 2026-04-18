"""
agents.py — LLM agent wrappers that load SKILL.md files and execute deterministic cores.

Each agent is a thin wrapper that:
1. Loads its SKILL.md file as context
2. Calls the deterministic Python function
3. Returns structured results

This enables the same skill files to work with Claude, GitHub Copilot Chat, or any LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import extractor, parser, hierarchy, flow, tasks, ui, docgen


@dataclass
class SkillExecution:
    agent_name: str
    skill_md_path: str
    skill_content: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    success: bool
    error: str | None


class PegaREAgent:
    """Base class for all PegaRE agents."""
    
    def __init__(self, skill_name: str, skill_dir: Path, deterministic_fn: Callable):
        self.skill_name = skill_name
        self.skill_file = skill_dir / f"skills/{skill_name}/SKILL.md"
        self.deterministic_fn = deterministic_fn
        self.skill_content = ""
        
        if self.skill_file.exists():
            self.skill_content = self.skill_file.read_text(encoding="utf-8")
    
    def get_skill_prompt(self, **kwargs) -> str:
        """
        Return the complete prompt for an LLM to execute this skill.
        This combines the SKILL.md content with the specific inputs.
        """
        prompt = f"""You are executing the {self.skill_name} skill for PegaRE.

{self.skill_content}

## Current Execution Context
"""
        for key, value in kwargs.items():
            prompt += f"- **{key}**: {value}\n"
        
        prompt += """
## Instructions
Execute this skill according to the instructions in the SKILL.md above. Call the corresponding Python function and report the results. Focus on the specific outputs and any warnings that should be surfaced to the user.
"""
        return prompt
    
    def execute(self, **kwargs) -> SkillExecution:
        """Execute the deterministic function and wrap results."""
        try:
            outputs = self.deterministic_fn(**kwargs)
            return SkillExecution(
                agent_name=self.skill_name,
                skill_md_path=str(self.skill_file),
                skill_content=self.skill_content,
                inputs=kwargs,
                outputs=outputs.__dict__ if hasattr(outputs, '__dict__') else outputs,
                success=True,
                error=None
            )
        except Exception as e:
            return SkillExecution(
                agent_name=self.skill_name,
                skill_md_path=str(self.skill_file),
                skill_content=self.skill_content,
                inputs=kwargs,
                outputs={},
                success=False,
                error=str(e)
            )


class PegaExtractorAgent(PegaREAgent):
    """JAR extraction and file cataloging agent."""
    
    def __init__(self, project_root: Path):
        super().__init__("pega-extractor", project_root, extractor.extract_and_catalog)
    
    def extract_jars(self, input_dir: str, workdir: str) -> SkillExecution:
        """Extract JAR files and build initial catalog."""
        return self.execute(input_dir=input_dir, workdir=workdir)


class PegaRuleParserAgent(PegaREAgent):
    """Rule XML parsing and classification agent."""
    
    def __init__(self, project_root: Path):
        super().__init__("pega-rule-parser", project_root, parser.parse_all)
    
    def parse_rules(self, catalog_path: str, unpacked_dir: str) -> SkillExecution:
        """Stream-parse rule XML into typed records."""
        return self.execute(catalog_path=catalog_path, unpacked_dir=unpacked_dir)


class PegaHierarchyMapperAgent(PegaREAgent):
    """Class hierarchy and ruleset organization agent."""
    
    def __init__(self, project_root: Path):
        super().__init__("pega-hierarchy-mapper", project_root, hierarchy.build)
    
    def build_hierarchy(self, catalog_path: str, workdir: str) -> SkillExecution:
        """Build the Ruleset → Class → Property hierarchy."""
        return self.execute(catalog_path=catalog_path, workdir=workdir)


class PegaFlowAnalyzerAgent(PegaREAgent):
    """Flow and process analysis agent."""
    
    def __init__(self, project_root: Path):
        super().__init__("pega-flow-analyzer", project_root, flow.analyse)
    
    def analyze_flows(self, catalog_path: str, workdir: str) -> SkillExecution:
        """Decode Case Types, Stages, Steps, and Flow diagrams."""
        return self.execute(catalog_path=catalog_path, workdir=workdir)


class PegaTaskExtractorAgent(PegaREAgent):
    """Assignment and task generation analysis agent."""
    
    def __init__(self, project_root: Path):
        super().__init__("pega-task-extractor", project_root, tasks.extract)
    
    def extract_tasks(self, catalog_path: str, workdir: str) -> SkillExecution:
        """Extract assignments with routing, SLAs, and trigger conditions."""
        return self.execute(catalog_path=catalog_path, workdir=workdir)


class PegaUIRendererAgent(PegaREAgent):
    """UI rendering and HTML generation agent."""
    
    def __init__(self, project_root: Path):
        super().__init__("pega-ui-renderer", project_root, ui.render_all)
    
    def render_ui(self, catalog_path: str, workdir: str) -> SkillExecution:
        """Render Sections and Harnesses into browsable HTML."""
        return self.execute(catalog_path=catalog_path, workdir=workdir)


class PegaDocSynthesizerAgent(PegaREAgent):
    """Program documentation synthesis agent."""
    
    def __init__(self, project_root: Path):
        super().__init__("pega-doc-synthesizer", project_root, self._docgen_wrapper)
    
    def _docgen_wrapper(self, catalog_path: str, workdir: str, app_name: str, llm_summarizer=None):
        """Wrapper to handle optional LLM parameter."""
        return docgen.synthesize(catalog_path, workdir, app_name, llm_summarizer)
    
    def synthesize_documentation(self, catalog_path: str, workdir: str, app_name: str, 
                                llm_summarizer: Callable[[str], str] | None = None) -> SkillExecution:
        """Generate the final Program Documentation."""
        return self.execute(
            catalog_path=catalog_path, 
            workdir=workdir, 
            app_name=app_name, 
            llm_summarizer=llm_summarizer
        )


class PegaREAgentSuite:
    """Complete suite of PegaRE agents for easy orchestration."""
    
    def __init__(self, project_root: str | Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent
        else:
            project_root = Path(project_root)
        
        self.project_root = project_root
        self.extractor = PegaExtractorAgent(project_root)
        self.parser = PegaRuleParserAgent(project_root)
        self.hierarchy = PegaHierarchyMapperAgent(project_root)
        self.flow = PegaFlowAnalyzerAgent(project_root)
        self.tasks = PegaTaskExtractorAgent(project_root)
        self.ui = PegaUIRendererAgent(project_root)
        self.doc_synthesizer = PegaDocSynthesizerAgent(project_root)
    
    def get_all_agents(self) -> list[PegaREAgent]:
        """Get all agents in execution order."""
        return [
            self.extractor, self.parser, self.hierarchy, 
            self.flow, self.tasks, self.ui, self.doc_synthesizer
        ]
    
    def execute_full_pipeline(self, input_dir: str, workdir: str, app_name: str,
                             llm_summarizer: Callable[[str], str] | None = None) -> list[SkillExecution]:
        """
        Execute the complete pipeline step-by-step.
        Returns a list of execution results for each agent.
        """
        results = []
        
        # 1. Extract JARs
        result = self.extractor.extract_jars(input_dir, workdir)
        results.append(result)
        if not result.success:
            return results
        
        catalog_path = str(Path(workdir) / "catalog.sqlite")
        unpacked_dir = str(Path(workdir) / "unpacked")
        
        # 2. Parse rules
        result = self.parser.parse_rules(catalog_path, unpacked_dir)
        results.append(result)
        if not result.success:
            return results
        
        # 3. Build hierarchy (parallel eligible)
        result = self.hierarchy.build_hierarchy(catalog_path, workdir)
        results.append(result)
        
        # 4. Analyze flows (parallel eligible)
        result = self.flow.analyze_flows(catalog_path, workdir)
        results.append(result)
        
        # 5. Render UI (parallel eligible)
        result = self.ui.render_ui(catalog_path, workdir)
        results.append(result)
        
        # 6. Extract tasks (depends on flows)
        if results[-2].success:  # flow analysis
            result = self.tasks.extract_tasks(catalog_path, workdir)
            results.append(result)
        
        # 7. Synthesize documentation (depends on all specialists)
        if all(r.success for r in results[-4:]):  # hierarchy, flow, ui, tasks
            result = self.doc_synthesizer.synthesize_documentation(
                catalog_path, workdir, app_name, llm_summarizer
            )
            results.append(result)
        
        return results


# Example LLM integration patterns
def create_github_copilot_summarizer():
    """Example: Create a summarizer using GitHub Copilot (for interactive sessions)."""
    def summarizer(prompt: str) -> str:
        # This would be used in interactive Copilot sessions
        return f"[Copilot: Use this prompt in GitHub Copilot Chat]\n\n{prompt}"
    return summarizer


def create_copilot_chat_workflow(agent_suite: PegaREAgentSuite, input_dir: str, workdir: str, app_name: str):
    """
    Generate optimized prompts for GitHub Copilot Chat workflow.
    
    This function demonstrates how to use the skill files with GitHub Copilot Chat:
    1. Each skill becomes a complete prompt for Copilot
    2. Copilot executes the Python function step by step
    3. Results flow into the next step automatically
    """
    agents = agent_suite.get_all_agents()
    
    print("=== GitHub Copilot Chat Workflow ===\n")
    print("Copy and paste each prompt below into GitHub Copilot Chat.\n")
    print("✅ Works with GitHub Copilot Pro or Enterprise")
    print("✅ No external API keys required") 
    print("✅ Each step builds on the previous\n")
    
    for i, agent in enumerate(agents, 1):
        print(f"## Step {i}: {agent.skill_name.replace('-', ' ').title()}")
        print(f"```")
        print(f"@workspace Execute this PegaRE skill step-by-step:")
        print(f"")
        
        # Add the skill content
        print(agent.skill_content)
        print(f"")
        print(f"## Execution Context for Step {i}")
        
        if agent.skill_name == "pega-extractor":
            print(f"- input_dir: {input_dir}")
            print(f"- workdir: {workdir}")
            print(f"")
            print(f"Call: pega_re.extractor.extract_and_catalog(input_dir, workdir)")
        elif agent.skill_name == "pega-rule-parser":
            print(f"- catalog_path: {workdir}/catalog.sqlite")
            print(f"- unpacked_dir: {workdir}/unpacked") 
            print(f"")
            print(f"Call: pega_re.parser.parse_all(catalog_path, unpacked_dir)")
        elif agent.skill_name in ["pega-hierarchy-mapper", "pega-flow-analyzer", "pega-ui-renderer"]:
            print(f"- catalog_path: {workdir}/catalog.sqlite")
            print(f"- workdir: {workdir}")
            print(f"")
            module = agent.skill_name.replace("pega-", "").replace("-", "_")
            if module == "hierarchy_mapper":
                module = "hierarchy"
            elif module == "flow_analyzer": 
                module = "flow"
            print(f"Call: pega_re.{module}.{'build' if module == 'hierarchy' else 'analyse' if module == 'flow' else 'render_all'}(catalog_path, workdir)")
        elif agent.skill_name == "pega-task-extractor":
            print(f"- catalog_path: {workdir}/catalog.sqlite")
            print(f"- workdir: {workdir}")
            print(f"")
            print(f"Call: pega_re.tasks.extract(catalog_path, workdir)")
        else:  # doc-synthesizer
            print(f"- catalog_path: {workdir}/catalog.sqlite")
            print(f"- workdir: {workdir}")
            print(f"- app_name: {app_name}")
            print(f"")
            print(f"Call: pega_re.docgen.synthesize(catalog_path, workdir, app_name)")
        
        print(f"```\n")
        print(f"**Wait for this step to complete before proceeding to Step {i+1}.**")
        print(f"Expected output: Success message + file paths created.")
        print("-" * 60 + "\n")
    
    print("### After All Steps Complete")
    print("Your key deliverables will be in:")
    print(f"- 📋 **Program Documentation**: {workdir}/program_doc.html")
    print(f"- 📊 **Task Ledger**: {workdir}/task_ledger.html") 
    print(f"- 📄 **Executive Summary**: {workdir}/executive_summary.md")
    print(f"- 🖼️  **UI Catalog**: {workdir}/ui/index.html")
    print(f"- 🌳 **Hierarchy**: {workdir}/hierarchy.html")
    print(f"")
    print(f"### Integration with Your Project")
    print(f"Each HTML file can be:")
    print(f"- 📎 Linked from Confluence pages")
    print(f"- 📧 Attached to steering committee emails") 
    print(f"- 📊 Embedded in PowerPoint presentations")
    print(f"- 🗂️  Stored in SharePoint document libraries")


# CLI for agent testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PegaRE Agent Testing")
    parser.add_argument("command", choices=["list-skills", "generate-copilot-workflow", "test-agent"])
    parser.add_argument("--input-dir", help="Input directory (for copilot workflow)")
    parser.add_argument("--workdir", default="./test_output", help="Working directory")
    parser.add_argument("--app-name", default="Test App", help="Application name")
    parser.add_argument("--agent", help="Agent name to test")
    
    args = parser.parse_args()
    
    suite = PegaREAgentSuite()
    
    if args.command == "list-skills":
        print("Available PegaRE agents and their skill files:")
        for agent in suite.get_all_agents():
            print(f"  {agent.skill_name:<25} → {agent.skill_file}")
    
    elif args.command == "generate-copilot-workflow":
        if not args.input_dir:
            print("Error: --input-dir required for copilot workflow")
            exit(1)
        create_copilot_chat_workflow(suite, args.input_dir, args.workdir, args.app_name)
        print("\n✅ GitHub Copilot workflow generated.")
        print("📋 Follow the step-by-step prompts above in GitHub Copilot Chat.")
        print("💡 Each step builds on the previous - wait for completion before proceeding.")
    
    elif args.command == "test-agent":
        if not args.agent:
            print("Error: --agent required for testing")
            exit(1)
        
        agent = getattr(suite, args.agent.replace("-", "_"), None)
        if not agent:
            print(f"Error: Unknown agent '{args.agent}'")
            exit(1)
        
        print(f"Testing agent: {agent.skill_name}")
        print(f"Skill file: {agent.skill_file}")
        print(f"Skill exists: {agent.skill_file.exists()}")
        print(f"Skill content length: {len(agent.skill_content)} chars")
