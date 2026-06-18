import streamlit as st

from agents.workflow import build_graph
from utils.state import AgentState

st.set_page_config(
    page_title="Multi-Agent Planner",
    page_icon="",
    layout="wide"
)

st.title("Multi-Agent Research Planner")

st.markdown("""
Planner -> Executor -> Verifier
""")

goal = st.text_area(
    "Research Goal",
    placeholder="Research and summarize top AI trends in 2026"
)

run = st.button("Run Agents")

if run and goal:

    graph = build_graph(AgentState)

    state = {
        "goal": goal,
        "tasks": [],
        "results": [],
        "critique": "",
        "approved": False,
        "iterations": 0
    }

    with st.spinner("Agents working..."):

        result = graph.invoke(state)

    st.success("Workflow Complete")

    col1, col2 = st.columns([1,1])

    with col1:

        st.subheader("Planned Tasks")

        for i, task in enumerate(result["tasks"]):
            st.info(f"{i+1}. {task}")

    with col2:

        st.subheader("Verification")

        st.metric(
            "Iterations",
            result["iterations"]
        )

        st.write(
            "Approved:",
            result["approved"]
        )

        st.write(
            "Critique:",
            result["critique"]
        )

    st.subheader("Results")

    for i, res in enumerate(result["results"]):

        with st.expander(
            f"Task {i+1}"
        ):
            st.write(res)