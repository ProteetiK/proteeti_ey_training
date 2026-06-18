import json
from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm import llm

def planner(state):

    messages = [
        SystemMessage(
            content="""
You are a planning agent.

Break the goal into max 5 actionable tasks.

Return ONLY JSON array.
"""
        ),
        HumanMessage(content=state["goal"])
    ]

    response = llm.invoke(messages).content

    try:
        tasks = json.loads(response)
    except:
        tasks = [response]

    return {**state, "tasks": tasks}