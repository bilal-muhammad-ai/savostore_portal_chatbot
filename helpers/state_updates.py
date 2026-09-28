"""Apply AgentState mutations from agent turns and tool calls."""

from __future__ import annotations

from typing import Any

from helpers.order_progress import sync_step
from models.agentState import AgentState


def _message_type(message: Any) -> str:
    return getattr(message, "type", None) or message.__class__.__name__


def _tool_call_id(call: Any) -> str | None:
    if isinstance(call, dict):
        return call.get("id")
    return getattr(call, "id", None)


def _tool_call_name(call: Any) -> str | None:
    if isinstance(call, dict):
        return call.get("name")
    return getattr(call, "name", None)


def _tool_call_args(call: Any) -> dict[str, Any]:
    if isinstance(call, dict):
        args = call.get("args") or call.get("arguments") or {}
    else:
        args = getattr(call, "args", None) or getattr(call, "arguments", None) or {}
    return dict(args) if isinstance(args, dict) else {}


def _is_tool_message(message: Any) -> bool:
    msg_type = _message_type(message)
    return msg_type in ("tool", "ToolMessage") or message.__class__.__name__ == "ToolMessage"


def _is_success_result(result: str) -> bool:
    text = (result or "").strip()
    if not text:
        return False
    lower = text.lower()
    return not (lower.startswith("invalid") or lower.startswith("error"))


def extract_tool_calls(result_messages: list[Any]) -> list[dict[str, Any]]:
    """Pair AI tool_calls with ToolMessage results into {name, args, result} entries."""
    calls_by_id: dict[str, dict[str, Any]] = {}
    ordered: list[dict[str, Any]] = []

    for message in result_messages:
        for call in getattr(message, "tool_calls", None) or []:
            name = _tool_call_name(call)
            if not name:
                continue
            entry = {
                "id": _tool_call_id(call),
                "name": name,
                "args": _tool_call_args(call),
                "result": None,
            }
            ordered.append(entry)
            if entry["id"]:
                calls_by_id[entry["id"]] = entry

        if not _is_tool_message(message):
            continue

        result = getattr(message, "content", "")
        if not isinstance(result, str):
            result = str(result)

        tool_call_id = getattr(message, "tool_call_id", None)
        name = getattr(message, "name", None)

        if tool_call_id and tool_call_id in calls_by_id:
            calls_by_id[tool_call_id]["result"] = result
            if name and not calls_by_id[tool_call_id].get("name"):
                calls_by_id[tool_call_id]["name"] = name
            continue

        # Fallback: match first pending call with same name and no result
        for entry in ordered:
            if entry["result"] is None and (not name or entry["name"] == name):
                entry["result"] = result
                break

    return ordered


def extract_tool_names(result_messages: list[Any]) -> set[str]:
    """Collect tool names from agent result messages."""
    return {c["name"] for c in extract_tool_calls(result_messages) if c.get("name")}


def apply_tool_effects(
    state: AgentState,
    tool_calls: list[dict[str, Any]] | set[str],
) -> AgentState:
    """Update OrderDraft from successful setter tool calls, then sync step."""
    # Back-compat: if a set of names is passed, nothing to apply (needs args).
    if isinstance(tool_calls, set):
        return sync_step(state)

    for call in tool_calls:
        name = call.get("name")
        args = call.get("args") or {}
        result = call.get("result")
        if result is None or not _is_success_result(str(result)):
            continue

        if name == "set_agreement":
            state.order.agreement_accepted = bool(args.get("accepted"))
        elif name == "set_currency":
            currency_id = str(args.get("currency_id", "")).strip().upper()
            if currency_id:
                state.order.currency_id = currency_id
        elif name == "set_warehouse":
            warehouse_id = str(args.get("warehouse_id", "")).strip().upper()
            if warehouse_id:
                state.order.warehouse_id = warehouse_id
        elif name == "set_amazon_url":
            url = str(args.get("url", "")).strip()
            if url:
                state.order.amazon_url = url
        elif name == "set_item_name":
            item_name = str(args.get("name", "")).strip()
            if item_name:
                state.order.item_name = item_name
        elif name == "set_item_info":
            item_info = str(args.get("info", "")).strip()
            if item_info:
                state.order.item_info = item_info
        elif name == "set_item_quantity":
            quantity = args.get("quantity")
            try:
                quantity_int = int(quantity)
            except (TypeError, ValueError):
                continue
            if quantity_int >= 1:
                state.order.item_quantity = quantity_int
        elif name == "confirm_order":
            confirmed = bool(args.get("confirmed"))
            state.order.confirmed = confirmed if confirmed else False

    return sync_step(state)


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
