"""
PM Agent Suite — Streamlit UI
Run with:  streamlit run app.py
"""

import os
import json
import streamlit as st
import pandas as pd
from pathlib import Path

from agents import (
    StatusSentinel, RiskRadar, StakeholderScribe,
    DecisionLogger, DependencyDetective, DeliveryCoach,
)
from roadmap_viz import (
    load_roadmap, build_gantt, build_dependency_graph, build_dependency_table,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PM Agent Suite",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #F8F8F6; }
.agent-card {
    background: white; border: 1px solid #E8E8E4;
    border-radius: 10px; padding: 14px 16px; margin-bottom: 8px;
}
.rag-G { color: #1D9E75; font-weight: 600; }
.rag-A { color: #BA7517; font-weight: 600; }
.rag-R { color: #E24B4A; font-weight: 600; }
.dep-chip {
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: 12px; font-weight: 500; margin: 2px;
}
.msg-user   { background: #EEF5FF; border-radius: 10px; padding: 10px 14px; margin: 6px 0; }
.msg-agent  { background: #F5F5F0; border-radius: 10px; padding: 10px 14px; margin: 6px 0; }
</style>
""", unsafe_allow_html=True)

# ── Agent registry ─────────────────────────────────────────────────────────────
AGENT_REGISTRY = {
    "Status Sentinel":      {"cls": StatusSentinel,      "icon": "◎", "color": "#1D9E75"},
    "Risk Radar":           {"cls": RiskRadar,           "icon": "⚑", "color": "#D85A30"},
    "Stakeholder Scribe":   {"cls": StakeholderScribe,   "icon": "✉", "color": "#185FA5"},
    "Decision Logger":      {"cls": DecisionLogger,      "icon": "✓", "color": "#639922"},
    "Dependency Detective": {"cls": DependencyDetective, "icon": "⟷", "color": "#BA7517"},
    "Delivery Coach":       {"cls": DeliveryCoach,       "icon": "▲", "color": "#7F77DD"},
}

SUGGESTIONS = {
    "Status Sentinel":      ["Give me a RAG status report for both programs",
                             "What milestones are at risk this quarter?"],
    "Risk Radar":           ["Log a risk: vendor delay on data migration Phase 2",
                             "Score and prioritise my top 5 risks"],
    "Stakeholder Scribe":   ["Draft a steering committee update for this week",
                             "Write a sponsor email about our go-live delay"],
    "Decision Logger":      ["Convert these meeting notes into structured minutes",
                             "Build a RACI for our upcoming UAT phase"],
    "Dependency Detective": ["Map critical dependencies between my two programs",
                             "Which blockers are on the critical path right now?"],
    "Delivery Coach":       ["We're 3 weeks behind on stream A — how do we recover?",
                             "Build a recovery plan narrative for leadership"],
}

# ── Session state ─────────────────────────────────────────────────────────────
if "active_agent_name" not in st.session_state:
    st.session_state.active_agent_name = "Status Sentinel"
if "agents" not in st.session_state:
    st.session_state.agents = {}
if "roadmap_data" not in st.session_state:
    st.session_state.roadmap_data = load_roadmap()
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Agents"


def get_agent(name: str):
    if name not in st.session_state.agents:
        cls = AGENT_REGISTRY[name]["cls"]
        st.session_state.agents[name] = cls()
    return st.session_state.agents[name]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ◎ PM Agent Suite")
    st.markdown("---")

    nav = st.radio("View", ["🤖  Agents", "📅  Roadmap", "🔗  Dependencies"], label_visibility="collapsed")
    st.session_state.active_tab = nav.split("  ")[1]

    if st.session_state.active_tab == "Agents":
        st.markdown("### Agents")
        for name, meta in AGENT_REGISTRY.items():
            selected = name == st.session_state.active_agent_name
            border = f"2px solid {meta['color']}" if selected else "1px solid #E8E8E4"
            if st.button(
                f"{meta['icon']}  {name}",
                key=f"btn_{name}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.active_agent_name = name

    st.markdown("---")

    # API key input
    api_key = st.text_input("Anthropic API Key", type="password",
                             value=os.environ.get("ANTHROPIC_API_KEY", ""),
                             help="Set ANTHROPIC_API_KEY env var or paste here.")
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    # Roadmap data upload
    st.markdown("### Roadmap Data")
    uploaded = st.file_uploader("Upload roadmap.json", type="json")
    if uploaded:
        st.session_state.roadmap_data = json.load(uploaded)
        st.success("Roadmap loaded!")

    if st.button("↺  Reset All Chats", use_container_width=True):
        st.session_state.agents = {}
        st.rerun()


# ── AGENTS TAB ────────────────────────────────────────────────────────────────
if st.session_state.active_tab == "Agents":
    name = st.session_state.active_agent_name
    meta = AGENT_REGISTRY[name]
    agent = get_agent(name)

    col_icon, col_title = st.columns([0.04, 0.96])
    col_icon.markdown(f"<span style='font-size:26px'>{meta['icon']}</span>", unsafe_allow_html=True)
    col_title.markdown(f"### {name}")

    cls = meta["cls"]
    st.caption(cls.description)
    st.markdown("---")

    # Conversation history
    history = agent.get_history()
    for msg in history:
        role_class = "msg-user" if msg["role"] == "user" else "msg-agent"
        label = "You" if msg["role"] == "user" else name
        st.markdown(
            f'<div class="{role_class}"><b>{label}</b><br>{msg["content"]}</div>',
            unsafe_allow_html=True,
        )

    # Suggestion chips
    if not history:
        st.markdown("**Quick starts:**")
        cols = st.columns(2)
        for i, sugg in enumerate(SUGGESTIONS.get(name, [])):
            if cols[i % 2].button(sugg, key=f"sugg_{name}_{i}"):
                with st.spinner(f"{name} is thinking…"):
                    agent.chat(sugg)
                st.rerun()

    # Chat input
    with st.form(key=f"chat_form_{name}", clear_on_submit=True):
        user_input = st.text_area("Your message", height=80, placeholder=f"Ask {name}…", label_visibility="collapsed")
        submitted = st.form_submit_button("Send →", use_container_width=False)

    if submitted and user_input.strip():
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Please set your Anthropic API key in the sidebar.")
        else:
            with st.spinner(f"{name} is thinking…"):
                agent.chat(user_input.strip())
            st.rerun()

    if history:
        if st.button("Clear conversation", key=f"clear_{name}"):
            agent.reset()
            st.rerun()


# ── ROADMAP TAB ───────────────────────────────────────────────────────────────
elif st.session_state.active_tab == "Roadmap":
    st.markdown("### Program Roadmap")

    data = st.session_state.roadmap_data

    col_filter, col_space = st.columns([0.3, 0.7])
    prog_options = ["All"] + [p["id"] for p in data["programs"]]
    prog_labels  = {"All": "All Programs"} | {p["id"]: p["name"] for p in data["programs"]}
    prog_choice = col_filter.selectbox(
        "Filter by program",
        options=prog_options,
        format_func=lambda x: prog_labels.get(x, x),
    )

    fig = build_gantt(data, filter_program=prog_choice)
    st.plotly_chart(fig, use_container_width=True)

    # Summary metrics
    from roadmap_viz import _flat_milestones
    all_m = _flat_milestones(data)
    if prog_choice != "All":
        all_m = [m for m in all_m if m["program_id"] == prog_choice]

    total  = len(all_m)
    done   = sum(1 for m in all_m if m["status"] == "done")
    active = sum(1 for m in all_m if m["status"] == "active")
    rag_r  = sum(1 for m in all_m if m["rag"] == "R")
    rag_a  = sum(1 for m in all_m if m["rag"] == "A")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Milestones", total)
    m2.metric("Completed", done)
    m3.metric("In Progress", active)
    m4.metric("🔴 Red", rag_r)
    m5.metric("🟡 Amber", rag_a)


# ── DEPENDENCIES TAB ──────────────────────────────────────────────────────────
elif st.session_state.active_tab == "Dependencies":
    st.markdown("### Dependency Network")

    data = st.session_state.roadmap_data

    col_filter, _ = st.columns([0.25, 0.75])
    rag_filter = col_filter.selectbox(
        "Filter by RAG",
        options=["All", "R", "A", "G"],
        format_func=lambda x: {"All": "All", "R": "🔴 Red", "A": "🟡 Amber", "G": "🟢 Green"}.get(x, x),
    )

    fig = build_dependency_graph(data, filter_rag=rag_filter)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Dependency Register")
    rows = build_dependency_table(data)
    if rag_filter != "All":
        rows = [r for r in rows if r["RAG"] == rag_filter]

    df = pd.DataFrame(rows)

    def color_rag(val):
        colors = {"R": "background-color:#FCEBEB; color:#A32D2D",
                  "A": "background-color:#FAEEDA; color:#854F0B",
                  "G": "background-color:#EAF3DE; color:#3B6D11"}
        return colors.get(val, "")

    st.dataframe(
        df.style.applymap(color_rag, subset=["RAG"]),
        use_container_width=True,
        hide_index=True,
    )
