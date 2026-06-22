import os
import io
import operator
from typing import Annotated, List, TypedDict, Literal

import streamlit as st
from dotenv import load_dotenv

from pydantic import BaseModel, Field

from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# ============================================================
# CONFIG
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY")
    st.stop()

if not TAVILY_API_KEY:
    st.error("Missing TAVILY_API_KEY")
    st.stop()

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🧠",
    layout="wide"
)

# ============================================================
# STATE
# ============================================================

class AgentState(TypedDict):
    task: str
    research_notes: Annotated[List[str], operator.add]
    draft: str
    next_node: str
    retry_count: int
    revision_feedback: str


class Router(BaseModel):
    """Supervisor routing decision"""

    next_worker: Literal[
        "researcher",
        "writer",
        "FINISH"
    ] = Field(description="Next node")

    instructions: str = Field(
        description="Instructions for worker"
    )

    is_critical: bool = Field(
        description="Whether human review is required"
    )


# ============================================================
# LLM + TOOLS
# ============================================================

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    api_key=GROQ_API_KEY,
)

search_tool = TavilySearchResults(
    k=3,
    tavily_api_key=TAVILY_API_KEY
)

# ============================================================
# AGENTS
# ============================================================

def researcher(state: AgentState):
    query = state["task"]

    results = search_tool.invoke(query)

    return {
        "research_notes": [str(results)],
        "retry_count": 0
    }


def writer(state: AgentState):
    context = "\n\n".join(state["research_notes"])

    prompt = f"""
    You are an expert technical writer.

    Task:
    {state['task']}

    Research:
    {context}

    Write a professional report with:

    - Executive Summary
    - Key Findings
    - Technical Analysis
    - Conclusion
    """

    response = llm.invoke(prompt)

    return {
        "draft": response.content
    }


def supervisor(state: AgentState):
    structured_llm = llm.with_structured_output(Router)

    prompt = f"""
    Task:
    {state['task']}

    Research Notes Count:
    {len(state['research_notes'])}

    Draft:
    {state['draft'][:500]}

    Routing Rules:

    - If no research exists -> researcher
    - If research exists but draft missing -> writer
    - If draft exists -> FINISH
    """

    decision = structured_llm.invoke(prompt)

    return {
        "next_node": decision.next_worker,
        "revision_feedback": decision.instructions,
    }

# ============================================================
# GRAPH
# ============================================================

@st.cache_resource
def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor)
    builder.add_node("researcher", researcher)
    builder.add_node("writer", writer)

    builder.set_entry_point("supervisor")

    builder.add_conditional_edges(
        "supervisor",
        lambda x: x["next_node"],
        {
            "researcher": "researcher",
            "writer": "writer",
            "FINISH": END,
        },
    )

    builder.add_edge("researcher", "supervisor")
    builder.add_edge("writer", "supervisor")

    memory = MemorySaver()

    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["writer"],
    )

    return graph


graph = build_graph()

# ============================================================
# SESSION STATE
# ============================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit-user"

if "paused" not in st.session_state:
    st.session_state.paused = False

if "draft" not in st.session_state:
    st.session_state.draft = ""

# ============================================================
# UI
# ============================================================

st.title("🧠 AI Research Agent")
st.caption("LangGraph + Groq + Tavily + Human Review")

task = st.text_area(
    "Research Task",
    value="Impact of LPU architecture on AI inference speeds",
    height=120,
)

col1, col2 = st.columns([1, 1])

# ============================================================
# START
# ============================================================

with col1:

    if st.button("🚀 Start Research", use_container_width=True):

        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id
            }
        }

        initial_input = {
            "task": task,
            "research_notes": [],
            "retry_count": 0,
            "draft": "",
        }

        progress_box = st.empty()

        with st.spinner("Running graph..."):

            for event in graph.stream(
                initial_input,
                config,
                stream_mode="values"
            ):

                if "next_node" in event:

                    progress_box.info(
                        f"Moving to: {event['next_node']}"
                    )

        snapshot = graph.get_state(config)

        if snapshot.next:

            st.session_state.paused = True

            st.success("Workflow paused for review.")

            st.session_state.feedback = snapshot.values.get(
                "revision_feedback",
                ""
            )

            st.session_state.notes = "\n\n".join(
                snapshot.values["research_notes"]
            )

# ============================================================
# HUMAN REVIEW
# ============================================================

if st.session_state.paused:

    st.divider()

    st.subheader("⏸ Human Review")

    st.info(
        st.session_state.get(
            "feedback",
            "Review research before writing."
        )
    )

    edited_notes = st.text_area(
        "Research Notes",
        value=st.session_state.notes,
        height=300,
    )

    if st.button(
        "✅ Approve & Continue",
        use_container_width=True
    ):

        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id
            }
        }

        snapshot = graph.get_state(config)

        snapshot.values["research_notes"] = [edited_notes]

        graph.update_state(
            config,
            snapshot.values
        )

        with st.spinner("Generating report..."):

            for event in graph.stream(
                None,
                config,
                stream_mode="values"
            ):

                if "draft" in event:
                    st.session_state.draft = event["draft"]

        st.session_state.paused = False
        st.rerun()

# ============================================================
# REPORT
# ============================================================

if st.session_state.draft:

    st.divider()

    st.subheader("📄 Final Report")

    st.markdown(st.session_state.draft)

    st.download_button(
        label="⬇ Download Report",
        data=st.session_state.draft,
        file_name="report.md",
        mime="text/markdown",
        use_container_width=True,
    )

# ============================================================
# GRAPH VISUALIZATION
# ============================================================

with col2:

    st.subheader("Graph Structure")

    try:
        png_bytes = graph.get_graph().draw_mermaid_png()

        st.image(
            png_bytes,
            use_container_width=True
        )

    except Exception:
        st.info(
            "Mermaid visualization unavailable in this environment."
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Built with LangGraph • Groq Llama 3.3 70B • Tavily Search"
)