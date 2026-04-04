# PM Agent Suite

Six specialized AI agents + a Streamlit UI with roadmap and dependency visualization, built for program managers running modernization programs.

---

## Project Structure

```
pm_suite/
├── agents/
│   ├── __init__.py          # Package exports
│   ├── base_agent.py        # BaseAgent (subclass to create your own)
│   └── agents.py            # All six specialized agents
├── data/
│   └── roadmap.json         # Sample roadmap (replace with yours)
├── app.py                   # Streamlit UI — run this
├── roadmap_viz.py           # Gantt + dependency graph (importable)
├── requirements.txt
└── README.md
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Run the Streamlit app
streamlit run app.py
```

Or paste the API key directly in the sidebar when the app opens.

---

## Importing Agents into Any Project

```python
from agents import StatusSentinel, RiskRadar, StakeholderScribe
from agents import DecisionLogger, DependencyDetective, DeliveryCoach

# Instantiate
agent = StatusSentinel()

# Single turn
response = agent.chat("Give me a RAG status report for Program Alpha.")
print(response)

# Multi-turn (history is maintained automatically)
agent.chat("Focus on the data migration workstream.")
agent.chat("What are the top 3 risks to the go-live date?")

# Streaming output
agent.chat("Draft an executive summary.", stream=True)

# Reset conversation
agent.reset()
```

All agents have the same interface — just swap the class.

---

## Available Agents

| Agent | Purpose |
|---|---|
| `StatusSentinel` | RAG status, milestone tracking, executive health summaries |
| `RiskRadar` | RAID log entries, risk scoring, mitigation plans |
| `StakeholderScribe` | Steering updates, sponsor emails, escalation memos |
| `DecisionLogger` | Meeting minutes, action items, RACI matrices |
| `DependencyDetective` | Cross-program dependency mapping, blocker analysis |
| `DeliveryCoach` | Timeline recovery, replanning, capacity guidance |

---

## Creating a Custom Agent

```python
from agents import BaseAgent

class MyCustomAgent(BaseAgent):
    name = "Change Manager"
    description = "Handles change control and impact assessment."
    system_prompt = """You are a Change Manager agent...
    [your system prompt here]
    """

agent = MyCustomAgent()
agent.chat("What's the impact of delaying the API gateway by 2 weeks?")
```

---

## Roadmap Data Format

Edit `data/roadmap.json` to reflect your programs. The schema:

```json
{
  "programs": [
    {
      "id": "prog-alpha",
      "name": "Program Alpha — Core Platform",
      "color": "#1D9E75",
      "workstreams": [
        {
          "id": "ws-a1",
          "name": "Infrastructure",
          "milestones": [
            {
              "id": "m-a1-1",
              "name": "Architecture Review",
              "start": "2025-01-06",
              "end":   "2025-02-14",
              "status": "done",      // done | active | planned
              "rag":    "G"          // G | A | R
            }
          ]
        }
      ]
    }
  ],
  "dependencies": [
    {
      "id": "dep-01",
      "from_milestone": "m-a1-1",
      "to_milestone":   "m-b1-1",
      "type": "Finish-to-Start",    // Finish-to-Start | Start-to-Start | Finish-to-Finish
      "description": "Dependency description.",
      "rag": "A"
    }
  ]
}
```

You can also upload your own `roadmap.json` directly in the sidebar.

---

## Using Roadmap Visualizations Without the UI

```python
from roadmap_viz import load_roadmap, build_gantt, build_dependency_graph

data = load_roadmap("data/roadmap.json")

# Gantt chart
fig = build_gantt(data)
fig.show()

# Filtered by one program
fig = build_gantt(data, filter_program="prog-alpha")

# Dependency network (only Red/critical)
fig = build_dependency_graph(data, filter_rag="R")
fig.show()
```

---

## UI Overview

The Streamlit app has three views:

- **Agents** — Chat with any of the six agents. Conversation history is kept per agent per session.
- **Roadmap** — Interactive Gantt chart with RAG colouring, today marker, and milestone metrics.
- **Dependencies** — Network graph of cross-program dependencies + filterable dependency register table.
