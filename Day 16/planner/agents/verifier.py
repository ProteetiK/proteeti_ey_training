import json
from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm import llm

def verifier(state):

    if state["iterations"] >= 3:
        return {
            **state,
            "approved": True
        }

    results = "\n".join(state["results"])

    messages = [
        SystemMessage(
            content="""
Evaluate result quality.

Return JSON:
{
 "score":0.9,
 "approved":true,
 "critique":"..."
}
"""
        ),
        HumanMessage(
            content=f"""
Goal:
{state['goal']}

Results:
{results}
"""
        )
    ]

    raw = llm.invoke(messages).content

    try:
        verdict = json.loads(raw)

        return {
            **state,
            "approved": verdict["approved"],
            "critique": verdict["critique"]
        }

    except:

        return {
            **state,
            "approved": False,
            "critique": raw
        }