import fakeredis
import hashlib
import json

cache = fakeredis.FakeStrictRedis()


def cache_key(
    system,
    messages
):

    payload = json.dumps(
        {
            "system": system,
            "messages": messages
        },
        sort_keys=True
    )

    return hashlib.sha256(
        payload.encode()
    ).hexdigest()


def get_cached(key):

    value = cache.get(
        f"prompt:{key}"
    )

    if not value:
        return None

    return json.loads(
        value.decode()
    )


def set_cached(
    key,
    response,
    ttl=3600
):

    cache.setex(
        f"prompt:{key}",
        ttl,
        json.dumps(response)
    )