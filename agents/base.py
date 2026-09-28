"""Order agent entrypoint: progress-driven step routing."""

from agents.steps import get_agent_for_step
from helpers.order_progress import format_progress_context, sync_step
from helpers.redis_store import get_state, save_state
from helpers.state_updates import (
    append_and_trim_messages,
    apply_tool_effects,
    extract_tool_calls,
)
from models.agentState import AgentState
from models.userQuery import UserQuery

_DONE_REPLY = (
    "Your order draft is already complete and confirmed. "
    "Start a new session if you need another order."
)


def run(request: UserQuery) -> str:
    state = get_state(request.session_id)
    if state is None:
        state = AgentState(
            session_id=request.session_id,
            user_id=request.user_id,
            messages=[],
            step="agreement",
        )

    state = sync_step(state)

    if state.step == "done":
        save_state(state)
        return _DONE_REPLY

    progress = format_progress_context(state)
    invoke_messages = [
        {"role": "system", "content": progress},
        *state.messages,
        {"role": "user", "content": request.query},
    ]

    agent = get_agent_for_step(state.step)
    result = agent.invoke({"messages": invoke_messages})
    last = result["messages"][-1]
    reply = last.content if isinstance(last.content, str) else str(last.content)

    state = append_and_trim_messages(state, request.query, reply)
    tool_calls = extract_tool_calls(result["messages"])
    state = apply_tool_effects(state, tool_calls)
    save_state(state)
    return reply
