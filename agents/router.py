"""LLM intent classifier for order-wizard message routing."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from config import llm
from helpers.order_progress import format_progress_context
from models.agentState import AgentState

Intent = Literal["continue_order", "show_draft", "faq", "edit"]

_VALID_INTENTS: frozenset[str] = frozenset(
    ("continue_order", "show_draft", "faq", "edit")
)
_DEFAULT_INTENT: Intent = "continue_order"


class RouteDecision(BaseModel):
    intent: Intent = Field(
        description=(
            "continue_order: user is answering or progressing the current order step. "
            "show_draft: user wants to see filled/missing order draft info. "
            "faq: side question (shipping, warehouse address, prohibited items, etc.). "
            "edit: user wants to change a field already filled in the draft."
        )
    )


def classify_intent(query: str, state: AgentState) -> Intent:
    """Classify the user message; default to continue_order on failure."""
    progress = format_progress_context(state)
    system = (
        "Classify the user's message for a Savostore order wizard.\n"
        f"Current step: {state.step}\n"
        f"{progress}\n\n"
        "Rules:\n"
        "- If they are clearly providing the next field value or accepting/declining "
        "the current step, use continue_order.\n"
        "- If they want to see what they have filled so far, use show_draft.\n"
        "- If they ask a side question unrelated to filling the current field, use faq.\n"
        "- If they want to change a value already recorded, use edit.\n"
        "- When unsure, prefer continue_order."
    )
    try:
        router_llm = llm.with_structured_output(RouteDecision)
        decision = router_llm.invoke(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": query},
            ]
        )
        intent = getattr(decision, "intent", None)
        if intent in _VALID_INTENTS:
            return intent  # type: ignore[return-value]
    except Exception:
        pass
    return _DEFAULT_INTENT
