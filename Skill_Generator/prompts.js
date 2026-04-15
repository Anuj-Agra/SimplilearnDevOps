/* ══════════════════════════════════════════════════════════════════════════════
   SkillForge — prompts.js
   All prompt templates live here. Edit these to customize generation behavior.
   ══════════════════════════════════════════════════════════════════════════════ */

/**
 * Example problem statements for quick-start buttons.
 * Add/remove/edit these freely.
 */
const EXAMPLES = [
  {
    title: "Code Review Pipeline",
    text: "Build an automated code review system that analyzes pull requests for security vulnerabilities, code quality issues, and adherence to team coding standards. It should generate detailed reports with severity levels and suggested fixes, integrate with GitHub webhooks, and support custom rule definitions via YAML config files."
  },
  {
    title: "Data Pipeline Monitor",
    text: "Create a data pipeline monitoring agent that tracks ETL job health across Airflow DAGs, detects anomalies in data quality metrics (row counts, null rates, schema drift), sends Slack alerts on failures with root-cause hints, and generates daily summary reports with trend analysis and SLA compliance tracking."
  },
  {
    title: "API Doc Generator",
    text: "Build a tool that scans a Java/Spring Boot codebase's REST API endpoints, extracts request/response schemas from controller annotations and DTOs, and generates comprehensive OpenAPI 3.0 documentation with usage examples, error codes, authentication requirements, and rate limiting details."
  }
];


/**
 * Analysis prompt: decomposes a problem statement into typed components.
 * The LLM should return ONLY a JSON object.
 */
const ANALYSIS_PROMPT_TEMPLATE = `You are SkillForge — an expert AI architect that designs skills, agents, and automation scripts.

Given the following problem statement, analyze it and respond ONLY with a valid JSON object (no markdown fences, no explanation, just raw JSON):

{
  "title": "Short project title",
  "summary": "2-sentence summary of what needs to be built",
  "components": [
    {
      "type": "skill | agent | script",
      "name": "Component name",
      "purpose": "What this component does"
    }
  ],
  "complexity": "low | medium | high",
  "tags": ["tag1", "tag2"]
}

Rules:
- "skill" = a reusable SKILL.md instruction file (when-to-trigger, workflow steps, best practices)
- "agent" = a system prompt for an AI agent (role, capabilities, guardrails, examples)
- "script" = a production-ready Python CLI script (argparse, logging, error handling)
- Most problems need 2-5 components. Think about what combination gives the best architecture.
- Be specific in naming and purpose — avoid generic names.

PROBLEM STATEMENT:
`;


/**
 * Per-type generation instructions.
 * Each key matches a component type ("skill" | "agent" | "script").
 * Edit these to change the output structure or quality bar.
 */
const TYPE_INSTRUCTIONS = {

  skill: `Generate a complete SKILL.md file with this exact structure:

---
name: <skill-name-kebab-case>
description: <one-line description of when to trigger this skill>
---

# <Skill Title>

## Overview
What this skill does, who uses it, and when to trigger it.

## Inputs
What the skill expects from the user or system — files, parameters, context.

## Workflow
Step-by-step numbered instructions the AI should follow when this skill is triggered:
1. First step...
2. Second step...
(Be thorough — 5-15 steps typically)

## Output Format
Exact deliverables this skill produces (file types, structure, naming conventions).

## Quality Checks
- Validation rules to apply before finalizing output
- Edge cases to handle
- Common mistakes to avoid

## Best Practices
- Performance tips
- Integration guidance
- Dos and don'ts

## Examples
### Example 1: <scenario>
Input: ...
Expected behavior: ...
Output: ...

### Example 2: <scenario>
Input: ...
Expected behavior: ...
Output: ...

Make it thorough, actionable, and production-ready. A developer should be able to follow this blindly and produce correct output.`,


  agent: `Generate a complete system prompt for an AI agent with this structure:

<role>
You are [Agent Name] — [one-line identity and mission].
</role>

<capabilities>
- Capability 1: detailed description
- Capability 2: detailed description
- Capability 3: detailed description
(List 4-8 capabilities)
</capabilities>

<instructions>
## Core Behavior
How the agent should think, reason, and approach problems.
Include chain-of-thought reasoning instructions where appropriate.

## Input Handling
How to parse, validate, and interpret user inputs.
Include expected input formats with examples.

## Processing Pipeline
Step-by-step reasoning process the agent should follow:
1. First...
2. Then...
(5-10 steps, be explicit)

## Output Format
Exact format of responses. Include a concrete template or example showing the structure.

## Guardrails
- What the agent must NEVER do
- Error handling procedures
- Boundary conditions and scope limits
- When to escalate or ask for clarification
- Security and safety considerations

## Few-Shot Examples

### Example 1
**User:** <realistic input>
**Agent:** <full realistic response>

### Example 2
**User:** <realistic input>
**Agent:** <full realistic response>

### Example 3 (edge case)
**User:** <tricky or ambiguous input>
**Agent:** <correct handling with explanation>
</instructions>

Make it specific, well-bounded, and robust. The agent should know exactly what it can and cannot do.`,


  script: `Generate a complete, production-ready Python script with ALL of these requirements:

1. Module docstring with:
   - Description of what the script does
   - Usage examples (2-3 command-line invocations)
   - Requirements list (pip install ...)

2. A "# Requirements: package1, package2, ..." comment at the top

3. Proper imports organized in sections:
   # Standard library
   # Third-party
   # Local

4. Type hints on ALL function signatures and return types

5. Docstrings on ALL functions and classes (Google style)

6. argparse CLI with:
   - Meaningful --help descriptions for every argument
   - Logical argument groups if needed
   - Default values documented

7. Logging setup with:
   - logging.basicConfig with format including timestamp
   - --verbose / -v flag to toggle DEBUG level
   - Use logger.info/warning/error, never print()

8. Error handling:
   - try/except with specific exception types
   - Meaningful error messages that help debugging
   - Graceful degradation where possible

9. Clean architecture:
   - Functions/classes with single responsibilities
   - No global mutable state
   - Configuration via dataclass or dict, not scattered constants

10. if __name__ == "__main__": block calling main()

11. A --dry-run or --mock flag that runs without side effects for testing

12. Exit codes: 0 = success, 1 = error, 2 = invalid input

The script should be immediately runnable. Include realistic mock/sample data so it works out of the box in mock mode.`
};


/**
 * Assembles the full generation prompt for a component.
 *
 * @param {Object} comp        - The component {type, name, purpose}
 * @param {Object} blueprint   - The full blueprint {title, summary, ...}
 * @param {string} problemText - The original problem statement
 * @returns {string} Complete prompt ready to paste into Copilot Chat
 */
function buildGenerationPrompt(comp, blueprint, problemText) {
  return `You are SkillForge Generator. Generate a production-quality ${comp.type} component.

PROJECT CONTEXT:
Title: ${blueprint.title}
Summary: ${blueprint.summary}
Full Problem: ${problemText}

COMPONENT TO GENERATE:
- Name: ${comp.name}
- Type: ${comp.type}
- Purpose: ${comp.purpose}

INSTRUCTIONS:
${TYPE_INSTRUCTIONS[comp.type]}

Respond ONLY with the raw file content. No markdown code fences wrapping it. No preamble or explanation. Just the content that goes directly into the file.`;
}
