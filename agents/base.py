"""Order agent entrypoint: intent-routed step handling."""

from agents.faq import get_faq_agent
from agents.router import classify_intent
from agents.steps import get_agent_for_step
from helpers.order_progress import (
    format_draft_for_user,
    format_progress_context,
    resume_prompt,
    sync_step,
)
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

_EDIT_STUB = (
    "Editing order details mid-flow is coming soon. "
    "For now, let's keep building your order."
)


def _handle_continue(state: AgentState, query: str) -> tuple[str, AgentState]:
    progress = format_progress_context(state)
    invoke_messages = [
        {"role": "system", "content": progress},
        *state.messages,
        {"role": "user", "content": query},
    ]
    agent = get_agent_for_step(state.step)
    result = agent.invoke({"messages": invoke_messages})
    last = result["messages"][-1]
    reply = last.content if isinstance(last.content, str) else str(last.content)
    tool_calls = extract_tool_calls(result["messages"])
    state = apply_tool_effects(state, tool_calls)
    return reply, state


def _handle_faq(query: str) -> str:
    agent = get_faq_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    last = result["messages"][-1]
    return last.content if isinstance(last.content, str) else str(last.content)


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

    intent = classify_intent(request.query, state)

    if intent == "show_draft":
        reply = f"{format_draft_for_user(state)}\n\n{resume_prompt(state)}"
    elif intent == "faq":
        reply = f"{_handle_faq(request.query)}\n\n{resume_prompt(state)}"
    elif intent == "edit":
        reply = f"{_EDIT_STUB}\n\n{resume_prompt(state)}"
    else:
        reply, state = _handle_continue(state, request.query)

    state = append_and_trim_messages(state, request.query, reply)
    save_state(state)
    return reply
