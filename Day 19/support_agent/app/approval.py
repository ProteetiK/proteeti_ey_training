import fakeredis
import json
import uuid

r = fakeredis.FakeStrictRedis()

APPROVAL_REQUIRED = {
    "escalate_ticket"
}


def request_approval(
    tool_name,
    payload
):

    approval_id = uuid.uuid4().hex[:8]

    r.set(
        f"approval:{approval_id}",
        json.dumps(
            {
                "tool": tool_name,
                "payload": payload,
                "status": "pending"
            }
        )
    )

    return approval_id


def approval_gate(
    tool_name,
    payload
):

    if tool_name not in APPROVAL_REQUIRED:
        return None

    approval_id = request_approval(
        tool_name,
        payload
    )

    print("\n" + "=" * 60)
    print("HUMAN APPROVAL REQUIRED")
    print("Tool:", tool_name)
    print("Payload:", payload)
    print("Approval ID:", approval_id)

    answer = input(
        "Approve? (y/n): "
    ).strip().lower()

    if answer != "y":

        return {
            "error": "approval denied",
            "approval_id": approval_id
        }

    return None