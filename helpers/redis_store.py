"""Redis-backed session store for order agent state."""

import redis

from config import ORDER_SESSION_TTL_SECONDS, REDIS_URL
from models.agentState import AgentState

_KEY_PREFIX = "savostore:order:"

_client = redis.from_url(REDIS_URL, decode_responses=True)


def _key(session_id: str) -> str:
    return f"{_KEY_PREFIX}{session_id}"


def get_state(session_id: str) -> AgentState | None:
    raw = _client.get(_key(session_id))
    if raw is None:
        return None
    return AgentState.model_validate_json(raw)


def save_state(state: AgentState) -> None:
    _client.set(
        _key(state.session_id),
        state.model_dump_json(),
        ex=ORDER_SESSION_TTL_SECONDS,
    )


def delete_state(session_id: str) -> None:
    _client.delete(_key(session_id))
