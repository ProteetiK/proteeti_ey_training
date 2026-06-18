from langgraph.graph import StateGraph, END

from agents.planner import planner
from agents.executor import executor
from agents.verifier import verifier

def route(state):
    return "end" if state["approved"] else "executor"

def build_graph(state_schema):

    graph = StateGraph(state_schema)

    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("verifier", verifier)

    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "verifier")

    graph.add_conditional_edges(
        "verifier",
        route,
        {
            "end": END,
            "executor": "executor"
        }
    )

    graph.set_entry_point("planner")

    return graph.compile()