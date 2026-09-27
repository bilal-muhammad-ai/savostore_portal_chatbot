"""Apply AgentState mutations from agent turns and tool calls."""

from __future__ import annotations

from typing import Any

from models.agentState import AgentState


def extract_tool_names(result_messages: list[Any]) -> set[str]:
    """Collect tool names from agent result messages (AIMessage tool_calls / ToolMessage)."""
    names: set[str] = set()
    for message in result_messages:
        tool_calls = getattr(message, "tool_calls", None) or []
        for call in tool_calls:
            if isinstance(call, dict):
                name = call.get("name")
            else:
                name = getattr(call, "name", None)
            if name:
                names.add(name)

        name = getattr(message, "name", None)
        # ToolMessage has name set to the tool that was run
        msg_type = getattr(message, "type", None) or message.__class__.__name__
        if name and (
            msg_type == "tool"
            or msg_type == "ToolMessage"
            or message.__class__.__name__ == "ToolMessage"
        ):
            names.add(name)

    return names


def apply_tool_effects(state: AgentState, tool_names: set[str]) -> AgentState:
    """Update order draft / step based on tools the agent called this turn."""
    if "get_currency_list" in tool_names:
        state.order.agreement_accepted = True
        state.step = "currency"
    return state


def append_and_trim_messages(
    state: AgentState,
    user_query: str,
    assistant_reply: str,
    max_messages: int = 20,
) -> AgentState:
    """Append the latest user/assistant turn and keep only the last N messages."""
    state.messages.append({"role": "user", "content": user_query})
    state.messages.append({"role": "assistant", "content": assistant_reply})
    state.messages = state.messages[-max_messages:]
    return state
