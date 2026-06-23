import json

from anthropic import Anthropic

from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from app.config import (
    LIVE,
    MODEL,
    ANTHROPIC_API_KEY
)

from app.router import route

from app.memory import (
    save_turn,
    load_context
)

from app.vector_store import (
    memory_context
)

from app.cache import (
    cache_key,
    get_cached,
    set_cached
)

from app.tools import (
    run_tool,
    run_worker
)

from app.tracing import (
    create_trace,
    trace
)

BASE_SYSTEM = """
You are a support and ordering agent.

ORDER FLOW:

1. check_inventory
2. create_order
3. send_confirmation

SUPPORT FLOW:

1. create_ticket

ESCALATION FLOW:

1. create_ticket
2. escalate_ticket

FAQ FLOW:

1. search_kb

Rules:

- Always use tools.
- Do not invent order ids.
- Do not invent ticket ids.
- Use tool results.
- Explain outcomes clearly.
"""

TOOLS = [
    {
        "name": "check_inventory",
        "description":
        "Check inventory for a SKU.",

        "input_schema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string"
                }
            },
            "required": ["sku"]
        }
    },

    {
        "name": "create_order",
        "description":
        "Create an order.",

        "input_schema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string"
                },
                "qty": {
                    "type": "integer"
                }
            },
            "required": [
                "sku",
                "qty"
            ]
        }
    },

    {
        "name": "send_confirmation",
        "description":
        "Queue confirmation email.",

        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string"
                },
                "order_id": {
                    "type": "integer"
                }
            },
            "required": [
                "to",
                "order_id"
            ]
        }
    },

    {
        "name": "search_kb",
        "description":
        "Search support knowledge base.",

        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string"
                }
            },
            "required": [
                "question"
            ]
        }
    },

    {
        "name": "create_ticket",
        "description":
        "Create support ticket.",

        "input_schema": {
            "type": "object",
            "properties": {
                "customer": {
                    "type": "string"
                },
                "issue": {
                    "type": "string"
                }
            },
            "required": [
                "customer",
                "issue"
            ]
        }
    },

    {
        "name": "get_ticket",
        "description":
        "Get ticket information.",

        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "integer"
                }
            },
            "required": [
                "ticket_id"
            ]
        }
    },

    {
        "name": "escalate_ticket",
        "description":
        "Escalate a ticket.",

        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "integer"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "ticket_id",
                "reason"
            ]
        }
    }
]

if LIVE:
    client = Anthropic(
        api_key=ANTHROPIC_API_KEY
    )
else:
    client = None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential()
)
def call_model(
    system,
    messages
):

    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        tools=TOOLS,
        messages=messages
    )

def offline_response(
    user_text
):

    text = user_text.lower()

    if "order" in text:

        inv, _ = run_tool(
            "check_inventory",
            {
                "sku": "MON-4"
            }
        )

        order, _ = run_tool(
            "create_order",
            {
                "sku": "MON-4",
                "qty": 1
            }
        )

        job, _ = run_tool(
            "send_confirmation",
            {
                "to": "demo@example.com",
                "order_id":
                order["order_id"]
            }
        )

        run_worker()

        return (
            f"Order "
            f"{order['order_id']} "
            f"created. "
            f"Email queued."
        )

    return (
        "Offline mode active. "
        "Configure API key "
        "for full tool calling."
    )

def agent(
    session_id,
    user_text,
    max_steps=8,
    verbose=True
):

    trace_id = create_trace()

    trace(
        trace_id,
        "agent_start",
        {
            "user_text":
            user_text
        }
    )

    if not LIVE:

        answer = offline_response(
            user_text
        )

        save_turn(
            session_id,
            "user",
            user_text
        )

        save_turn(
            session_id,
            "assistant",
            answer
        )

        return answer

        intent = route(
        user_text
    )

    trace(
        trace_id,
        "route",
        {
            "intent":
            intent
        }
    )

    history = load_context(
        session_id
    )

    recalled = memory_context(
        user_text
    )
    system = (
        BASE_SYSTEM
        + "\n\n"
        + f"Detected intent: {intent}\n\n"
        + "Relevant memories:\n"
        + recalled
    )
    messages = []

    for msg in history:

        messages.append(
            {
                "role":
                msg["role"],
                "content":
                msg["content"]
            }
        )

    messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    key = cache_key(
        system,
        messages
    )

    cached = get_cached(
        key
    )

    if cached:

        trace(
            trace_id,
            "cache_hit"
        )

        return cached

    for _ in range(max_steps):

        trace(
            trace_id,
            "model_call"
        )

        response = call_model(
            system,
            messages
        )
        if (
            response.stop_reason
            == "tool_use"
        ):

            messages.append(
                {
                    "role":
                    "assistant",

                    "content":
                    [
                        block.model_dump()
                        for block
                        in response.content
                    ]
                }
            )

            tool_results = []

            for block in response.content:

                if block.type != "tool_use":
                    continue

                trace(
                    trace_id,
                    "tool_start",
                    {
                        "tool":
                        block.name
                    }
                )

                output, is_error = (
                    run_tool(
                        block.name,
                        block.input
                    )
                )

                trace(
                    trace_id,
                    "tool_end",
                    {
                        "tool":
                        block.name,
                        "output":
                        output
                    }
                )

                tool_results.append(
                    {
                        "type":
                        "tool_result",

                        "tool_use_id":
                        block.id,

                        "content":
                        json.dumps(
                            output
                        ),

                        "is_error":
                        is_error
                    }
            messages.append(
                {
                    "role":
                    "user",

                    "content":
                    tool_results
                }
            )

            run_worker()

            continue
        answer = "".join(
            block.text
            for block
            in response.content
            if block.type == "text"
        )

        save_turn(
            session_id,
            "user",
            user_text
        )

        save_turn(
            session_id,
            "assistant",
            answer
        )

        set_cached(
            key,
            answer
        )

        trace(
            trace_id,
            "agent_end"
        )

        return answer
    return (
        "Maximum tool steps "
        "reached."
    )
