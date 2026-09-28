"""Derive next missing OrderDraft field and step routing."""

from __future__ import annotations

from models.agentState import AgentState, OrderDraft

# (field_name, user-facing prompt, step)
FIELD_ORDER: list[tuple[str, str, str]] = [
    ("agreement_accepted", "Confirm the shipping agreement (agree or decline)", "agreement"),
    ("currency_id", "Choose a currency (KES or USD)", "currency"),
    ("warehouse_id", "Choose a warehouse", "warehouse"),
    ("amazon_url", "Provide the Amazon product URL", "item"),
    ("item_name", "Provide the item name", "item"),
    ("item_info", "Provide brief item info / notes", "item"),
    ("item_quantity", "Provide the item quantity (positive integer)", "item"),
]

FIELD_TO_STEP = {field: step for field, _, step in FIELD_ORDER}


def _is_missing(order: OrderDraft, field: str) -> bool:
    value = getattr(order, field)
    if field == "agreement_accepted":
        return value is not True
    return value is None


def next_missing(order: OrderDraft) -> tuple[str, str] | None:
    """Return (field, prompt) for the first incomplete OrderDraft field, or None."""
    for field, prompt, _ in FIELD_ORDER:
        if _is_missing(order, field):
            return field, prompt
    return None


def step_for(field: str | None, order: OrderDraft | None = None) -> str:
    """Map a missing field to a step. None means confirm or done."""
    if field is None:
        if order is not None and order.confirmed is True:
            return "done"
        return "confirm"
    return FIELD_TO_STEP.get(field, "agreement")


def sync_step(state: AgentState) -> AgentState:
    """Align state.step with OrderDraft progress (recovers stale Redis steps)."""
    if state.order.confirmed is True:
        state.step = "done"
        return state
    missing = next_missing(state.order)
    if missing is None:
        state.step = "confirm"
    else:
        state.step = step_for(missing[0])
    return state


def format_progress_context(state: AgentState) -> str:
    """Build a short context block telling the agent what to ask for."""
    lines = ["Order draft status:"]
    for field, prompt, _ in FIELD_ORDER:
        value = getattr(state.order, field)
        if field == "agreement_accepted":
            status = "filled" if value is True else "missing"
        elif value is None:
            status = "missing"
        else:
            status = f"filled ({value})"
        lines.append(f"- {field}: {status}")

    if state.order.confirmed is True:
        lines.append("- confirmed: filled (True)")
        lines.append("Order is complete. Do not ask for more fields.")
        return "\n".join(lines)

    missing = next_missing(state.order)
    if missing is None:
        lines.append("- confirmed: missing")
        lines.append(
            "All draft fields are filled. Summarize the order and ask the user "
            "to confirm or decline. Call confirm_order when they clearly answer."
        )
    else:
        field, prompt = missing
        lines.append(f"Ask ONLY for: {field} — {prompt}")
        lines.append("Do not ask for later fields. Use tools to record answers.")

    return "\n".join(lines)
