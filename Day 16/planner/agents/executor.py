from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from utils.llm import llm

search = DuckDuckGoSearchRun()

def executor(state):

    results = []

    for task in state["tasks"]:

        search_result = ""

        try:
            search_result = search.run(task)
        except:
            pass

        messages = [
            SystemMessage(
                content="Complete task thoroughly."
            ),
            HumanMessage(
                content=f"""
Task:
{task}

Search:
{search_result}
"""
            )
        ]

        result = llm.invoke(messages).content
        results.append(result)

    return {
        **state,
        "results": results,
        "iterations": state["iterations"] + 1
    }