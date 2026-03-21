# Getting Started

## Three ways to use the PEGA KYC Agent Hub

---

### Option A — Claude.ai interactive app (fastest, no setup)

1. Download `app/pega-kyc-agent-hub.jsx`
2. Go to [claude.ai](https://claude.ai)
3. Start a new conversation and attach the `.jsx` file, or open it as an Artifact
4. Select your agent, role, and hierarchy context in the app
5. Paste your PEGA JSON, BIN content, or description and click **Run**

Best for: Quick analysis, mixed teams, one-off deliverables.

---

### Option B — Claude.ai Projects (team use, persistent context)

Claude.ai Projects let you store system prompts and context files permanently, so every conversation with the agent already knows your client's PEGA hierarchy and KYC context.

**Setup per agent:**

1. In Claude.ai, go to **Projects** → **New Project**
2. Name it: `PEGA KYC — [Agent Name]` (e.g. `PEGA KYC — Flow Narrator`)
3. In **Project Instructions**, paste:
   - The full contents of `agents/01-flow-narrator/system-prompt.md`
   - Then paste the relevant skill files from `skills/`
   - Then paste your completed `hierarchy/L<n>-<tier>/context.md`
4. Add the role adapter (`skills/role-adapters/<role>.md`) for your primary audience
5. Save the Project — every new conversation in this Project starts with the full agent context

**Recommended Project setup for a team of 4:**

| Project | Agent | Primary audience |
|---------|-------|----------------|
| `KYC — Flow Narrator` | 01 | All team members |
| `KYC — BRD Writer` | 02 | Business Analyst, PO |
| `KYC — FRD Writer` | 03 | Business Analyst |
| `KYC — Jira Breakdown` | 04 | PO, Delivery Manager |
| `KYC — Acceptance Criteria` | 05 | QA, BA |
| `KYC — PEGA Expert` | 06 | PEGA Developer, Architect |

---

### Option C — Anthropic API (automated pipeline)

For teams building an automated documentation pipeline.

**System prompt assembly (Python example):**

```python
def build_system_prompt(agent_id: str, role_id: str, hierarchy_tier: int) -> str:
    """Assemble a complete agent system prompt from component files."""
    
    # Load agent base prompt
    with open(f"agents/{agent_id}/system-prompt.md") as f:
        agent_prompt = f.read()
    
    # Load agent config to find required skills
    with open(f"agents/{agent_id}/config.json") as f:
        config = json.load(f)
    
    # Load required skill files
    skills_content = []
    for skill_path in config["skills_required"]:
        with open(skill_path) as f:
            skills_content.append(f"## Skill: {skill_path}\n\n" + f.read())
    
    # Load hierarchy context if applicable
    hierarchy_content = ""
    if config.get("hierarchy_context_required") and hierarchy_tier:
        tier_map = {1: "L1-enterprise", 2: "L2-division", 3: "L3-application", 4: "L4-module"}
        tier_folder = tier_map.get(hierarchy_tier, "L3-application")
        with open(f"hierarchy/{tier_folder}/context.md") as f:
            hierarchy_content = f.read()
    
    # Load role adapter
    role_adapter = ""
    if config.get("role_adapter_required"):
        role_map = {"ba": "business-analyst", "po": "product-owner", "dev": "pega-developer", "qa": "qa-tester"}
        role_file = role_map.get(role_id, "business-analyst")
        with open(f"skills/role-adapters/{role_file}.md") as f:
            role_adapter = f.read()
    
    # Assemble
    parts = [agent_prompt]
    if skills_content:
        parts.append("\n\n---\n# Injected Skills\n\n" + "\n\n---\n\n".join(skills_content))
    if hierarchy_content:
        parts.append("\n\n---\n# Client PEGA Hierarchy Context\n\n" + hierarchy_content)
    if role_adapter:
        parts.append("\n\n---\n# Role Adapter\n\n" + role_adapter)
    
    return "\n".join(parts)


def call_agent(agent_id: str, role_id: str, hierarchy_tier: int, user_input: str) -> str:
    """Call a specific agent with assembled context."""
    import anthropic
    
    client = anthropic.Anthropic()
    system_prompt = build_system_prompt(agent_id, role_id, hierarchy_tier)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_input}]
    )
    
    return message.content[0].text


# Example: Run the Flow Narrator for a BA on the L4 work type
output = call_agent(
    agent_id="01-flow-narrator",
    role_id="ba",
    hierarchy_tier=4,
    user_input=open("examples/sample-inputs/flow-json-example.json").read()
)
print(output)
```

**Agent chaining example:**

```python
# Chain: JSON → Flow Narrative → BRD → Jira Breakdown
pega_json = open("examples/sample-inputs/flow-json-example.json").read()

# Step 1: Flow Narrator
flow_narrative = call_agent("01-flow-narrator", "ba", 4, pega_json)
print("✓ Flow narrative generated")

# Step 2: BRD Writer (uses flow narrative as input)
brd = call_agent("02-brd-writer", "ba", 3, flow_narrative)
print("✓ BRD generated")

# Step 3: FRD Writer (uses BRD + flow narrative)
frd_input = f"# Flow Narrative\n\n{flow_narrative}\n\n# Business Requirements Document\n\n{brd}"
frd = call_agent("03-frd-writer", "ba", 4, frd_input)
print("✓ FRD generated")

# Step 4: Jira Breakdown (uses FRD)
jira = call_agent("04-jira-breakdown", "po", 4, frd)
print("✓ Jira breakdown generated")

# Save outputs
for name, content in [("flow-narrative", flow_narrative), ("brd", brd), ("frd", frd), ("jira", jira)]:
    with open(f"output/{name}.md", "w") as f:
        f.write(content)
    print(f"✓ Saved output/{name}.md")
```

---

## Recommended first session (new team)

1. **Decode a flow** — Pick one PEGA flow JSON from your BIN export. Run it through Agent 01 (Flow Narrator) with role = BA. Share the output with your SME to validate.
2. **Generate your first BRD** — Feed the validated narrative into Agent 02. Use this as the basis for your first stakeholder workshop.
3. **Fill in the hierarchy files** — With your PEGA developer, complete `hierarchy/L3-application/context.md` and `hierarchy/L4-module/context.md` with your actual class names. This dramatically improves output quality for all agents.
4. **Run the full chain** — Process your most complex flow end-to-end: JSON → Narrative → BRD → FRD → Jira → Acceptance Criteria.

---

## Tips for best results

| Tip | Detail |
|-----|--------|
| More context = better output | Paste the full JSON, not just a summary. The agents read JSON field names directly. |
| Fill in hierarchy files | Class names in the context files mean agents use your client's actual rule names in outputs |
| Run the chain in order | Each agent's output is designed to be the next agent's input — don't skip steps |
| Use PEGA Expert for blockers | When you can't decode a BIN file or understand a rule, ask Agent 06 first |
| Validate with SMEs early | The Flow Narrator output is the best artefact to validate with a PEGA developer before generating BRD/FRD |
| Save your prompts in Projects | Use Claude.ai Projects to persist agent context so your team doesn't need to reassemble prompts each session |
