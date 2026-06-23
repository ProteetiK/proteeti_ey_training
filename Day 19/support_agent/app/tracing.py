import json
import time
import uuid


def create_trace():

    return uuid.uuid4().hex


def trace(
    trace_id,
    event,
    payload=None
):

    payload = payload or {}

    record = {
        "trace_id": trace_id,
        "event": event,
        "payload": payload,
        "timestamp": round(
            time.time(),
            3
        )
    }

    print(
        json.dumps(
            record,
            indent=None
        )
    )