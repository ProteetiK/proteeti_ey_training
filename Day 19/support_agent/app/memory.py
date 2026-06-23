import fakeredis
import json
import time

memory = fakeredis.FakeStrictRedis()


def save_turn(session_id: str, role: str, content: str):

    memory.rpush(
        f"chat:{session_id}",
        json.dumps(
            {
                "role": role,
                "content": content,
                "ts": time.time()
            }
        )
    )


def load_context(
    session_id: str,
    limit: int = 10
):

    rows = memory.lrange(
        f"chat:{session_id}",
        -limit,
        -1
    )

    result = []

    for row in rows:
        result.append(
            json.loads(
                row.decode()
            )
        )

    return result


def clear_session(
    session_id: str
):
    memory.delete(
        f"chat:{session_id}"
    )