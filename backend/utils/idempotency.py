"""Idempotency-key support for mutating endpoints (signing, payments).

Usage pattern in a service method:
    from utils.idempotency import idempotency_guard

    cached = idempotency_guard(idempotency_key, endpoint="/signing/sign", user_id=user_id)
    if cached is not None:
        return cached          # return the previously stored response

    ... do the real work ...
    result = {...}

    store_idempotency_result(idempotency_key, result)
    return result
"""
import json
import datetime
import db as _db

# Keys are valid for 24 hours — long enough to survive any reasonable retry window.
_TTL_HOURS = 24


def idempotency_guard(key: str, endpoint: str, user_id: str) -> dict | None:
    """Check whether this idempotency key has been seen before.

    Returns the cached response dict if the key already exists and belongs to
    the same (endpoint, user_id) combination, so the caller can return it
    immediately without re-executing the mutation.

    Returns None if the key is new, meaning the caller should proceed normally.

    Raises ValueError if the key exists but was issued by a different user or
    endpoint — which indicates a key-reuse attack.
    """
    if not key:
        return None  # no key supplied → fall through (no protection)

    rows = _db.query(
        "SELECT user_id, endpoint, response FROM idempotency_keys WHERE id = %s",
        (key,),
    )
    if not rows:
        return None  # first time we've seen this key

    row = rows[0]
    if row["user_id"] != user_id or row["endpoint"] != endpoint:
        raise ValueError(
            "Idempotency key reuse: the supplied key was issued for a different "
            f"user or endpoint. Expected user={row['user_id']!r} endpoint={row['endpoint']!r}."
        )
    # Return cached response
    try:
        return json.loads(row["response"])
    except Exception:
        return {"status": "already_processed"}


def store_idempotency_result(key: str, endpoint: str, user_id: str, result: dict) -> None:
    """Persist the result of a successful mutation under the given idempotency key."""
    if not key:
        return
    expires_at = (
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=_TTL_HOURS)
    ).isoformat()
    _db.execute(
        """
        INSERT INTO idempotency_keys (id, endpoint, user_id, response, expires_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """,
        (key, endpoint, user_id, json.dumps(result), expires_at),
    )
